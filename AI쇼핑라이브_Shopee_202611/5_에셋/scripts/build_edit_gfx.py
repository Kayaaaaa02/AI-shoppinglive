"""편집용 그래픽 (1080x1920) — HTML/CSS → Playwright PNG. 폰트 Pretendard, 로고는 정식 로고 PNG(5_에셋/logo/).
python -X utf8 build_edit_gfx.py   → 5_에셋/edit_gfx/

화면 영역은 계획서 4장 기준(세로 %): Shopee 상단 UI 0~33 · 헤드라인 34~40 · 카드 40~68 · 자막 70~76 · AI 고지 76~78 · 채팅 78~100.
- overlay_*.png  투명 PNG. 호스트 화면 위에 얹는다 (헤드라인·측면 카드·고지)
- g_*.png        불투명 전체 화면 카드. 핵심 내용은 34~68% 안에만 둔다
제품은 그리지 않는다: 공식 누끼(5_에셋/banner/src_cutouts)와 공식 발색컷(src_swatch)만 비율 유지로 배치.
"""
import csv, html, importlib.util, json, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
A = ROOT / '5_에셋'
OUT = A / 'edit_gfx'
spec = importlib.util.spec_from_file_location('bb', A / 'banner' / 'template' / 'build_banners.py')
bb = importlib.util.module_from_spec(spec); spec.loader.exec_module(bb)
u, CUT, SW, SHADES = bb.u, bb.CUT, bb.SW, bb.SHADES
LOGO_W = A / 'logo' / 'BANILACO_logo_white.png'
P, INK, BG = '#E9579A', '#2B1F25', '#F8EDF1'
SB = '#F7E8EE'  # G 화면 배경: 레퍼런스 배너의 연핑크 종이 근사
W, H = 1080, 1920
COPY = []


def t(name, text, level='cosmetic'):
    COPY.append((name, text, level))
    return html.escape(text)


def im(key, h, extra=''):
    return f'<img src="{u(CUT / (key + ".png"))}" style="height:{h}px;width:auto;{extra}" alt="{key}">'


def sw(kind, n, w, h, r=18, photo=False):
    # photo=True: G 화면용 — 흰 테두리 사진처럼(레퍼런스 스크랩북 톤)
    deco = 'border:7px solid #fff;box-shadow:0 6px 14px #6b2a4426;' if photo else ''
    return f'<img src="{u(SW / f"{kind}_{n}.jpg")}" style="width:{w}px;height:{h}px;object-fit:cover;border-radius:{2 if photo else r}px;{deco}" alt="{kind} {n}">'


