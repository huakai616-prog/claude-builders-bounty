"""Build the Mac app that puts 编曲交付中心 in the user's Dock.

The app only opens the pinned delivery page in the default browser, so the
page is always the latest version. What gets delivered:

    编曲交付中心_安装包.zip
      编曲交付中心_安装包/编曲交付中心.app   ready-made app (fallback, manual install)
      编曲交付中心_安装包/安装.sh           builds a native applet with osacompile,
                                          copies it to /Applications, adds it to the Dock
      编曲交付中心_安装包/安装说明.txt

The zip travels base64 inside files/macapp/app.json because the artifact host
refuses to serve .zip files; center.html turns it back into a zip and saves it.

    python3 tools/deliver/macapp/build.py          # zip + app.json + icon.png, prints the files map
    python3 tools/deliver/macapp/build.py --icon   # also redraw icon.svg → AppIcon.png / AppIcon.icns
                                                   # (needs Playwright + Chromium, see SKILL.md)
"""
import base64
import io
import json
import os
import plistlib
import struct
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "..", "dist", "files", "macapp")

URL = "https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN"
NAME = "编曲交付中心"
PKG = NAME + "_安装包"
EXE = "open-center"
VERSION = "1.0"

INK = "#23508e"


# ---- icon -------------------------------------------------------------------

