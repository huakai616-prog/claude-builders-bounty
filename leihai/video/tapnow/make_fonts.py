"""把思源宋体（Noto Serif CJK SC）裁成只含本片用字的小字库，放进 assets/。

    python3 make_fonts.py

只有改了歌词、署名、钩子字幕或 shots.py 里的文字时才需要重跑。
需要 fonttools 和系统里的 Noto Serif CJK（Ubuntu：apt-get install fonts-noto-cjk fonts-noto-cjk-extra）。
字体是 SIL Open Font License 1.1，许可证见 assets/OFL.txt。
"""
import pathlib
import subprocess
import sys

import assemble as A
import shots as SH

SRC = '/usr/share/fonts/opentype/noto/NotoSerifCJK-{}.ttc'


def charset():
    text = [A.CAPTION, A.CARD_TEXT, ''.join(A.LABELS), ''.join(c[0] for c in A.CREDITS)]
    text += [L['text'] for L in SH.TIMING['lines']]
    for s in SH.SHOTS:
        text += [s['id'], s['title'], s['music'], s['refs']]
    chars = set(''.join(text)) | set('0123456789:：.–-·、，。（）「」《》 ★☆→IVX/')
    chars |= {chr(c) for c in range(0x20, 0x7f)}
    return ''.join(sorted(chars))


def main():
    chars = charset()
    out = A.ASSETS
    (out / 'chars.txt').write_text(chars, encoding='utf-8')
    for w in ('Regular', 'Medium', 'Bold'):
        src = SRC.format(w)
        if not pathlib.Path(src).exists():
            sys.exit(f'找不到 {src}')
        dst = out / f'NotoSerifSC-{w}-subset.otf'
        subprocess.run([sys.executable, '-m', 'fontTools.subset', src, '--font-number=2', f'--text-file={out / "chars.txt"}',
                        f'--output-file={dst}', '--layout-features=*', '--name-IDs=*', '--name-languages=*'], check=True)
        print(dst.name, dst.stat().st_size // 1024, 'KB')
    (out / 'chars.txt').unlink()


if __name__ == '__main__':
    main()
