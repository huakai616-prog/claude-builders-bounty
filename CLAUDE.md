# Notes for Claude

Project context (project map, the user's preferences, how to build and verify, known pitfalls, open tasks, ACE Studio steps) lives in AGENTS.md, which is shared with the other agents working in this repo (GPT / Codex). Update it there, not here.

@AGENTS.md

## Claude-only

- ACE Studio MCP server (fallback only if the CLI in AGENTS.md is blocked by sandboxing/permissions): register as `ace-studio` with user scope:
  `claude mcp add --scope user ace-studio "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"`
- Hollywood score skill: `.claude/skills/hollywood-score/SKILL.md`. Load it before producing or updating any song's score, PDF, Sibelius file or MIDI (deliverables, 花开当富贵 credits, Hollywood PDF with cover, adding the work to the pinned 编曲交付中心 page, merging into main).
- Know-how skills: plugin `acestudio@acestudio` from https://github.com/BeatMagic/acestudio_agent_plugin (enabled in `.claude/settings.json`). Load `ace-studio-features` / `ace-studio-workflows` before driving ACE Studio.
