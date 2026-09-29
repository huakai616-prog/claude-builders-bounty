#!/usr/bin/env python3
"""Run build.py's checks and show only the problems in bars FIRST..LAST.
Usage: python3 check_section.py FIRST LAST [sections/secNN.py]
With a section file, only that file is loaded (other sections may be
half-written).  The piano transcription comes from piano_source.json or
$UNRAVEL_PIANO."""
import os
import re
import sys

if len(sys.argv) > 3:
    os.environ["ARR_ONLY"] = sys.argv[3]
import build  # noqa: E402

a, z = int(sys.argv[1]), int(sys.argv[2])
parsed = {p["id"]: build.parse_part(p["data"]) for p in build.PARTS}
for line in build.check(parsed):
    m = re.search(r"\bm(\d+)\b", line)
    if m is None or a <= int(m.group(1)) <= z:
        print(line)
