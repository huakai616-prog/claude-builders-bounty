#!/bin/sh
D="$(cd "$(dirname "$0")" && pwd)"
OUT=${1:-frame.png}
/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell --no-sandbox --hide-scrollbars --force-device-scale-factor=1 --window-size=1080,1920 --virtual-time-budget=5000 --screenshot=$D/$OUT file://$D/frame.html 2>&1 | grep -i "written"
