<?xml version="1.0" encoding="UTF-8"?>
<!--
  Hollywood full-score house style for MuseScore Studio 4.4 (partial style:
  only the keys listed here change, everything else stays at MS4 defaults).

  Applied by tools/hollywood/score_pdf.py as `-S hollywood.mss` on an .mscz
  (MS4 ignores -S when it imports MusicXML directly, so the script imports
  to .mscz first).

  Conventions (see .claude/skills/hollywood-score/SKILL.md):
    * 11 x 17 in (tabloid) portrait full score, concert pitch
    * margins leave room for the header / footer that score_pdf.py draws
    * bar number on every bar, boxed, centred over the bar
    * boxed bold rehearsal marks, bold tempo marks
    * Leland music font, Edwin text, Noto Serif CJK SC for Chinese
    * MuseScore's own header / footer / page numbers switched off
-->
<museScore version="4.40">
  <Style>
    <!-- page: 11 x 17 in, header zone 1.05 in, footer zone 0.95 in -->
    <pageWidth>11</pageWidth>
    <pageHeight>17</pageHeight>
    <pagePrintableWidth>9.8</pagePrintableWidth>
    <pageEvenLeftMargin>0.6</pageEvenLeftMargin>
    <pageOddLeftMargin>0.6</pageOddLeftMargin>
    <pageEvenTopMargin>1.05</pageEvenTopMargin>
    <pageOddTopMargin>1.05</pageOddTopMargin>
    <pageEvenBottomMargin>0.95</pageEvenBottomMargin>
    <pageOddBottomMargin>0.95</pageOddBottomMargin>
    <pageTwosided>0</pageTwosided>
    <Spatium>1.8</Spatium>

    <!-- vertical spacing: generous, systems spread to fill each page -->
    <staffDistance>7.5</staffDistance>
    <akkoladeDistance>6.5</akkoladeDistance>
    <minSystemDistance>11</minSystemDistance>
    <maxSystemDistance>20</maxSystemDistance>
    <enableVerticalSpread>1</enableVerticalSpread>
    <minSystemSpread>10</minSystemSpread>
    <maxSystemSpread>30</maxSystemSpread>
    <maxStaffSpread>10</maxStaffSpread>
    <maxPageFillSpread>10</maxPageFillSpread>
    <lastSystemFillLimit>0</lastSystemFillLimit>
    <measureSpacing>1.5</measureSpacing>
    <minMeasureWidth>10</minMeasureWidth>

    <!-- engraving weights -->
    <staffLineWidth>0.11</staffLineWidth>
    <barWidth>0.18</barWidth>
    <bracketWidth>0.5</bracketWidth>
    <hairpinLineWidth>0.13</hairpinLineWidth>

    <!-- header, footer, page numbers are drawn by score_pdf.py -->
    <showHeader>0</showHeader>
    <showFooter>0</showFooter>
    <showPageNumber>0</showPageNumber>
    <showPageNumberOne>0</showPageNumberOne>

    <!-- bar numbers: every bar, boxed, bold, centred above the top staff -->
    <showMeasureNumber>1</showMeasureNumber>
    <showMeasureNumberOne>1</showMeasureNumberOne>
    <measureNumberInterval>1</measureNumberInterval>
    <measureNumberSystem>0</measureNumberSystem>
    <measureNumberAllStaves>0</measureNumberAllStaves>
    <measureNumberVPlacement>0</measureNumberVPlacement>
    <measureNumberHPlacement>1</measureNumberHPlacement>
    <measureNumberFontFace>Edwin</measureNumberFontFace>
    <measureNumberFontSize>10</measureNumberFontSize>
    <measureNumberFontStyle>1</measureNumberFontStyle>
    <measureNumberFrameType>1</measureNumberFrameType>
    <measureNumberFramePadding>0.35</measureNumberFramePadding>
    <measureNumberFrameWidth>0.1</measureNumberFrameWidth>
    <measureNumberPosAbove x="0" y="-3"/>
    <!-- 0.5 sp: a fermata or dynamic just under the row must not push a
         single box above its neighbours -->
    <measureNumberMinDistance>0.5</measureNumberMinDistance>

    <!-- rehearsal marks: big, bold, boxed -->
    <rehearsalMarkFontFace>Edwin</rehearsalMarkFontFace>
    <rehearsalMarkFontSize>16</rehearsalMarkFontSize>
    <rehearsalMarkFontStyle>1</rehearsalMarkFontStyle>
    <rehearsalMarkFrameType>1</rehearsalMarkFrameType>
    <rehearsalMarkFramePadding>0.6</rehearsalMarkFramePadding>
    <rehearsalMarkFrameWidth>0.22</rehearsalMarkFrameWidth>
    <rehearsalMarkMinDistance>1</rehearsalMarkMinDistance>

    <!-- tempo -->
    <tempoFontFace>Edwin</tempoFontFace>
    <tempoFontSize>13</tempoFontSize>
    <tempoFontStyle>1</tempoFontStyle>
    <metronomeFontFace>Edwin</metronomeFontFace>
    <metronomeFontSize>13</metronomeFontSize>
    <metronomeFontStyle>1</metronomeFontStyle>

    <!-- text -->
    <defaultFontFace>Edwin</defaultFontFace>
    <expressionFontFace>Edwin</expressionFontFace>
    <expressionFontSize>10.5</expressionFontSize>
    <staffTextFontFace>Edwin</staffTextFontFace>
    <staffTextFontSize>10.5</staffTextFontSize>
    <systemTextFontFace>Edwin</systemTextFontFace>
    <systemTextFontSize>11</systemTextFontSize>
    <longInstrumentFontFace>Edwin</longInstrumentFontFace>
    <longInstrumentFontSize>11</longInstrumentFontSize>
    <shortInstrumentFontFace>Edwin</shortInstrumentFontFace>
    <shortInstrumentFontSize>10</shortInstrumentFontSize>

    <!-- lyrics: Chinese serif -->
    <lyricsOddFontFace>Noto Serif CJK SC</lyricsOddFontFace>
    <lyricsOddFontSize>10.5</lyricsOddFontSize>
    <lyricsEvenFontFace>Noto Serif CJK SC</lyricsEvenFontFace>
    <lyricsEvenFontSize>10.5</lyricsEvenFontSize>
    <lyricsPosBelow x="0" y="3.5"/>
    <lyricsMinBottomDistance>2</lyricsMinBottomDistance>

    <!-- first-page title block (credits come from the MusicXML) -->
    <titleFontFace>Noto Serif CJK SC</titleFontFace>
    <titleFontSize>30</titleFontSize>
    <titleFontStyle>1</titleFontStyle>
    <subTitleFontFace>Noto Serif CJK SC</subTitleFontFace>
    <subTitleFontSize>14</subTitleFontSize>
    <!-- MS4's default (10 mm) leaves the 30 pt title touching the subtitle -->
    <subTitleOffset x="0" y="13"/>
    <composerFontFace>Noto Serif CJK SC</composerFontFace>
    <composerFontSize>10.5</composerFontSize>
    <lyricistFontFace>Noto Serif CJK SC</lyricistFontFace>
    <lyricistFontSize>10.5</lyricistFontSize>
  </Style>
</museScore>
