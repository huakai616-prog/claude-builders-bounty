#!/usr/bin/env python3
"""Mechanical QA for tools/hollywood PDFs, MusicXML and MIDI: catches the
layout slips a reviewer would hunt for on PNGs, and lists only the pages
not yet seen in their current form.  Standard library + poppler (pdftotext, pdftoppm) + xmllint.
pN is always the PDF page (a full score's cover is p1).

  qa.py score <pdf> [--bars N] [--musicxml F] [--systems 3] [-v]
      Full score (11 x 17 in, cover first) or parts (9 x 12 in, numbering
      restarts per instrument), told apart by page size.  Reads the boxed
      bar numbers back with `pdftotext -bbox`, groups them into systems and
      prints a summary plus one "PROBLEM:" line per finding: bars missing,
      printed twice or out of order (1..N; an unnumbered pickup is fine, a
      parts multi-rest covers its bars), one-bar systems, score pages
      before the last without --systems systems, a last page (per part)
      holding one system, header page number / footer "PAGE n OF N" /
      花开当富贵 in footer and title block wrong or missing, page sizes or
      /Title metadata off, a cover without title, 改编 / 制谱 rows naming
      花开当富贵, key line or instrumentation, and parts missing, doubled
      or out of score order.  N and the parts come from --bars and the
      score's MusicXML (--musicxml, default: the only *.musicxml next to
      the PDF; measures with implicit="yes" are not counted), else N is
      the last bar found.  -v adds "p3: 9-12 | 13-16 | 17-19" per page.
      Exit 0 clean, 1 problems, 2 not a Hollywood PDF (skipped).

  qa.py pages <pdf> <dir>
      Renders the pages at 90 dpi on white into <dir>/round-K/pNN.png (K =
      next free number) and prints the round's path, "look at:" (pages
      whose decoded pixels you have not marked as seen) and "unchanged:"
      (pixel-identical to the same page of the same PDF as you marked it
      seen).  Keep <dir> outside the repo (e.g. the session scratchpad or
      /tmp/qa-<song>), one <dir> per PDF (score and parts apart).
  qa.py seen --round K <dir> [pN ...]
      After looking at the "look at" pages of round K, mark them as seen
      (default: every page of that round; or only the pages named, as p2,
      p02 or 2).  `pages` prints the exact command.  A page you never
      marked stays "look at" in every later round, so a rendered-but-
      unviewed round can never hide a page.

  qa.py midi <output dir>
      Every *带歌词*.mid, and the vocal tracks of the *全轨*.mid: each note
      has a non-empty lyric (a syllable or "-") at its onset, and the
      lyrics decode (UTF-8, or GBK for the *GBK* file).  Every *.mid: prints
      its track names (check them yourself).  Exit 0 clean, 1 problems.

  qa.py xml <file.musicxml|.mxl>  "OK: valid" or the first 20 xmllint errors
  qa.py fetch-schema            only fill the schema cache (tools/setup.sh)
      The MusicXML 4.0 schema (musicxml.xsd with the xml.xsd and xlink.xsd it
      imports, from w3c/musicxml) is cached in ~/.cache/musicxml.
"""
import argparse
import collections
import fcntl
import hashlib
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib

# kind -> (boxed bar-number height, header zone bottom, y jump that always
# starts a new system), in pt.  Heights: measureNumberFontSize 10 / 8.5 in
# hollywood.mss / hollywood_part.mss; tuplets (8.4-9.2) and footer digits
# (8.647) fall outside BN_TOL.  Systems are 250+ / 70+ pt apart; high notes
# push a bar number up by up to ~30 pt.
SIZES = {(792, 1224): "score", (648, 864): "parts"}
KINDS = {"score": (10.0, 62, 90), "parts": (8.6, 54, 55)}
BN_TOL = 0.03
FOOT = 54   # footer zone: the bottom 0.75 in
CREDIT = "花开当富贵"
# cover_html(): key · tempo · duration at 13.25 in, instrumentation at
# 13.75 in, signature at 15.1 in
COVER_LINES = (("key · tempo · duration", 13.0, 13.55),
               ("instrumentation", 13.55, 14.7))
