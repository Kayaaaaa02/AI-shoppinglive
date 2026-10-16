# -*- coding: utf-8 -*-
"""자막 디자인 시안 A~E + 'AI-generated host' 배지 시안 1~3 (우측 상단 배치 목업).

- 바탕 프레임은 최종 편집과 같은 재료로 자막 없이 다시 합성: 플레이트 + 호스트(340px 아래) + 헤드라인 (+ 측면 카드) / G 카드.
- 시안 PNG(투명 1080x1920)는 HTML/CSS → Playwright, 폰트는 Pretendard(로컬 OTF).
출력: 4_테스트/caption_proposal/ (목업) · 5_에셋/edit_gfx/badge/ (배지 단독 PNG)
python -X utf8 5_에셋/scripts/build_caption_proposals.py
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import html
import json
import subprocess
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
FF = cfg.FFMPEG
GFX = ROOT / '5_에셋/edit_gfx'
FONTS = ROOT / '5_에셋/banner/fonts'
SEG = ROOT / '4_테스트/edit_seg'
OUT = ROOT / '4_테스트/caption_proposal'
BADGE = GFX / 'badge'
OUT.mkdir(parents=True, exist_ok=True)
BADGE.mkdir(parents=True, exist_ok=True)
W, H, SHIFT = 1080, 1920, 340
CAP_BOTTOM = 1458   # 현행 자막 상자 아래 끝(약 76%) — 모든 시안 같은 위치로 비교
PINK, INK = '#E9579A', '#2B1F25'


def host_frame(sid, t):
    cut = next((ROOT / '4_테스트/h3_qa' / sid).glob('*_cut.mp4'), None)
    src = cut or ROOT / '3_소스클립/H3' / sid / 'native.mp4'
    p = OUT / f'_host_{sid}.png'
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-ss', str(t), '-i', str(src), '-frames:v', '1',
                    '-vf', f'scale={W}:{H}', str(p)], check=True)
    return Image.open(p).convert('RGBA')


def base_host(sid, t, overlays):
    plate = Image.open(SEG / '_plate.png').convert('RGBA')
    mask = Image.open(SEG / '_hostmask.png').convert('L')
    h = host_frame(sid, t)
    h.putalpha(mask)
    im = plate.copy()
    im.alpha_composite(h, (0, SHIFT))
    for o in overlays:
        im.alpha_composite(Image.open(GFX / f'{o}.png').convert('RGBA'))
    return im.crop((0, 0, W, H))


BASES = {
    'H': (base_host('V1_P1_1', 3.0, ['overlay_headline_V1']), "Be honest — does your base slide off by lunch?"),
    'H+G': (base_host('V1_P3-1_2', 2.0, ['overlay_headline_V1', 'card_V1_P3-1']),
            "It is sun care and primer in one step — so on busy mornings, you can skip one layer."),
    'G': (Image.open(GFX / 'g_V2_L6.png').convert('RGBA'), "Cool tones, try 02, 05 and 09."),
}
for k, (im, _) in BASES.items():
    im.convert('RGB').save(OUT / f'base_{k.replace("+", "")}.png')

FONT_CSS = ''.join(f"@font-face{{font-family:P;font-weight:{w};src:url('{(FONTS / f'Pretendard-{n}.otf').as_uri()}')}}"
                   for n, w in (('Medium', 500), ('SemiBold', 600), ('Bold', 700), ('ExtraBold', 800), ('Black', 900)))
KEY = {'sun care', 'primer', 'one step', '02,', '05', '09.'}


def hl(text):
    out = []
    for w in text.split(' '):
        out.append(f'<span class="k">{html.escape(w)}</span>' if w.lower() in KEY or w.lower().rstrip(',') in KEY else html.escape(w))
    s = ' '.join(out)
    for ph in ('sun care', 'one step'):
        a, b = ph.split()
        s = s.replace(f'{a} {b}', f'<span class="k">{ph}</span>')
    return s


# (코드, 이름, 설명, CSS, 하이라이트 사용)
STYLES = [
    ('A', '현행 — 반투명 다크 박스', 'Pretendard Bold 42 · 흰 글자 · 검정 60% 상자 · 모서리 18',
     '.c{font:700 42px/58px P;color:#fff;background:rgba(20,12,16,.59);border-radius:18px;padding:4px 22px}', False),
    ('B', '외곽선 — 상자 없음 (숏폼형)', 'Pretendard ExtraBold 48 · 흰 글자 + 진한 테두리 3px + 그림자',
     '.c{font:800 48px/62px P;color:#fff;text-shadow:3px 0px 0 #2B1F25,-3px 0px 0 #2B1F25,0px 3px 0 #2B1F25,0px -3px 0 #2B1F25,2px 2px 0 #2B1F25,-2px 2px 0 #2B1F25,2px -2px 0 #2B1F25,-2px -2px 0 #2B1F25,3px 1px 0 #2B1F25,-3px 1px 0 #2B1F25,3px -1px 0 #2B1F25,-3px -1px 0 #2B1F25,1px 3px 0 #2B1F25,-1px 3px 0 #2B1F25,1px -3px 0 #2B1F25,-1px -3px 0 #2B1F25,0 5px 14px rgba(0,0,0,.4);padding:0 10px}', False),
    ('C', '화이트 카드 + 핑크 바', 'Pretendard Bold 42 · 진한 글자(#2B1F25) · 흰 상자 94% · 왼쪽 핑크 바 8px',
     '.c{font:700 42px/58px P;color:' + INK + ';background:rgba(255,255,255,.94);border-radius:20px;'
     'padding:8px 26px 8px 30px;border-left:8px solid ' + PINK + ';box-shadow:0 6px 18px rgba(43,31,37,.18)}', False),
    ('D', '다크 박스 + 핵심어 핑크', 'A와 같은 상자 · Pretendard SemiBold 42 · 제품명·숫자 등 핵심어만 ExtraBold 핑크(#FF8CC0)',
     '.c{font:600 42px/58px P;color:#fff;background:rgba(20,12,16,.62);border-radius:18px;padding:4px 22px}'
     '.k{font-weight:800;color:#FF8CC0}', True),
    ('E', '핑크 줄 상자 (줄마다)', 'Pretendard Bold 42 · 흰 글자 · 브랜드 핑크(#E9579A) 92% 상자를 줄마다 따로',
     '.c{font:700 42px/66px P;color:#fff;padding:0}.c span.l{background:rgba(233,87,154,.92);border-radius:14px;'
     'padding:4px 18px;box-decoration-break:clone;-webkit-box-decoration-break:clone}', False),
]

BADGES = [
    ('1', '다크 글라스', '검정 55% · 흰 글자 · 핑크 "AI" 칩',
     f'<div class="b" style="background:rgba(20,12,16,.55);color:#fff"><i style="background:{PINK};color:#fff">AI</i>AI-generated host</div>'),
    ('2', '화이트 + 핑크 테두리', '흰 상자 · 핑크 테두리 2px · 핑크 글자',
     f'<div class="b" style="background:#fff;color:{PINK};border:2px solid {PINK}"><i style="background:{PINK};color:#fff">AI</i>AI-generated host</div>'),
    ('3', '브랜드 핑크', '핑크 상자 · 흰 글자 · 흰 "AI" 칩',
     f'<div class="b" style="background:{PINK};color:#fff"><i style="background:#fff;color:{PINK}">AI</i>AI-generated host</div>'),
]
BADGE_CSS = ('.b{display:inline-flex;align-items:center;gap:10px;font:600 24px/1 P;padding:9px 18px 9px 9px;border-radius:999px;'
             'letter-spacing:.2px}.b i{font:800 18px/1 P;font-style:normal;padding:6px 9px;border-radius:999px}')
# 배치 후보: Shopee 상단 UI(0~33%) 안 맨 위 / 헤드라인(649~749px) 바로 위
SPOTS = {'top': 48, 'above_headline': 588}


def page(body, css):
    return (f'<html><head><style>{FONT_CSS}*{{margin:0;padding:0;box-sizing:border-box}}'
            f'html,body{{width:{W}px;height:{H}px;background:transparent;overflow:hidden}}{css}</style></head><body>{body}</body></html>')


report = {'styles': [], 'badges': [], 'cap_bottom_px': CAP_BOTTOM, 'spots_px': SPOTS}
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={'width': W, 'height': H})

    TMP = OUT / '_page.html'

    def load(html_):
        TMP.write_text(html_, encoding='utf-8')
        pg.goto(TMP.as_uri())

    def shot(html_, path, clip=None):
        load(html_)
        pg.evaluate('document.fonts.ready')
        assert pg.evaluate("Promise.all(['500','600','700','800'].map(w=>document.fonts.load(w+' 42px P'))).then(a=>a.every(x=>x.length>0))"), 'Pretendard 로딩 실패'
        pg.wait_for_timeout(150)
        pg.screenshot(path=str(path), omit_background=True, clip=clip)

    # 자막 시안
    for code, name, desc, css, use_hl in STYLES:
        tiles = []
        for k, (bg, text) in BASES.items():
            body_txt = hl(text) if use_hl else html.escape(text)
            if code == 'E':
                body_txt = '<span class="l">' + body_txt + '</span>'
            wrap = (f'<div style="position:absolute;left:50px;right:50px;bottom:{H - CAP_BOTTOM}px;text-align:center">'
                    f'<span class="c" style="display:inline;box-decoration-break:clone;-webkit-box-decoration-break:clone">{body_txt}</span></div>')
            if code in ('A', 'C', 'D'):  # 여러 줄이어도 상자 하나
                wrap = (f'<div style="position:absolute;left:50px;right:50px;bottom:{H - CAP_BOTTOM}px;display:flex;justify-content:center">'
                        f'<div class="c" style="text-align:center;max-width:980px">{body_txt}</div></div>')
            ov = OUT / f'_cap_{code}_{k.replace("+", "")}.png'
            shot(page(wrap, css), ov)
            im = bg.copy()
            im.alpha_composite(Image.open(ov).convert('RGBA'))
            tiles.append(im)
        sheet = Image.new('RGB', (W * 3 + 40, H), 'white')
        for i, t in enumerate(tiles):
            sheet.paste(t.convert('RGB'), (i * (W + 20), 0))
        sheet = sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS)
        sp = OUT / f'caption_{code}.jpg'
        sheet.save(sp, quality=90)
        report['styles'].append({'code': code, 'name': name, 'desc': desc, 'mockup': sp.relative_to(ROOT).as_posix()})
        print('caption', code)

    # 배지 단독 PNG (여백 없이) + 전체 프레임 오버레이 + 목업
    for code, name, desc, body in BADGES:
        load(page(f'<div style="position:absolute;left:0;top:0">{body}</div>', BADGE_CSS))
        pg.evaluate("Promise.all(['600','800'].map(w=>document.fonts.load(w+' 24px P')))"); pg.wait_for_timeout(150)
        bb = pg.locator('.b').bounding_box()
        solo = BADGE / f'badge_ai_{code}.png'
        pg.screenshot(path=str(solo), omit_background=True,
                      clip={'x': 0, 'y': 0, 'width': round(bb['width']), 'height': round(bb['height'])})
        entry = {'code': code, 'name': name, 'desc': desc, 'png': solo.relative_to(ROOT).as_posix(),
                 'size_px': [round(bb['width']), round(bb['height'])], 'mockups': {}}
        for spot, y in SPOTS.items():
            ov = BADGE / f'overlay_badge_ai_{code}_{spot}.png'
            shot(page(f'<div style="position:absolute;right:32px;top:{y}px">{body}</div>', BADGE_CSS), ov)
            im = BASES['H'][0].copy()
            im.alpha_composite(Image.open(ov).convert('RGBA'))
            mp = OUT / f'badge_{code}_{spot}.jpg'
            im.convert('RGB').resize((W // 2, H // 2), Image.LANCZOS).save(mp, quality=90)
            entry['mockups'][spot] = mp.relative_to(ROOT).as_posix()
        report['badges'].append(entry)
        print('badge', code, entry['size_px'])
    br.close()

(OUT / 'proposal.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok')
