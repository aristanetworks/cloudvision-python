#!/usr/bin/env python
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.


# Fetches a session token and/or the SSL certificate from CVP.
# Helpful for authentication in the provided examples.

import argparse
import requests
import ssl
import json

TOKEN_FILE = 'token.txt'
SSL_CERT_FILE = 'cvp.crt'


def main(args):
    if (not args.username and not args.password) and not args.ssl:
        exit(
            "Error: Arguments --username and --password are required (for token generation), "
            "and/or --ssl argument is required (for SSL cert generation)."
        )
        return

    if args.username and args.password:
        r = requests.post(
            'https://' + args.server + '/cvpservice/login/authenticate.do',
            auth=(args.username, args.password), verify=args.ssl is False)

        r.json()['sessionId']

        with open(TOKEN_FILE, "w") as f:
            f.write(r.json()['sessionId'])

    if args.ssl:
        with open(SSL_CERT_FILE, "w") as f:
            f.write(ssl.get_server_certificate((args.server, 443)))


if __name__ == '__main__':
    ds = (
        "Get a session token and/or the SSL cert from CVP, and store them respectively "
        "in token.txt and cvp.crt.\n"
        "Example 1 (token.txt and cvp.crt generation): \n  "
        "python3 get_token.py --server 10.0.0.1 --username <username> --password <password> --ssl\n"
        "Example 2 (cvp.crt generation only): \n  "
        "python3 get_token.py --server 10.0.0.1 --ssl"
    )
    parser = argparse.ArgumentParser(
        description=ds,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host> format.")
    parser.add_argument("--username", type=str,
                        help="Username to authorize with")
    parser.add_argument("--password", type=str,
                        help="Password to authorize with")
    parser.add_argument("--ssl", action="store_true",
                        help="Save the self-signed certficate to cvp.crt")

    args = parser.parse_args()
    main(args)