WORD = re.compile(r'<word xMin="([-\d.]+)" yMin="([-\d.]+)" xMax="([-\d.]+)" '
                  r'yMax="([-\d.]+)">(.*?)</word>')


def read_pdf(path):
    """(title from the metadata, [(width, height, words)]); a word is
    (x0, y0, x1, y1, text), y growing downwards."""
    r = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True,
                       text=True)
    if r.returncode:
        raise SystemExit(f"ERROR: pdftotext: {r.stderr.strip()}")
    title = re.search(r"<title>(.*?)</title>", r.stdout, re.S)
    pages = []
    for chunk in r.stdout.split("<page ")[1:]:
        w, h = map(float, re.match(r'width="([\d.]+)" height="([\d.]+)"',
                                   chunk).groups())
        pages.append((w, h, [(*map(float, g[:4]), html.unescape(g[4]))
                             for g in WORD.findall(chunk)]))
    return html.unescape(title.group(1)) if title else "", pages


def norm(s):
    return re.sub(r"\s+", "", s).upper()


def joined(words):
    """Left to right, no spaces, upper case: letter-spaced text ("P A G E")
    comes out of pdftotext as one word per letter."""
    return norm("".join(t for *_, t in sorted(words, key=lambda w: w[0])))


def yc(wd):
    return (wd[1] + wd[3]) / 2


def ranges(nums):
    """[3, 4, 5, 9] -> "3-5, 9"."""
    out = []
    for n in sorted(nums):
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def smufl_number(t):
    """Multi-rest counts (and time signatures) are SMuFL digits U+E080-9."""
    if t and all(0xE080 <= ord(c) <= 0xE089 for c in t):
        return int("".join(str(ord(c) - 0xE080) for c in t))
    return None


class Page:
    """A music page: header, footer, and its boxed bar numbers as systems.
    A multi-rest prints only its first bar's number, with the count right
    under that box."""

    def __init__(self, index, w, h, words, kind):
        bn_h, head, ygap = KINDS[kind]
        self.index = index
        head_w = [wd for wd in words if yc(wd) < head]
        foot_w = sorted((wd for wd in words if yc(wd) > h - FOOT),
                        key=lambda wd: wd[0])
        self.header, self.footer = joined(head_w), joined(foot_w)
        self.body = norm("".join(wd[4] for wd in words
                                 if head <= yc(wd) <= h - FOOT))
        m = re.search(r"PAGE(\d+)OF(\d+)", self.footer)
        self.n, self.total = map(int, m.groups()) if m else (0, 0)
        m = re.search(r"([ -~]*)·\s*PAGE\b",   # parts: "VIOLIN II · PAGE"
                      " ".join(wd[4] for wd in foot_w).upper())
        self.name = m.group(1).strip() if m else ""
        self.label = f"p{index}" + (f" ({self.name})" * (kind == "parts"))
        nums = [wd for wd in head_w if wd[4].isdecimal() and wd[0] > w * .6]
        big = max(nums, key=lambda wd: wd[3] - wd[1], default=None)
        self.head_n = int(big[4]) if big else None   # the big one, top right
        bars = [(int(wd[4]), (wd[0] + wd[2]) / 2, yc(wd)) for wd in words
                if re.fullmatch(r"[0-9]+", wd[4]) and head < yc(wd) < h - FOOT
                and abs(wd[3] - wd[1] - bn_h) < BN_TOL]
        # a multi-rest count is centred under its box; the glyph's (font-wide)
        # box starts ~27 pt above the number's centre and ends ~50 pt below.
        # Only parts have multi-rests (a time signature's digits sit ~10 pt
        # lower); check_bars drops a "count" whose inner bars are printed.
        self.mm = {}
        for wd in words if kind == "parts" else ():
            count = smufl_number(wd[4]) or 0
            for n, x, y in bars if count > 1 else ():
                if (abs((wd[0] + wd[2]) / 2 - x) < 8 and 15 < y - wd[1] < 40
                        and 35 < wd[3] - y < 70):
                    self.mm[n] = count
        # within a system the numbers grow left to right: a new system
        # starts where x goes back left (or y jumps)
        self.systems = []
        for n, x, y in sorted(bars):
            last = self.systems[-1][-1] if self.systems else None
            if last and x > last[1] and abs(y - last[2]) < ygap:
                self.systems[-1].append((n, x, y))
            else:
                self.systems.append([(n, x, y)])
        self.systems = [[n for n, _, _ in s] for s in self.systems]

    def end(self, n):
        return n + self.mm.get(n, 1) - 1

    def layout(self):
        return " | ".join(f"{s[0]}" if self.end(s[-1]) == s[0] else
                          f"{s[0]}-{self.end(s[-1])}" for s in self.systems
                          ) or "(no bar numbers)"


