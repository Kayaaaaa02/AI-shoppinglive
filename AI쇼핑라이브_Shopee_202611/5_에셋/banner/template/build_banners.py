"""Shopee AI 쇼호스트 (v2 2026-10-15: 폰트 Pretendard, 상단 정식 로고. v1 Poppins판은 4_테스트/banner_v1_poppins/)
 — 1080x1920 배너·화면 레이아웃 1차 렌더 (HTML/CSS → Playwright PNG).

python -X utf8 build_banners.py            # 배너 8종 + 레이아웃 3종
제품은 그리지 않는다: src_cutouts/ 의 공식 누끼(알파 bbox 크롭, 비율 유지 축소)만 <img object-fit:contain> 으로 배치.
립·치크 발색은 src_swatch/ 의 공식 발색컷 크롭.
"""
import csv
import html
import json
import pathlib

from playwright.sync_api import sync_playwright

T = pathlib.Path(__file__).resolve().parent          # 5_에셋/banner/template
BN = T.parent                                          # 5_에셋/banner
A = BN.parent                                          # 5_에셋
CUT = BN / 'src_cutouts'
SW = BN / 'src_swatch'
FONTS = BN / 'fonts'
OUT_B = BN / 'common'
OUT_L = A / 'layout'
LOGO = A / 'logo' / 'BANILACO_logo_white.png'   # 정식 로고(공식 영상 엔드카드 추출) — 폰트로 재조판하지 않음
W, H = 1080, 1920


def u(p):
    return pathlib.Path(p).resolve().as_uri()


def img(key, cls='', style=''):
    return f'<img class="{cls}" style="{style}" src="{u(CUT / (key + ".png"))}" alt="{key}">'


BASE_CSS = f'''
@font-face{{font-family:Pretendard;font-weight:500;src:url("{u(FONTS/'Pretendard-Medium.otf')}")}}
@font-face{{font-family:Pretendard;font-weight:600;src:url("{u(FONTS/'Pretendard-SemiBold.otf')}")}}
@font-face{{font-family:Pretendard;font-weight:700;src:url("{u(FONTS/'Pretendard-Bold.otf')}")}}
@font-face{{font-family:Pretendard;font-weight:800;src:url("{u(FONTS/'Pretendard-ExtraBold.otf')}")}}
@font-face{{font-family:Pretendard;font-weight:900;src:url("{u(FONTS/'Pretendard-Black.otf')}")}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:Pretendard,sans-serif;color:#2B1F25;background:#F8EDF1;position:relative}}
.abs{{position:absolute}}
img{{display:block;object-fit:contain}}
.kicker{{font-weight:600;font-size:34px;letter-spacing:.18em;text-transform:uppercase;color:#B5476F}}
.serif{{font-family:Pretendard}}
.pill{{display:inline-block;border-radius:999px;padding:10px 28px;font-weight:700}}
.brand{{position:absolute;top:150px;left:50%;transform:translateX(-50%);background:#E9579A;border-radius:999px;padding:20px 46px}}.brand img{{height:30px;width:auto}}
.foot{{position:absolute;left:0;right:0;bottom:400px;text-align:center;font-weight:500;font-size:28px;color:#8C6B78}}
'''

# ---------------------------------------------------------------- banners
COPY = []   # (file, element, text, claim_level)


def c(file, el, text, level='cosmetic'):
    COPY.append((file, el, text, level))
    return html.escape(text)


