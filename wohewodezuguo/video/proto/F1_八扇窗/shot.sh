#!/bin/bash
# usage: shot.sh out.png [hash]   (窗口 2010 高 → 视口正好 ≥1920，再裁成 1080×1920)
D="$(cd "$(dirname "$0")" && pwd)"
timeout 120 /opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless=new --no-sandbox --hide-scrollbars --force-device-scale-factor=1 --window-size=1080,2010 --virtual-time-budget=20000 --screenshot=$D/_raw.png "file://$D/frame.html$2" >/dev/null 2>&1
python3 -c "
from PIL import Image
im=Image.open('$D/_raw.png').convert('RGB').crop((0,0,1080,1920)); im.save('$D/$1'); print(im.size)"
rm -f $D/_raw.png