def check_cover(words, title, problems):
    text = norm("".join(t for *_, t in sorted(
        words, key=lambda w: (round(w[3] / 4), w[0]))))
    if "FULLSCORE" not in text or re.search(r"PAGE\d+OF\d+", text):
        problems.append("p1 is not a cover (no FULL SCORE, or a page footer)")
        return
    if not title or norm(title) not in text:
        problems.append(f"p1 cover: title {title!r} not found")
    for label in ("改编", "制谱"):
        lx = next((w for w in words if w[4] == label), None)
        row = joined(w for w in words if lx and w[0] > lx[2]
                     and abs(yc(w) - yc(lx)) < 10)
        if CREDIT not in row:
            problems.append(f"p1 cover: no {label} row naming {CREDIT}")
    for what, top, bottom in COVER_LINES:
        if not any(top * 72 < yc(w) < bottom * 72 for w in words):
            problems.append(f"p1 cover: no {what} line")


def check_pages(pages, kind, title, problems):
    """Headers, footers and title blocks; returns the pages grouped into
    parts (one group for a full score)."""
    parts = []
    for pg in pages:
        p = pg.label
        if kind == "score":
            if not parts:
                parts.append([])
            want = pg.index - 1
            if "FULLSCOREINC" not in pg.header:
                problems.append(f"{p}: header lacks FULL SCORE IN C")
        else:
            if not parts or pg.n == 1 or pg.name != parts[-1][0].name:
                parts.append([])
            want = len(parts[-1]) + 1
            rest = pg.header.split(norm(title), 1)[-1] if title else ""
            if not pg.name or (norm(pg.name) != re.match(r"[A-Z0-9.]*", rest)
                               .group() if title else
                               norm(pg.name) not in pg.header):
                problems.append(f"{p}: header and footer do not name the "
                                "same instrument")
        parts[-1].append(pg)
        if title and norm(title) not in pg.header:
            problems.append(f"{p}: header lacks the title {title!r}")
        if not pg.n:
            problems.append(f"{p}: footer has no PAGE n OF N")
        elif pg.n != want:
            problems.append(f"{p}: footer says PAGE {pg.n}, expected {want}")
        if pg.head_n != (pg.n or want):
            problems.append(f"{p}: header page number {pg.head_n}, "
                            f"expected {pg.n or want}")
        if CREDIT not in pg.footer:
            problems.append(f"{p}: footer lacks {CREDIT}")
        for label in ("改编", "制谱") if len(parts[-1]) == 1 else ():
            if not re.search(label + "[:：]?" + CREDIT, pg.body):
                problems.append(f"{p}: title block lacks {label}：{CREDIT}")
    for part in parts:
        bad = " ".join(f"p{pg.index}" for pg in part
                       if pg.total and pg.total != len(part))
        if bad:
            problems.append(f"{part[0].name + ': ' if kind == 'parts' else ''}"
                            f"footer 'OF N' wrong on {bad}: there are "
                            f"{len(part)} pages")
    return parts


