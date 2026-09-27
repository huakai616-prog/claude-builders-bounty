# Notes for Claude

## ACE Studio (on the user's Mac)

- CLI (use this first): `"/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"` — quote the path, it contains a space; run it with `help` to list commands.
- MCP server (fallback only if the CLI is blocked by sandboxing/permissions): register as `ace-studio` with user scope:
  `claude mcp add --scope user ace-studio "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"`
- Know-how skills: plugin `acestudio@acestudio` from https://github.com/BeatMagic/acestudio_agent_plugin (enabled in `.claude/settings.json`). Load `ace-studio-features` / `ace-studio-workflows` before driving ACE Studio.
- ACE Studio and the agent must run on the same machine; a cloud session cannot reach it.

## Open task: 泪海 chorus arrangement → ACE Studio

Files are in `leihai/output/` (regenerate with `python3 leihai/build.py`). F major, ♩=59, voice + string quartet. To render it in ACE Studio:

1. Import `泪海_副歌_人声弦乐四重奏_全轨.mid` at bar 1, keeping its tempo map (allargando/rit. from bar 24).
2. Track "Vocal 人声" → Vocal Synth, a Mandarin female pop voice (lyrical, breathy). Lyrics are on the notes (UTF-8, `-` = melisma continuation). If the lyrics come through garbled, use `泪海_人声_带歌词_GBK编码备用.mid` instead.
3. Tracks Violin I / Violin II / Viola / Violoncello → AI instrument **String Section** with speakers Violins I / Violins II / Violas / Celli. Keep smart articulation mode (no pizz/mute in this arrangement).
4. Bar 15 beat 4 is intentionally empty in the strings (voice a cappella) — do not fill it.
5. Make sure no track is muted/soloed so every track renders, then play it through.
