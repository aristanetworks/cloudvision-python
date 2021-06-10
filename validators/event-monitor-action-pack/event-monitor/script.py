# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import re
import signal

# Import the event resource API models to be able to easily parse the rAPI output
from arista.event.v1 import models
# Import the python service implementations of the event rAPI to be able to
# handle sending and receiving requests and responses from the rAPI
from arista.event.v1.services import EventServiceStub, EventStreamRequest
# Import the operation type from the subscriptions so we can tell if an rAPI
# response is a delete, update, etc.
from arista.subscriptions.subscriptions_pb2 import Operation

# A mapping from the string values of the alert severities to the event rAPI format
SEVERITIES = {
    "INFO": models.EVENT_SEVERITY_INFO,
    "WARNING": models.EVENT_SEVERITY_WARNING,
    "ERROR": models.EVENT_SEVERITY_ERROR,
    "CRITICAL": models.EVENT_SEVERITY_CRITICAL,
}

# Types of notifications from the event rAPI that we want to ignore
IGNORED_NOTIFS = {
    # An unknown update type, an error
    Operation.UNSPECIFIED,
    # This filters out already active events from before the action
    Operation.INITIAL,
    # An update type that happens when we go transition to the subscription phase
    Operation.INITIAL_SYNC_COMPLETE
}


class EventMonitoringFinished(BaseException):
    # A custom exception class to be raised when we are done monitoring the events
    # This is done so we can be absolutely sure that it is not some other type of issue
    pass


def monitorTimerHandler(signum, frame):  # pylint: disable=unused-argument
    # A handler function for the timer that will raise our custom exception
    raise EventMonitoringFinished("monitoring duration has finished")


# A set for storing what events are currently active, used when fail_fast is False
activeEventSet = set()

# Default filters for checking events. "None" filters will not filter any events
device_filter = None
event_filter = None
severity_filter = [
    models.EVENT_SEVERITY_WARNING,
    models.EVENT_SEVERITY_ERROR,
    models.EVENT_SEVERITY_CRITICAL,
]

# Extract the user-defined filter from user args, will be an empty string if unspecified
severity_filter_str = ctx.changeControl.args.get("severity_filter")
# Empty strings are falsy, so will only parse user input if it exists
if severity_filter_str:
    # User arg is a comma seperated string, split on the comma
    severity_filter_list = re.split(',', severity_filter_str)
    # Converts the user-severities to the model severities through our mapping above
    # Any invalid severity in the args will be dropped
    severity_filter = [SEVERITIES[sev] for sev in severity_filter_list]

# Repeat filter extraction for event types
event_filter_str = ctx.changeControl.args.get("event_filter")
if event_filter_str:
    event_filter_list = re.split(',', event_filter_str)
    event_filter = list(filter(None, event_filter_list))

# Repeat filter extraction for devices
device_filter_str = ctx.changeControl.args.get("device_filter")
if device_filter_str:
    device_filter_list = re.split(',', device_filter_str)
    device_filter = list(filter(None, device_filter_list))


# Set up a signal handler that will cause a signal.SIGALRM signal to trigger our timer handler
signal.signal(signal.SIGALRM, monitorTimerHandler)

# User configured 'Raise' event timeouts may be impacted here. This timeout is a realtime timeout,
# but we can have events generated later which have a timestamp which was within the timeout window
# if there is a raise timer configured.
# These will not be caught if the raisetimer is longer than the timeout
timeout = ctx.changeControl.args.get("duration")
if timeout:
    # User timeout arg is a string, convert it to an integer
    timeout = int(timeout)
else:
    # If user has not specified a timeout, default to 300 seconds (5 min)
    timeout = 300

# Check to see if the fail_fast arg is "True", anything else is interpreted as False
fail_fast = ctx.changeControl.args.get("fail_fast") == "True"

# Create a stub to the event rAPI so we can send and receive requests and responses
event_stub = ctx.getApiClient(EventServiceStub)
try:
    # Set an alarm to fire in <timeout> seconds
    signal.alarm(timeout)
    # Subscribe to the set of
    for resp in event_stub.Subscribe(EventStreamRequest(), timeout=timeout):
        # Response is of type EventStreamResponse

        # Discard initial get phase of subscribe, only interested in new events
        if resp.type in IGNORED_NOTIFS:
            continue

        # Event delete signifying event has ended, remove from list of active events if it exists
        if resp.type == Operation.DELETED:
            activeEventSet.discard(resp.value.key.key.value)
            continue

        # Only possible response type left is Operation.UPDATED
        # Operation.UPDATED means that a new event has occurred
        # Check to see if new event satisfies current filters

        # Drop event if there is a severity filter and the new event's severity is not in the list
        if severity_filter and resp.value.severity not in severity_filter:
            continue

        # Repeat for the the event type
        if event_filter and resp.value.event_type.value not in event_filter:
            continue

        # As the deviceId in the event is not a top level field, we need to extract information
        # Only perform it if there is a device filter in place
        if device_filter:
            # Extract the device components of the event into a list
            dev_components = [comp for comp in resp.value.components if
                              comp.type == models.COMPONENT_TYPE_DEVICE]
            # If no device components in event, drop event as device filter in place
            if not dev_components:
                continue
            # Extract the deviceIds from the device components
            event_devices = [dev for dev in dev_components.components["deviceId"]]
            # Drop the event if no intersection between device components and filter
            if not [dev for dev in device_filter if dev in event_devices]:
                continue

        # A new event has occurred, log it
        ctx.alog("Event \"{}:{}\" raised at {}".format(
            resp.value.key.key.value, resp.value.title.value, resp.time))

        # If failfast is set, exit after disabling alarm
        if fail_fast:
            signal.alarm(0)
            # Raising an uncaught exception fails the action with the following note
            raise ValueError("new events detected in failfast mode")

        # Else add to the set of active events to check at the end of the timeout
        activeEventSet.add(resp.value.key.key.value)
# Handle our custom exception raised by our timer here
except EventMonitoringFinished as e:
    # Fail the action if any events that started during the action are still active
    # Only can happen if fail_fast is False, activeEventSet is always empty if fail_fast is True
    if len(activeEventSet) != 0:
        # Log the keys of the events that cause the failure
        ctx.alog("New, unended events found after Change Control with keys: {}".format(activeEventSet))
        # Raising an uncaught exception from our custom exception
        # fails the action with the following note
        raise UserWarning("new events detected after change control") from e
