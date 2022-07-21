# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import json
from logging import getLogger
from typing import List, Optional
import signal
import requests
from google.protobuf.timestamp_pb2 import Timestamp

from cloudvision.Connector.grpc_client import GRPCClient, create_notification, create_query

from .action import Action
from .changecontrol import ChangeControl
from .topology import Topology
from .connections import addHeaderInterceptor, AuthAndEndpoints
from .device import Device
from .execution import Execution
from .exceptions import DeviceCommandsFailed, InvalidContextException, TimeoutExpiry
from .logger import Logger
from .studio import Studio
from .user import User

import grpc

ACCESS_TOKEN = "access_token"
CMDS = "cmds"
DEVICE_ID = "deviceID"
EXEC_ACTION = "execaction"
HEADERS = {"Accept": "application/json"}
HOST = "host"
JSON = "json"
REQ_FORMAT = "fmt"
STOP_ON_ERROR = "stopOnError"
TIMEOUT_CLI = "timeout"
TIMEOUT_CONN = "connTimeout"
USERNAME = "username"

systemLogger = getLogger(__name__)


class Context:
    '''
    Context object that stores a number of system and user-defined parameters:
    - user:           Info on the user executing this script
    - device:         Info on the device the script is operating on, if applicable
    - action:         Info on the action associated with the current context, if applicable
    - changeControl:  Common change-control script parameters
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
                 logger: Optional[Logger] = None):
        self.user = user
        self.device = device
        self.action = action
        self.changeControl = changeControl
        self.studio = studio
        self.execution = execution
        # When connections is None, replace with an empty AuthAndEndpoints obj
        # so that further lookups succeed without throwing exceptions
        self.connections = connections if connections else AuthAndEndpoints()
        self.logger = logger
        # In the case where the context is not passed a logger, create a backup one and use that
        if not self.logger:
            self.__useBackupLogger()
        self.__connector = None
        self.__serviceChann = None
        self.topology: Optional[Topology] = None
        self.preserveWhitespace = False

    def getDevice(self):
        '''
        Returns the device associated to the context.
        '''
        return self.device

    def getDeviceHostname(self):
        '''
        Returns the hostname of the device associated to the context.
        Retrieves that information if the context device doesn't have it
        '''
        if not self.device:
            raise InvalidContextException(
                "Context does not have device associated with it")
        if not self.device.hostName:
            cmdResponse = self.runDeviceCmds(["enable", "show hostname"])
            if len(cmdResponse) != 2:
                raise DeviceCommandsFailed((f"'show hostname' failed on device {self.device.id}"
                                            f" with response: {cmdResponse}"))
            hostnameErr = cmdResponse[1].get('error')
            if hostnameErr:
                raise DeviceCommandsFailed((f"'show hostname' failed on device {self.device.id}"
                                            f" with error: {hostnameErr}"))
            self.device.hostName = cmdResponse[1]['response']['hostname']
        return self.device.hostName

    def setTopology(self, topology: Topology):
        '''
        Sets the topology of the context.
        Called during context initialisation during script execution
        Does not need to be called by the script writers
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
        # Use test api addresses for client if they were set
        if self.connections.testAddresses:
            testAddr = self.connections.testAddresses.get("apiServer")
            if not testAddr:
                return None
            return GRPCClient(testAddr)

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

        # Use test api addresses for client if they were set
        if self.connections.testAddresses:
            testAddr = self.connections.testAddresses.get(stub.__name__)
            if not testAddr:
                return None
            chann = grpc.insecure_channel(testAddr)
            chann = add_user_context(chann)
            stubChann = stub(chann)
            return stubChann

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
            return None

        # Verify that we have a correct token
        token = self.user.token
        if token is None:
            systemLogger.error("no valid token for authenticating the API Client")
            return None

        # Try and read the ca cert
        caData = None
        if self.connections.serviceCACert:
            with open(self.connections.serviceCACert, 'rb') as cf:
                caData = cf.read()

        # Build the grpc connection with the token and the potential ca cert
        creds = grpc.ssl_channel_credentials(root_certificates=caData)
        tokCreds = grpc.access_token_call_credentials(token)
        creds = grpc.composite_channel_credentials(creds, tokCreds)
        self.__serviceChann = grpc.secure_channel(self.connections.serviceAddr, creds)
        self.__serviceChann = add_user_context(self.__serviceChann)
        return stub(self.__serviceChann)

    def runDeviceCmds(self, commandsList: List[str], device: Optional[Device] = None, fmt=JSON):
        '''
        Sends a post request to DI, encodes commandsList in message body.
        Receives output of cli commands from DI as json object
        :param commandsList:
        :param device: device that the commands are run on.
                       Defaults to the context change control device if unspecified
        :return: json object containing output of commandsList
        '''
        if not self or not self.changeControl:
            raise InvalidContextException(
                "runDeviceCmds is only available during change controls")

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

        request = {
            HOST: deviceInteractionHost,
            DEVICE_ID: device.id,
            CMDS: commandsList,
            TIMEOUT_CLI: self.connections.connectionTimeout,
            TIMEOUT_CONN: self.connections.cliTimeout,
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
            self.debug(f"Executing command : {runCmdURL}")
            response = requests.post(runCmdURL, data=data, headers=HEADERS,
                                     cookies=cookies, verify=False)
        except requests.ConnectionError as e:
            self.error(f"Got exception while establishing connection to DI : {e}")
            raise e

        self.debug(f"Status code received from DI : {response.status_code}")
        if response.status_code != 200:
            response.raise_for_status()
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
        return resp

    @staticmethod
    def doWithTimeout(f, timeout: int):
        '''
        Takes a function and a timeout in seconds.
        Will call and return the result of f, but raises a cvlib.TimeoutExpiry
        exception if it runs longer than <timeout>
        '''

        # A handler function for the timer that will raise our custom exception
        def monitorTimerHandler(signum, frame):
            raise TimeoutExpiry

        # Set up a signal handler that will cause a signal.SIGALRM signal to trigger our timer handler
        signal.signal(signal.SIGALRM, monitorTimerHandler)
        # Set an alarm to fire in <timeout> seconds. This will call the handler we bound earlier
        signal.alarm(timeout)
        result = f()
        # Turn off the alarm as the function has been executed successfully
        signal.alarm(0)
        return result

    def Get(self, path: List[str], dataset="analytics"):
        if not isinstance(path, List) or any([not(isinstance(i, str)) for i in path]):
            raise TypeError("path should be a list of type string")
        client: GRPCClient = self.getCvClient()
        query = create_query(pathKeys=[(path, [])], dId=dataset)
        try:
            return list(client.get([query]))[0]["notifications"][0]["updates"]
        except (IndexError, KeyError) as e:
            self.error(str(e))
            return []

    def _get_key(self, key: str = None) -> str:
        if key is None:
            if self.studio is not None:
                key = self.studio.studioId + self.studio.workspaceId
            elif self.action is not None and self.device is not None and self.device.id is not None:
                key = self.device.id + self.action.name
            else:
                raise InvalidContextException("""
If calling store without a key, please provide a studio or changeControl object to the context
                                             """)
        return key

    def _get_path(self, path: str = None) -> List[str]:
        save_path = ["changecontrol", "actionTempStorage"]
        if path is not None:
            save_path.append(path)
        elif self.action is not None:
            save_path.append(self.action.name)
        elif self.studio is not None:
            save_path.append(self.studio.studioId)
        else:
            raise InvalidContextException("""
If calling store without a path, please provide a studio or changeControl object to the context
                                         """)
        return save_path

    def store(self, data, path: str = None, key: str = None):
        key = self._get_key(key)
        save_path = self._get_path(path)
        update = [(key, data)]
        client: GRPCClient = self.getCvClient()
        ts = Timestamp()
        ts.GetCurrentTime()
        client.publish(dId="cvp", notifs=[create_notification(ts, save_path, updates=update)])

    def retrieve(self, path: str = None, key: str = None, delete=True):
        key = self._get_key(key)
        save_path = self._get_path(path)
        client: GRPCClient = self.getCvClient()
        query = create_query(pathKeys=[(save_path, [key])], dId="cvp")
        data = client.get([query])
        if delete:
            ts = Timestamp()
            ts.GetCurrentTime()
            client.publish(dId="cvp", notifs=[create_notification(ts, save_path, deletes=[key])])
        return data

    @staticmethod
    def showIf(linefmt, args):
        if args:
            return linefmt.format(args)
        return ''

    def alog(self, message, userName=None, customKey=None):
        self.logger.alog(self, message, userName, customKey)

    def trace(self, msg):
        self.logger.trace(self, msg)

    def debug(self, msg):
        self.logger.debug(self, msg)

    def info(self, msg):
        self.logger.info(self, msg)

    def warning(self, msg):
        self.logger.warning(self, msg)

    def error(self, msg):
        self.logger.warning(self, msg)

    def critical(self, msg):
        self.logger.critical(self, msg)

    def keepBlankLines(self, preserve=True):
        # This function is only relevant for Studio Templates.
        # Script executor code introspects this value to decide whether to
        # clean rendered templates post-rendering
        self.preserveWhitespace = preserve

    # In the case where the context has no logger defined,
    # we can create a compatible backup logger using the system logger
    # This is called in init if no logger is provided
    def __useBackupLogger(self):
        def backupAlog(_, message, _userName=None, _customKey=None):
            systemLogger.info(message)

        def backupTrace(_, message):
            systemLogger.debug(message)

        def backupDebug(_, message):
            systemLogger.debug(message)

        def backupInfo(_, message):
            systemLogger.info(message)

        def backupWarning(_, message):
            systemLogger.warning(message)

        def backupError(_, message):
            systemLogger.error(message)

        def backupCritical(_, message):
            systemLogger.critical(message)

        backupLogger = Logger(
            alog=backupAlog,
            trace=backupTrace,
            debug=backupDebug,
            info=backupInfo,
            warning=backupWarning,
            error=backupError,
            critical=backupCritical
        )
        self.logger = backupLogger