def promo(file, *, eyebrow, big, plus, products, line, accent, tint, gift=True, note='While stocks last.'):
    prods = ''.join(f'<div class="p" style="height:{h}px">{img(k)}</div>' for k, h in products)
    gift_tile = (f'<div class="gift"><svg viewBox="0 0 64 64" width="96" height="96"><rect x="8" y="26" width="48" height="32" rx="4" fill="none" stroke="{accent}" stroke-width="4"/>'
                 f'<rect x="4" y="16" width="56" height="12" rx="3" fill="none" stroke="{accent}" stroke-width="4"/><path d="M32 16v42" stroke="{accent}" stroke-width="4"/>'
                 f'<path d="M32 16c-6-10-18-10-16-2 1 4 10 3 16 2zM32 16c6-10 18-10 16-2-1 4-10 3-16 2z" fill="none" stroke="{accent}" stroke-width="4"/></svg>'
                 f'<b>{c(file, "gift tile", "FREE GIFT")}</b><span>{c(file, "gift sub", "with purchase")}</span></div>') if gift else ''
    return f'''<style>
.top{{top:300px;left:0;right:0;text-align:center}}
.big{{font-weight:800;font-size:250px;line-height:.9;letter-spacing:-.04em;color:{accent}}}
.big small{{font-size:120px;letter-spacing:-.02em}}.big br+small{{display:block;margin-top:18px}}
.plus{{margin-top:22px;font-family:Pretendard;font-style:normal;font-weight:800;letter-spacing:-.02em;font-size:78px;color:#2B1F25}}
.stage{{left:60px;right:60px;top:860px;height:520px;border-radius:44px;background:{tint};display:flex;align-items:flex-end;justify-content:center;gap:18px;padding:0 30px 56px}}
.p img{{height:100%;width:auto}}
.gift{{flex:none;width:180px;height:240px;border-radius:28px;border:4px dashed {accent};background:#fff8;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;align-self:flex-end}}
.gift b{{font-size:31px;color:{accent}}}.gift span{{font-size:21px;color:#7a5a67}}
.line{{top:1410px;left:60px;right:60px;text-align:center;font-weight:600;font-size:40px;line-height:1.35}}
</style>
<div class="abs top"><div class="kicker">{c(file, "eyebrow", eyebrow)}</div>
<div class="big" style="margin-top:26px">{big}</div><div class="plus">{c(file, "plus", plus)}</div></div>
<div class="abs stage">{prods}{gift_tile}</div>
<div class="abs line">{c(file, "line", line)}</div>
<div class="foot">{c(file, "footnote", note)}</div>'''


def info(file, *, eyebrow, title, cards, accent, note='', extra=''):
    cs = ''.join(f'''<div class="card" style="background:{bg}"><div class="ci">{img(k)}</div><div class="ct">
<div class="tag" style="color:{accent}">{c(file, "card label", tag)}</div>
<ul>{''.join(f"<li>{c(file, 'card point', p, lv)}</li>" for p, lv in pts)}</ul></div></div>''' for k, bg, tag, pts in cards)
    n = len(cards)
    ch = {3: 300, 4: 232}[n]
    return f'''<style>
.head{{top:250px;left:70px;right:70px}}
.title{{margin-top:14px;font-family:Pretendard;font-style:normal;font-weight:800;letter-spacing:-.02em;font-size:84px;line-height:1.02}}
.cards{{top:{560 if n == 3 else 520}px;left:60px;right:60px;display:flex;flex-direction:column;gap:22px}}
.card{{height:{ch}px;border-radius:34px;display:flex;align-items:center;gap:30px;padding:20px 34px}}
.ci{{width:{220 if n == 3 else 170}px;height:{ch - 40}px;flex:none;display:flex;align-items:center;justify-content:center}}
.ci img{{max-width:100%;max-height:100%}}
.tag{{font-weight:800;font-size:{40 if n == 3 else 36}px;letter-spacing:.02em;text-transform:uppercase}}
.ct ul{{list-style:none;margin-top:8px}}.ct li{{font-weight:500;font-size:{33 if n == 3 else 30}px;line-height:1.32}}
.ct li:before{{content:"·";margin-right:10px;color:{accent};font-weight:800}}
</style>
<div class="abs head"><div class="kicker">{c(file, "eyebrow", eyebrow)}</div><div class="title">{c(file, "title", title)}</div></div>
<div class="abs cards">{cs}</div>{extra}
<div class="foot" style="bottom:330px">{c(file, "footnote", note) if note else ''}</div>'''


