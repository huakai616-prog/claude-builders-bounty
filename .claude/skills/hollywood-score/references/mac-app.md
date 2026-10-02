# Mac Dock app

The user asked for the delivery center as an app in the Mac Dock. The card below the song list, 「放进 Mac 程序坞」 (collapsed by default so the songs come first), handles it:

- 「下载 Mac 应用」 saves `编曲交付中心_安装包.zip`. It contains a ready-made `编曲交付中心.app` (a shell-script launcher with the icon), `安装.sh`, and `安装说明.txt`.
- 「复制安装命令」 copies a one-line `bash -c '…'` command. The command finds the newest download in `~/Downloads`, which is the zip for Chrome and the unpacked folder for Safari, and runs `安装.sh`.
- `安装.sh` does the rest:
  - builds a native applet with `osacompile` (`open location "<page URL>"`), so there is no Gatekeeper prompt and no Rosetta;
  - swaps in the icon (removes `Assets.car` and `CFBundleIconName`) and re-signs it ad hoc;
  - copies it to `/Applications` (or `~/Applications`);
  - adds it to the Dock unless it is already there, then opens it once.
- Without the Terminal, the user can drag the ready-made app into Applications. It is unsigned, so the first launch needs 「系统设置 → 隐私与安全性 → 仍要打开」. Safari 「文件 → 添加到程序坞…」 is the other fallback.

The source is `tools/deliver/macapp/`: `build.py`, `install.sh`, `安装说明.txt`, `icon.svg`, `AppIcon.png` and `AppIcon.icns`. The app only opens the page URL, so it never needs rebuilding for new songs. Rebuild it only if the page URL, the scripts or the icon change:

```bash
python3 tools/deliver/macapp/build.py          # add --icon to redraw the icon (Playwright + Chromium)
```

Pitfalls, learned on the user's Mac:

- macOS `/bin/bash` is 3.2. In UTF-8 locales it treats bytes 0x80–0xFF as letters, so in `"「$NAME」"` the first byte of 」 becomes part of the variable name, and the output shows 「??. Write `${NAME}` whenever Chinese text follows a variable. To reproduce on Linux, build a Latin-1 locale with `localedef -i en_US -f ISO-8859-1 <dir>/en_US.ISO-8859-1` and run with `LOCPATH=<dir> LC_ALL=en_US.ISO-8859-1`.
- The 'already in the Dock' check reads only `persistent-apps` (via `plutil -extract`). The app also shows up in `recent-apps`, which must not count.
- `MAC_CMD` sorts downloads with `ls -tdc`, because unzipping back-dates mtimes. It accepts only `*.zip` and `*/安装.sh`, skipping partial downloads. It also runs `ls .` first, so a Terminal that is denied the Downloads folder gets a real message and not 「没找到安装包」.

Then publish `center.html` with the printed `files` map (`files/macapp/app.json`, `files/macapp/icon.png`). The install command itself lives in `center.html` as `MAC_CMD`.
