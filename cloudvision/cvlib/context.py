# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import json
import signal
from collections.abc import Callable
from enum import IntEnum
from logging import getLogger
from time import process_time_ns
from typing import Any, Dict, List, Optional

import grpc
import requests
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import RpcError, StatusCode

from cloudvision.Connector.codec import Path
from cloudvision.Connector.grpc_client import (
    GRPCClient,
    create_notification,
    create_query,
)

from .action import Action
from .changecontrol import ChangeControl
from .connections import AuthAndEndpoints, addHeaderInterceptor
from .constants import (
    BUILD_ID_ARG,
    STUDIO_ID_ARG,
    STUDIO_IDS_ARG,
    TIMEOUT_REQUEST,
    TIMEOUT_REQUEST_DI,
    WORKSPACE_ID_ARG,
)
from .device import Device, Interface
from .exceptions import (
    ConnectionFailed,
    DeviceCommandsFailed,
    InvalidContextException,
    InvalidCredentials,
    LoggingFailed,
    TimeoutExpiry,
)
from .execution import Execution
from .logger import Logger
from .studio import Studio, StudioCustomData
from .tags import Tag, Tags
from .topology import Topology
from .user import User
from .utils import extractJSONEncodedListArg
from .workspace import Workspace

ACCESS_TOKEN = "access_token"
CMDS = "cmds"
DEVICE_ID = "deviceID"
EXEC_ACTION = "execaction"
HEADER_ACCEPT = "Accept"
HEADER_AUTH = "Authorization"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_JSON_APPLICATION = "application/json"
HEADERS = {HEADER_ACCEPT: HEADER_JSON_APPLICATION}
HOST = "host"
JSON = "json"
REQ_FORMAT = "format"
STOP_ON_ERROR = "stopOnError"
TIMEOUT_CLI = "readTimeout"
TIMEOUT_CONN = "connTimeout"
TMP_STORAGE_PATH = ["action", "tmp"]
USERNAME = "username"
DATASET_TYPE = "dataset_type"
ORGANIZATION = "organization"
GRPC_RETRY_POLICY_JSON = json.dumps(
    {
        "methodConfig": [
            {
                "name": [{"service": ""}],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "1s",
                    "maxBackoff": "16s",
                    "backoffMultiplier": 2.0,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }
        ]
    }
)

systemLogger = getLogger(__name__)


class LoggingLevel(IntEnum):
    Trace = 0,
    Debug = 1,
    Info = 2,
    Warn = 3,
    Error = 4,
    Critical = 5


def monitorTimerHandler(signum, frame):
    '''
    A handler function for the timer that will raise our custom exception
    Needs to be declared out here so that we can compare it to ensure that
    no ongoing timer is running
    '''
    raise TimeoutExpiry