SHADES = {  # Product Spec v10 무드·추천 톤 (14·20은 문서에 추천 정보 없음)
    '02': ('Milky', 'Cool'), '04': ('Milky', 'Warm & Cool'), '05': ('Milky', 'Cool'),
    '07': ('Muted', 'Warm & Cool'), '08': ('Muted', 'Warm & Cool'), '09': ('Muted', 'Cool'),
    '12': ('Mellow', 'Warm'), '13': ('Mellow', 'Warm & Cool'), '14': ('Mellow', ''),
    '17': ('Moody', 'Warm'), '18': ('Moody', 'Warm'), '20': ('Moody', ''),
}


def shade_banner(file, shades, part):
    rows = ''
    for n in shades:
        mood, tone = SHADES[n]
        rows += f'''<div class="row"><div class="no"><b>{c(file, "shade no", n)}</b><span>{c(file, "mood", mood)}</span>{f'<i>{c(file, "tone", tone)}</i>' if tone else ''}</div>
<div class="sw"><img src="{u(SW / f'lip_{n}.jpg')}"><em>LIP</em></div><div class="sw"><img src="{u(SW / f'cheek_{n}.jpg')}"><em>CHEEK</em></div></div>'''
    return f'''<style>
.head{{top:250px;left:70px;right:70px}}
.title{{margin-top:10px;font-family:Pretendard;font-style:normal;font-weight:800;letter-spacing:-.02em;font-size:76px;line-height:1.02}}
.rows{{top:470px;left:50px;right:50px;display:flex;flex-direction:column;gap:14px}}
.row{{height:162px;display:flex;gap:14px;align-items:stretch}}
.no{{width:190px;flex:none;border-radius:22px;background:#fff;display:flex;flex-direction:column;justify-content:center;padding-left:26px}}
.no b{{font-weight:800;font-size:64px;line-height:1;color:#2B1F25}}.no span{{font-weight:600;font-size:26px;color:#B5476F}}
.no i{{font-style:normal;font-weight:500;font-size:20px;color:#8C6B78}}
.sw{{flex:1;position:relative;border-radius:22px;overflow:hidden}}.sw img{{width:100%;height:100%;object-fit:cover}}
.sw em{{position:absolute;right:14px;bottom:10px;font-style:normal;font-weight:700;font-size:20px;letter-spacing:.14em;color:#fff;text-shadow:0 1px 4px #0006}}
</style>
<div class="abs head"><div class="kicker">{c(file, "eyebrow", f"12 shades · {part}")}</div>
<div class="title">{c(file, "title", "One stick for lips & cheeks")}</div></div>
<div class="abs rows">{rows}</div>
<div class="foot" style="bottom:330px">{c(file, "footnote", "Actual color may vary by skin tone and screen.")}</div>'''


