"""The arrangement: global settings here, the notes in sections/secNN.py.

Each section file holds the bars of one section (VN1, VN2, VA, VC dicts
keyed by bar, plus DYN, HAIR, TEXT, CLEFS, OTTAVA); this module merges them
for build.py.  See ARRANGING.md."""
import glob
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))

VN1, VN2, VA, VC = {}, {}, {}, {}
DYN = {k: [] for k in ("vn1", "vn2", "va", "vc")}
HAIR = {k: [] for k in ("vn1", "vn2", "va", "vc")}
TEXT = {k: [] for k in ("vn1", "vn2", "va", "vc")}
CLEFS = {k: [] for k in ("vn1", "vn2", "va", "vc")}
OTTAVA = []
ALLOW = set()
_TARGET = dict(VN1=VN1, VN2=VN2, VA=VA, VC=VC)

# ARR_ONLY=sections/sec05.py loads just that file (a drafter checking one
# section while others are still being written)
_FILES = ([os.path.join(HERE, os.environ["ARR_ONLY"])]
          if os.environ.get("ARR_ONLY")
          else sorted(glob.glob(os.path.join(HERE, "sections", "sec*.py"))))
for _f in _FILES:
    _spec = importlib.util.spec_from_file_location(
        os.path.basename(_f)[:-3], _f)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    for _name, _dst in _TARGET.items():
        for _b, _s in getattr(_m, _name, {}).items():
            assert _b not in _dst, f"{_f}: bar {_b} of {_name} set twice"
            _dst[_b] = _s
    for _name, _dst in (("DYN", DYN), ("HAIR", HAIR), ("TEXT", TEXT),
                        ("CLEFS", CLEFS)):
        for _k, _v in getattr(_m, _name, {}).items():
            _dst[_k].extend(_v)
    OTTAVA.extend(getattr(_m, "OTTAVA", []))
    ALLOW |= set(getattr(_m, "ALLOW", set()))

# Rehearsal letters and section titles (bar, letter or None, title)
SECTIONS = [
    (0, None, "Intro 前奏"),
    (16, "A", "Riff 主题动机"),
    (24, "B", "Verse 主歌"),
    (32, "C", "Pre-Chorus 导歌"),
    (36, "D", "Chorus 副歌"),
    (50, "E", "Interlude 间奏"),
    (58, "F", "Bridge 桥段"),
    (66, "G", "Solo 华彩"),
    (78, "H", "Breakdown 崩落"),
    (82, "J", "Pre-Chorus 导歌"),
    (90, "K", "Music Box 八音盒"),
    (97, "L", "Chorus 副歌"),
    (104, "M", "Interlude 间奏"),
    (108, "N", "Final Chorus 终副歌"),
    (118, "P", "Coda 尾声"),
]
# Tempo map (bar, pos, bpm) and printed tempo words (bar, pos, text)
TEMPI = [(0, 0, 134)]
TEMPO_TEXT = []
# Hollywood layout: 3 systems per page, every rehearsal letter starts a
# system (planned with layout.py, budget 74; the coda split by hand so the
# last page also has three systems)
SYSTEM_BREAKS = (6, 11, 19, 21, 28, 32, 40, 44, 50, 52, 58, 60, 66, 68, 72,
                 74, 78, 80, 84, 87, 92, 94, 99, 101, 106, 108, 114, 118,
                 126, 129)
PAGE_BREAKS = (16, 24, 36, 47, 55, 63, 70, 76, 82, 90, 97, 104, 111, 123)
# Accepted check items live in the section files as ALLOW:
# ("mel"|"bass"|"foreign", bar) or ("stop", part, bar), each with a reason
