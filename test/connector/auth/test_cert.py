# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Test certificate helper functions."""


from pathlib import Path
from typing import Union
from cryptography.hazmat.primitives import hashes

import pytest
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509.base import load_der_x509_csr

from cloudvision.Connector.auth.cert import (
    cert_from_pem,
    create_csr,
    gen_csr_der,
    key_from_pem,
    load_cert,
    load_key,
    load_key_cert_pair,
)

THIS_DIR = Path(__file__).parent
TEST_DIR = THIS_DIR.parent.parent
TEST_DATA_DIR = Path.joinpath(TEST_DIR, "test_data")


def fqfp(file_name: str) -> Path:
    """Fully Qualified File Path.

    :param file_name: Test file name
    :return: Fully qualified/absolute file path of given test file
    """

    return Path.joinpath(TEST_DATA_DIR, file_name)


def data(file_name: str, mode: str = "rb") -> Union[str, bytes]:
    """Data of given test file.

    :param file_name: Test file name
    :param mode: Mode to read test file
    :return: Data of the given file
    """

    with open(fqfp(file_name), mode) as f:
        return f.read()


class TestCert:
    @pytest.mark.parametrize("cert_path, key_path", [(fqfp("cert.pem"), fqfp("key.pem"))])
    def test_gen_csr_der(self, cert_path, key_path):
        csr_der = gen_csr_der(str(cert_path), str(key_path))
        csr = load_der_x509_csr(csr_der)
        cert, key = load_key_cert_pair(cert_path, key_path)
        assert csr.subject == cert.subject
        assert isinstance(csr.signature_hash_algorithm, hashes.SHA256)
        assert csr.public_key().public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        ) == key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        assert csr.public_key().public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        ) == cert.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    @pytest.mark.parametrize("cert_path, key_path", [(fqfp("cert.pem"), fqfp("key.pem"))])
    def test_create_csr(self, cert_path, key_path):
        cert, key = load_key_cert_pair(cert_path, key_path)
        csr: x509.CertificateSigningRequest = create_csr(cert, key)
        assert csr.subject == cert.subject
        assert isinstance(csr.signature_hash_algorithm, hashes.SHA256)
        assert csr.public_key().public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        ) == key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        assert csr.public_key().public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        ) == cert.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    @pytest.mark.parametrize("cert_path, key_path", [(fqfp("cert.pem"), fqfp("key.pem"))])
    def test_load_key_cert_pair(self, cert_path: str, key_path: str):
        cert, key = load_key_cert_pair(cert_path, key_path)
        assert cert is not None
        assert key is not None
        assert isinstance(cert, x509.Certificate)
        assert isinstance(key, rsa.RSAPrivateKey)
        assert key.public_key().public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        ) == cert.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    @pytest.mark.parametrize("cert_path", [fqfp("cert.pem")])
    def test_load_cert(self, cert_path: str):
        cert = load_cert(cert_path)
        assert cert is not None
        assert isinstance(cert, x509.Certificate)

    @pytest.mark.parametrize("key_path", [fqfp("key.pem")])
    def test_load_key(self, key_path: str):
        key = load_key(key_path)
        assert key is not None
        assert isinstance(key, rsa.RSAPrivateKey)

    @pytest.mark.parametrize("cert_pem", [data("cert.pem")])
    def test_cert_from_pem(self, cert_pem):
        cert = cert_from_pem(cert_pem)
        assert cert is not None
        assert isinstance(cert, x509.Certificate)

    @pytest.mark.parametrize("key_pem", [data("key.pem")])
    def test_key_from_pem(self, key_pem):
        key = key_from_pem(key_pem)
        assert key is not None
        assert isinstance(key, rsa.RSAPrivateKey)