def printed_bars(part):
    """Bar number -> times printed.  Also drops a multi-rest "count" whose
    inner bars are printed: a real multi-rest's never are."""
    printed = collections.Counter(n for pg in part for s in pg.systems
                                  for n in s)
    for pg in part:
        pg.mm = {n: c for n, c in pg.mm.items()
                 if not any(b in printed for b in range(n + 1, n + c))}
    return printed


def check_bars(part, kind, top, args, problems):
    """Missing / duplicated / out-of-order bars (1..top), one-bar systems,
    systems per page."""
    who = f"{part[0].name}: " if kind == "parts" else ""
    printed = printed_bars(part)
    covered = {b for pg in part for s in pg.systems for n in s
               for b in range(n, pg.end(n) + 1)}
    if not printed:
        problems.append(f"{who}no boxed bar numbers found")
        return
    first = 0 if 0 in printed else 1
    for what, bars in (("bars missing", set(range(first, top + 1)) - covered),
                       ("bars printed twice", [n for n in printed
                                               if printed[n] > 1]),
                       (f"bars beyond {top}", [n for n in covered
                                               if n > top])):
        if bars:
            problems.append(f"{who}{what}: {ranges(bars)}")
    seq = [(pg, s) for pg in part for s in pg.systems]
    for (pa, a), (pb, b) in zip(seq, seq[1:]):
        if b[0] <= pa.end(a[-1]):
            problems.append(f"{pb.label}: bars out of order (a system starts "
                            f"at bar {b[0]} after bar {pa.end(a[-1])})")
    off = collections.defaultdict(list)   # systems -> pages off target
    for i, pg in enumerate(part):
        k = len(pg.systems)
        for s in pg.systems:
            if len(s) == 1:
                what = (f"multi-rest {s[0]}-{pg.end(s[0])}" if s[0] in pg.mm
                        else f"bar {s[0]}")
                problems.append(f"{pg.label}: one-bar system ({what})")
        if not k:
            problems.append(f"{pg.label}: no bar numbers on this page")
        elif i == len(part) - 1 and len(part) > 1 and k == 1:
            problems.append(f"{pg.label}: lonely last page (one system, bars "
                            f"{pg.layout()})")
        elif kind == "score" and (k > args.systems if i == len(part) - 1
                                  else k != args.systems):
            off[k].append(pg.index)
    for k, idx in sorted(off.items()):
        problems.append(f"pages {ranges(idx)}: {k} systems (target "
                        f"{args.systems})")


def score_ref(args):
    """(file name, bars, part names) from the score's MusicXML: --musicxml,
    else the only *.musicxml next to the PDF; None if there is none.
    MuseScore numbers every measure except implicit="yes" ones (pickups)."""
    path = args.musicxml
    if not path:
        d = os.path.dirname(os.path.abspath(args.pdf))
        xs = [f for f in os.listdir(d) if f.lower().endswith(".musicxml")]
        if len(xs) != 1:
            return None
        path = os.path.join(d, xs[0])
    try:
        r = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as e:
        raise SystemExit(f"ERROR: cannot read {path}: {e}")
    part = r.find("part")
    bars = sum(m.get("implicit") != "yes" for m in part.iter("measure")
               ) if part is not None else 0
    names = [(sp.findtext("part-name") or "").strip()
             for sp in r.iter("score-part")]
    return os.path.basename(path), bars, names


def check_parts(parts, ref, problems):
    """Every part of the score once, in score order."""
    names = [norm(part[0].name) for part in parts]
    twice = sorted({part[0].name for part in parts
                    if names.count(norm(part[0].name)) > 1})
    if twice:
        problems.append(f"parts printed more than once: {', '.join(twice)}")
    if not ref:
        return
    want = [norm(n) for n in ref[2]]
    gone = [n for n in ref[2] if norm(n) not in names]
    if gone:
        problems.append(f"no part for {', '.join(gone)} (in {ref[0]})")
    known = [n for n in dict.fromkeys(names) if n in want]
    if known != sorted(known, key=want.index):
        problems.append(f"parts not in score order ({ref[0]}: "
                        f"{', '.join(ref[2])})")