def banners():
    P = '#E9579A'
    out = {}
    f = 'BNR_V1_PrimePrimer_promo'
    out[f] = promo(f, eyebrow='Prime Primer line', big='50<small>%</small> OFF', plus='+ Free Gift',
                   products=[('primer_classic', 330), ('primer_powder', 140), ('primer_fixer', 350), ('primer_sunbase', 310)],
                   line='Prep · Finish · Set — your base, all in one line', accent=P, tint='#FFFFFF')
    f = 'BNR_V1_PrimePrimer_info'
    out[f] = info(f, eyebrow='Prime Primer line', title='Before makeup, after makeup', accent=P, cards=[
        ('primer_classic', '#FFFFFF', 'Primer · Prep', [('Pea-size amount is enough', 'cosmetic'), ('Smooths the look of skin texture', 'cosmetic'), ('Foundation glides on evenly', 'cosmetic')]),
        ('primer_powder', '#FFFFFF', 'Finish Powder · Finish', [('Translucent loose powder', 'cosmetic'), ('Soft-matte, shine-free look', 'cosmetic'), ('Pores look softly blurred', 'RA')]),
        ('primer_fixer', '#FFFFFF', 'Setting Fixer · Set', [('Ultra-fine, even mist', 'cosmetic'), ('Semi-matte finish', 'cosmetic'), ('Helps makeup stay in place', 'RA')]),
        ('primer_sunbase', '#FFFFFF', 'Sun Base · Prep', [('Primer and sun care in one step', 'RA'), ('Lightweight, no white cast', 'cosmetic'), ('Cool feel on the skin', 'cosmetic')]),
    ], note='Individual results may vary.')
    f = 'BNR_V2_LipCheek_promo'
    out[f] = promo(f, eyebrow='Romantic Blush Lip & Cheek', big='BUY 2<br><small>GET 1 FREE</small>', plus='12 shades to mix & match',
                   products=[('lc_05', 380), ('lc_13', 380)], line='Lips and cheeks, one stick — build your trio',
                   accent=P, tint='#FFFFFF', gift=False).replace(
        '</div>\n<div class="abs line">',
        f'<div class="free"><div class="fi">{img("lc_18")}</div><b>+1 FREE</b></div></div>\n<div class="abs line">', 1) + \
        f'<style>.free{{width:250px;height:440px;border-radius:30px;border:4px dashed {P};display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:16px;gap:8px}}.free .fi{{height:330px}}.free .fi img{{height:100%;width:auto;opacity:.92}}.free b{{font-weight:800;font-size:40px;color:{P}}}</style>'
    COPY.append((f, 'free tile', '+1 FREE', 'cosmetic'))
    f = 'BNR_V2_LipCheek_info'
    out[f] = info(f, eyebrow='Romantic Blush Lip & Cheek', title='A soft touch of color', accent=P, cards=[
        ('lc_group_pink', '#FFFFFF', 'Lips + cheeks', [('One stick for both', 'cosmetic'), ('Match your lip and cheek tone', 'cosmetic')]),
        ('lc_08', '#FFFFFF', 'Buildable cream', [('Melts with body warmth', 'cosmetic'), ('Sheer with one layer,', 'cosmetic'), ('deeper with two', 'cosmetic')]),
        ('lc_13', '#FFFFFF', 'How to', [('Warm on the back of your hand', 'cosmetic'), ('Tap on with a puff', 'cosmetic'), ('Lips: lip balm first, then tap', 'cosmetic')]),
    ])
    out['BNR_V2_LipCheek_shades_1'] = shade_banner('BNR_V2_LipCheek_shades_1', ['02', '04', '05', '07', '08', '09'], 'Milky & Muted')
    out['BNR_V2_LipCheek_shades_2'] = shade_banner('BNR_V2_LipCheek_shades_2', ['12', '13', '14', '17', '18', '20'], 'Mellow & Moody')
    f = 'BNR_V3_CleanItZero_promo'
    out[f] = promo(f, eyebrow='Clean it Zero cleansing balm · 3 types', big='50<small>%</small> OFF', plus='+ Free Gift',
                   products=[('balm_original', 230), ('balm_pore', 230), ('balm_calming', 230)],
                   line='Sherbet balm → silky oil → milky rinse', accent=P, tint='#FFFFFF', gift=False) +         f'<div class="abs sticker"><b>FREE</b><span>GIFT</span></div><style>.sticker{{top:800px;right:70px;width:190px;height:190px;border-radius:50%;background:{P};color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-8deg);box-shadow:0 8px 24px #e9579a55}}.sticker b{{font-weight:800;font-size:48px;line-height:1}}.sticker span{{font-weight:700;font-size:34px;letter-spacing:.12em}}</style>'
    COPY.append((f, 'sticker', 'FREE GIFT', 'cosmetic'))
    f = 'BNR_V3_CleanItZero_info'
    out[f] = info(f, eyebrow='Clean it Zero cleansing balm', title='Pick your balm', accent=P, cards=[
        ('balm_original', '#FCE3EF', 'Original', [('All-in-one deep cleansing', 'cosmetic'), ('Melts away waterproof makeup', 'cosmetic'), ('and sunscreen', 'cosmetic')]),
        ('balm_pore', '#E3F2DC', 'Pore Clarifying', [('Fresh, clean finish', 'cosmetic'), ('Made for oily skin', 'RA'), ('Fresh green tea scent', 'cosmetic')]),
        ('balm_calming', '#DFE8FA', 'Calming', [('Gentle cleanse', 'cosmetic'), ('For sensitive-feeling skin', 'RA'), ('Calming aroma essential oils', 'RA')]),
    ], note='Sherbet texture · melts into oil · rinses off milky')
    return out


