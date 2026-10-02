# MuseScore-file touch-ups

Read this when the engraved PDF shows a problem the MusicXML cannot fix: a section title that does not lift onto its own row, too little room under one staff, a tuplet number on the wrong side, an 8va hook running into the next note, or an accidental dropped after an 8va ends mid-bar. The fixes go into the imported MuseScore file through `META["mscx_hook"]` (score) and `META["mscx_part_hook"]` (parts), applied before engraving.

Learned on 冬风 (`dongfeng/build.py` hooks, `_mscx_hook`):

- Section titles written at 12 pt import as `<text><font size="12"/><b>…`, and after `_engrave_fixes` they also carry CJK `<font face>` tags, so `_lift_sections` (which matches `<text><b>[^<]*</b>`) never lifts them. Match them with `<text><font size="12"/><b>(?:(?!</text>).)*</b></text>` and apply the offsets in the song's hook.
- More room under one staff on one line: `<vspacerDown>9</vspacerDown>` right after that staff's `<Measure>` (a `<Spacer>` inside `<voice>` is ignored).
- A tuplet number's side: `<direction>up|down</direction>` after the `<Tuplet>`'s `<eid>` (MS4 ignores MusicXML `placement` on `<tuplet>`).
- An 8va hook short of the next note: `<Segment><subtype>0</subtype><offset x="0" y="0"/><off2 x="-1.5" y="0"/></Segment>` after `<subtype>8va</subtype>`.
- MS4 decides accidentals by written position, so after an 8va ends mid-bar it drops an accidental written for the other octave. `<accidental cautionary="yes" parentheses="no">` keeps it and prints it plain; `cautionary="yes"` alone prints it in parentheses.