def cmd_score(args):
    title, raw = read_pdf(args.pdf)
    w, h = raw[0][:2] if raw else (0, 0)
    kind = SIZES.get((round(w), round(h)))
    if not kind:
        print(f"SKIP: not a Hollywood PDF ({w:.0f} x {h:.0f} pt; "
              "tools/hollywood makes 792 x 1224 scores and 648 x 864 parts)")
        return 2
    title = title.split(" — ")[0].strip()
    problems = [] if title else ["no /Title in the PDF metadata (the title "
                                 "checks on the pages are skipped)"]
    for i, (pw, ph, _) in enumerate(raw, 1):
        if (round(pw), round(ph)) != (round(w), round(h)):
            problems.append(f"p{i}: page is {pw:.0f} x {ph:.0f} pt, p1 is "
                            f"{w:.0f} x {h:.0f}")
    if kind == "score":
        check_cover(raw[0][2], title, problems)
    first = 2 if kind == "score" else 1
    pages = [Page(i, *pg, kind) for i, pg in enumerate(raw[first - 1:], first)]
    if not pages:
        problems.append("no music pages")
    parts = check_pages(pages, kind, title, problems)
    ref = score_ref(args)
    for part in parts:
        printed_bars(part)
    top = args.bars or (ref[1] if ref else max(
        (pg.end(n) for pg in pages for s in pg.systems for n in s), default=0))
    for part in parts:
        check_bars(part, kind, top, args, problems)
    bars = f"{top} bars " + ("(--bars)" if args.bars else f"({ref[0]})" if ref
                             else "(the last found: no MusicXML to compare)")
    if kind == "score":
        counts = [len(pg.systems) for pg in pages]
        stats = f"{len(raw)} pages, {bars}, " + (
            f"{counts[0]} systems/page" if len(set(counts)) == 1 else
            "systems per page " + (" ".join(map(str, counts)) or "-"))
    else:
        check_parts(parts, ref, problems)
        stats = f"{len(raw)} pages, {len(parts)} parts (" + ", ".join(
            f"{part[0].name or '?'} {len(part)} p." for part in parts
        ) + f"), {bars}"
    n = len(problems)
    print(f"{n} problem{'s' * (n > 1)}: {stats}" if n else f"OK: {stats}")
    for pr in problems:
        print("PROBLEM:", pr)
    for pg in pages if args.verbose else ():
        print(f"{pg.label}: {pg.layout()}")
    return 1 if problems else 0


def png_hash(path):
    """Hash of the decoded image (header, palette, inflated pixels), not of
    the file."""
    data, pos, head, idat = open(path, "rb").read(), 8, [], []
    while pos < len(data):
        n = int.from_bytes(data[pos:pos + 4], "big")
        typ, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        if typ in (b"IHDR", b"PLTE", b"tRNS"):
            head.append(typ + body)
        elif typ == b"IDAT":
            idat.append(body)
        pos += 12 + n
    return hashlib.sha1(b"".join(head) + zlib.decompress(b"".join(idat))
                        ).hexdigest()


