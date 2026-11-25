#!/usr/bin/env python3
"""Unsent: The Micro-Confession Sprint — entry program.

Writes one two-part micro-confession to /output/entry.txt (or
$MAKEFUN_OUTPUT_DIR/entry.txt): a To: line naming who it was meant for,
then the unsent message itself, one line written exactly as it was typed.

The text is fixed and deterministic. Before writing, the program checks
the text against its pinned byte count and SHA-256 so a changed output
can never slip through silently.
"""

import hashlib
import os
import sys

TEXT = (
    "To: the nurse who held my hand the night my mom died\n"
    "i never learned your name, so i've been thanking a stranger "
    "in my head for three years"
)

EXPECTED_BYTES = 139
EXPECTED_SHA256 = "f1b33de4cab5796bc98cf169e02423f03fee834cb49a19fe22bafb1e787834eb"


def verify(path, data) -> bool:
    """Read the written file back and check it byte for byte against the pin."""
    with open(path, "rb") as fh:
        written = fh.read()
    if written != data:
        print(f"FAIL: {path} bytes differ from the pinned text", file=sys.stderr)
        return False
    if len(written) != EXPECTED_BYTES:
        print(
            f"FAIL: {path} is {len(written)} bytes, expected {EXPECTED_BYTES}",
            file=sys.stderr,
        )
        return False
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        print(
            f"FAIL: {path} sha256 {digest}, expected {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return False
    return True


def main() -> int:
    data = TEXT.encode("utf-8")
    if len(data) != EXPECTED_BYTES:
        print(
            f"refusing to write: {len(data)} bytes, expected {EXPECTED_BYTES}",
            file=sys.stderr,
        )
        return 1
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print(
            f"refusing to write: sha256 {digest}, expected {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1
    if not (1 <= len(TEXT) <= 260):
        print(f"refusing to write: {len(TEXT)} chars outside 1-260", file=sys.stderr)
        return 1
    message = TEXT.split("\n", 1)[1]
    if len(message) > 200:
        print(f"refusing to write: message {len(message)} chars over 200", file=sys.stderr)
        return 1
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.txt")
    with open(path, "wb") as fh:
        fh.write(data)
    verified = verify(path, data)
    if not verified:
        print(f"read-back verification failed for {path}", file=sys.stderr)
        return 1
    print(f"wrote {path}: {len(data)} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
