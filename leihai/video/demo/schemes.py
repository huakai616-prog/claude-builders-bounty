from mockup import *

def credits_block_old(cv):   # previous video's layout, for comparison
    d = ImageDraw.Draw(cv)
    d.text((76, 1740), '泪海 · 弦乐四重奏', font=font(24), fill=GREY)
    d.text((76, 1782), '词：许常德、李忠屏  曲：李忠屏', font=font(30, 'Bold'), fill=INK)
    d.text((76, 1828), '原唱：许茹芸', font=font(30, 'Bold'), fill=INK)
    t = '编配：花开当富贵'; f = font(30, 'Bold'); d.text((1004 - d.textlength(t, font=f), 1782), t, font=f, fill=INK)
    t = '翻唱：小梅'; d.text((1004 - d.textlength(t, font=f), 1828), t, font=f, fill=INK)

OUT = '/home/user/claude-builders-bounty/leihai/video/demo/'
# 0. previous layout (for comparison)
t = 40.0; cv = base('scene1_hq.png'); lyric(cv, t)
score(cv, t, [1100, 1235, 1370, 1505]); credits_block_old(cv); douyin_zones(cv)
cv.save(OUT + '署名方案0_沿用上次版式_对照.png', optimize=True)

# A. same block, moved up above the Douyin caption area, kept left of the buttons
t = 40.0; cv = base('scene1_hq.png'); lyric(cv, t)
score(cv, t, [1060, 1180, 1300, 1420])
d = ImageDraw.Draw(cv)
d.text((76, 1478), '泪海 · 弦乐四重奏', font=font(22), fill=GREY)
d.text((76, 1506), '词：许常德、李忠屏　曲：李忠屏', font=font(26, 'Bold'), fill=INK)
d.text((76, 1540), '原唱：许茹芸　翻唱：小梅　编配：花开当富贵', font=font(26, 'Bold'), fill=INK)
douyin_zones(cv); cv.save(OUT + '署名方案A_署名上移常驻.png', optimize=True)

# B. title card in the intro + end card, nothing at the bottom during the song
t = 6.0; cv = base('scene0_hq.png'); score(cv, t, [1080, 1220, 1360, 1500])
d = ImageDraw.Draw(cv)
f = font(92, 'Bold'); s = '泪 海'; d.text(((W - d.textlength(s, font=f)) / 2, 820), s, font=f, fill=INK)
f = font(26); s = '弦乐四重奏版　·　原唱 许茹芸　·　翻唱 小梅'; d.text(((W - d.textlength(s, font=f)) / 2, 948), s, font=f, fill=GREY)
douyin_zones(cv); cv.save(OUT + '署名方案B1_片头标题卡_6秒.png', optimize=True)
t = 108.0; cv = base('scene0_hq.png'); score(cv, t, [1080, 1220, 1360, 1500], alpha=0.3)
d = ImageDraw.Draw(cv, 'RGBA')
d.rounded_rectangle([150, 1010, 930, 1470], radius=18, fill=(246, 239, 227, 225))
lines = [('泪 海', font(64, 'Bold'), INK), ('作词　许常德、李忠屏', font(30), INK), ('作曲　李忠屏', font(30), INK), ('原唱　许茹芸', font(30), INK),
         ('翻唱　小梅', font(30), INK), ('弦乐改编 · 制谱　花开当富贵', font(30), INK)]
y = 1040
for s, f, c in lines:
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=c); y += 92 if s == '泪 海' else 58
douyin_zones(cv); cv.save(OUT + '署名方案B2_片尾署名卡_108秒.png', optimize=True)

# C. small info tag in the top-left of the animation, whole video
t = 23.2; cv = base('scene1_hq.png'); lyric(cv, t)
score(cv, t, [1080, 1220, 1360, 1500])
d = ImageDraw.Draw(cv, 'RGBA')
d.rounded_rectangle([36, 186, 470, 318], radius=14, fill=(246, 239, 227, 200))
d.text((58, 198), '泪海 · 弦乐四重奏版', font=font(30, 'Bold'), fill=INK)
d.text((58, 244), '原唱 许茹芸　翻唱 小梅', font=font(22), fill=INK)
d.text((58, 278), '词 许常德、李忠屏　曲 李忠屏　编配 花开当富贵', font=font(18), fill=GREY)
douyin_zones(cv); cv.save(OUT + '署名方案C_左上角信息牌.png', optimize=True)
print('done')