def cmd_pages(args):
    pdf = os.path.abspath(args.pdf)
    if not os.path.isfile(pdf):
        raise SystemExit(f"ERROR: no such PDF: {args.pdf}")
    os.makedirs(args.dir, exist_ok=True)
    done = sorted(int(m.group(1)) for d in os.listdir(args.dir)
                  if (m := re.fullmatch(r"round-(\d+)", d)))
    k_out = done[-1] + 1 if done else 1
    while True:  # two `pages` runs into one dir at once take different rounds
        out = os.path.join(args.dir, f"round-{k_out}")
        try:
            os.makedirs(out)
            break
        except FileExistsError:
            k_out += 1
    r = subprocess.run(["pdftoppm", "-r", "90", "-png", pdf,
                        os.path.join(out, "p")], capture_output=True, text=True)
    files = {int(m.group(1)): f for f in os.listdir(out)
             if (m := re.fullmatch(r"p-(\d+)\.png", f))}
    if r.returncode or not files:
        shutil.rmtree(out)
        raise SystemExit("ERROR: pdftoppm: " + " / ".join(
            r.stderr.strip().splitlines()[-3:]))
    width = max(2, len(str(max(files))))
    pages = {}
    for n, f in sorted(files.items()):
        png = os.path.join(out, f"p{n:0{width}d}.png")
        os.replace(os.path.join(out, f), png)
        pages[str(n)] = png_hash(png)
    # pages whose pixels were marked seen (qa.py seen) need no second look
    seen = seen_of(load_seen(args.dir), pdf)
    prev, since = {}, None  # last round of the same PDF (other PDFs may share dir)
    for k in reversed(done):
        rec = load_round(args.dir, k)
        if rec and rec.get("pdf") == pdf:
            prev, since = rec["pages"], k
            break
    with open(os.path.join(out, "pages.json"), "w") as fh:
        json.dump({"pdf": pdf, "pages": pages}, fh)
    show = lambda ns: " ".join(f"p{n}" for n in ns) or "none"
    print(f"round: {out}" + (f" (previous round of this PDF: round-{since})"
                             if since else " (no earlier round of this PDF)"))
    look = [n for n in pages if pages[n] not in seen.get(n, [])]
    print("look at:", show(look))
    print("unchanged:", show(n for n in pages if n not in look))
    if set(prev) - set(pages):
        print("gone (the PDF is shorter now):",
              show(sorted(set(prev) - set(pages), key=int)))
    if look:
        print(f"after looking at them: python3 {shlex.quote(sys.argv[0])} "
              f"seen --round {k_out} {shlex.quote(args.dir)}")
    return 0


def load_round(d, k):
    try:
        with open(os.path.join(d, f"round-{k}", "pages.json")) as fh:
            rec = json.load(fh)
    except (OSError, ValueError):
        return None
    return rec if isinstance(rec.get("pages"), dict) else None


def load_seen(d):
    try:
        with open(os.path.join(d, "seen.json")) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def seen_of(seen, pdf):
    """The seen hashes of one PDF as {page: [hash, ...]}; anything malformed
    counts as not seen (the safe direction)."""
    mine = seen.get(pdf)
    if not isinstance(mine, dict):
        return {}
    return {p: [h for h in v if isinstance(h, str)]
            for p, v in mine.items() if isinstance(v, list)}


