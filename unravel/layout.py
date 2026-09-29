#!/usr/bin/env python3
"""Choose SYSTEM_BREAKS / PAGE_BREAKS for the Hollywood layout.

Every rehearsal section starts a new system; inside a section, bars are
packed so that each system's width estimate (onsets per bar + a per-bar
overhead) stays under the budget, preferring even phrase lengths.  Pages
hold 3 systems (house style).  Prints the two tuples to paste into
arrangement.py.

    python3 layout.py [budget]
"""
import sys

import build

BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 62
BAR_OVERHEAD = 4
SYS_OVERHEAD = 6


def weights():
    parsed = {p["id"]: build.parse_part(p["data"]) for p in build.PARTS}
    w = {}
    for b in build.MEASURES:
        ons = {e["pos"] for evs in parsed.values() for e in evs
               if e["bar"] == b}
        w[b] = len(ons) + BAR_OVERHEAD
    return w


def plan():
    w = weights()
    starts = sorted({b for b, _, _ in build.SECTIONS} | {0})
    bars = build.MEASURES
    systems = []
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else bars[-1] + 1
        sec = [b for b in bars if s <= b < end]
        # DP over the section: best split into systems
        n = len(sec)
        best = [(0.0, [])] + [(float("inf"), [])] * n
        for j in range(1, n + 1):
            for k in range(max(0, j - 7), j):
                chunk = sec[k:j]
                cost = SYS_OVERHEAD + sum(w[b] for b in chunk)
                if cost > BUDGET and len(chunk) > 1:
                    continue
                under = max(0.0, BUDGET - 6 - cost)
                bad = under ** 2
                if len(chunk) == 1 and n > 1:
                    bad += 400          # no one-bar systems
                if len(chunk) % 2 and len(chunk) > 1 and chunk[0] != 0:
                    bad += 30           # prefer 2 / 4 bar phrases
                tot = best[k][0] + bad
                if tot < best[j][0]:
                    best[j] = (tot, best[k][1] + [chunk])
        systems += best[n][1]
    return systems, w


def main():
    systems, w = plan()
    sys_breaks = [s[0] for s in systems[1:]]
    pages = [systems[i:i + 3] for i in range(0, len(systems), 3)]
    page_breaks = [p[0][0] for p in pages[1:]]
    for i, p in enumerate(pages):
        print(f"page {i + 1}: " + " | ".join(
            f"{s[0]}-{s[-1]} ({sum(w[b] for b in s) + SYS_OVERHEAD})"
            for s in p))
    print(f"{len(systems)} systems, {len(pages)} pages")
    print("SYSTEM_BREAKS =", tuple(b for b in sys_breaks
                                  if b not in page_breaks))
    print("PAGE_BREAKS =", tuple(page_breaks))


if __name__ == "__main__":
    main()
