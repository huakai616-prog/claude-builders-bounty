# Known pitfalls

- MS4 **ignores `-S style` when it imports MusicXML directly**. `render_pdf` imports to `.mscz` first, then exports with the style.
- MS4 gives imported MusicXML credits odd offsets: the composer drifts to the top and the lyricist falls into the music. `render_pdf` resets the title frame (`_fix_title_frame`).
- The boxed bar numbers sit above every bar, so a rehearsal letter and its bold section title would share their row and run into the section's first bar number ("A Chorus 副歌 [10]"). `render_pdf` lifts both by 5 spaces onto their own row (`_lift_sections`). MS4 ignores `default-y` from MusicXML, so the offset is written into the imported `.mscz`. Set `META["section_lift"] = 0` to turn it off.
- `render_pdf` also sets the Chinese in staff texts ("Chorus 副歌") in Noto Serif CJK SC (otherwise MS4 falls back to WenQuanYi Zen Hei, a sans) and labels 8va lines "8va", "(8va)" after a system break (MS4 imports them as a bare "8" and `-S` does not reset that: `_engrave_fixes` edits the score's own style). `polish_musicxml` makes rehearsal letters bold.
- `hollywood.mss` places ties **between the noteheads** (`tiePlacement… inside`): with the default "outside" a phrase slur ending on a tied note meets the tie in one point.
- Letter-spaced cover lines need `padding-left` equal to their `letter-spacing`, or they sit left of the page axis (CSS adds the spacing after the last glyph too).
- music21 writes the tempo words and the metronome as two directions. Use `tempo_text` so they print as one mark.
- The cover and header are an HTML page printed by headless Chromium on a transparent background and merged onto the MS4 pages. Page size must stay 11 × 17 in on both sides.
- EB Garamond has no ♩ ♭ ♯; `hollywood._sym` wraps them in a fallback font.
- MuseScore 3 (`mscore3`) cannot read this style. The Hollywood PDF needs MuseScore 4.
