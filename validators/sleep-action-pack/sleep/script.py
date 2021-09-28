# Copyright (c) 2021 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from time import sleep

duration = ctx.changeControl.args.get("duration")
# User timeout arg is a string, convert it to an integer. If not specified, default to 30 seconds
duration = int(duration) if duration else 30

# Sleep for the desired duration
sleep(duration)