CSS = f'''
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Pretendard,sans-serif;color:{INK}}}
.abs{{position:absolute}} img{{display:block}}
.k{{font-weight:700;font-size:24px;letter-spacing:.14em;text-transform:uppercase;color:{P}}}
.logo-pill{{display:inline-flex;align-items:center;background:{P};border-radius:999px;padding:16px 34px}}
.logo-pill img{{height:24px}}
/* side card 40~68% */
.sc{{left:690px;top:790px;width:366px;background:#fffffff2;border-radius:30px;padding:24px 24px 26px;box-shadow:0 10px 30px #6b2a4433}}
.sc .imgs{{display:flex;align-items:flex-end;justify-content:center;gap:10px;margin:14px 0 12px}}
.sc .ttl{{font-weight:800;font-size:33px;line-height:1.12;letter-spacing:-.02em}}
.sc ul{{list-style:none;margin-top:10px}}.sc li{{font-weight:600;font-size:24px;line-height:1.3;margin-top:6px;padding-left:18px;position:relative}}
.sc li:before{{content:"";position:absolute;left:0;top:12px;width:8px;height:8px;border-radius:50%;background:{P}}}
.big{{font-weight:900;color:{P};letter-spacing:-.04em;line-height:.92}}
/* full G 화면 — 2026-10-15 사용자: 배너 레퍼런스 '10월 더블데이 배너(RM).jpg'(노트·스크랩북) 톤으로 재디자인, 로고는 검정·테두리 없이
   요소: 스프링 노트 상단 · 검정 로고 · 찢은 메모지 제목 + 핑크 테이프 · 핑크 형광펜 · 모눈종이 패널 · 핑크 숫자 블록 · 반짝이 */
.g{{left:0;top:0;width:{W}px;height:{H}px;background:radial-gradient(#ffffff70 1px,transparent 1.4px) 0 0/7px 7px,{SB}}}
.g .spiral{{position:absolute;left:0;right:0;top:0;height:74px;display:flex;justify-content:space-around;padding:0 18px}}
.g .spiral i{{display:block;width:16px;height:64px;border-radius:8px;background:#1d1d1f;box-shadow:inset -4px 0 0 #4a4a4e}}
.g .brand{{position:absolute;top:300px;left:50%;transform:translateX(-50%)}}
.g .brand img{{height:46px}}
.g .zone{{position:absolute;left:50px;right:50px;top:655px;height:650px}}
.g .note{{position:relative;background:repeating-linear-gradient(180deg,#fff 0 37px,#F2D3DE 37px 39px);padding:18px 32px 30px;transform:rotate(-.8deg);
  clip-path:polygon(0 0,100% 0,100% 88%,97% 92%,93% 88%,88% 94%,83% 89%,77% 95%,71% 90%,65% 96%,58% 90%,52% 95%,46% 89%,40% 94%,33% 90%,27% 96%,20% 90%,14% 95%,8% 89%,3% 94%,0 90%);
  filter:drop-shadow(0 4px 6px #6b2a4420)}}
.g .tape{{position:absolute;width:170px;height:46px;background:#F59CC0a6;transform:rotate(-24deg)}}
.g .ttl{{font-weight:900;font-size:58px;line-height:1.08;letter-spacing:-.03em;margin-top:6px;color:#111}}
.g .hl{{background:linear-gradient(180deg,transparent 56%,#F8A9C8 56% 90%,transparent 90%)}}
.g .k{{font-size:22px}}
.g .big{{color:#111}}
.g .panel{{background:#fff linear-gradient(#F4DCE5 1.5px,transparent 1.5px) 0 0/24px 24px,linear-gradient(90deg,#F4DCE5 1.5px,transparent 1.5px) 0 0/24px 24px;
  border-radius:2px;box-shadow:0 6px 16px #6b2a4418}}
.g .pbox{{background:#fff}}
/* 2026-10-15 사용자: 제품 누끼 뒤 배경은 흰색 — 제품이 놓인 칸은 모눈 없이 흰 바탕 */
.g .panel.pw{{background:#fff}}
.g .num{{display:inline-flex;align-items:center;justify-content:center;width:62px;height:62px;background:#F78FB7;color:#111;font-weight:900;font-size:40px;flex:none}}
.g .star{{position:absolute}}
'''
LOGO_B = A / 'logo' / 'BANILACO_logo_black.png'  # 흰 로고와 같은 알파, #111 채움


def overlay(body):
    return f'<div class="abs" style="left:0;top:0;width:{W}px;height:{H}px">{body}</div>'


# 2026-10-15 사용자: AI 배지(시안 2)와 헤드라인을 둘 다 우측 상단으로. 배지 y48(높이 52) → 헤드라인 y116
BADGE_TOP, HEADLINE_TOP = 48, 116


def headline(line):
    return (f'<div class="abs" style="right:24px;top:{HEADLINE_TOP}px;display:flex;align-items:center;gap:16px;background:{P};border-radius:999px;padding:16px 28px 16px 30px;box-shadow:0 6px 18px #6b2a4433">'
            f'<img src="{u(LOGO_W)}" style="height:22px" alt="BANILA CO"><span style="width:2px;height:28px;background:#fff9"></span>'
            f'<b style="color:#fff;font-weight:700;font-size:28px;letter-spacing:-.01em">{t("headline", line)}</b></div>')


def side(name, kicker, title, bullets=(), imgs='', big=''):
    li = ''.join(f'<li>{t(name, b, lv)}</li>' for b, lv in bullets)
    return overlay(f'<div class="abs sc"><div class="k">{t(name, kicker)}</div>{big}'
                   f'{f"<div class=imgs>{imgs}</div>" if imgs else ""}<div class="ttl">{t(name, title)}</div>'
                   f'{f"<ul>{li}</ul>" if li else ""}</div>')


