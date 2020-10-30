#!/usr/bin/env python
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.


# Fetches a session token and optional SSL certificate from CVP.
# Useful when authenticating in the included examples.

import argparse
import requests
import ssl
import json


def main(args):
    r = requests.post('https://' + args.server + '/cvpservice/login/authenticate.do',
                      auth=(args.username, args.password), verify=args.ssl is False)

    r.json()['sessionId']

    with open("token.txt", "w") as f:
        f.write(r.json()['sessionId'])

    if args.ssl:
        with open("cvp.crt", "w") as f:
            f.write(ssl.get_server_certificate((args.server, 443)))


if __name__ == '__main__':
    ds = ("Get a session token (and optional SSL cert) from CVP and store to token.txt")
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host> format.")
    parser.add_argument("--username", required=True, type=str,
                        help="Username to authorize with")
    parser.add_argument("--password", required=True, type=str,
                        help="Password to authorize with")
    parser.add_argument("--ssl", action="store_true",
                        help="Save the self-signed certficate to cvp.crt")

    args = parser.parse_args()
    main(args)
