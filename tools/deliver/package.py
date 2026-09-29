#!/usr/bin/env python3
"""Build the downloads for 编曲交付中心 (the pinned delivery page).

    python3 tools/deliver/package.py            # every work in catalog.py
    python3 tools/deliver/package.py wobunanguo # just one
    python3 tools/deliver/package.py wobunanguo --files
        # also print the Artifact `files` map to publish for that work

For each work it pulls the files from the work's git ref (or the working
tree), and writes to tools/deliver/dist/ (not committed):

    dist/files/<slug>/bundle.json  everything, laid out for the user: the
                                   page turns it into <title>_编曲交付.zip
                                   in the browser (the artifact cannot host
                                   .zip); small files inline as base64,
                                   media as separate served files
    dist/files/<slug>/m-*.<ext>    media referenced by bundle.json
    dist/files/<slug>/bundle.zip   the same zip, for local checks only
    dist/files/<slug>/score.pdf    the score PDF, if any
    dist/files/<slug>/preview.mp3  the GM preview, if any
    dist/files/<slug>/cover.jpg    first PDF page as a thumbnail
    dist/files/<slug>/clip.mp4     a video, if any
    dist/works.json                one db document per work ("works/<slug>")
    dist/rows/<slug>.json          the same document, for ArtifactData file_path

Then publish center.html with dist/files/** to the delivery-center artifact
and write the rows from works.json with ArtifactData (see the
hollywood-score skill, "Delivery center").
"""
import base64
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DIST = os.path.join(HERE, "dist")
sys.path.insert(0, HERE)
from catalog import WORKS  # noqa: E402

# served by the artifact host as-is; anything else goes inline as base64
MEDIA = {".pdf", ".mp3", ".mp4", ".webm", ".wav", ".ogg", ".png", ".jpg",
         ".jpeg", ".gif", ".webp", ".otf", ".ttf", ".woff", ".woff2"}
LABELS = dict(musicxml="西贝柳斯工程", pdf="总谱 PDF", strings="弦乐总 MIDI",
              vocal="人声带歌词 MIDI")
SONG_KEYS = ("musicxml", "pdf", "strings", "vocal")
CN_NUM = {1: "一", 2: "两", 3: "三", 4: "四"}
OTHER_DIR = "2_其他文件"


def main_keys(w):
    """The main deliverables of a work: the usual four, or (instrumental
    works, no voice) musicxml / pdf / strings."""
    return ("musicxml", "pdf", "strings") if w.get("instrumental") \
        else SONG_KEYS


def main_dir(w):
    return f"1_{CN_NUM[len(main_keys(w))]}样主文件"
CREDIT = "花开当富贵"


def git(*args, binary=False):
    out = subprocess.run(["git", "-C", REPO, "-c", "core.quotepath=off", *args],
                         check=True, capture_output=True)
    return out.stdout if binary else out.stdout.decode("utf-8")


def fetch_tree(ref, paths, dest):
    """Copy `paths` (files or dirs) from `ref` (None = working tree)."""
    if ref is None:
        for p in paths:
            src = os.path.join(REPO, p)
            dst = os.path.join(dest, p)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__"))
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        return
    tar = git("archive", "--format=tar", ref, "--", *paths, binary=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(dest, filter="data")


def last_commit(ref, path):
    iso, subj = git("log", "-1", "--format=%cI%x09%s", ref or "HEAD", "--",
                    path).strip().split("\t", 1)
    return iso, subj


def files_under(root):
    out = []
    for d, _, fs in os.walk(root):
        for f in fs:
            full = os.path.join(d, f)
            out.append(os.path.relpath(full, root))
    return sorted(out)


def readme_txt(w, main_rel, layout_note):
    lines = [f"{w['title']}（{w['subtitle']}）", ""]
    meta = " · ".join(x for x in (w.get("key"), w.get("tempo"),
                                  w.get("instrumentation")) if x)
    if meta:
        lines.append(meta)
    if w.get("artist"):
        lines.append(f"原唱：{w['artist']}")
    if w["section"] == "song":
        lines.append(f"改编、制谱：{CREDIT}")
    lines.append("")
    if main_rel:
        lines.append(f"{CN_NUM[len(main_rel)]}样主文件：")
        for k, rel in main_rel:
            label = (w.get("labels") or {}).get(k, LABELS[k])
            lines.append(f"  · {label}：{rel if rel else '（这首还没有）'}")
        lines.append("")
        lines += ["怎么用：",
                  "  · 西贝柳斯：文件 → 打开，选 .musicxml（或 .mxl），打开后「另存为」就是 .sib 工程。"]
        if w.get("instrumental"):
            lines += ["  · 分谱：西贝柳斯打开总谱后会自动生成各声部分谱（窗口 → 分谱）。",
                      "  · ACE Studio：导入「全轨」MIDI，四条轨都加载 AI 乐器 String Section，speaker 分别选 Violins I / Violins II / Violas / Celli。",
                      ""]
        else:
            lines += ["  · ACE Studio：导入「全轨」MIDI（或人声带歌词 MIDI），歌词已经在音符上；乱码就换 GBK 那份。",
                      ""]
    if layout_note:
        lines += [layout_note, ""]
    if w.get("note"):
        lines += [w["note"], ""]
    if w.get("questions"):
        lines.append("待你确认：")
        lines += [f"  · {q}" for q in w["questions"]]
        lines.append("")
    lines.append(f"打包日期：{datetime.date.today():%Y-%m-%d}")
    return "﻿" + "\r\n".join(lines) + "\r\n"


def cover_jpg(pdf, out_jpg):
    from PIL import Image
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "60", "-png",
                        pdf, os.path.join(t, "c")], check=True)
        png = [f for f in os.listdir(t) if f.endswith(".png")][0]
        im = Image.open(os.path.join(t, png)).convert("RGB")
        w = 420
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(out_jpg, quality=86, optimize=True, progressive=True)


