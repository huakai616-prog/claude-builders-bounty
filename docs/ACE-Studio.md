# ACE Studio（在用户的 Mac 上）

要驱动 ACE Studio、或者用户问怎么在 ACE 里渲染时读这一页。

- ACE Studio 和操作它的 AI 必须在同一台机器上，云端环境连不上。
- **命令行（优先用）**：`"/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"`。路径里有空格，要加引号。用 `help` 参数列出所有命令。
- **MCP server**：命令行被沙盒或权限挡住时才用。可执行文件是 `"/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"`，按你自己的 agent 的方式注册。
- **操作知识**：见 https://github.com/BeatMagic/acestudio_agent_plugin 。
- **泪海的渲染步骤**：
  1. 在第 1 小节导入 `leihai/output/泪海_副歌_人声弦乐四重奏_全轨.mid`，保留速度信息（第 24 小节起渐宽、渐慢）。
  2. 「Vocal 人声」轨加载 Vocal Synth，选中文流行女声（抒情、气声多一点）。歌词已经在音符上。如果乱码，改用 `泪海_人声_带歌词_GBK编码备用.mid`。
  3. Violin I / Violin II / Viola / Violoncello 四轨加载 AI 乐器 **String Section**，speaker 分别选 Violins I / Violins II / Violas / Celli。演奏法保持智能模式，这版没有拨弦，也没有弱音器。
  4. 第 15 小节第 4 拍弦乐是故意空着的（人声清唱），不要补。
  5. 确认没有轨被静音或独奏，然后从头播放一遍，让所有轨都渲染。

- **ACE 里拨弦和弱音器只能手动设**：智能模式不会从 MIDI 推出来。要导给 ACE 的编配尽量不用；诀别书全曲没有用；土耳其进行曲的拨弦段要在 ACE 里手动改演奏法（见 `alla-turca/README.md`）。
