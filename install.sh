#!/bin/bash
python3 -m pip install .[dev]
mypy --install-types --non-interactive
