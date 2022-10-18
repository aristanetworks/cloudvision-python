# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Import readme and create package info."""
import setuptools

from cloudvision import __version__ as version

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = []
with open("requirements.txt", "r") as fh:
    for dep in fh:
        install_requires.append(dep.strip())

setuptools.setup(
    name="cloudvision",
    version=version,
    description="A Python library for Arista's CloudVision APIs.",
    maintainer_email="support@arista.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aristanetworks/cloudvision-python",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