def package(w):
    slug = w["slug"]
    out = os.path.join(DIST, "files", slug)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    with tempfile.TemporaryDirectory() as tmp:
        paths = [w["src"]] + [p for ps in (w.get("extra") or {}).values()
                              for p in ps]
        fetch_tree(w["ref"], paths, tmp)
        src = os.path.join(tmp, w["src"])
        top = f"{w['title']}_编曲交付" if w["section"] == "song" \
            else w["title"]
        entries = []          # (arcname, abs path)
        main_rel = []
        MAIN_DIR = main_dir(w)
        if w["layout"] == "standard":
            main = w["main"]
            main_names = {v for v in main.values() if v}
            for f in files_under(src):
                sub = MAIN_DIR if f in main_names else OTHER_DIR
                entries.append((f"{top}/{sub}/{f}", os.path.join(src, f)))
            entries.sort()  # 1_四样主文件 before 2_其他文件
            for k in main_keys(w):
                v = main.get(k)
                main_rel.append((k, f"{MAIN_DIR}/{v}" if v else None))
            note = w.get("zip_note") or (
                f"「{MAIN_DIR}」是你要的四样，「{OTHER_DIR}」里是 GBK 备用歌词、"
                "全轨 MIDI、试听 mp3 和字幕。")
        else:
            inc = w.get("include")
            for f in files_under(src):
                if inc and f not in inc:
                    continue
                if f == w.get("video"):  # offered on its own, see below
                    continue
                entries.append((f"{top}/{f}", os.path.join(src, f)))
            for folder, ps in (w.get("extra") or {}).items():
                for p in ps:
                    entries.append((f"{top}/{folder}/{os.path.basename(p)}",
                                    os.path.join(tmp, p)))
            for k in main_keys(w):
                if k in w["main"]:
                    v = w["main"][k]
                    main_rel.append((k, v))
            note = None
        for arc, path in entries:
            assert os.path.exists(path), (slug, arc)
        zpath = os.path.join(out, "bundle.zip")
        readme = readme_txt(w, main_rel, note).encode("utf-8")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED,
                             compresslevel=9) as z:
            z.writestr(f"{top}/说明.txt", readme)
            for arc, path in entries:
                z.write(path, arc)
        bundle = [dict(path=f"{top}/说明.txt",
                       b64=base64.b64encode(readme).decode())]
        for arc, path in entries:
            ext = os.path.splitext(path)[1].lower()
            data = open(path, "rb").read()
            if ext in MEDIA:
                name = "m-" + hashlib.sha1(data).hexdigest()[:12] + ext
                shutil.copy2(path, os.path.join(out, name))
                bundle.append(dict(path=arc, href=f"files/{slug}/{name}"))
            else:
                bundle.append(dict(path=arc, b64=base64.b64encode(data).decode()))
        with open(os.path.join(out, "bundle.json"), "w", encoding="utf-8") as fh:
            json.dump(dict(top=top, files=bundle), fh, ensure_ascii=False)

        def served(path, fallback):
            """Reuse the bundle's media copy of a file, else copy it."""
            data = open(path, "rb").read()
            ext = os.path.splitext(path)[1].lower()
            name = "m-" + hashlib.sha1(data).hexdigest()[:12] + ext
            if not os.path.exists(os.path.join(out, name)):
                name = fallback
                shutil.copy2(path, os.path.join(out, name))
            return f"files/{slug}/{name}"

        def inside(rel):  # a file named relative to the zip's top folder
            for arc, path in entries:
                if arc == f"{top}/{rel}" or arc.endswith("/" + rel):
                    return path
            if os.path.exists(os.path.join(src, rel)):
                return os.path.join(src, rel)
            raise KeyError((slug, rel))

        row = dict(slug=slug, section=w["section"], title=w["title"],
                   subtitle=w["subtitle"], artist=w.get("artist", ""),
                   meta=" · ".join(x for x in (w.get("key"), w.get("tempo"),
                                                w.get("instrumentation")) if x),
                   note=w.get("note", ""), questions=w.get("questions", []),
                   pdf_kind=w.get("pdf_kind"))
        iso, subj = last_commit(w["ref"], w["src"])
        row["updated"] = iso[:10]
        row["sort"] = iso
        row["zip"] = dict(href=f"files/{slug}/bundle.json", name=f"{top}.zip",
                          size=os.path.getsize(zpath), count=len(entries) + 1)
        row["main"] = []
        for k, rel in main_rel:
            label = (w.get("labels") or {}).get(k, LABELS[k])
            row["main"].append(dict(key=k, label=label, ok=bool(rel),
                                    name=os.path.basename(rel) if rel else ""))
        row["pdf"] = None
        pdf_rel = (w.get("main") or {}).get("pdf")
        if pdf_rel:
            p = inside(pdf_rel)
            cover_jpg(p, os.path.join(out, "cover.jpg"))
            row["pdf"] = dict(href=served(p, "score.pdf"),
                              name=os.path.basename(pdf_rel),
                              size=os.path.getsize(p))
            row["cover"] = f"files/{slug}/cover.jpg"
        else:
            row["cover"] = None
        row["audio"] = None
        if w.get("audio"):
            row["audio"] = served(inside(w["audio"]), "preview.mp3")
        row["video"] = None
        if w.get("video"):
            p = inside(w["video"])
            clip = os.path.join(out, "clip.mp4")
            # visually lossless re-encode: keeps the page under its per-file
            # limit; the original stays in the repo
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p,
                            "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a",
                            "192k", "-movflags", "+faststart", clip],
                           check=True)
            row["video"] = dict(href=f"files/{slug}/clip.mp4",
                                name=os.path.basename(p),
                                size=os.path.getsize(clip))
        if w["section"] == "song":
            have = [m["key"] for m in row["main"] if m["ok"]]
            n = len(main_keys(w))
            full = len(have) == n
            if full and w.get("pdf_kind") == "hollywood":
                row["status"], row["status_zh"] = "ready", (
                    f"{CN_NUM[n]}样齐全" + (" · 器乐曲" if w.get("instrumental")
                                          else ""))
            elif full:
                row["status"], row["status_zh"] = \
                    "old", f"{CN_NUM[n]}样齐全 · PDF 是旧版预览"
            else:
                row["status"], row["status_zh"] = "partial", \
                    f"只有 {len(have)} 样，其余还没做"
        else:
            row["status"], row["status_zh"] = "media", "视频 / 动画"
        return row


