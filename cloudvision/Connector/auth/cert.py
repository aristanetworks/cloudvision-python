# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from typing import Any, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization


def gen_csr_der(cert_path: str, key_path: str) -> bytes:
    """Generate ASN.1 DER encoded CSR.

    :param cert_path: Certificate file path (PEM encoded)
    :param key_path: Private Key file path (PEM encoded)
    :return: ASN.1 DER encoded CSR data
    """

    cert, key = load_key_cert_pair(cert_path, key_path)
    csr = create_csr(cert, key)
    return csr.public_bytes(serialization.Encoding.DER)


def create_csr(cert: x509.Certificate, key: Any) -> x509.CertificateSigningRequest:
    """Create CSR from given cert and private key.

    :param cert: Certificate object
    :param key: Private Key object
    :return: CSR object
    """

    return (
        x509.CertificateSigningRequestBuilder().subject_name(cert.subject)
        # Use SHA256 as signing algorithm
        .sign(key, hashes.SHA256())
    )


def load_key_cert_pair(cert_path: str, key_path: str) -> Tuple[x509.Certificate, Any]:
    """Load key & cert files.

    :param cert_path: Certificate file path (PEM encoded)
    :param key_path: Private key file path (PEM encoded)
    :return: Certificate and Key object
    """

    return load_cert(cert_path), load_key(key_path)


def load_cert(cert_path: str) -> x509.Certificate:
    """Load certificate file (PEM encoded).

    :param cert_path: Certificate file (PEM encoded)
    :return: Certificate object
    """

    cert_pem: bytes
    with open(cert_path, "rb") as f:
        cert_pem = f.read()
    return cert_from_pem(cert_pem)


def cert_from_pem(cert_pem: bytes) -> x509.Certificate:
    """Generate cert object from PEM encoded cert.

    :param cert_pem: Certificate PEM data
    :return: Certificate object
    """

    return x509.load_pem_x509_certificate(cert_pem)


def load_key(key_path: str, passphrase: Optional[str] = None) -> Any:
    """Load private key file (PEM encoded).

    :param key_path: Private key file (PEM encoded)
    :param passphrase: Passphrase used to decrypt the key
    :return: Private key object
    """

    key_pem: bytes
    with open(key_path, "rb") as f:
        key_pem = f.read()

    _passphrase: Optional[bytes] = bytes(passphrase, "utf-8") if passphrase else None
    return key_from_pem(key_pem, _passphrase)


def key_from_pem(key_pem: bytes, passphrase: Optional[bytes] = None) -> Any:
    """Generate key object from PEM encoded private key.

    :param key_pem: Private key (PEM encoded)
    :param passphrase: Passphrase used to decrypt the key
    :return: Private key object
    """

    return serialization.load_pem_private_key(key_pem, password=passphrase)
