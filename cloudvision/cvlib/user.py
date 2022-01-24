# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

class User:
    '''
    Object to store information on the user executing this script:
    - username:      Cloudvision username
    - token:         Auth token used to create connections
    '''

    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token
