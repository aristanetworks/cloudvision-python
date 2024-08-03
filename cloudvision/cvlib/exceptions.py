# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import List, Optional


class CVException(Exception):
    """Overarching base exception class for all cloudvision exceptions"""

    def __init__(self, message: str = "cloudvision has encountered an error"):
        self.message = message
        super().__init__(self.message)


# -------------------------- Common Exceptions --------------------------

class InvalidContextException(CVException):
    """Exception raised when context methods are called invalidly"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidCredentials(CVException):
    """Exception raised if provided credentials are invalid"""

    def __init__(self, message: str = "provided credentials were not valid"):
        super().__init__(message)


class ConnectionFailed(CVException):
    """
    Exception raised when a connection to the CloudVision API Server
    could not be established, or if it was unexpectedly closed
    """

    def __init__(self, message: str = "connection issue with the CloudVision API server"):
        super().__init__(message)


# ------------------------ Generic Script Execution Exceptions ------------------------


class ScriptException(CVException):
    """Overarching class for Script exceptions"""

    def __init__(self, message: str = "cloudvision has encountered a script error"):
        super().__init__(message)


class ActionFailed(ScriptException):
    """
    Exception to raise if you wish to fail a script or autofill action being executed.

    For the case of a script action, e.g. CCA, it means that the user has declared
    that the action has failed due to some condition being met or missed. This is
    "expected" in the sense that the action did not hit an unexpected exception.

    In the autofill action case, it means the autofill could not be completed due to
    some expected reason (e.g. could not reach IPAM or IPAM block was exhausted).
    """

    __noReasonFail = "Action failed with no reason specified"

    def __init__(self, message: str = ""):
        super().__init__(message)

    def __str__(self):
        if not self.message:
            return self.__noReasonFail
        return f"Action failed due to the following: {self.message}"


class BatchException(ScriptException):
    """
    Exception for when a script needs to raise multiple issues in a single error.
    This is useful for when scripts do all invariant checking at once, and tell
    the user about all the problems they've seen (instead of making the user fix one problem,
    rebuild to see the next problem, and repeat).
    """

    def __init__(self, message: str = "Multiple errors encountered",
                 cvErrors: List[str] = None):
        super().__init__(message)
        self.errors = cvErrors

    def __str__(self):
        if not self.errors:
            return self.message

        return f"{self.message}:\n" + "\n".join(self.errors)


class DeviceCommandsFailed(ScriptException):
    """
    Exception raised when device fails to run commands with ctx.runDeviceCmds.
    This is separate to the commands on the device themselves failing.
    This can be caused by the command request being invalid, not caused by
    invalid commands being issued
    message is the user-facing message for the exception
    errCode is the error code returned from the DI service
    errMsg is the message that the DI service returned with the error code
    """

    def __init__(self, message: str, errCode: Optional[int] = None, errMsg: Optional[str] = None):
        super().__init__(message)
        self.errCode = errCode
        self.errMsg = errMsg


class LoggingFailed(ScriptException):
    """Exception raised when a logging request fails."""

    __noReasonFail = "Failed to post log with no reason specified"

    def __init__(self, message: str = ""):
        super().__init__(message)

    def __str__(self):
        if not self.message:
            return self.__noReasonFail
        return f"Failed to post log: {self.message}"


class TimeoutExpiry(ScriptException):
    """
    Exception to raise when alarm signals are used in scripts as timers so that script writers
    do not need to define their own exceptions for use in that situation.
    Users should raise and catch this exception in the signal handler
    so that they can be sure no other exception occurred while the timer was running
    """

    def __init__(self):
        super().__init__("Timeout for function call has been exceeded")


# ----------------------- Studio Template Exceptions -----------------------


class TemplateException(ScriptException):
    """Overarching class for Template exceptions"""

    def __init__(self, message: str = "cloudvision has encountered a template error"):
        super().__init__(message)


class TemplateTypeNotSupported(TemplateException):
    """Exception for when a template type is not supported"""

    def __init__(self, message: str = "Unsupported template type", templateType=None):
        super().__init__(message)
        self.templateType = templateType

    def __str__(self):
        if not self.templateType:
            return "Provided template type is unsupported"
        return f"Unsupported template type {self.templateType}"


class InputError:
    """
    This is the primary error that Studio Template writers would raise.
    It is raised manually by a template script if the set of inputs violates the script-author's
    assumptions.
    - message:      A user-friendly text message of the error
    - inputPath:    The path to the field that is in error. It is a list of field names
                    (the "name" attribute in the schema) starting from the root.
                    E.g.: ["networkConfig", "0", "config", "monitoredHosts", "1"]
    - fieldId:      The unique ID of the field (the "id" attribute in the schema).
    - members:      A list of all members in a group-type input that are in conflict. inputs easily.
                    In most cases, a script will only specify a single member to show that inputA
                    has a problem that the end user needs to fix. In certain cases, though, you may
                    want to indicate to the end user that either inputA or inputB needs fixing, but
                    both can't coexist in their current form.
    """

    def __init__(self, message: str = "Error in input field",
                 inputPath: List[str] = None, fieldId: str = None, members: List[str] = None):
        self.message = message
        self.inputPath = inputPath
        self.fieldId = fieldId
        self.members = members

    def __str__(self):
        return (
            f"{{"
            f"message: '{self.message}', "
            f"inputPath: {self.inputPath}, "
            f"fieldId: '{self.fieldId}', "
            f"members: {self.members}"
            f"}}"
        )


class InputErrorException(TemplateException):
    """
    Exception for when a user needs to raise an error with one or more InputError
    structures in it.
    For Studios, this is raised manually by a template script to report an error with
    one or more input values. It allows for errors in multiple input fields to be
    reported at once. These errors are displayed to the user in the Studio UI.
    """

    def __init__(self, message: str = "Error in input fields",
                 inputErrors: List[InputError] = None):
        super().__init__(message)
        self.errors = inputErrors

    def __str__(self):
        if not self.errors:
            return self.message
        return f"{self.message}:\n" + "\n".join([str(err) for err in self.errors])


class InputEmptyException(TemplateException):
    """
    Exception for when an action/template script tries to access an input that wasn't
    populated and that input was not optional or doesn't have a default value.
    The members field is something that can be used to determine what input was missing.
    Members should be usable by the UI to guide users to the right section to fill
    out the missing input.
    For studios, this is only raised by the internal studios python library utilities.

    For autofill actions, this could be useful for the autofill action to show that it
    can't autofill because some of the existing inputs don't make any sense. This also
    lets autofill actions act as validators (users press a button to validate in real time)
    """

    def __init__(self, message: str = "attempted to access unpopulated input",
                 members=None):

        super().__init__(message)
        self.members = members


# -------------------- Studio Autofill Action Exceptions --------------------

# Autofill actions also make use of the script ActionFailed exception
# Note: These autofill actions are executed via Action Exec API.
# This might change the way these exceptions are marshalled.

class AutofillActionException(ScriptException):
    """Overarching class for Autofill Action exceptions"""

    def __init__(self, message: str = "cloudvision has encountered an autofill action error"):
        super().__init__(message)


class InputException(AutofillActionException):
    """ Superclass for autofill input exceptions """

    def __init__(self, message: str = "Error encountered with inputs", inputPath: List[str] = None,
                 err=None):
        super().__init__(message)
        self.inputPath = inputPath
        self.err = err

    def __str__(self):
        msg = self.message
        if self.inputPath:
            msg += f" ({self.inputPath})"
        if self.err:
            msg += f": {self.err}"
        return msg


class InputRequestException(InputException):
    """
    Exception raised when an request to get studio inputs fails
    """

    def __init__(self, inputPath: List[str] = None, err=None):
        super().__init__("Failed to retrieve studio inputs", inputPath, err)


class InputUpdateException(InputException):
    """
    Exception raised when an update made to studio inputs fails
    """

    def __init__(self, inputPath: List[str] = None, err=None):
        super().__init__("Unable to update studio input", inputPath, err)


class InputNotFoundException(InputException):
    """
    Exception raised when an input path does not exist in the provided studio inputs
    """

    def __init__(self, inputPath: List[str] = None, err=None):
        super().__init__("Input path does not exist in inputs", inputPath, err)


# --------------------------- Topology Exceptions ---------------------------


class InvalidTopologyException(CVException):
    '''
    Exception class raised when topology model contains invalid configuration
    '''

    def __init__(self, errors):
        super().__init__("Invalid topology configuration:\n" + "\n".join(errors))
        self.errors = errors


# ---------------------------- Tag Exceptions ------------------------------


class TagErrorException(CVException):
    '''
    Exception raised for tag errors
    '''

    def __init__(self, message: str):
        super().__init__("Tag error: " + message)

    def expTagField(self, field: str):
        return field if field else '<unspecified>'


class TagOperationException(TagErrorException):
    """
    Exception raised when an attempted tag operation is invalid
    """

    def __init__(self, label: str, value: str, operation: str,
                 devId: str = None, intfId: str = None):
        message = (f"invalid attempt to {operation} tag "
                   f"{self.expTagField(label)}:{self.expTagField(value)}")
        if devId:
            message = message + " for device " + devId
        if intfId:
            message = message + " on interface " + intfId
        super().__init__(message)


class TagMissingException(TagErrorException):
    """
    Exception raised when a tag is missing from a device
    """

    def __init__(self, label: str, devId: str, intfId: str = None):
        message = (f"{self.expTagField(label)} tag missing"
                   f" for device {devId}")
        if intfId:
            message = message + " on interface " + intfId
        super().__init__(message)


class TagTooManyValuesException(TagErrorException):
    """
    Exception raised when a tag has too many values assigned to a device
    """

    def __init__(self, label: str, devId: str, currVals: List[str] = None,
                 intfId: str = None):
        message = (f"{self.expTagField(label)} tag has too many values"
                   f" assigned to device {devId}")
        if intfId:
            message = message + " on interface " + intfId
        if currVals:
            message = message + ", assigned values: " + ", ".join(currVals)
        super().__init__(message)


class TagInvalidTypeException(TagErrorException):
    """
    Exception raised when a tag value is not of the correct type
    """

    def __init__(self, label: str, devId: str, valType: str, currVals: List[str] = None):
        message = (f"{self.expTagField(label)} tag"
                   f" assigned to device {devId}"
                   f" must have a {valType} value")
        if currVals:
            message = message + ", assigned values: " + ", ".join(currVals)
        super().__init__(message)


class TagInvalidValuesException(TagErrorException):
    """
    Exception raised when a tag has invalid values assigned to a device
    """

    def __init__(self, label: str, devId: str, allowedVals: List[str] = None,
                 currVals: List[str] = None):
        message = (f"{self.expTagField(label)} tag has invalid values"
                   f" assigned to device {devId}")
        if allowedVals:
            message = message + ", allowed values: " + ", ".join(allowedVals)
        if currVals:
            message = message + ", assigned values: " + ", ".join(currVals)
        super().__init__(message)


# ---------------------------- IP Utils Exceptions -------------------------


class IpErrorException(CVException):
    '''
    Exception raised for IP addressing errors
    '''

    def __init__(self, message: str):
        super().__init__("IP addressing error: " + message)

    def expTagField(self, field: str):
        return field if field else '<unspecified>'


class IpSubnetIndexException(IpErrorException):
    """
    Exception raised when subnet indexing into a subnet pool is invalid
    """

    def __init__(self, network, subnet_mask: int,
                 num_subnets: int, index: int,
                 hostname: str = None, poolname: str = None):
        message = ''
        poolmessage = ''
        if hostname:
            message = f"Device {hostname}: "
        message = message + (
            f"Exceeding number of "
            f"/{subnet_mask} subnets in {network}. "
            f"Index {index} into subnets exceeds "
            f"the {num_subnets} available subnets. ")
        if poolname:
            poolmessage = (
                f"The size of pool {poolname} must be increased "
                f"in the studio inputs.")
        else:
            poolmessage = (
                "The size of the pool must be increased "
                "in the studio inputs.")
        message = message + poolmessage
        super().__init__(message)


class IpHostIndexException(IpErrorException):
    """
    Exception raised when host indexing into a subnet is invalid
    """

    def __init__(self, network, num_hosts: int, index: int,
                 hostname: str = None, poolname: str = None):
        message = ''
        poolmessage = ''
        if hostname:
            message = f"Device {hostname}: "
        message = message + (
            f"Exceeding number of "
            f"addresses in subnet {network}. "
            f"Index {index} into subnet exceeds "
            f"the {num_hosts} available subnets. ")
        if poolname:
            poolmessage = (
                f"The size of pool {poolname} must be increased "
                f"in the studio inputs.")
        else:
            poolmessage = (
                "The size of the pool must be increased "
                "in the studio inputs.")
        message = message + poolmessage
        super().__init__(message)


class IpNetworkOverlapException(IpErrorException):
    """
    Exception raised when networks unexpectedly overlap
    """

    def __init__(self, network1, network2,
                 hostname: str = None, poolname: str = None):
        message = ''
        poolmessage = ''
        if hostname:
            message = f"Device {hostname}: "
        message = message + (
            f"Subnets {network1} and {network2} overlap. ")
        if poolname:
            poolmessage = (
                f"Avoid overlapping networks by changing {poolname} "
                f"in the studio inputs.")
        else:
            poolmessage = (
                "Avoid overlapping networks by changing the pool "
                "in the studio inputs.")
        message = message + poolmessage
        super().__init__(message)
