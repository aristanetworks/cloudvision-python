#!/usr/bin/env python3
# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Make imports between generated protobuf modules package-relative."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


BARE_PROTO_IMPORT = re.compile(
    r"^import (?P<module>[A-Za-z_][A-Za-z0-9_]*_pb2) as (?P<alias>[A-Za-z_][A-Za-z0-9_]*)$",
    re.MULTILINE,
)


def fix_imports(generated_dir: Path) -> int:
    """Rewrite bare sibling imports and return the number of changed files."""
    changed = 0
    generated_files = sorted(generated_dir.glob("*_pb2.py"))
    generated_files.extend(sorted(generated_dir.glob("*_pb2.pyi")))
    generated_files.extend(sorted(generated_dir.glob("*_pb2_grpc.py")))

    for generated_file in generated_files:
        contents = generated_file.read_text()
        rewritten = BARE_PROTO_IMPORT.sub(
            r"from . import \g<module> as \g<alias>", contents
        )
        if rewritten != contents:
            generated_file.write_text(rewritten)
            changed += 1

        remaining = BARE_PROTO_IMPORT.search(rewritten)
        if remaining:
            raise RuntimeError(
                f"bare protobuf import remains in {generated_file}: "
                f"{remaining.group(0)}"
            )

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated_dir", type=Path)
    args = parser.parse_args()

    if not args.generated_dir.is_dir():
        parser.error(f"not a directory: {args.generated_dir}")

    changed = fix_imports(args.generated_dir)
    print(f"Updated protobuf imports in {changed} file(s) under {args.generated_dir}")


if __name__ == "__main__":
    main()
