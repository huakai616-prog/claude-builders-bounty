#!/bin/sh
# One-command environment setup for a fresh Linux cloud container:
#
#     sh tools/setup.sh          (from any directory; safe to run again)
#
# Installs only what is missing for building songs and rendering the
# Hollywood PDF: Python packages (music21 mido pypdf cffi), apt packages
# (fonts, poppler, fluidsynth + GM soundfont, ffmpeg, xmllint), MuseScore 4
# (hollywood.find_ms4 puts the AppImage in /opt/ms4) and the MusicXML 4.0
# schema (tools/hollywood/qa.py fetch-schema, cached in ~/.cache/musicxml).
# It also reports whether hollywood.find_chrome finds a browser.
#
# Quiet by design: every command's output goes to the log
# (${TMPDIR:-/tmp}/setup-music.log); the terminal gets one line per
# component and, when one fails, the last 15 lines of its log.  Exits
# non-zero if anything failed.
#
# On macOS (the user's Mac) it installs nothing and only lists what is
# missing.  Plain POSIX sh, so `sh tools/setup.sh` and `bash tools/setup.sh`
# both work.

if [ "$(uname)" = Darwin ]; then
    # The user's Mac: install nothing, only say what is missing.
    echo "setup.sh installs only on Linux cloud containers; on the Mac, MuseScore 4 and Chrome are picked up from /Applications."
    miss=$(python3 -c "import importlib.util as u, sys
print(' '.join(m for m in sys.argv[1:] if u.find_spec(m) is None))" music21 mido pypdf cffi 2>/dev/null)
    [ -n "$miss" ] && echo "missing Python packages: pip3 install $miss"
    tools=""
    command -v pdftotext >/dev/null 2>&1 || tools="$tools poppler"
    command -v fluidsynth >/dev/null 2>&1 || tools="$tools fluid-synth"
    command -v ffmpeg >/dev/null 2>&1 || tools="$tools ffmpeg"
    [ -n "$tools" ] && echo "missing tools: brew install$tools"
    exit 0
fi

ROOT=$(cd "$(dirname "$0")/.." && pwd)
HOLLYWOOD="$ROOT/tools/hollywood"
LOG="${TMPDIR:-/tmp}/setup-music.log"
PY_PKGS="music21 mido pypdf cffi"
# libegl1 + libopengl0: the MuseScore 4 AppImage does not bundle them (it
# fails with "libEGL.so.1: cannot open shared object file" without them).
APT_PKGS="fonts-noto-cjk fonts-ebgaramond fonts-ebgaramond-extra poppler-utils
          fluidsynth fluid-soundfont-gm ffmpeg libxml2-utils libegl1 libopengl0"
FAILED=0
START=$(date +%s)
: > "$LOG" || { echo "setup: cannot write $LOG"; exit 1; }
echo "setup: log in $LOG"

SUDO=""
if [ "$(id -u)" != 0 ] && command -v sudo >/dev/null 2>&1; then
    SUDO="sudo -n"
fi

# --- output helpers --------------------------------------------------------
# begin NAME: print the component name (no newline) and remember where its
# part of the log starts; ok / done_ / fail end the line.
begin() {
    printf '%-12s' "$1"
    MARK=$(wc -l < "$LOG")
    echo "===== $1 =====" >> "$LOG"
}
ok()    { echo "ok${1:+ ($1)}"; }
done_() { echo "installed${1:+ ($1)}"; }
fail() {
    echo "FAILED${1:+ ($1)}"
    FAILED=$((FAILED + 1))
    tail -n +"$((MARK + 2))" "$LOG" | tail -n 15 | sed 's/^/    | /'
}
run() { "$@" >> "$LOG" 2>&1; }          # run a command into the log

# hollywood.py helper: python code that sees `hollywood` imported.
holly() {
    python3 -B - "$HOLLYWOOD" "$@" <<'EOF'
import sys
sys.path.insert(0, sys.argv[1])
import hollywood
exec(sys.argv[2])
EOF
}

# --- 1. Python packages ----------------------------------------------------
py_missing() {
    python3 -c "import importlib.util as u, sys
print(' '.join(m for m in sys.argv[1:] if u.find_spec(m) is None))" $PY_PKGS
}
begin "python"
missing=$(py_missing 2>> "$LOG")
if [ -z "$missing" ]; then
    ok
else
    PIP="python3 -m pip install -q --disable-pip-version-check --root-user-action=ignore"
    if ! run $PIP $missing && grep -q externally-managed "$LOG"; then
        run $PIP --break-system-packages $missing
    fi
    if [ -z "$(py_missing 2>> "$LOG")" ]; then done_ "$(echo $missing)"; else fail "$(echo $missing)"; fi
fi

# --- 2. apt packages -------------------------------------------------------
apt_missing() {
    for p in $APT_PKGS; do
        dpkg -s "$p" 2>/dev/null | grep -q '^Status: install ok installed' || printf '%s ' "$p"
    done
}
begin "apt"
missing=$(apt_missing)
FONTS_NEW=""
if [ -z "$missing" ]; then
    ok
elif [ "$(id -u)" != 0 ] && [ -z "$SUDO" ]; then
    echo "not root and no sudo; cannot install: $missing" >> "$LOG"
    fail "need root"
else
    export DEBIAN_FRONTEND=noninteractive
    APT="$SUDO env DEBIAN_FRONTEND=noninteractive apt-get -qq -o DPkg::Lock::Timeout=300"
    # A partly failing update (one unreachable third-party repo) is not
    # fatal; the install below says whether what we need was reachable.
    run $APT update || echo "(apt-get update reported errors; trying the install anyway)" >> "$LOG"
    # No recommends: fluidsynth would otherwise pull qsynth and a Qt 6 GUI
    # stack (40+ packages); of those, MuseScore needs only libegl1 and
    # libopengl0, which are listed above.
    run $APT install -y --no-install-recommends $missing
    still=$(apt_missing)
    case "$missing" in *fonts-*) FONTS_NEW=1 ;; esac
    if [ -z "$still" ]; then done_ "$(echo $missing)"; else fail "missing: $(echo $still)"; fi
