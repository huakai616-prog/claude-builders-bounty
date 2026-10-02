# Delivery center (编曲交付中心)

**GPT / Codex** (no `Artifact` / `ArtifactData` tools): do step 1 (the catalog entry; you merge into `main` in step 8, so `ref=None`), commit `<song>/output/` and run step 2 only to check that the work packs, skip steps 3–7 (your reply does not open with the center link: say the files are committed but not yet in the delivery center), and do step 8, setting the work's status in AGENTS.md's 精简表 and `docs/项目地图.md` to 「已完成，还没进交付中心」. End the reply with 「请 Claude 把它加进交付中心：slug `<slug>`，目录 `<dir>/`，已合并进 main，catalog.py 已写」.

The page is `tools/deliver/center.html`, published at https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN and pinned in the user's claude.ai sidebar.

- It lists the works from its database: collection `works`, one document per work, sorted newest first.
- It serves each work's files from `files/<slug>/`.
- 「下载到电脑」 builds `<歌名>_编曲交付.zip` in the browser from `bundle.json` and saves it through the `downloads` capability. The zip has `说明.txt`, `1_四样主文件/` and `2_其他文件/`. (The artifact host refuses to serve .zip, .mid or .musicxml files, so small files travel base64 inside `bundle.json`; PDF, mp3, mp4, png and fonts are served as themselves.)
- 「全部歌曲一次下载」 merges every song into one zip.
- 「选择文件」 opens a file browser inside the card. Folders are collapsed; clicking a folder's name opens it. Every folder and file has a checkbox and its own 下载 / 删除; the bar at the bottom downloads or deletes the selection, and 「删除整个…」 deletes the whole work.
  - The save dialog only takes some types (pdf, zip, mp4, txt, json, png, jpg …). A single MIDI / MusicXML / mp3 / srt goes out as `<name>.zip`; several files go out as one zip.
  - Every delete opens an in-page confirmation first (`window.confirm` is blocked in artifacts).
  - Deletes never touch the published files. They go on the work's db row: `removed` holds paths relative to the bundle's top folder, and `deleted: true` hides the whole work. The 「已删除」 section at the bottom restores either.
  - Deleted files are left out of every zip, and the PDF / video buttons hide when those files are removed.

To add or update a work, after its files are built and committed:

1. Add or edit its entry in `tools/deliver/catalog.py`.
   - `ref=None` means "the current working tree", i.e. the song you just built.
   - Fill in `main` (the four files), `pdf_kind` (`"hollywood"` for the tools/hollywood PDF), `audio`, and the open questions for the user.
   - Instrumental work: `main=dict(musicxml=…, pdf=…, strings=…, parts=…)` plus `other_note` and `howto` (no SRT or GBK file); with a pickup, `howto` says 「ACE 第 N 小节 = 总谱第 N−1 小节」. See `instrumental.md`.
   - Pizzicato or con sordino anywhere: ACE's smart mode does not read them from the MIDI, so `howto` lists the bars where the user must switch the technique by hand (see alla-turca).
2. `python3 tools/deliver/package.py <slug> --files` (commit `<song>/output/` first: on an uncommitted `src` it dies with `ValueError: not enough values to unpack`). This prints the `files` map to publish. Output goes to `tools/deliver/dist/`, which is git-ignored.
3. `Artifact` `action: "read"` on the URL. A publish from a new conversation is refused until you have read it. Also `Artifact` `action: "list"` with `scope: "files"` on the URL: a publish that replaces a published path you have neither read nor listed (`files/works.json`, an existing song's `files/<slug>/…`) is refused. If the page the read returns differs from `tools/deliver/center.html`, merge the difference into the repo file before publishing.
4. `Artifact` publish:
   - `url` = the page URL;
   - `file_path` = `tools/deliver/center.html`;
   - `files` = the printed map.
   Files you leave out are kept. Omit `capabilities` and `icon` so they stay as they are.
5. `ArtifactData` `set` on collection `works`, doc_id `<slug>`, `file_path` = `tools/deliver/dist/rows/<slug>.json`. If the document already exists, `get` it first and pass its `version` as `if_version`. Also carry over its `removed` and `deleted` fields into the new row (write them into `tools/deliver/dist/rows/<slug>.json` before the `set`), because those are the user's own deletions. Drop them only if the user asked to bring the files back, or if the new bundle no longer has those paths.
6. Refresh the fallback list: `ArtifactData` `list` on collection `works` with `out_dir` = a scratch dir, then `python3 tools/deliver/package.py --snapshot <dir>` and publish the printed `files/works.json`. The page shows this snapshot when its database does not answer.
7. Reply to the user with the page link first, then what changed.
8. Commit (including `catalog.py`, the song's entry in `docs/编配手法索引.md` (at the end of section 三, plus its name in section 一 items, or a new section 一 item for a device it shares with one earlier song), and its rows in `docs/项目地图.md` and in AGENTS.md's 精简表), push, open a PR to `main`, and merge it.

Whenever you edit `center.html`, check that its script still parses before publishing. One syntax error and the page shows no songs and no download buttons at all:

```bash
python3 -c "s=open('tools/deliver/center.html',encoding='utf-8').read(); open('/tmp/page.js','w').write(s[s.index('<script>\n')+9:s.rindex('</script>')])" && node --check /tmp/page.js
```

Shell commands inside a JS template literal (`MAC_CMD`) must escape `${` as `\${`; an unescaped `${p%/…}` broke the page once.

Works that live on other branches keep `origin/<branch>` as `ref` (e.g. `ref="origin/claude/serene-darwin-2l4jy4"`). `package.py` reads them with `git archive`, so fetch first: `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`.