STAR = '<svg class="star" style="{pos}" width="{s}" height="{s}" viewBox="0 0 40 40"><path d="M20 2 C21 15 25 19 38 20 C25 21 21 25 20 38 C19 25 15 21 2 20 C15 19 19 15 20 2Z" fill="{fill}" stroke="{st}" stroke-width="2.4" stroke-linejoin="round"/></svg>'
HEART = '<svg class="star" style="{pos}" width="54" height="54" viewBox="0 0 40 40"><path d="M20 34 C8 25 4 18 6 12 C8 6 16 6 20 13 C24 6 32 6 34 12 C36 18 32 25 20 34Z" fill="none" stroke="#F48FB6" stroke-width="3.2" stroke-linejoin="round"/></svg>'


def gscreen(name, kicker, title, body):
    """G 화면 공통 틀: 스프링(상단, Shopee UI 아래로 가려도 되는 장식) · 검정 로고(테두리 없음) · 반짝이 · 찢은 메모지 제목 + 테이프 · 본문(34~68% 안)."""
    deco = (STAR.format(pos='left:84px;top:236px', s=48, fill='#fff', st='#F48FB6') + HEART.format(pos='right:92px;top:226px')
            + STAR.format(pos='right:70px;top:560px', s=40, fill='#fff', st='#F48FB6') + STAR.format(pos='left:40px;top:604px', s=34, fill='#7FA6E8', st='#7FA6E8'))
    ttl = f'<div class="ttl"><span class="hl">{t(name, title)}</span></div>' if title else ''
    return (f'<div class="abs g"><div class="spiral">{"<i></i>" * 22}</div><div class="brand"><img src="{u(LOGO_B)}" alt="BANILA CO"></div>{deco}'
            f'<div class="zone"><div class="note"><div class="k">{t(name, kicker)}</div>{ttl}</div>'
            f'<div class="tape" style="right:-40px;top:-14px;transform:rotate(22deg)"></div>{body}</div></div>')


def promo_g(name, kicker, big, plus, prods):
    return gscreen(name, kicker, '', f'''<div style="text-align:center;margin-top:14px"><div class="big" style="font-size:168px"><span class="hl">{big}</span></div>
<div style="display:inline-block;margin-top:12px;background:#fff;padding:10px 34px 14px;transform:rotate(-1.5deg);box-shadow:0 4px 10px #6b2a4418;font-weight:800;font-size:52px;color:{P}">{t(name, plus)}</div></div>
<div class="panel pw" style="margin-top:24px;height:282px;padding:18px"><div class="pbox" style="height:100%;display:flex;align-items:flex-end;justify-content:center;gap:22px;padding-bottom:20px">{prods}</div></div>''')


def steps(name, items, img_h=150):
    cells = ''
    for i, (lab, key) in enumerate(items):
        if i: cells += f'<div style="font-weight:800;font-size:40px;color:{P};align-self:center">›</div>'
        cells += (f'<div class="panel{' pw' if key else ''}" style="flex:1;height:390px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding:18px 10px 22px;gap:14px">'
                  f'{im(key, int(img_h * 0.42) if key == "primer_powder" else img_h) if key else ""}<div class="num" style="transform:rotate({-3 if i % 2 else 3}deg)">{i + 1}</div>'
                  f'<div style="font-weight:700;font-size:25px;line-height:1.2;text-align:center">{t(name, lab)}</div></div>')
    return f'<div style="display:flex;gap:10px;margin-top:40px">{cells}</div>'


