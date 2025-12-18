# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import re
import crypt
import random
from typing import Any, Dict
from json import loads

from cloudvision.Connector.grpc_client import GRPCClient, create_query

from .exceptions import ScriptException


def queryCCStartTime(client: GRPCClient, ccId: str):
    # Create a query to the cvp dataset in the database for the root entry of the change control
    # with the provided ID. The root contains all general information regarding the CC
    query = [
        create_query([(["changecontrol", "config", ccId, "root"], [])], "cvp")
    ]
    changeControls = client.get(query)
    for batch in changeControls:
        # There will only be a single notification here as we're only querying a single path
        for notif in batch["notifications"]:
            # The updates received will be in the form of nested dictionaries
            updates: Dict[str, Dict[str, Dict[str, Any]]] = notif["updates"]

            # There should be a root key entry at this path, if not the CC is invalid
            cc = updates.get("root")
            if cc is None:
                raise ScriptException(f"Change control ID {ccId} is invalid: missing 'root' key")

            # The 'Start' key of the root entry of a change control holds information on
            # when the entire change control started, before any actions ran.
            # This should be here by default
            start = cc.get("Start")
            if not start:
                raise ScriptException(f"Change control ID {ccId} is invalid: missing 'Start' key")

            # The 'Start' Dict should always have a 'Timestamp' key
            startTs = start.get("Timestamp")
            if not startTs:
                raise ScriptException(
                    f"Change control ID {ccId} is invalid: 'Start' missing 'Timestamp' key")

            # If the Timestamp in that entry is 0, it means that the CC has not started
            if startTs == 0:
                raise ScriptException(f"Change control ID {ccId} has not yet started")

            return cc["Start"]["Timestamp"]

    raise ScriptException(f"No entries found for Change control ID {ccId}")


def extractJSONEncodedListArg(listArg: str):
    """
    Extracts a string arg in JSON-encoded list form and converts it to a list for use

    Args:
        listArg (str): The stringified list
    """
    extractedList = loads(listArg)  # Evaluate this into a list
    if not isinstance(extractedList, list):
        raise ValueError("Extracted arg must be a list")
    return extractedList


OBFUSCATOR = "dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87"


def doType7Obfuscation(plaintext: str, salt: int | None = None, obf: str = ""):
    """
    Perform Type 7 password obfuscation using XOR encoding.

    Args:
        plaintext (str): The plaintext password to obfuscate.
        salt (int | None): The salt value (0-15). If None, a random salt is generated.
        obf (str): The obfuscator string for XOR encoding. If empty,
            a default obfuscator is used.

    Returns:
        The obfuscated password prefixed with the 2-digit salt,
            or empty string if plaintext is empty.
    """
    if not plaintext:
        # If the password is empty, return an empty string without the salt
        return plaintext

    if salt is None:
        salt = random.randint(0, 15)

    if salt < 0 or salt > 15:
        raise ValueError("Salt must be between 0 and 15")

    if not obf:
        obf = OBFUSCATOR

    obf_bytes = obf.encode("UTF-8")
    plaintext_bytes = plaintext.encode("UTF-8")

    result_bytes = bytearray()
    for i, char_byte in enumerate(plaintext_bytes):
        key_byte = obf_bytes[(i + salt) % len(obf_bytes)]
        result_bytes.append(char_byte ^ key_byte)

    return f"{salt:02d}{result_bytes.hex().upper()}"


def doSHA512Hashing(plaintext: str, salt: str):
    """
    Generate SHA-512 password hash using Unix crypt format.

    Args:
        plaintext (str): The plaintext password to hash.
        salt (str): Salt string (only alphanumeric characters, periods, and slashes are used).

    Returns:
        The hashed password in Unix crypt format ($6$salt$hash).
    """
    if not plaintext:
        return plaintext
    sanitized_salt = re.sub(r'[^A-Za-z0-9\.\/]', '', salt)
    return crypt.crypt(plaintext, f"$6${sanitized_salt}$")
