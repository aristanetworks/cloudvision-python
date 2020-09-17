# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""
Basic argparser to be reused in examples.

Mirrors the usage of the -auth flag in the arista go monorepo for
convenience and convention's sake
"""
import argparse
import os.path
from parser import AuthAction, AUTH_HELP


class AuthActionDst(argparse.Action):
    """
    AuthAction is responsible for parsing arguments to the grpc_client.

    Possible values currently are

    'none': no authentication
    'none-tls[,{caFile}]': no authentication, TLS encryption
    'token,{tokenFile}[,{caFile}]': access token based authentication
    'certs,{certFile},{keyFile}[,{caFile}]': client-side certificate
    """
    NONE = 'none'
    NONE_TLS = 'none-tls'
    CERTS = 'certs'
    TOKEN = 'token'

    VALID_AUTHS = [NONE, NONE_TLS, CERTS, TOKEN]

    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        argparse.Action.__init__(self, option_strings, dest=dest, nargs=nargs,
                                 default=default, type=type, choices=choices,
                                 required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str):
            err = "%s is not a valid auth type"
            raise argparse.ArgumentTypeError(self, err % values)

        split = values.split(',')
        authtype = split[0]
        authargs = split[1:]

        if authtype not in self.VALID_AUTHS:
            err = "%s is not a valid authentication scheme"
            raise argparse.ArgumentError(self, err % authtype)

        opts = {
            'caFileDst': None,
            'certFileDst': None,
            'keyFileDst': None,
            'tokenFileDst': None,
        }

        if authtype == self.NONE:
            pass
        elif authtype == self.NONE_TLS:
            if len(authargs) != 1:
                err = "expected 1 argument for 'none-tls' auth, got %d"
                raise argparse.ArgumentError(self, err % len(authargs))

            opts['caFileDst'] = os.path.expanduser(authargs[0])
        elif authtype == self.CERTS:
            if len(authargs) < 2 or len(authargs) > 3:
                err = "expected 2-3 arguments for 'certs' auth got %d"
                raise argparse.ArgumentError(self, err % len(authargs))

            opts['certFileDst'] = os.path.expanduser(authargs[0])
            opts['keyFileDst'] = os.path.expanduser(authargs[1])
            if len(authargs) == 3:
                opts['caFileDst'] = os.path.expanduser(authargs[2])
        elif authtype == self.TOKEN:
            if len(authargs) != 1 and len(authargs) != 2:
                err = "expected exactly 1 argument for 'token' auth, got %d"
                raise argparse.ArgumentError(self, err % len(authargs))
            opts['tokenFileDst'] = os.path.expanduser(authargs[0])
            if len(authargs) == 2:
                opts['caFileDst'] = os.path.expanduser(authargs[1])

        for opt, val in opts.items():
            setattr(namespace, opt, val)
        setattr(namespace, self.dest, values)  # also set the base auth string


def add_arguments(base):

    base.add_argument('--src', help='URL and port of src CVP apiserver to connect to'
                      'in the format HOST:PORT i.e. (apiserver.examplecvp.com:11002)')
    base.add_argument('--srcauth', action=AuthAction, default='', help=AUTH_HELP)
    base.add_argument('--dst', help='URL and port of dest CVP apiserver to connect to'
                      'in the format HOST:PORT i.e. (apiserver.examplecvp.com:11002)')
    base.add_argument('--dstauth', action=AuthActionDst, default='', help=AUTH_HELP)
