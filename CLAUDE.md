# Notes for Claude

## ACE Studio (on the user's Mac)

- CLI (use this first): `"/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"` — quote the path, it contains a space; run it with `help` to list commands.
- MCP server (fallback only if the CLI is blocked by sandboxing/permissions): register as `ace-studio` with user scope:
  `claude mcp add --scope user ace-studio "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"`
- Know-how skills: plugin `acestudio@acestudio` from https://github.com/BeatMagic/acestudio_agent_plugin (enabled in `.claude/settings.json`). Load `ace-studio-features` / `ace-studio-workflows` before driving ACE Studio.
- ACE Studio and the agent must run on the same machine; a cloud session cannot reach it.

## Open task: 甲乙丙丁 chorus arrangement → ACE Studio

Files are in `jiayibingding/output/` (regenerate with `python3 jiayibingding/build.py`). To render it in ACE Studio:

1. Import `甲乙丙丁_副歌_人声弦乐五重奏_全轨.mid` at bar 1, keeping its tempo map (rit. in the last two bars).
2. Track "Vocal 人声" → Vocal Synth, a Mandarin female pop voice. Lyrics are on the notes (UTF-8, `-` = melisma continuation). If the lyrics come through garbled, use `甲乙丙丁_人声_带歌词_GBK编码备用.mid` instead.
3. Tracks Violin I / Violin II / Viola / Violoncello / Contrabass → AI instrument **String Section** with speakers Violins I / Violins II / Violas / Celli / Basses. Keep smart articulation mode (no pizz/mute in this arrangement).
4. Make sure no track is muted/soloed so every track renders, then play it through.