def clef_path():
    """Treble clef outline from FreeSerif (U+1D11E), baseline = bottom staff line."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    font = TTFont("/usr/share/fonts/truetype/freefont/FreeSerif.ttf")
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs)
    gs[font.getBestCmap()[0x1D11E]].draw(pen)
    return pen.getCommands()


def icon_svg():
    sp = 30                        # staff space in px
    s = sp / 187                   # font units per staff space in FreeSerif
    bottom = 476                   # bottom staff line
    lines = [bottom - i * sp for i in range(5)]
    staff = "".join(f'<line x1="330" x2="694" y1="{y}" y2="{y}"/>' for y in lines)

    def note(cx, cy, stem_top, filled=True):
        head = (f'<ellipse cx="{cx}" cy="{cy}" rx="17" ry="12.5" transform="rotate(-22 {cx} {cy})"'
                + ('' if filled else f' fill="none" stroke="{INK}" stroke-width="6"') + '/>')
        return head + f'<rect x="{cx + 12}" y="{stem_top}" width="5" height="{cy - stem_top - 2}"/>'

    notes = (note(476, bottom - sp // 2, 342) + note(556, bottom - 3 * sp // 2, 320)
             + '<path d="M488 342 L573 320 L573 335 L488 357 Z"/>'
             + note(640, bottom - 2 * sp, 324, filled=False))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>
    <linearGradient id="body" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3a70b8"/><stop offset="1" stop-color="#16345f"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f0c766"/><stop offset="1" stop-color="#c98f25"/>
    </linearGradient>
    <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fdfaf2"/><stop offset="1" stop-color="#efe8d8"/>
    </linearGradient>
    <filter id="drop" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#000" flood-opacity=".30"/>
    </filter>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#06142a" flood-opacity=".40"/>
    </filter>
  </defs>
  <!-- macOS icon grid: 824 px body, 100 px margins -->
  <rect x="100" y="100" width="824" height="824" rx="185" fill="url(#body)" filter="url(#drop)"/>
  <rect x="100" y="100" width="824" height="824" rx="185" fill="none" stroke="#ffffff" stroke-opacity=".10" stroke-width="3"/>
  <!-- full-score title page -->
  <g filter="url(#soft)">
    <rect x="292" y="196" width="440" height="604" rx="14" fill="url(#paper)"/>
  </g>
  <rect x="314" y="218" width="396" height="560" fill="none" stroke="{INK}" stroke-width="6"/>
  <rect x="326" y="230" width="372" height="536" fill="none" stroke="{INK}" stroke-width="2"/>
  <g stroke="{INK}" stroke-width="4">{staff}</g>
  <path fill="{INK}" transform="translate({338 - 120 * s:.1f} {bottom}) scale({s:.5f} {-s:.5f})" d="{clef_path()}"/>
  <g fill="{INK}">{notes}</g>
  <rect x="382" y="574" width="260" height="22" rx="3" fill="{INK}"/>
  <rect x="417" y="620" width="190" height="11" rx="2" fill="{INK}" fill-opacity=".45"/>
  <rect x="442" y="646" width="140" height="11" rx="2" fill="{INK}" fill-opacity=".45"/>
  <!-- delivery badge -->
  <g filter="url(#soft)"><circle cx="722" cy="742" r="108" fill="url(#gold)"/></g>
  <circle cx="722" cy="742" r="108" fill="none" stroke="#ffffff" stroke-opacity=".55" stroke-width="5"/>
  <g stroke="#ffffff" stroke-width="24" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M722 680 V772"/><path d="M682 734 L722 774 L762 734"/><path d="M676 800 H768"/>
  </g>
</svg>
'''


def render_png(svg_path, png_path):
    """SVG → 1024 px transparent PNG with Playwright's Chromium."""
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: 1024, height: 1024 }} }});
  await p.goto('file://{svg_path}');
  await p.screenshot({{ path: '{png_path}', omitBackground: true }});
  await b.close();
}})();
"""
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", "-e", js], check=True, env=env)


# PNG-backed icns entries: (type, pixel size)
ICNS_TYPES = [("icp4", 16), ("icp5", 32), ("icp6", 64), ("ic07", 128), ("ic08", 256),
              ("ic09", 512), ("ic10", 1024), ("ic11", 32), ("ic12", 64), ("ic13", 256),
              ("ic14", 512)]


def write_icns(png_path, icns_path):
    from PIL import Image
    src = Image.open(png_path).convert("RGBA")
    chunks = b""
    for kind, px in ICNS_TYPES:
        buf = io.BytesIO()
        src.resize((px, px), Image.LANCZOS).save(buf, "PNG", optimize=True)
        data = buf.getvalue()
        chunks += kind.encode() + struct.pack(">I", len(data) + 8) + data
    with open(icns_path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", len(chunks) + 8) + chunks)


def make_icon():
    svg = os.path.join(HERE, "icon.svg")
    png = os.path.join(HERE, "AppIcon.png")
    with open(svg, "w", encoding="utf-8") as f:
        f.write(icon_svg())
    render_png(svg, png)
    write_icns(png, os.path.join(HERE, "AppIcon.icns"))


# ---- app bundle + zip -------------------------------------------------------

def info_plist():
    return plistlib.dumps({
        "CFBundleDevelopmentRegion": "zh_CN",
        "CFBundleName": NAME,
        "CFBundleDisplayName": NAME,
        "CFBundleIdentifier": "com.huakaidangfugui.delivery-center",
        "CFBundleExecutable": EXE,
        "CFBundleIconFile": "AppIcon",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "????",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "LSMinimumSystemVersion": "10.13",
        # A script as the main executable has no architecture; without this an
        # Apple-silicon Mac may ask to install Rosetta first.
        "LSArchitecturePriority": ["arm64", "x86_64"],
        "LSApplicationCategoryType": "public.app-category.music",
        "NSHighResolutionCapable": True,
        "NSHumanReadableCopyright": "改编 · 制谱 花开当富贵",
    })


LAUNCHER = f"""#!/bin/sh
# 编曲交付中心：用默认浏览器打开交付中心页面（总是最新版）。
exec /usr/bin/open "{URL}"
"""


def entries():
    """(path inside zip, bytes or None for a folder, unix mode)."""
    app = f"{PKG}/{NAME}.app/Contents"
    read = lambda name: open(os.path.join(HERE, name), "rb").read()
    return [
        (f"{PKG}/", None, 0o755),
        (f"{PKG}/{NAME}.app/", None, 0o755),
        (f"{app}/", None, 0o755),
        (f"{app}/Info.plist", info_plist(), 0o644),
        (f"{app}/PkgInfo", b"APPL????", 0o644),
        (f"{app}/MacOS/", None, 0o755),
        (f"{app}/MacOS/{EXE}", LAUNCHER.encode(), 0o755),
        (f"{app}/Resources/", None, 0o755),
        (f"{app}/Resources/AppIcon.icns", read("AppIcon.icns"), 0o644),
        (f"{PKG}/安装.sh", read("install.sh"), 0o755),
        (f"{PKG}/安装说明.txt", b"\xef\xbb\xbf" + read("安装说明.txt"), 0o644),
    ]


def build_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path, data, mode in entries():
            info = zipfile.ZipInfo(path, date_time=(2026, 9, 29, 12, 0, 0))
            info.create_system = 3                      # Unix: keep the modes
            if data is None:
                info.external_attr = ((0o040000 | mode) << 16) | 0x10
                z.writestr(info, b"")
            else:
                info.external_attr = (0o100000 | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
    return buf.getvalue()


def main():
    if "--icon" in sys.argv:
        make_icon()
    os.makedirs(DIST, exist_ok=True)
    data = build_zip()
    with open(os.path.join(DIST, "app.json"), "w", encoding="utf-8") as f:
        json.dump({"filename": PKG + ".zip", "size": len(data), "version": VERSION,
                   "b64": base64.b64encode(data).decode()}, f)
    from PIL import Image
    Image.open(os.path.join(HERE, "AppIcon.png")).resize((256, 256), Image.LANCZOS) \
        .save(os.path.join(DIST, "icon.png"), optimize=True)
    if "--zip" in sys.argv:                            # local copy for testing
        with open(os.path.join(DIST, PKG + ".zip"), "wb") as f:
            f.write(data)
    rel = os.path.relpath(DIST, os.path.join(HERE, "..", "..", ".."))
    print(json.dumps({"files/macapp/app.json": f"{rel}/app.json",
                      "files/macapp/icon.png": f"{rel}/icon.png"}, ensure_ascii=False, indent=1))
    print(f"zip {len(data)} bytes", file=sys.stderr)


if __name__ == "__main__":
    main()