class Context:
    '''
    Context object that stores a number of system and user-defined parameters:
    - user:           Info on the user executing this script
    - device:         Info on the device the script is operating on, if applicable
    - action:         Info on the action associated with the current context, if applicable
    - changeControl:  Common change-control script parameters (Deprecated, use action)
    - studio:         Common studio parameters
    - execution:      Info on the standalone execution context
    - connections:    Object storing connection info used by the context, e.g. apiserver address
    - logger:         Logging functions to be used by the context
    '''

    def __init__(self, user: User,
                 device: Optional[Device] = None,
                 action: Optional[Action] = None,
                 changeControl: Optional[ChangeControl] = None,
                 studio: Optional[Studio] = None,
                 execution: Optional[Execution] = None,
                 connections: Optional[AuthAndEndpoints] = None,
                 logger: Optional[Logger] = None,
                 loggingLevel: Optional[LoggingLevel] = None):
        self.user = user
        self.device = device
        self.action = action
        self.changeControl = changeControl
        self.studio = studio
        self.execution = execution
        # When connections is None, replace with an empty AuthAndEndpoints obj
        # so that further lookups succeed without throwing exceptions
        self.connections = connections if connections else AuthAndEndpoints()
        # In the case where the context is not passed a logger, create a backup one and use that
        self.logger = logger if logger else self.__getBackupLogger()
        self.__connector = None
        self.__serviceChann = None
        self.topology: Optional[Topology] = None
        self.preserveWhitespace = False
        self.loggingLevel = loggingLevel if loggingLevel else LoggingLevel.Info
        self.stats: Dict = {}
        self.benchmarking = False
        self.tags = Tags(self)
        self.studioCustomData = StudioCustomData(self)
        self.workspace: Optional[Workspace] = None

    def cleanup(self):
        '''
        Cleans up open channels and other connections
        Called by the script execution infra once a script or template has been executed
        '''
        if self.__connector:
            self.__connector.close()
        if self.__serviceChann:
            self.__serviceChann.close()

    def getDevice(self):
        '''
        Returns the device associated to the context.
        '''
        return self.device

    def getDeviceHostname(self, device: Device = None):
        '''
        Returns the hostname of the device associated to the context.
        Retrieves that information if the context device doesn't have it
        '''
        if not device:
            device = self.device
        if not device:
            raise InvalidContextException(("getDeviceHostname requires either a device or the"
                                           " calling context to have a device associated with it"))
        if not device.hostName:
            cmdResponse = self.runDeviceCmds(["enable", "show hostname"], device)
            if len(cmdResponse) != 2:
                raise DeviceCommandsFailed((f"'show hostname' failed on device {device.id}"
                                            f" with response: {cmdResponse}"))
            hostnameErr = cmdResponse[1].get('error')
            if hostnameErr:
                raise DeviceCommandsFailed((f"'show hostname' failed on device {device.id}"
                                            f" with error: {hostnameErr}"))
            device.hostName = cmdResponse[1]['response']['hostname']
        return device.hostName

    def setTopology(self, topology: Topology):
        '''
        Sets the topology of the context.
        Called during context initialisation during script execution,
        to set the Topology to that of the Inventory and Topology Studio.
        Does not need to be called by the script writers.
        '''
        self.topology = topology
        self.topology.setLogger(systemLogger)

        # Studios can have a device associated with it through it's inputs, which is only extracted
        # after the topology is set, not passed into the context at it's creation.
        # In the case where a device was not passed to the ctx, and a topology is set where there is
        # only a single device in the topology, set that device as the one used in the context
        if self.topology and self.studio and self.device is None:
            topologyDevs = self.topology.getDevices(self.studio.deviceIds)
            if len(topologyDevs) == 1:
                self.device = topologyDevs[0]

    def getCvClient(self):
        '''
        Instantiates a cloudvision connector client to the cv database
        based on the current user auth token
        :return: cloudvision Connector client
        '''
        if self.__connector:
            return self.__connector
        if self.connections.apiserverAddr is None or self.user is None:
            return None
        connector = GRPCClient(self.connections.apiserverAddr,
                               ca=self.connections.aerisCACert,
                               tokenValue=self.user.token)
        self.__connector = connector
        return connector

    def getApiClient(self, stub):
        '''
        Instantiates a resource api client to the service server
        based on the current user auth token and passed stub
        :param: stub of the resource api to connect to
        :return: resource api client to the passed stub
        '''
        def add_user_context(chann):
            # If provided, add the user context to the grpc metadata
            # This allows the context to access services correctly
            if self.user is not None:
                username_interceptor = addHeaderInterceptor(USERNAME, self.user.username)
                chann = grpc.intercept_channel(chann, username_interceptor)
            return chann

        if self.__serviceChann:
            return stub(self.__serviceChann)
        if self.connections.serviceAddr is None:
            systemLogger.error(
                "service address is None, trying to establish connection to apiserver")
            # use api server's secure grpc channel if service address is not provided
            if self.getCvClient():
                self.__serviceChann = self.getCvClient().channel
                self.__serviceChann = add_user_context(self.__serviceChann)
                return stub(self.__serviceChann)
            systemLogger.error(
                "cannot establish connection to apiserver: %s", self.__connector)
            raise ConnectionFailed("cannot establish connection to api server")

        # Verify that we have a correct token
        token = self.user.token
        if token is None:
            systemLogger.error("no valid token for authenticating the API Client")
            raise InvalidCredentials("no valid token for authenticating the API Client")

        # Try and read the ca cert
        caData = None
        if self.connections.serviceCACert:
            with open(self.connections.serviceCACert, 'rb') as cf:
                caData = cf.read()

        # Build the grpc connection with the token and the potential ca cert
        creds = grpc.ssl_channel_credentials(root_certificates=caData)
        tokCreds = grpc.access_token_call_credentials(token)
        creds = grpc.composite_channel_credentials(creds, tokCreds)
        channel_options = []
        channel_options.append(("grpc.enable_retries", 1))
        channel_options.append(("grpc.service_config", GRPC_RETRY_POLICY_JSON))
        self.__serviceChann = grpc.secure_channel(
            self.connections.serviceAddr, creds, channel_options
        )
        self.__serviceChann = add_user_context(self.__serviceChann)
        return stub(self.__serviceChann)

    def runDeviceCmds(self, commandsList: List[str], device: Optional[Device] = None, fmt=JSON,
                      validateResponse=True, timeout=TIMEOUT_REQUEST_DI, diConnTimeout=None,
                      diCliTimeout=None):
        '''
        Sends a post request to DI, encodes commandsList in message body.
        Receives output of cli commands from DI as json object.

        :param commandsList:
        :param device: device that the commands are run on.
                       Defaults to the context change control device if unspecified
        :param validateResponse: Validates that the commands ran successfully. Defaults to true and
                                 will raise an exception in the case an error message is present in
                                 the command response.
                                 Can be set to false to allow commands to run without raising any
                                 resultant error as an exception, e.g. device reboot commands can
                                 cause heartbeat error messages in the response, but we can discard
                                 them as the device will reboot.
        :param timeout: The timeout for the request from the script to DI.
                        Defaults to 5m if unspecified.
        :param diConnTimeout: The timeout for the follow-up request from the DI service
                              to the device. Defaults to 250s if unspecified
        :param diCliTimeout: The timeout for the follow-up request from the DI service to the.
                             device to complete the commands. Defaults to 200s if unspecified.

        :return: json object containing output of commandsList (if validateResponse is True)
                 OR
                 raw request response (if validateResponse is False)
        :raises: InvalidContextException when context is invalid for execution of device commands
                 requests.ConnectionError if connection cannot be established to the command
                 endpoint address
                 HTTPError if the status code from the command request is not a 200
                 DeviceCommandsFailed if validating command responses and the contents
                 contain an error code/message (can occur if request is a 200)
        '''
        if not self or not self.action:
            raise InvalidContextException(
                "runDeviceCmds is only available in action contexts")

        if device is None:
            if self.device is None:
                raise InvalidContextException(
                    "runDeviceCmds is only available when a device is set")
            device = self.device

        if not device.id:
            raise InvalidContextException(
                "runDeviceCmds requires a device with an id")

        if not self.connections.serviceAddr or not self.connections.commandEndpoint:
            raise InvalidContextException("runDeviceCmds must have a valid service "
                                          "address and command endpoint specified")

        # From the DI service documentation about the HOST field:
        # Host can be either IP address or hostname
        deviceInteractionHost = device.ip if device.ip else device.hostName
        diCliTo = diCliTimeout if diCliTimeout else self.connections.cliTimeout
        diConnTo = diConnTimeout if diConnTimeout else self.connections.connectionTimeout

        request = {
            HOST: deviceInteractionHost,
            DEVICE_ID: device.id,
            CMDS: commandsList,
            TIMEOUT_CLI: diCliTo,
            TIMEOUT_CONN: diConnTo,
            REQ_FORMAT: fmt,
            STOP_ON_ERROR: False
        }
        data = json.dumps(request)

        accessToken = ""
        if self:
            accessToken = self.user.token

        cookies = {ACCESS_TOKEN: accessToken}
        try:
            runCmdURL = f"https://{self.connections.serviceAddr}/{self.connections.commandEndpoint}"
            self.debug(f"Executing the following command(s) on device {device.id}: {commandsList}")
            response = requests.post(runCmdURL, data=data, headers=HEADERS,
                                     cookies=cookies, timeout=timeout, verify=False)
        except requests.ConnectionError as e:
            self.error(f"Got exception while establishing connection to DI : {e}")
            raise

        self.debug(f"Status code received from DI : {response.status_code}")
        if response.status_code != 200:
            response.raise_for_status()

        # In the case where a response is not validated do not check for errors or convert
        # the response to JSON. Simply return it as-is
        if not validateResponse:
            return response

        resp = response.json()
        # Check that some other issue did not occur. It has been seen that a statuscode 200 was
        # received for the response, but when the response contents are jsonified and returned,
        # they can be a simple dictionary with two entries, 'errorCode' and 'errorMessage',
        # instead of the usual list of dictionaries for each command response.
        # This is not caused by the commands that the user provided, but is an issue with
        # the request that was sent to the command endpoint
        # If that occurs, raise a DeviceCommandsFailedException
        # An example of this is {'errorCode': '341604', 'errorMessage': 'Invalid request'}
        if all(key in resp for key in ["errorCode", "errorMessage"]):
            errCode = resp["errorCode"]
            errMsg = resp["errorMessage"]
            raise DeviceCommandsFailed((f"Commands failed to run on device \"{device.id}\","
                                        f" returned {errCode}:\"{errMsg}\""), errCode, errMsg)

        # Check that none of the commands have outright failed
        for i, cmdResp in enumerate(resp):
            err = cmdResp.get("error")
            if err:
                raise DeviceCommandsFailed((f"Command \"{commandsList[i]}\" failed to run on "
                                           f"device \"{device.id}\", returned {err}"))

        return resp

    @staticmethod
    def doWithTimeout(f, timeout: int):
        '''
        Takes a function and a timeout in seconds.
        Will call and return the result of f, but raises a cvlib.TimeoutExpiry
        exception if it runs longer than <timeout>
        NOTE: If there is an attempt to recursively call this function, an InvalidContextException
        will be raised.
        '''

        # Store the default alarm signal so we can set it back again when we're done
        originalSigHandler = signal.getsignal(signal.SIGALRM)
        # Ensure that the current signal is not the monitorTimerHandler which would indicate a
        # recursive call. This is not supported as due to any ongoing alarm timeouts of previous
        # calls will be be overwritten and we can only have 1 alarm at a time.
        if originalSigHandler is monitorTimerHandler:
            raise InvalidContextException("Cannot recursively call doWithTimeout")

        # Set up a signal handler that will cause a signal.SIGALRM signal to trigger our timer
        # handler
        signal.signal(signal.SIGALRM, monitorTimerHandler)
        # Set an alarm to fire in <timeout> seconds. This will call the handler we bound earlier
        signal.alarm(timeout)

        try:
            return f()
        finally:
            # Always turn off the alarm, whether returning a value or propagating an exception
            signal.alarm(0)
            # Reset the alarm signal handler
            signal.signal(signal.SIGALRM, originalSigHandler)

    def initializeStudioCtxFromArgs(self):
        '''
        initializeStudioCtxFromArgs associates studio(s) and a workspace with the current
        context from argument information available in the current context's action class.
        This allows for actions such as Studio Autofill Actions and Studio Build Hook Actions
        to associate a studio with their active contexts, allowing them to access various helper
        methods that require the presence of a studio or workspace with the active context,
        such as those offered by the tags class.

        NOTE: Will raise InvalidContextException if called and either a studio is already
        bound to the context or no action is available in the context
        '''
        if self.studio or self.workspace:
            raise InvalidContextException(
                "initializeStudioCtxFromArgs already has studio ctx initialised")
        if not self.action:
            raise InvalidContextException("initializeStudioCtxFromArgs must be"
                                          " run in an action context")

        buildId = self.action.args.get(BUILD_ID_ARG)
        # Will be set if action is in a studio scope
        studioId = self.action.args.get(STUDIO_ID_ARG)
        # Will be present for some execution contexts, e.g. Studio Build Hook actions
        studioIdsStr = self.action.args.get(STUDIO_IDS_ARG)
        workspaceId = self.action.args.get(WORKSPACE_ID_ARG)
        studioIds = None
        if studioIdsStr:
            try:
                studioIds = extractJSONEncodedListArg(studioIdsStr)
            except ValueError as e:
                self.warning((f"Unable to extract json encoded list '{STUDIO_IDS_ARG}': {e}\n"
                              f"Ignoring {STUDIO_IDS_ARG} contents"))
        if not workspaceId:
            raise InvalidContextException(
                ("initializeStudioCtxFromArgs: Missing minimum required argument"
                 f" {WORKSPACE_ID_ARG} for studio ctx initialisation"))
        self.workspace = Workspace(
            workspaceId=workspaceId,
            studioIds=studioIds,
            buildId=buildId
        )
        if studioId:
            self.studio = Studio(
                workspaceId=workspaceId,
                studioId=studioId,
                buildId=buildId
            )

    def getWorkspaceId(self):
        if not (self.workspace or self.studio):
            raise InvalidContextException(("Context does not have a workspace or studio "
                                          "associated with it"))
        return self.workspace.id if self.workspace else self.studio.workspaceId

    def httpGet(self, path: str):
        '''
        Issues a https GET to a given endpoint in CloudVision and returns the json
        content if there are no errors
        '''
        if not (self.user and self.user.token):
            raise InvalidContextException("httpGet requires an authenticated"
                                          + " user associated with the context")

        if not self.connections.serviceAddr:
            raise InvalidContextException("httpGet must have a valid service address specified")

        # Perform a split to ensure to drop any ports that are provided as part of the serviceAddr
        url = "https://" + self.connections.serviceAddr.split(':', maxsplit=1)[0]
        endpoint = url + path
        headers = {
            HEADER_ACCEPT: HEADER_JSON_APPLICATION,
            HEADER_CONTENT_TYPE: HEADER_JSON_APPLICATION,
            HEADER_AUTH: f"Bearer {self.user.token}"
        }
        try:
            response = requests.get(endpoint, headers=headers, verify=False)
            response.raise_for_status()
            respJson = json.loads(response.text)
        except requests.ConnectionError as e:
            self.error(f"Got exception while establishing connection to url '{endpoint}': {e}")
            raise
        except requests.HTTPError as e:
            self.error(f"Got error response from get on '{endpoint}': {e}")
            raise
        return respJson

    def httpGetConfig(self, path: str):
        '''
        Issues a http get to retrieve the device config content at a cvp url and formats it.
        '''
        rawConfig = self.httpGet(path).get('config')
        if not rawConfig:
            return ""
        formattedConfig = rawConfig.replace('\\n', '\n').replace('\\t', '\t')
        return formattedConfig

    def httpPost(self, path, request={}):
        '''
        Issues a https POST to a given endpoint in CloudVision
        '''
        data = json.dumps(request)

        if not (self.user and self.user.token):
            raise InvalidContextException("httpPost requires an authenticated"
                                          + " user associated with the context")

        if not self.connections.serviceAddr:
            raise InvalidContextException("httpPost must have a valid service address specified")

        # Perform a split to ensure to drop any ports that are provided as part of the serviceAddr
        url = "https://" + self.connections.serviceAddr.split(':', maxsplit=1)[0]
        endpoint = url + path
        headers = {
            HEADER_ACCEPT: HEADER_JSON_APPLICATION,
            HEADER_CONTENT_TYPE: HEADER_JSON_APPLICATION,
            HEADER_AUTH: f"Bearer {self.user.token}"
        }
        try:
            response = requests.post(endpoint, data=data, headers=headers, verify=False)
            response.raise_for_status()
        except requests.ConnectionError as e:
            self.error(f"Got exception while establishing connection to url '{endpoint}': {e}")
            raise
        except requests.HTTPError as e:
            self.error(f"Got error response from get on '{endpoint}': {e}")
            raise

    def Get(self, path: List[str], keys: List[str] = [], dataset: str = "analytics"):
        '''
        Get issues a get request to the provided path/key(s) combo, and returns the contents
        of that path as a dictionary. Wildcarding is not advised as the returned dictionary
        is only a single level deep, so adding wildcards will cause overwrites in the results.

        Params:
        - path:     The path to issue the get to, in the form of a list of strings
        - keys:     The key(s) to get at the path. Defaults to all keys
        - dataset:  The dataset to issue the get to. Defaults to the `analytics` dataset
        '''
        client: GRPCClient = self.getCvClient()
        query = create_query(pathKeys=[(path, keys)], dId=dataset)

        results = {}
        for batch in client.get([query]):
            for notif in batch["notifications"]:
                results.update(notif.get("updates", {}))
        return results

    def _getGenericKey(self) -> str:
        '''
        Creates a generic key for use in store/retrieve based off of the available
        context information such that overwrites will be done on successive runs of
        the same calling studio/WS or action.

        When building the key based on the context;
        - If it is a studio context, the key generated will be in the form of
          "<studioId>:<buildId>" if a build ID is present, else "<studioId>"
        - If it is an action context, the key generated will be in the form of
          "<executionID>"

        Raises InvalidContextException if not enough context information is present
        to create a key
        '''
        if self.studio is not None:
            if self.studio.buildId:
                return ":".join([self.studio.studioId, self.studio.buildId])
            return self.studio.studioId
        if self.action and self.execution:
            return self.execution.executionId
        raise InvalidContextException(
            "store/retrieve without key requires a studio or action in the context")

    def _getStoragePath(self, additionalElems: List[str] = []) -> List[str]:
        '''
        Builds a generic path for use in store/retrieve based off of either the passed
        additional elements provided by the user or the available context information.
        All paths will contain "action/tmp" as the root.

        When building a path based on the context;
        - If it is a studio context, the path generated will be in the form of
          /action/tmp/workspace/<workspaceId>/studio
        - If it is an action context, the path generated will be in the form of
          /action/tmp/action/<actionId>

        Raises InvalidContextException if no additional elems were passed by the user
        and not enough context information is present to create a path
        '''
        storage_path = TMP_STORAGE_PATH.copy()
        if additionalElems:
            storage_path.extend(additionalElems)
            return storage_path
        if self.studio and self.studio.workspaceId:
            storage_path.extend(["workspace", self.studio.workspaceId, "studio"])
            return storage_path
        if self.action and self.action.id:
            storage_path.extend(["action", self.action.id])
            return storage_path
        raise InvalidContextException(
            "store without specified path requires a studio or action in the context")

    def store(self, data, path: List[str] = [], customKey=""):
        '''
        store puts the passed data into a path in the Database

        NOTE: This function is only available to those with write permissions to the
        'action' path in the cvp dataset (granted by the action module), as that is
        where the store is.

        This should be used in conjunction with the retrieve method to ensure that
        the entry is cleaned up after use.

        Params:
        - data:      The data to store
        - path:      The path to store the data at, in the form of a list of strings.
                     If this argument is omitted, a generic path will be created for
                     use. All paths have "action/tmp" as the root.
        - customKey: The key to store the data at in the path. If this argument is
                     omitted, a generic string key will be created for use.

        Raises InvalidContextException if not enough context information is
        present to create a generic key/path (if required)
        '''
        key = customKey if customKey else self._getGenericKey()
        storagePath = self._getStoragePath(additionalElems=path)
        update = [(key, data)]
        ts = Timestamp()
        ts.GetCurrentTime()
        notifs = [create_notification(ts, storagePath, updates=update)]
        # Generate the list of path pointer notifs that lead to the new entry
        for i, pathElem in enumerate(storagePath):
            if i == 0:
                # We don't want to keep writing the path pointer to actions
                # in the top level of the cvp dataset
                continue
            pathPointerPath = storagePath[:i]
            pathPointerUpdate = [(pathElem, Path(keys=storagePath[:i + 1]))]
            notifs.append(create_notification(ts, pathPointerPath, updates=pathPointerUpdate))
        try:
            self.getCvClient().publish(dId="cvp", notifs=notifs)
        except RpcError as exc:
            # If the exception is not a permissions error, reraise the original
            # exception as something went wrong
            if exc.code() != StatusCode.PERMISSION_DENIED:
                raise
            raise InvalidCredentials(
                f"Context user does not have permission to write to path '{storagePath}'")

    def retrieve(self, path: List[str] = [], customKey="", delete=True):
        '''
        retrieve gets the passed key's data from the provided path from the
        Database store.

        NOTE: This function is only available to those with read permissions to the
        'action' path in the cvp dataset (granted by the action module), as that is
        where the store is.

        Params:
        - path:      The path where the data is stored at, in the form of a list
                     of strings. If this argument is omitted, a generic path will be
                     created for use. All paths have "action/tmp" as the root.
        - customKey: The key where the data is stored at in the path. If this argument
                     is omitted, a generic string key will be created for use.
        - delete:    Boolean flag marking whether a delete should be issued to the
                     store for the key/path combo to clean up after use.
                     Deleting once the contents have been retrieved is the default.

        Raises InvalidContextException if not enough context information is
        present to create a generic key/path (if required)
        '''
        key = customKey if customKey else self._getGenericKey()
        storagePath = self._getStoragePath(additionalElems=path)
        try:
            results = self.Get(path=storagePath, keys=[key], dataset="cvp")
        except RpcError as exc:
            # If the exception is not a permissions error, reraise the original
            # exception as something went wrong
            if exc.code() != StatusCode.PERMISSION_DENIED:
                raise
            raise InvalidCredentials(
                f"Context user does not have permission to read from path '{storagePath}'")
        if delete:
            ts = Timestamp()
            ts.GetCurrentTime()
            try:
                self.getCvClient().publish(
                    dId="cvp", notifs=[create_notification(ts, storagePath, deletes=[key])])
            except RpcError as exc:
                # If the exception is not a permissions error, reraise the original
                # exception as something went wrong
                if exc.code() != StatusCode.PERMISSION_DENIED:
                    raise
                raise InvalidCredentials(
                    f"Context user does not have permission to write to path '{storagePath}'")
        return results.get(key)

    def clear(self, path: List, keys: List = [], fullPathOnly: bool = False):
        """
        clear issues deletes to the backend data store for cleanup, where retrieve with
        delete is not required or not suitable. By default, it walks upwards through
        each element in the path provided and issues a delete-all at each sub-path
        to purge the information store. The fullPathOnly flag can be set to true to only
        issue a deletes to the full path, instead of at all sub-paths in the path. A list
        of keys to specifically delete can be provided to only delete those fields.

        NOTE: While this function accepts wildcards, note that using them may
        impact other storage paths used in other actions.

        Params:
        - path:         The path where the data should be purged, in the form of a list
                        of strings or Connector Wildcards.
        - keys:         The list of keys to delete. Defaults to a delete-all.
        - fullPathOnly: Boolean flag marking whether a delete-all should only be issued
                        to the store for full path.
                        By default, deletes are issued at all sub-paths.
        """
        storagePath = self._getStoragePath(additionalElems=path)
        client = self.getCvClient()
        ts = Timestamp()
        ts.GetCurrentTime()
        # Repeatedly issue delete-alls until we reach the root storage path
        while len(storagePath) > len(TMP_STORAGE_PATH):
            client.publish(dId="cvp",
                           notifs=[create_notification(ts, storagePath, deletes=keys)])
            if fullPathOnly:
                break
            storagePath.pop()

    @staticmethod
    def showIf(linefmt, args):
        if args:
            return linefmt.format(args)
        return ''

    def alog(self, message, userName=None, customKey=None, tags: Dict[str, str] = None,
             ignoreFailures=False):
        """
        Creates an audit log entry in CloudVision, with the provided info.
        The context's associated device name and id will be added to the audit log metadata
        if it is available in the context.

        Note: This method is a no-op when run in a Studio template rendering context. Use the
        preferred ctx.info, ctx.error, ctx.debug etc. logging methods there instead.

        Args:
            message:        The string message for the audit log entry
            userName:       The user to make the audit log entry under. If unspecified, will
                            use the context's user's username
            customKey:      A custom key that will be used to alias the audit log entry if provided
            tags:           A string dictionary of additional custom tags to add to the audit log
                            entry. The action ID is always added as a tag to the audit log
            ignoreFailures: Prevents logging exceptions from being raised
        """
        try:
            self.logger.alog(self, message, userName, customKey, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def trace(self, msg, ignoreFailures=False, tags: Dict[str, str] = None):
        """
        Creates a trace level log if the context's logging level is set to allow for it
        If the logging level is higher, is a no-op
        Args:
            msg:            The string message for the  log entry
            ignoreFailures: Prevents logging exceptions from being raised
            tags:           A string dictionary of additional custom tags to add to the log
                            entry. Some system tags are always inserted, e.g. buildID
                            when logging is done in a studio context.
        """
        if self.getLoggingLevel() > LoggingLevel.Trace:
            return
        try:
            self.logger.trace(self, msg, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def debug(self, msg, ignoreFailures=False, tags: Dict[str, str] = None):
        """
        Creates a debug level log if the context's logging level is set to allow for it
        If the logging level is higher, is a no-op
        Args:
            msg:            The string message for the  log entry
            ignoreFailures: Prevents logging exceptions from being raised
            tags:           A string dictionary of additional custom tags to add to the log
                            entry. Some system tags are always inserted, e.g. buildID
                            when logging is done in a studio context.
        """
        if self.getLoggingLevel() > LoggingLevel.Debug:
            return
        try:
            self.logger.debug(self, msg, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def info(self, msg, ignoreFailures=False, tags: Dict[str, str] = None):
        """
        Creates an info level log if the context's logging level is set to allow for it
        If the logging level is higher, is a no-op
        Args:
            msg:            The string message for the  log entry
            ignoreFailures: Prevents logging exceptions from being raised
            tags:           A string dictionary of additional custom tags to add to the log
                            entry. Some system tags are always inserted, e.g. buildID
                            when logging is done in a studio context.
        """
        if self.getLoggingLevel() > LoggingLevel.Info:
            return
        try:
            self.logger.info(self, msg, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def warning(self, msg, ignoreFailures=False, tags: Dict[str, str] = None):
        """
        Creates a warning level log if the context's logging level is set to allow for it
        If the logging level is higher, is a no-op
        Args:
            msg:            The string message for the  log entry
            ignoreFailures: Prevents logging exceptions from being raised
            tags:           A string dictionary of additional custom tags to add to the log
                            entry. Some system tags are always inserted, e.g. buildID
                            when logging is done in a studio context.
        """
        if self.getLoggingLevel() > LoggingLevel.Warn:
            return
        try:
            self.logger.warning(self, msg, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def error(self, msg, ignoreFailures=False, tags: Dict[str, str] = None):
        """
        Creates an error level log if the context's logging level is set to allow for it
        If the logging level is higher, is a no-op
        Args:
            msg:            The string message for the  log entry
            ignoreFailures: Prevents logging exceptions from being raised
            tags:           A string dictionary of additional custom tags to add to the log
                            entry. Some system tags are always inserted, e.g. buildID
                            when logging is done in a studio context.
        """
        if self.getLoggingLevel() > LoggingLevel.Error:
            return
        try:
            self.logger.error(self, msg, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def critical(self, msg, ignoreFailures=False, tags: Dict[str, str] = None):
        """
        Creates a critical level log
        Args:
            msg:            The string message for the  log entry
            ignoreFailures: Prevents logging exceptions from being raised
            tags:           A string dictionary of additional custom tags to add to the log
                            entry. Some system tags are always inserted, e.g. buildID
                            when logging is done in a studio context.
        """
        try:
            self.logger.critical(self, msg, tags)
        except LoggingFailed:
            if not ignoreFailures:
                raise

    def keepBlankLines(self, preserve=True):
        # This function is only relevant for Studio Templates.
        # Script executor code introspects this value to decide whether to
        # clean rendered templates post-rendering
        self.preserveWhitespace = preserve

    def setLoggingLevel(self, loggingLevel: LoggingLevel):
        """
        Takes a logging level value and applies it for use in logging call checks
        """
        self.loggingLevel = loggingLevel

    def getLoggingLevel(self):
        """
        Gets the current logging level of the context
        """
        return self.loggingLevel

    def activateDebugMode(self):
        """
        Activates debug logging by setting the logging level to debug
        """
        self.loggingLevel = LoggingLevel.Debug

    def deactivateDebugMode(self):
        """
        Deactivates debug logging by setting the logging level to info
        """
        self.loggingLevel = LoggingLevel.Info

    # In the case where the context has no logger defined,
    # we can create a compatible backup logger using the system logger
    # This is called in init if no logger is provided
    def __getBackupLogger(self) -> Logger:
        def backupAlog(_, message, _userName=None, _customKey=None, tags=None):
            systemLogger.info(message)

        def backupDebugOrTrace(_, message, tags=None):
            systemLogger.debug(message)

        def backupInfo(_, message, tags=None):
            systemLogger.info(message)

        def backupWarning(_, message, tags=None):
            systemLogger.warning(message)

        def backupError(_, message, tags=None):
            systemLogger.error(message)

        def backupCritical(_, message, tags=None):
            systemLogger.critical(message)

        return Logger(
            alog=backupAlog,
            trace=backupDebugOrTrace,
            debug=backupDebugOrTrace,
            info=backupInfo,
            warning=backupWarning,
            error=backupError,
            critical=backupCritical
        )

    def benchmarkingOn(self):
        '''
        Turns on benchmarking to collect stats such as time consumed in a routine
        of the template
        To use add the following lines into the template:
            ctx.benchmarkingOn()   - place this as the first line after imports in the template
            @ctx.benchmark         - decorate the functions of the template to be benchmarked
            ctx.benchmarkDump()    - place this as the last line in the template
        '''
        self.benchmarking = True

    def benchmarkingOff(self):
        self.benchmarking = False

    def benchmark(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            startTime = process_time_ns()
            result = func(*args, **kwargs)
            timer = process_time_ns() - startTime
            if not self.stats.get(func.__name__):
                self.stats[func.__name__] = {'sum': 0, 'count': 0, 'instances': []}

            self.stats[func.__name__]['count'] += 1
            self.stats[func.__name__]['sum'] += timer
            self.stats[func.__name__]['instances'].append(timer)
            return result
        if not self.benchmarking:
            return func
        return wrapper

    def benchmarkDump(self):
        if not self.stats:
            return
        self.logger.info(self, f'benchmarks for device {self.device.id}:')
        for fun, timings in self.stats.items():
            timings['sum'] = timings['sum'] / 1e9
            timings['average'] = timings['sum'] / timings['count']

        self.logger.info(self,
                         f"{'functions':<40}:{'total(s)':>8}{'avg(s)':>8}"
                         + f"{'count':>10}")
        self.logger.info(self, "-" * 40 + "-" * 8 + "-" * 8 + "-" * 11)
        for fun, timings in dict(sorted(self.stats.items(),
                                 key=lambda item: item[1]['sum'],
                                 reverse=True)).items():
            self.logger.info(self,
                             f"{fun:<40}:{timings['sum']:>8.4f}{timings['average']:>8.4f}"
                             + f"{timings['count']:>10}")

    def getDevicesByTag(self, tag: Tag, inTopology: bool = True):
        '''
        Returns list of devices that have the user tag assigned to them.
        If tag.value is unspecified then returns devices having that label assigned.
        By default only devices in the topology are returned.
        '''
        devices = []
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for devId in list(allTags := self.tags._getAllDeviceTags()):
            tags = allTags.get(devId, {})
            if tags.get(tag.label) and (
                    not tag.value or tag.value in tags.get(tag.label, [])):
                if dev := self.topology._deviceMap.get(devId) if self.topology else None:
                    devices.append(dev)
                elif not inTopology:
                    devices.append(Device(deviceId=devId))
        return devices

    def getInterfacesByTag(self, tag: Tag, inTopology: bool = True):
        '''
        Returns list of interfaces that have the user tag assigned to them.
        If tag.value is unspecified then returns interfaces having that label assigned.
        By default only interfaces in the topology are returned.
        '''
        interfaces = []
        # Note use list instead of .items()
        # parallel thread might add/delete tags
        for devId in list(allTags := self.tags._getAllInterfaceTags()):
            for intfId in list(devIntfTags := allTags.get(devId, {})):
                tags = devIntfTags.get(intfId, {})
                if tags.get(tag.label) and (
                        not tag.value or tag.value in tags.get(tag.label, [])):
                    if dev := self.topology._deviceMap.get(devId) if self.topology else None:
                        if intf := dev.getInterface(intfId):
                            interfaces.append(intf)
                        elif not inTopology:
                            interfaces.append(Interface(name=intfId, device=dev))
                    elif not inTopology:
                        interfaces.append(
                            Interface(name=intfId,
                                      device=Device(deviceId=devId)))
        return interfaces
