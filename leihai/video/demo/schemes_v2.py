from mockup import *
OUT = '/home/user/claude-builders-bounty/leihai/video/demo/'
SC = dict(space=12.0, band_px=55, x0=250, x1=885, fade=70)
CENT = [1085, 1200, 1315, 1430]

# A2: credits under the score, arranger emphasised, all inside the safe area
for t, top, name in [(40.0, 'scene1_hq.png', '署名方案A2_编配突出_40秒.png'), (87.5, 'scene2_hq.png', '署名方案A2_编配突出_87秒最高音.png')]:
    cv = base(top); lyric(cv, t, y=880)
    score(cv, t, CENT, **SC)
    d = ImageDraw.Draw(cv)
    d.text((76, 1482), '泪海 · 弦乐四重奏版', font=font(21), fill=GREY)
    d.text((76, 1507), '弦乐编配　花开当富贵', font=font(32, 'Bold'), fill=INK)
    d.text((76, 1550), '原唱 许茹芸 · 翻唱 小梅 · 词 许常德、李忠屏 · 曲 李忠屏', font=font(18), fill=GREY)
    douyin_zones(cv); cv.save(OUT + name, optimize=True)

# B1-2: intro title card with the arranger right under the title
t = 6.0; cv = base('scene0_hq.png'); score(cv, t, CENT, **SC)
d = ImageDraw.Draw(cv)
f = font(92, 'Bold'); s = '泪 海'; d.text(((W - d.textlength(s, font=f)) / 2, 800), s, font=f, fill=INK)
f = font(34, 'Bold'); s = '弦乐编配　花开当富贵'; w = d.textlength(s, font=f); x = (W - w - 50) / 2
d.text(((W - w) / 2, 925), s, font=f, fill=TERRA)
f = font(22); s = '原唱 许茹芸　·　翻唱 小梅　·　弦乐四重奏版'; d.text(((W - d.textlength(s, font=f)) / 2, 978), s, font=f, fill=GREY)
douyin_zones(cv); cv.save(OUT + '署名方案B1-2_片头标题卡_编配突出.png', optimize=True)

# C2: top-left tag led by the arranger
t = 23.2; cv = base('scene1_hq.png'); lyric(cv, t, y=880); score(cv, t, CENT, **SC)
d = ImageDraw.Draw(cv, 'RGBA')
d.rounded_rectangle([36, 186, 500, 300], radius=14, fill=(246, 239, 227, 205))
d.text((58, 198), '花开当富贵 · 弦乐编配', font=font(28, 'Bold'), fill=INK)
d.text((58, 246), '《泪海》原唱 许茹芸　翻唱 小梅', font=font(21), fill=INK)
d.text((58, 274), '词 许常德、李忠屏　曲 李忠屏', font=font(17), fill=GREY)
douyin_zones(cv); cv.save(OUT + '署名方案C2_左上角_编配突出.png', optimize=True)
print('done')