def steps_box(name, items, box):
    """2026-10-15 사용자: '제품이 네모 안에' — 왼쪽 정사각 패널(핑크 사진칸) 안에 실물 누끼, 오른쪽에 단계 4개 세로 목록."""
    rows = ''.join(f'<div class="panel" style="height:96px;display:flex;align-items:center;gap:20px;padding:0 20px">'
                   f'<div class="num" style="transform:rotate({-3 if i % 2 else 3}deg)">{i + 1}</div>'
                   f'<div style="font-weight:800;font-size:31px;line-height:1.15;color:#111">{t(name, lab)}</div></div>' for i, lab in enumerate(items))
    return (f'<div style="display:flex;gap:20px;margin-top:22px"><div class="panel pw" style="width:430px;height:432px;padding:18px;flex:none">'
            f'<div class="pbox" style="position:relative;height:100%">{box}</div></div>'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:16px">{rows}</div></div>')


def build():
    o, g = {}, {}
    # ---------------------------------------------------------------- 공통 크롬
    for v, line in (('COMMON', 'Live'), ('V1', 'Prime Primer'), ('V2', 'Romantic Blush Lip & Cheek'), ('V3', 'Clean it Zero')):
        o[f'overlay_headline_{v}'] = overlay(headline(line))
    o['overlay_disclosure'] = overlay(f'<div class="abs" style="right:24px;top:{BADGE_TOP}px;display:inline-flex;align-items:center;gap:10px;background:#fff;color:{P};border:2px solid {P};font-weight:600;font-size:24px;line-height:1;padding:9px 18px 9px 9px;border-radius:999px;letter-spacing:.2px"><i style="font-style:normal;font-weight:800;font-size:18px;line-height:1;padding:6px 9px;border-radius:999px;background:{P};color:#fff">AI</i>{t("disclosure", "AI-generated host")}</div>')
    # ---------------------------------------------------------------- 측면 카드 (H+G)
    o['card_EC-1'] = side('card_EC-1', 'Before you go', 'Your deal is waiting below', [('Tap the product card', 'cosmetic')])
    o['card_EC-2'] = side('card_EC-2', 'How to buy', 'Tap the product card ↓', [('Add to cart', 'cosmetic'), ('Check out in a few taps', 'cosmetic')])
    o['card_EC-3'] = side('card_EC-3', 'Questions?', 'Leave them in the chat', [('Thanks for watching!', 'cosmetic')])
    o['card_V1_O-P'] = side('card_V1_O-P', 'Prime Primer line', '4 steps for your base',
                            big=f'<div class="big" style="font-size:96px;margin-top:10px">50%<span style="font-size:52px"> OFF</span></div><div style="font-weight:800;font-size:30px;margin-top:6px">{t("card_V1_O-P", "+ Free Gift")}</div>',
                            imgs=im('primer_sunbase', 120) + im('primer_classic', 128) + im('primer_powder', 52) + im('primer_fixer', 134))
    o['card_V1_P3-1'] = side('card_V1_P3-1', 'Step 1 · Prep', 'Prime Primer Sun Base', [('Sun care + primer in one step', 'RA'), ('Light, no white cast', 'cosmetic')], im('primer_sunbase', 230))
    o['card_V1_P4-1'] = side('card_V1_P4-1', 'Step 2 · Prep', 'Prime Primer Classic', [('Cream primer', 'cosmetic'), ('Right before foundation', 'cosmetic')], im('primer_classic', 230))
    o['card_V1_P5-1'] = side('card_V1_P5-1', 'Step 3 · Finish', 'Prime Primer Finish Powder', [('Translucent loose powder', 'cosmetic'), ("Won't change your cushion shade", 'cosmetic')], im('primer_powder', 120))
    o['card_V1_P6-1'] = side('card_V1_P6-1', 'Step 4 · Set', 'Prime Primer Setting Fixer', [('Ultra-fine mist', 'cosmetic'), ('Helps keep makeup in place', 'RA')], im('primer_fixer', 240))
    o['card_V1_P7'] = side('card_V1_P7', 'Quick tips', 'By skin type', [('Oily: Classic on T-zone, then powder', 'cosmetic'), ('Dry: less powder, fixer on your puff', 'cosmetic'), ('Start with one, or build the routine', 'cosmetic')],
                           im('primer_classic', 150) + im('primer_powder', 60) + im('primer_fixer', 160))
    o['card_V2_O-L'] = side('card_V2_O-L', 'Romantic Blush Lip & Cheek', '12 shades to mix & match',
                            big=f'<div class="big" style="font-size:84px;margin-top:10px">BUY 2</div><div class="big" style="font-size:46px;margin-top:4px">GET 1 FREE</div>',
                            imgs=im('lc_05', 150) + im('lc_13', 150) + im('lc_18', 150))
    o['card_V2_L1'] = side('card_V2_L1', 'Why we love it · 1', 'One stick for lips + cheeks', [('Fewer things in your pouch', 'cosmetic'), ('A matching look in seconds', 'cosmetic')], im('lc_group_pink', 230))
    o['card_V2_L4-2'] = side('card_V2_L4-2', 'Why we love it · 4', 'Stick with a lock cap', [('No fingers, no tools', 'cosmetic'), ('Quick touch-ups on the go', 'cosmetic')], im('lc_13', 230))
    rows = ''.join(f'<div style="display:flex;align-items:center;gap:10px;margin-top:12px"><b style="width:110px;font-weight:800;font-size:25px">{t("card_V2_L7", lab)}</b>'
                   + ''.join(f'<div style="text-align:center">{sw("lip", n, 66, 46, 10)}<div style="font-weight:700;font-size:20px;margin-top:2px">{n}</div></div>' for n in ns) + '</div>'
                   for lab, ns in (('Office', ('07', '08')), ('Date', ('05', '13')), ('Weekend', ('17',))))
    o['card_V2_L7'] = overlay(f'<div class="abs sc"><div class="k">{t("card_V2_L7", "Shade picks")}</div><div class="ttl" style="margin-top:8px">{t("card_V2_L7", "For every moment")}</div>{rows}</div>')
    o['card_V3_O-B'] = side('card_V3_O-B', 'Clean it Zero cleansing balm', '3 balms, 3 skin types',
                            big=f'<div class="big" style="font-size:96px;margin-top:10px">50%<span style="font-size:52px"> OFF</span></div><div style="font-weight:800;font-size:30px;margin-top:6px">{t("card_V3_O-B", "+ Free Gift")}</div>',
                            imgs=im('balm_original', 82) + im('balm_pore', 82) + im('balm_calming', 82))
    o['card_V3_C3-1'] = side('card_V3_C3-1', 'Original', 'All-in-one cleansing balm', [('Sunscreen to waterproof makeup', 'cosmetic'), ('In one step', 'cosmetic')], im('balm_original', 170))
    o['card_V3_C3-2'] = side('card_V3_C3-2', 'Original', 'Acerola + jojoba seed oil', [('Soft, not tight after rinsing', 'cosmetic')], im('balm_original', 150))
    o['card_V3_C4-1'] = side('card_V3_C4-1', 'Pore Clarifying', 'Fresh, clean finish', [('For oily & combination skin', 'RA'), ('Green tea scent', 'cosmetic')], im('balm_pore', 170))
    o['card_V3_C5-1'] = side('card_V3_C5-1', 'Calming', 'Gentle, low-pH cleanser', [('For sensitive-feeling skin', 'RA'), ('Close to skin\'s natural pH', 'RA')], im('balm_calming', 170))
    # overlay_V3_C4-2(Tea tree·AHA·BHA·PHA·LHA 성분 칩) — 2026-10-15 사용자 요청으로 삭제
    # ---------------------------------------------------------------- 전체 화면 (G · G+H)
    g['g_V1_P2'] = gscreen('g_V1_P2', 'Prime Primer routine', 'Four steps, four jobs',
                           steps('g_V1_P2', [('Sun Base', 'primer_sunbase'), ('Classic', 'primer_classic'), ('Finish Powder', 'primer_powder'), ('Setting Fixer', 'primer_fixer')], 170)
                           + f'<div style="text-align:center;margin-top:18px;font-weight:600;font-size:26px;color:#8C6B78">{t("g_V1_P2", "Your cushion goes on after Classic")}</div>')
    g['g_V1_P4-4'] = gscreen('g_V1_P4-4', 'Prime Primer Classic · how to', 'Pea-size, press, wait',
                             steps_box('g_V1_P4-4', ['Pea-size', 'Press in', 'Wait a moment', 'Then your base'],
                                       f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">{im("primer_classic", 350)}</div>'))
    g['g_V1_P6-4'] = gscreen('g_V1_P6-4', 'Prime Primer Setting Fixer', 'Double cap — easy to carry',
                             f'<div class="panel pw" style="margin-top:36px;height:430px;display:flex;align-items:center;justify-content:center">{im("primer_fixer", 380)}</div>')
    g['g_V1_P8'] = promo_g('g_V1_P8', 'Prime Primer line', '50<span style="font-size:110px">%</span> OFF', '+ Free Gift',
                           im('primer_sunbase', 161) + im('primer_classic', 172) + im('primer_powder', 70) + im('primer_fixer', 179))  # 2026-10-15 사용자: 기존(230·245·100·255)의 70%
    g['g_V2_L0'] = gscreen('g_V2_L0', "Today's look", 'Lips + cheeks, one shade: 05',
                           f'<div style="display:flex;gap:18px;margin-top:34px;align-items:stretch">{sw("lip", "05", 360, 400, 26, True)}{sw("cheek", "05", 360, 400, 26, True)}'
                           f'<div class="panel pw" style="flex:1;display:flex;align-items:center;justify-content:center">{im("lc_05", 264)}</div></div>')
    for n, (mood, tone) in SHADES.items():
        cut = (CUT / f'lc_{n}.png').exists()
        right = f'<div class="panel pw" style="width:230px;display:flex;align-items:center;justify-content:center">{im(f"lc_{n}", 256)}</div>' if cut else ''
        wsw = 385 if cut else 485
        g[f'g_V2_L5_{n}'] = gscreen(f'g_V2_L5_{n}', f'{mood}' + (f' · {tone}' if tone else ''), f'Shade {n}',
                                    f'<div style="display:flex;gap:16px;margin-top:30px">'
                                    f'<div style="position:relative">{sw("lip", n, wsw, 420, 26)}<b style="position:absolute;left:18px;bottom:14px;color:#fff;font-size:24px;letter-spacing:.14em;text-shadow:0 1px 4px #0007">LIP</b></div>'
                                    f'<div style="position:relative">{sw("cheek", n, wsw, 420, 26)}<b style="position:absolute;left:18px;bottom:14px;color:#fff;font-size:24px;letter-spacing:.14em;text-shadow:0 1px 4px #0007">CHEEK</b></div>{right}</div>'
                                    f'<div style="margin-top:14px;font-weight:600;font-size:22px;color:#8C6B78">{t(f"g_V2_L5_{n}", "Actual color may vary by skin tone and screen.")}</div>')
    cols = ''.join(f'<div class="panel" style="flex:1;padding:24px 18px;text-align:center"><div style="font-weight:800;font-size:34px;color:{P}">{t("g_V2_L6", lab)}</div>'
                   + ''.join(f'<div style="display:flex;align-items:center;gap:12px;margin-top:16px;justify-content:center">{sw("lip", n, 150, 96, 14, True)}<b style="font-weight:900;font-size:40px;width:56px">{n}</b></div>' for n in ns) + '</div>'
                   for lab, ns in (('Cool', ('02', '05', '09')), ('Warm', ('12', '17', '18')), ('Both', ('04', '08', '13'))))
    g['g_V2_L6'] = gscreen('g_V2_L6', 'Find your trio', 'Pick 3 by your tone', f'<div style="display:flex;gap:16px;margin-top:34px">{cols}</div>')
    g['g_V2_L8'] = gscreen('g_V2_L8', 'Romantic Blush Lip & Cheek', '',
                           f'<div style="text-align:center;margin-top:10px"><div class="big" style="font-size:136px"><span class="hl">BUY 2</span></div><div class="big" style="font-size:76px;margin-top:6px;color:{P}">GET 1 FREE</div></div>'
                           + '<div style="display:flex;gap:16px;margin-top:30px">' + ''.join(
                               f'<div class="panel pw" style="flex:1;height:262px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:16px;gap:8px">{im(k, 180)}<b style="font-weight:800;font-size:28px">{t("g_V2_L8", lab)}</b></div>'
                               for k, lab in (('lc_05', 'Lips'), ('lc_13', 'Cheeks'), ('lc_18', 'Backup'))) + '</div>')
    g['g_V3_C5-2'] = gscreen('g_V3_C5-2', 'Clean it Zero Calming', 'Cica blend + calming aroma',
                             f'<div style="display:flex;gap:20px;margin-top:34px"><div class="panel pw" style="width:400px;height:420px;display:flex;align-items:center;justify-content:center">{im("balm_calming", 260)}</div>'
                             f'<div style="flex:1;display:flex;flex-direction:column;gap:14px">' + ''.join(
                                 f'<div class="panel" style="padding:20px 24px;font-weight:700;font-size:30px">{t("g_V3_C5-2", x, "RA")}</div>' for x in ('Cica blend', 'Eucalyptus', 'Bergamot', 'Chamomile')) + '</div></div>')
    g['g_V3_C6'] = gscreen('g_V3_C6', 'Clean it Zero cleansing balm', 'Which balm is for me?',
                           '<div style="display:flex;gap:16px;margin-top:34px">' + ''.join(
                               f'<div class="panel" style="flex:1;height:420px;padding:22px 14px;text-align:center;background:{bg}"><div style="height:170px;display:flex;align-items:center;justify-content:center">{im(k, 140)}</div>'
                               f'<div style="font-weight:800;font-size:32px;margin-top:12px">{t("g_V3_C6", nm)}</div><div style="font-weight:600;font-size:25px;line-height:1.3;margin-top:10px">{t("g_V3_C6", who, lv)}</div></div>'
                               for k, nm, who, bg, lv in (('balm_original', 'Original', 'Lots of makeup · all-rounder', '#FCE3EF', 'cosmetic'),
                                                          ('balm_pore', 'Pore Clarifying', 'Oily or combination skin', '#E3F2DC', 'RA'),
                                                          ('balm_calming', 'Calming', 'Sensitive-feeling skin', '#DFE8FA', 'RA'))) + '</div>')
    # 밤 3종을 레퍼런스처럼 위 1 · 아래 2로 쌓아 사진칸 안에 (누끼 비율 그대로, 높이만 지정)
    g['g_V3_C7'] = gscreen('g_V3_C7', 'Clean it Zero · how to', 'Dry hands, dry face',
                           steps_box('g_V3_C7', ['Dry hands, dry face', 'Massage', 'Add a little water', 'Rinse with lukewarm water'],
                                     f'<div style="position:absolute;left:0;right:0;top:44px;display:flex;justify-content:center">{im("balm_original", 140)}</div>'
                                     f'<div style="position:absolute;left:0;right:0;bottom:50px;display:flex;justify-content:center;gap:8px">{im("balm_pore", 140)}{im("balm_calming", 140)}</div>'))
    g['g_V3_C8'] = gscreen('g_V3_C8', 'Clean it Zero cleansing balm', 'Pick the size that suits you',
                           f'<div style="display:flex;gap:16px;margin-top:34px">' + ''.join(
                               f'<div class="panel" style="flex:1;height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px"><div style="font-weight:800;font-size:40px;color:{P}">{t("g_V3_C8", a)}</div><div style="font-weight:700;font-size:30px">{t("g_V3_C8", b)}</div></div>'
                               for a, b in (('Small', 'for travel'), ('Big', 'for every day'))) + '</div>'
                           f'<div style="margin-top:20px;font-weight:600;font-size:24px;color:#8C6B78;text-align:center">{t("g_V3_C8", "Available sizes may vary by store.")}</div>')
    g['g_V3_C9'] = promo_g('g_V3_C9', 'Clean it Zero cleansing balm · 3 types', '50<span style="font-size:110px">%</span> OFF', '+ Free Gift',
                           im('balm_original', 170) + im('balm_pore', 170) + im('balm_calming', 170))
    return o, g


def render(pages, transparent):
    OUT.mkdir(parents=True, exist_ok=True); rep = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})
        for name, body in pages.items():
            bgcss = 'html,body{background:transparent}' if transparent else ''
            doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}{CSS}{bgcss}</style></head><body>{body}</body></html>'
            src = OUT / '_html' / f'{name}.html'; src.parent.mkdir(exist_ok=True); src.write_text(doc, encoding='utf-8')
            pg.goto(src.as_uri()); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
            rep[name] = pg.evaluate('''() => {const r={broken:[],overflow:[],fonts:[...new Set([...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family))]};
              for (const i of document.images) if(!i.complete||!i.naturalWidth) r.broken.push(i.alt);
              for (const e of document.querySelectorAll('body *')){const b=e.getBoundingClientRect(); if(b.width&&(b.right>innerWidth+1||b.left<-1)) r.overflow.push(e.className||e.tagName);
                if(e.children.length===0&&e.scrollWidth>e.clientWidth+2) r.overflow.push('text:'+e.textContent.slice(0,30));}
              return r}''')
            pg.screenshot(path=str(OUT / f'{name}.png'), omit_background=transparent)
        b.close()
    return rep


FONTS = ''.join(f"@font-face{{font-family:Pretendard;font-weight:{w};src:url('{u(A / 'banner' / 'fonts' / f'Pretendard-{n}.otf')}')}}"
                for w, n in ((500, 'Medium'), (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')))

if __name__ == '__main__':
    o, g = build()
    rep = {**render(o, True), **render(g, False)}
    with open(OUT / 'edit_gfx_copy.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh); w.writerow(['graphic', 'text', 'claim_level (cosmetic / RA=RA·법무 사전검토)']); w.writerows(COPY)
    json.dump(rep, open(OUT / 'render_check.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bad = {k: v for k, v in rep.items() if v['broken'] or v['overflow'] or 'Pretendard' not in v['fonts']}
    print('rendered', len(rep), 'issues', json.dumps(bad, ensure_ascii=False)[:2000])
