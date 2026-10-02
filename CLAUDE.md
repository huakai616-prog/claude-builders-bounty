# Notes for Claude

Project context lives in AGENTS.md (the always-needed rules: the user's preferences, how to build and verify, known pitfalls, open tasks, a short project map), which is shared with the other agents working in this repo (GPT / Codex), and in the on-demand files its 「什么时候读哪个文件」 table points to (docs/项目地图.md for the full project map, docs/编配手法索引.md, docs/钢琴谱改编.md, docs/ACE-Studio.md for the ACE Studio steps, and the hollywood-score skill's references/). Update them there, not here, and follow AGENTS.md's rule about what belongs in AGENTS.md itself.

@AGENTS.md

## Claude-only

- ACE Studio MCP server (fallback only if the CLI in docs/ACE-Studio.md is blocked by sandboxing/permissions): register as `ace-studio` with user scope:
  `claude mcp add --scope user ace-studio "/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"`
- Hollywood score skill: `.claude/skills/hollywood-score/SKILL.md`. Load it before producing or updating any song's score, PDF, Sibelius file or MIDI (deliverables, 花开当富贵 credits, Hollywood PDF with cover, adding the work to the pinned 编曲交付中心 page, merging into main).
- Know-how skills: plugin `acestudio@acestudio` from https://github.com/BeatMagic/acestudio_agent_plugin (enabled in `.claude/settings.json`). Load `ace-studio-features` / `ace-studio-workflows` before driving ACE Studio.