# ---------------------------------------------------------------- layouts (§4 zones)
def zone(top, bottom, color, label, left=0, right=0, extra=''):
    t, b = top / 100 * H, bottom / 100 * H
    return (f'<div class="z" style="top:{t:.0f}px;height:{b - t:.0f}px;left:{left}px;right:{right}px;'
            f'background:{color};{extra}"><span>{label} · {top:g}–{bottom:g}%</span></div>')


HOST = '''<svg class="abs host" viewBox="0 0 400 520" style="left:340px;top:700px;width:400px;height:720px">
<circle cx="200" cy="140" r="96" fill="#d9c2cb"/><path d="M40 520c0-150 70-240 160-240s160 90 160 240z" fill="#d9c2cb"/></svg>'''


def layout(name, title, table_items, demo_label, card_label, chips=''):
    items = ''.join(f'<div style="height:{h}px">{img(k)}</div>' for k, h in table_items)
    return f'''<style>
body{{background:linear-gradient(#F9DCE8,#F3C6DA)}}
.z{{position:absolute;border:3px dashed #0007;display:flex;align-items:flex-start;justify-content:flex-start}}
.z span{{background:#000a;color:#fff;font-weight:600;font-size:24px;padding:4px 12px;border-radius:0 0 10px 0}}
.host{{opacity:.95}}
.table{{left:0;right:0;top:{0.74 * H:.0f}px;height:{0.26 * H:.0f}px;background:#fff6f9}}
.shelf{{left:60px;right:60px;top:{0.68 * H:.0f}px;height:{0.06 * H:.0f}px;display:flex;align-items:flex-end;justify-content:center;gap:24px}}
.shelf div img{{height:100%;width:auto}}
.ttl{{left:40px;top:{0.415 * H:.0f}px;font-weight:800;font-size:30px;color:#2B1F25;background:#fffc;padding:6px 14px;border-radius:10px}}
.legend{{left:30px;right:30px;bottom:30px;font-size:22px;color:#fff;background:#000b;padding:14px 18px;border-radius:12px;line-height:1.45}}
</style>
<div class="abs table"></div>{HOST}
<div class="abs shelf">{items}</div>
{zone(0, 33, '#4a4a4a55', 'Shopee top UI (overlay)')}
{zone(24, 38, '#ffffff66', 'Shopee product card', right=560)}
{zone(34, 40, '#E9579A55', 'L4 headline', left=520)}
{zone(40, 76, '#2878E833', 'L4 graphic card · ' + card_label, left=700, right=24)}
{zone(50, 68, '#1f8a5b44', 'L3 demo window · ' + demo_label, left=24, right=640)}
{zone(68, 78, '#ffb74d44', 'L2 real cutouts (composite)', left=40, right=40)}
{zone(70, 76, '#ffffff00', 'Captions ≤2 lines', left=120, right=120, extra='border-color:#c0392b;')}
{zone(76, 78, '#c0392b55', 'L6 disclosure: AI-generated host')}
{zone(78, 100, '#4a4a4a77', 'Shopee chat / input (overlay)')}
{chips}
<div class="abs ttl">{title}</div>
<div class="abs legend">1st-pass layout (not final). Host = placeholder silhouette (generated later). Products = official cutouts, ratio kept. % = height of 1920px frame, from plan §4.</div>'''