def main():
    want = {a for a in sys.argv[1:] if not a.startswith("--")}
    works = [w for w in WORKS if not want or w["slug"] in want]
    os.makedirs(DIST, exist_ok=True)
    jpath = os.path.join(DIST, "works.json")
    rows = json.load(open(jpath, encoding="utf-8")) if os.path.exists(jpath) \
        else {}
    for w in works:
        rows[w["slug"]] = package(w)
        r = rows[w["slug"]]
        print(f"{w['slug']:14s} {r['zip']['size']/1e6:6.2f} MB zip, "
              f"{r['zip']['count']} files, updated {r['updated']}, "
              f"{r['status_zh']}")
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(DIST, "rows"), exist_ok=True)
    for slug, r in rows.items():
        with open(os.path.join(DIST, "rows", f"{slug}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(r, fh, ensure_ascii=False)
    total = sum(os.path.getsize(os.path.join(d, f))
                for d, _, fs in os.walk(os.path.join(DIST, "files"))
                for f in fs)
    print(f"dist/files total {total/1e6:.1f} MB -> {jpath}")
    if "--files" in sys.argv:  # publish map (bundle.zip is local-only)
        fmap = {}
        for w in works:
            d = os.path.join(DIST, "files", w["slug"])
            for f in sorted(os.listdir(d)):
                if f != "bundle.zip":
                    fmap[f"files/{w['slug']}/{f}"] = os.path.join(d, f)
        print(json.dumps(fmap, ensure_ascii=False))


if __name__ == "__main__":
    main()
