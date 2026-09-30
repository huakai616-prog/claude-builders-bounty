#!/bin/bash
# usage: shot.sh out.png   (窗口 2010 高 → 视口 ≥1920，再裁成 1080×1920；同时 dump DOM 读自检结果)
D="$(cd "$(dirname "$0")" && pwd)"
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
timeout 120 $CH --headless=new --no-sandbox --hide-scrollbars --force-device-scale-factor=1 --window-size=1080,2010 --virtual-time-budget=20000 --screenshot=$D/_raw.png "file://$D/frame.html" >/dev/null 2>&1
timeout 120 $CH --headless=new --no-sandbox --virtual-time-budget=20000 --dump-dom "file://$D/frame.html" 2>/dev/null | grep -o '<div id="check">[^<]*' | cut -c1-300
python3 -c "
from PIL import Image
im=Image.open('$D/_raw.png').convert('RGB').crop((0,0,1080,1920)); im.save('$D/${1:-frame.png}'); print(im.size)"
rm -f $D/_raw.png