def layouts():
    chips = ''.join(f'<div class="abs" style="left:{724 + (i % 3) * 108}px;top:{int(0.455 * H) + (i // 3) * 74}px;width:96px;height:64px;border-radius:12px;overflow:hidden;border:2px solid #fff"><img src="{u(SW / f"lip_{n}.jpg")}" style="width:100%;height:100%;object-fit:cover"></div>'
                    for i, n in enumerate(['02', '04', '05', '07', '08', '09', '12', '13', '14', '17', '18', '20']))
    return {
        'V1_layout': layout('V1', 'V1 · Prime Primer', [('primer_classic', 110), ('primer_powder', 52), ('primer_fixer', 115), ('primer_sunbase', 105)],
                            'fingerprint / powder before-after', 'benefit · routine'),
        'V2_layout': layout('V2', 'V2 · Romantic Blush Lip & Cheek', [('lc_02', 100), ('lc_05', 100), ('lc_13', 100), ('lc_18', 100)],
                            'hand warm-up → puff tap', 'B2G1 · shade chips', chips),
        'V3_layout': layout('V3', 'V3 · Clean it Zero balm', [('balm_original', 88), ('balm_pore', 88), ('balm_calming', 88)],
                            'spatula → oil → milky rinse', 'pick-your-balm card'),
    }


def render(pages, outdir, brand=False):
    outdir.mkdir(parents=True, exist_ok=True)
    report = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H})
        for name, body in pages.items():
            brand_html = f'<div class="brand"><img src="{u(LOGO)}" alt="BANILA CO"></div>' if brand else ''
            doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head><body>{body}{brand_html}</body></html>'
            src = (T / f'{name}.html')
            src.write_text(doc, encoding='utf-8')
            pg.goto(src.as_uri()); pg.wait_for_load_state('networkidle')
            pg.evaluate('document.fonts.ready')
            chk = pg.evaluate('''() => {
              const r = {overflow: [], broken: [], fonts: [...new Set([...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight))]};
              for (const e of document.querySelectorAll('body *')) {
                const b = e.getBoundingClientRect(); if (!b.width) continue;
                if (b.right > innerWidth + 1 || b.bottom > innerHeight + 1 || b.left < -1) r.overflow.push(e.className || e.tagName);
                if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'hidden' && e.tagName !== 'svg' && e.children.length === 0) r.overflow.push('text:' + (e.textContent || '').slice(0, 30));
              }
              for (const i of document.images) {
                if (!i.complete || !i.naturalWidth) { r.broken.push(i.src.slice(-40)); continue; }
                const b = i.getBoundingClientRect();
                r[i.alt || i.src.split('/').pop()] = [Math.round(b.width), Math.round(b.height), +(i.naturalWidth / i.naturalHeight).toFixed(4), +(b.width / b.height).toFixed(4)];
              }
              return r; }''')
            pg.screenshot(path=str(outdir / f'{name}.png'))
            report[name] = chk
        b.close()
    return report


if __name__ == '__main__':
    rb = render(banners(), OUT_B, brand=True)
    rl = render(layouts(), OUT_L)
    with open(OUT_B / 'banner_copy.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh); w.writerow(['banner', 'element', 'text', 'claim_level (cosmetic / RA=RA·법무 사전검토)'])
        w.writerows(COPY)
    json.dump({'banners': rb, 'layouts': rl}, open(BN / 'template' / 'render_check.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in {**rb, **rl}.items():
        print(k, 'overflow=', v['overflow'][:6], 'broken=', v['broken'])