def cmd_seen(args):
    k = args.round
    rec = load_round(args.dir, k) if os.path.isdir(args.dir) else None
    if not rec:
        raise SystemExit(f"ERROR: no round-{k} in {args.dir}; run qa.py pages "
                         "first and use the command it prints")
    want = []
    for p in args.pages:
        m = re.fullmatch(r"[pP]?0*(\d+)", p)
        if not m:
            raise SystemExit(f"ERROR: {p!r}: name pages as p2, p02 or 2")
        want.append(m.group(1))
    want = want or list(rec["pages"])
    bad = [p for p in want if p not in rec["pages"]]
    if bad:
        raise SystemExit(f"ERROR: round-{k} has no page " + " ".join(bad))
    with open(os.path.join(args.dir, "seen.lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # concurrent `seen` runs keep all marks
        seen = load_seen(args.dir)
        mine = seen[rec["pdf"]] = seen_of(seen, rec["pdf"])
        for p in want:
            if rec["pages"][p] not in mine.setdefault(p, []):
                mine[p].append(rec["pages"][p])
        fd, tmp = tempfile.mkstemp(dir=args.dir, prefix="seen.", suffix=".part")
        with os.fdopen(fd, "w") as fh:
            json.dump(seen, fh)
        os.replace(tmp, os.path.join(args.dir, "seen.json"))
    print(f"seen: round-{k} of {os.path.basename(rec['pdf'])}: "
          + " ".join(f"p{p}" for p in want))
    return 0


SCHEMA_DIR = os.path.expanduser("~/.cache/musicxml")
SCHEMA_URL = "https://raw.githubusercontent.com/w3c/musicxml/v4.0/schema/"


def download(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except OSError:  # fall back to curl (proxy / CA setups urllib misses)
        r = subprocess.run(["curl", "-fsSL", "--max-time", "120", url],
                           capture_output=True)
        if r.returncode:
            raise SystemExit(
                f"fetch-schema: cannot download {url}: "
                + r.stderr.decode(errors="replace").strip()
                + f"\noffline? copy musicxml.xsd, xml.xsd and xlink.xsd from "
                "w3c/musicxml v4.0 (schema/) into " + SCHEMA_DIR
                + " (minimal xml.xsd / xlink.xsd stubs also work; each file "
                "must end with </xs:schema>)")
        return r.stdout


def complete(data):
    """A whole schema file (a cut-off download is re-fetched)."""
    return data.rstrip().endswith((b"</xs:schema>", b"</xsd:schema>"))


def fetch_schema():
    """Fill SCHEMA_DIR; musicxml.xsd imports the local xml.xsd / xlink.xsd."""
    os.makedirs(SCHEMA_DIR, exist_ok=True)
    for name in ("xml.xsd", "xlink.xsd", "musicxml.xsd"):
        path = os.path.join(SCHEMA_DIR, name)
        data = open(path, "rb").read() if os.path.exists(path) else b""
        if not complete(data):
            data = download(SCHEMA_URL + name)
            if not complete(data):
                raise SystemExit(f"fetch-schema: {SCHEMA_URL}{name}: not a "
                                 "whole schema")
        elif name != "musicxml.xsd" or b'schemaLocation="http' not in data:
            continue
        if name == "musicxml.xsd":  # import the local copies (xmllint --nonet)
            data = re.sub(rb'schemaLocation="[^"]*?([a-z]+\.xsd)"',
                          rb'schemaLocation="\1"', data)
        with open(path + ".part", "wb") as fh:
            fh.write(data)
        os.replace(path + ".part", path)
    return os.path.join(SCHEMA_DIR, "musicxml.xsd")


def cmd_xml(args):
    """xmllint against the 4.0 schema; a compressed .mxl is validated by
    its root file (META-INF/container.xml)."""
    schema = fetch_schema()
    with tempfile.TemporaryDirectory() as tmp:
        path = args.file
        if zipfile.is_zipfile(path):
            try:
                with zipfile.ZipFile(path) as z:
                    root = next(e.get("full-path") for e in ET.fromstring(
                        z.read("META-INF/container.xml")).iter()
                        if e.tag.endswith("rootfile"))
                    data = z.read(root)
            except (KeyError, StopIteration, TypeError, ET.ParseError) as e:
                print(f"not a MusicXML .mxl: {e!r}")
                return 1
            path = os.path.join(tmp, os.path.basename(root))
            with open(path, "wb") as fh:
                fh.write(data)
        r = subprocess.run(["xmllint", "--noout", "--nonet", "--schema",
                            schema, path], capture_output=True, text=True)
    if r.returncode == 0:
        print("OK: valid")
        return 0
    # "<file>:12: element x: Schemas validity error : ..." -> "line 12: ..."
    # (xmllint %-escapes some paths); lines about the schema stay as they are
    lines = [ln if ln.startswith(SCHEMA_DIR) else
             re.sub(r"^.*?:(\d+): (element \S+ )?(Schemas validity error : )?",
                    r"line \1: ", ln)
             for ln in r.stderr.splitlines() if not ln.endswith("validate")]
    print("\n".join(lines[:20]) or r.stderr.strip())
    if len(lines) > 20:
        print(f"... {len(lines) - 20} more lines")
    return 1


def cmd_midi(args):
    import mido
    if not os.path.isdir(args.dir):
        raise SystemExit(f"ERROR: no such directory: {args.dir}")
    files = sorted(f for f in os.listdir(args.dir) if f.endswith(".mid"))
    if not files:
        raise SystemExit(f"ERROR: no .mid files in {args.dir}")
    read, problems = {}, 0
    for f in files:
        try:
            read[f] = mido.MidiFile(os.path.join(args.dir, f), charset=(
                "gbk" if "GBK" in f.upper() else "utf-8"))
        except Exception as e:  # mido raises many types on corrupt data
            print(f"PROBLEM: {f}: cannot read ({type(e).__name__}: {e})")
            problems += 1

    def tracks(mf):
        for tr in mf.tracks:
            t, ons, lyr, name, cjk = 0, [], set(), "", 0
            for msg in tr:
                t += msg.time
                if msg.type == "track_name":
                    name = msg.name
                elif msg.type == "note_on" and msg.velocity:
                    ons.append(t)
                elif msg.type == "lyrics" and msg.text.strip():
                    lyr.add(t)
                    cjk += bool(re.search(r"[\u4e00-\u9fff]", msg.text))
            if ons:
                yield name, ons, lyr, cjk

    # vocal tracks = the tracks of the *带歌词* files; the 全轨 file's
    # tracks of the same name must carry the lyrics too (ACE reads them)
    vocal = {n for f, mf in read.items() if "带歌词" in f
             for n, *_ in tracks(mf)}
    for f, mf in read.items():
        names, notes, missing, cjk, checked = [], 0, [], 0, False
        for name, ons, lyr, c in tracks(mf):
            names.append(name or "(no name)")
            if "带歌词" in f or ("全轨" in f and name in vocal):
                checked = True
                notes += len(ons)
                cjk += c
                missing += [(name, t) for t in ons if t not in lyr]
        print(f"{f}: tracks: {' / '.join(names) or 'none'}")
        if not checked:
            continue
        if missing:
            problems += 1
            ticks = ", ".join(f"{n or '?'}@{t}" for n, t in missing[:8])
            print(f"PROBLEM: {f}: {len(missing)} of {notes} vocal notes have "
                  f"no lyric at their onset ({ticks}"
                  f"{' ...' if len(missing) > 8 else ''})")
        if not cjk:
            problems += 1
            print(f"PROBLEM: {f}: no Chinese characters in the lyrics "
                  "(wrong encoding, or no lyrics?)")
        if not missing and cjk:
            print(f"  OK: {notes} vocal notes, every one with a lyric or '-'")
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("pdf")
    s.add_argument("--bars", type=int, help="number of the last bar")
    s.add_argument("--musicxml", help="the score's MusicXML (bar count, "
                   "parts); default: the only *.musicxml next to the PDF")
    s.add_argument("--systems", type=int, default=3,
                   help="systems per full-score page (default 3)")
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_score)
    s = sub.add_parser("pages")
    s.add_argument("pdf")
    s.add_argument("dir")
    s.set_defaults(fn=cmd_pages)
    s = sub.add_parser("seen")
    s.add_argument("dir")
    s.add_argument("--round", type=int, required=True, help="the round you "
                   "looked at (pages prints the whole command)")
    s.add_argument("pages", nargs="*", default=[], help="pN ... (default: "
                   "all pages of that round)")
    s.set_defaults(fn=cmd_seen)
    s = sub.add_parser("midi")
    s.add_argument("dir", help="the song's output directory")
    s.set_defaults(fn=cmd_midi)
    s = sub.add_parser("xml")
    s.add_argument("file")
    s.set_defaults(fn=cmd_xml)
    sub.add_parser("fetch-schema").set_defaults(
        fn=lambda _: print("schema:", fetch_schema()))
    args = ap.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