fi

# --- 3. Fonts (cover: EB Garamond + Noto Serif CJK SC) ---------------------
begin "fonts"
if [ -n "$FONTS_NEW" ]; then run fc-cache -f; fi
fams=$(fc-list : family 2>> "$LOG")
lack=""
echo "$fams" | grep -q "Noto Serif CJK SC" || lack="$lack Noto-Serif-CJK-SC"
echo "$fams" | grep -q "EB Garamond" || lack="$lack EB-Garamond"
if [ -n "$lack" ]; then
    echo "fontconfig does not list:$lack" >> "$LOG"
    fail "missing:$lack"
elif [ -n "$FONTS_NEW" ]; then done_ "fc-cache refreshed"
else ok
fi

# --- 4. MuseScore 4 --------------------------------------------------------
ms4_path() { holly 'print(hollywood.find_ms4(install=False) or "")' 2>> "$LOG"; }
ms4_works() { run timeout 120 env QT_QPA_PLATFORM=offscreen "$1" --version; }
begin "musescore4"
MS4=$(ms4_path)
how=ok
if [ -z "$MS4" ]; then
    how=done_
    run holly 'hollywood.find_ms4()'
    MS4=$(ms4_path)
fi
good=""
if [ -n "$MS4" ] && ms4_works "$MS4"; then
    good=1
elif [ "$MS4" = /opt/ms4/squashfs-root/AppRun ] \
     && ! tail -n +"$((MARK + 2))" "$LOG" | grep -q "error while loading shared libraries"; then
    # A half-finished earlier download or extraction: start over once.
    # (A missing system library is reported as is: downloading again
    # would not help.)
    echo "(MuseScore 4 in /opt/ms4 does not start; reinstalling)" >> "$LOG"
    run $SUDO rm -rf /opt/ms4/squashfs-root /opt/ms4/ms4.AppImage
    how=done_
    run holly 'hollywood.find_ms4()'
    MS4=$(ms4_path)
    [ -n "$MS4" ] && ms4_works "$MS4" && good=1
fi
if [ -n "$good" ]; then $how "$MS4"; else fail "$MS4"; fi

# --- 5. Chromium (cover page and running headers) --------------------------
begin "chromium"
CHROME=$(holly 'print(hollywood.find_chrome())' 2>> "$LOG")
if [ -n "$CHROME" ]; then ok "$CHROME"; else fail "not found; set CHROME=/path"; fi

# --- 6. MusicXML 4.0 schema ------------------------------------------------
begin "schema"
if [ -f "$HOLLYWOOD/qa.py" ]; then
    had=$(ls -A "$HOME/.cache/musicxml" 2>/dev/null)
    if run python3 "$HOLLYWOOD/qa.py" fetch-schema; then
        if [ -n "$had" ]; then ok "~/.cache/musicxml"; else done_ "~/.cache/musicxml"; fi
    else
        fail
    fi
else
    echo "skipped (tools/hollywood/qa.py not present)"
fi

# --- summary ---------------------------------------------------------------
secs=$(($(date +%s) - START))
if [ "$FAILED" -eq 0 ]; then
    echo "setup: all ok (${secs}s)"
else
    echo "setup: $FAILED FAILED (${secs}s); full log: $LOG"
    exit 1
fi
