#!/bin/bash
# 把「编曲交付中心」装进「应用程序」，放进程序坞，然后打开一次。
# 交付中心页面上的「复制安装命令」会找到下载好的安装包并运行这个脚本；
# 也可以自己在终端里运行：bash 安装.sh
#
# 用 osacompile 在这台 Mac 上现编一个原生小程序（不会被安全设置拦，也不用 Rosetta），
# 换上交付中心的图标。编不出来时，退回安装包里现成的 编曲交付中心.app。
#
# 注意：Mac 的 /bin/bash 是 3.2，变量后面紧跟中文时会把中文的第一个字节当成变量名，
# 所以挨着中文的变量一律写成 ${NAME} 这种带大括号的形式。

URL="https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN"
NAME="编曲交付中心"
NAME_URL="%E7%BC%96%E6%9B%B2%E4%BA%A4%E4%BB%98%E4%B8%AD%E5%BF%83"   # 程序坞里存的是网址编码的路径
HERE="$(cd "$(dirname "$0")" && pwd)"
ICON="$HERE/$NAME.app/Contents/Resources/AppIcon.icns"

DEST=/Applications
[ -w "$DEST" ] || { DEST="$HOME/Applications"; mkdir -p "$DEST"; }
APP="$DEST/$NAME.app"

echo "正在安装「${NAME}」到 ${DEST} …"
TMP="$(mktemp -d)"
NEW="$TMP/$NAME.app"
if osacompile -o "$NEW" -e "open location \"$URL\"" 2>/dev/null; then
  R="$NEW/Contents/Resources"
  rm -f "$R/Assets.car"                                          # 否则系统用默认的脚本图标
  plutil -remove CFBundleIconName "$NEW/Contents/Info.plist" 2>/dev/null
  cp "$ICON" "$R/applet.icns"
  codesign --force --deep --sign - "$NEW" 2>/dev/null
else
  ditto "$HERE/$NAME.app" "$NEW"
fi
xattr -cr "$NEW" 2>/dev/null
rm -rf "$APP"
if ! ditto "$NEW" "$APP"; then
  echo "没装上：没有权限写入 ${DEST}。"
  rm -rf "$TMP"
  exit 1
fi
rm -rf "$TMP"
touch "$APP"

# 放进程序坞（已经钉在上面就不重复加）。只查钉住的 persistent-apps：
# 「最近使用」里也会出现它，那不算。程序坞会把路径改存成网址编码的 file:// 形式，两种都认。
DOCKP="$(mktemp)"
defaults export com.apple.dock "$DOCKP" 2>/dev/null
if plutil -extract persistent-apps xml1 -o - "$DOCKP" 2>/dev/null \
     | grep -qE "Applications/(${NAME}|${NAME_URL})\.app"; then
  echo "程序坞里已经有它了。"
else
  defaults write com.apple.dock persistent-apps -array-add \
    "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>${APP}</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
  killall Dock
fi
rm -f "$DOCKP"

open "$APP"
echo "装好了：以后点程序坞里的「${NAME}」图标，就会打开交付中心（总是最新版）。"
