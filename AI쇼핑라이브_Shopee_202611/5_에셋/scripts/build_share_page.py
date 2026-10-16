# -*- coding: utf-8 -*-
"""공유용 한 장 HTML (dcsai Quick Dashboard) — 개발자용 v4에서 필요한 것만 골라 새로 구성.

2026-10-15 사용자: 공유판에는 상세 작업 플로우를 빼고 ① 영상 최종본 ② 대본 상세(토글) ③ 배너 시안 ④ 실무자 확인 필요 내용만.
QD 제약(실측): mp4·wav·mp3 업로드 불가 → 최종본은 장면별 대표 프레임(스토리보드)으로 보여 준다.
이미지 파일 이름은 영문 + 빌드마다 새 이름(한글 경로·같은 이름 재업로드 시 이미지 깨짐 실측), 한 폴더에 평평하게.
입력: 0_기획/개발자용/Shopee_AI쇼호스트_제작설계_v4.html (build_v4.py 출력)
출력: 0_기획/공유용/dcsai_bundle/ (index.html + 이미지) — 이전 묶음은 4_테스트/_old_dcsai_qd_* 로 이동
배포: cd 0_기획/공유용 && dcs-ai-cli app update shopee-ai-live-plan --path ./dcsai_bundle
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import copy
import hashlib
import re
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '0_기획/개발자용/Shopee_AI쇼호스트_제작설계_v4.html'
OUT = ROOT / '0_기획/공유용/dcsai_bundle'
FF = cfg.FFMPEG
BUILD = str(int(time.time()))
FINALS = [('V1', 'V1 Prime Primer', '아침 "Prep & Stay" — 프라이머 라인 4종', '1_최종영상/V1_PrimePrimer_AI라이브_v2.mp4'),
          ('V2', 'V2 Romantic Blush Lip & Cheek', '낮 "Add some color" — 립·치크 12색', '1_최종영상/V2_RomanticBlushLipCheek_AI라이브_v2.mp4'),
          ('V3', 'V3 Clean it Zero', '저녁 "Melt it off" — 클렌징밤 3종', '1_최종영상/V3_CleanItZero_AI라이브_v2.mp4')]

if OUT.exists():
    shutil.move(str(OUT), str(ROOT / '4_테스트' / f'_old_dcsai_qd_{int(OUT.stat().st_mtime)}'))
OUT.mkdir(parents=True)
src = BeautifulSoup(SRC.read_text(encoding='utf-8'), 'html.parser')


def frag(h):
    return BeautifulSoup(h, 'html.parser')


def sec(sid):
    return src.find('section', id=sid)


def flat_name(rel):
    stem = re.sub(r'[^A-Za-z0-9._-]+', '_', Path(rel).stem).strip('_')[:60] or 'f'
    return f'{hashlib.md5((BUILD + rel).encode()).hexdigest()[:6]}_{stem}{Path(rel).suffix.lower()}'


def clone(node):
    return copy.copy(node)


# ── 1. 최종 영상: 장면 시작 +0.8초 프레임 ──
def chapters(vid_path):
    fv = next(f for f in sec('s16').find_all('div', class_='fv') if vid_path in f.find('video')['src'])
    return [(float(bt['data-t']), bt.get_text(' ', strip=True).split(' ', 1)[1]) for bt in fv.select('.chap button.seek')], \
        fv.find('span', class_='small').get_text(' ', strip=True).split('·')


def frame(vid_path, t, name):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(ROOT / vid_path), '-frames:v', '1',
                    '-vf', 'scale=300:-2', '-q:v', '4', str(OUT / name)], check=True)
    return name


def mmss(t):
    return f'{int(t // 60)}:{int(t % 60):02d}'


videos = ''
for vid, title, sub, path in FINALS:
    chs, meta = chapters(path)
    figs = ''
    for k, (t, lab) in enumerate(chs):
        nm = frame(path, t + 0.8, flat_name(f'{vid}_ch{k:02d}.jpg'))
        figs += f'<figure class="sb"><img loading="lazy" src="{nm}" alt="{lab}"><figcaption><b>{mmss(t)}</b> {lab}</figcaption></figure>'
    videos += (f'<h3>{title} <span class="small">— {sub}</span></h3>'
               f'<p class="small">{meta[0].strip()} · {meta[1].strip()} · 1080×1920 세로 · 영어 · 원본 파일 <code>{Path(path).name}</code></p>'
               f'<div class="storyboard">{figs}</div>')

# ── 2. 대본 (토글) ──
s3 = sec('s3')
legend = clone(s3.find('p', class_='tl-legend'))
ra_note = clone(s3.find('p', class_='small'))
scripts = ''
for d in s3.find_all('details', recursive=False):
    lab = d.find('summary').get_text(strip=True)
    if '공통 오프닝' in lab:
        name = '세 편 공통 — 오프닝 (OC-1~3)'
    elif '공통 엔딩' in lab:
        name = '세 편 공통 — 엔딩 (EC-1~3)'
    else:
        h = d.find_previous_sibling('h3').get_text(' ', strip=True)
        name = re.sub(r'\s*\(약 \d+:\d+\)', '', re.sub(r'^3-\d\.\s*', '', h))  # 계획 단계 길이(약 7:50 등)는 실제 완성본과 달라 뺌
    body = d.find('div', class_='tbl') or d
    scripts += f'<details class="script"><summary>{name}</summary>{clone(body)}</details>'

# ── 3. 배너·그래픽 시안 (9-0) ──
s9 = sec('s9')
h90 = next(h for h in s9.find_all('h3') if h.get_text().startswith('9-0'))
banner = ''
n = h90.find_next_sibling()
while n is not None and n.name not in ('h3', 'h2'):
    txt = n.get_text(' ', strip=True)
    if not (n.name == 'p' and txt.startswith('파일:')) and 'warn' not in (n.get('class') or []):
        banner += str(n)
    n = n.find_next_sibling()

# ── 4. 실무자 확인 필요 ──
# 2026-10-15 사용자: 기존 4-1(16-8)·4-2(13장 R1~R11·T) 내용을 지우고 아래 12개 표로 교체 (사용자 원문 그대로, 줄바꿈만 정리)
def _ul(*xs):
    return '<ul style="margin:0;padding-left:18px">' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul>'


CHECK = [
    ('국가별 가격', 'TH·MY·ID·VN 각각, SKU별 정가 · 판매가 · 통화 · 할인율<br>— 프라이머 4종, 립앤치크 12색, 클렌징밤 3종', '할인율(50% OFF · Buy 2 Get 1)만 표기, 가격 숫자 없음', ''),
    ('사은품', '품명(영문), 고해상도 누끼 PNG, 증정 조건(구매액·품목), 소진 시 대체품과 안내 문구, 프로모션 기간', '일반 "FREE GIFT" 아이콘만', ''),
    ('립앤치크 Buy 2 Get 1 조건', '무료 1개를 고르는 범위(12색 중 아무거나? 같은 가격대만?), 다른 할인과 중복 여부, 1인 구매 한도, 프로모션 기간', '"Buy 2 Get 1"만 표기, 조건 문구 없음', ''),
    ('RA 표현 승인', '① 대본·이미지의 <span class="tag t-r">RA</span> 표시 문장 (<a href="#bn">4장 배너·그래픽</a>)<br>'
     '② 패키지 인쇄 문구 SPF50+ PA++++·24H의 국가별 표기 가능 여부<br>&nbsp;&nbsp;• 24시간 등 국가별 세부사항<br>③ "AI-generated host" 고지 문구·위치',
     '이미 영상에 들어가 있음 → 수정 나오면 해당 클립·카드만 재생성',
     '<b>4-① 배너 8종</b>' + _ul('BNR_V1_PrimePrimer_info', 'BNR_V3_CleanItZero_info') + '<b>4-② 영상 전체 화면 카드 24장</b>' + _ul('g_V3_C6')
     + '<b>4-③ 측면 카드 18장 · 오버레이</b>' + _ul('card_V1_P6-1', 'card_V3_C4-1')),
    ('Shopee 규격', _ul('스트리밍 방법론', '베트남 외 3개국 라이브 화면 캡처 각 1장(앱 UI가 덮는 범위 확인용)', '배너·라이브 커버 크기·용량·형식', '영상 유형(ex. mov/mp4?), 화질, 업로드 가능한 최대 용량'),
     '베트남 레퍼런스 기반(상단 0~33%, 하단 78~100%)으로 배치', ''),
    ('행사명·방송 일정', '11월 행사명(확정 시), 국가별 방송 일정', '없음', ''),
    ('세금 각주', '국가별 세금 포함가인지 (price before GST 표기 여부)', '없음', ''),
    ('2차 활용 영상', _ul('2차 활용 범위: 립앤치크 판매하지 않은 호수 노출 이슈 여부, 해당 국가 외 채널 노출 가능 여부'), '이슈 X', ''),
    ('시연 영상 모델 초상권', '시연 영상에 나오는 모델의 해외 4개국 Shopee 사용 가능 여부', '사용 가능', ''),
    ('채팅 응대', _ul('질문 남기는 위치(채널?), 응답 소요 시간', '진행 제품들 FAQ 리스트'), '"Leave it in the chat"까지만 말함 (답변 약속 문구 뺌)', ''),
    ('캠페인 배너', _ul('Shopee 라이브 홍보 등 활용 예정인 이미지, 배너 최종본'), '', ''),
    ('AI쇼호스트 이미지', _ul('AI쇼호스트 캐릭터 시트 및 방송 배경 제작을 위한 레퍼런스'), '', ''),
    ('프라이머 라인 2차 활용 영상', _ul('Prime Primer 라인(Sun Base · Classic · Finish Powder · Setting Fixer) 2차 활용 가능한 영상', '국가별 사용 가능 범위(TH·MY·ID·VN)'),
     '2차 활용 콘텐츠 폴더에 프라이머 라인 영상 없음 → <a href="#sec2">3장</a> 참고', ''),
]
chk_tbl = ('<div class="tbl"><table><tr><th>#</th><th>요청</th><th>구체적으로 필요한 것</th><th>현재 영상</th><th>상세</th></tr>'
           + ''.join(f'<tr><td style="white-space:nowrap">{i}</td><td style="min-width:110px"><b>{a}</b></td><td>{b_}</td><td>{c}</td><td style="min-width:190px;word-break:break-all">{d}</td></tr>' for i, (a, b_, c, d) in enumerate(CHECK, 1))
           + '</table></div>')

# ── 0. 제품·용량/호수·프로모션 (2026-10-15 사용자 제공 내용 그대로 표로) ──
PROD = [  # 2026-10-15 사용자: V1 → V2 → V3 순, 프라이머는 4종 전체 이름
    ('V1 프라이머 라인', 'Prime Primer 4종' + _ul('프라임 프라이머 클래식<br><span class="small">Prime Primer Classic</span>',
                                                 '프라임 프라이머 세팅 픽서<br><span class="small">Prime Primer Setting Fixer</span>',
                                                 '프라임 프라이머 피니쉬 파우더<br><span class="small">Prime Primer Finish Powder</span>',
                                                 '프라임 프라이머 선 베이스<br><span class="small">Prime Primer Sun Base</span>'),
     '세팅 픽서 100ml · 피니쉬 파우더 12g · 선 베이스 50ml<br><span class="small">선 베이스 50ml는 바닐라코 공식몰 상품명 기준. 클래식 용량은 받은 내용에 없음</span>',
     '<b>50% OFF + Free gift</b>', ''),
    ('V2 립앤치크', 'Romantic Blush Lip &amp; Cheek', '12호<br>02 · 04 · 05 · 07 · 08 · 09 · 12 · 13 · 14 · 17 · 18 · 20',
     '<b>Buy 2, Get 1</b>', '영상의 호수별 발색 카드 12장과 같은 호수'),
    ('V3 클렌징밤 3종', 'Clean it Zero Cleansing Balm<br>Original · Pore Clarifying · Calming', '25 / 50 / 100 / 180ml<br><span class="small">총 4개 옵션</span>',
     '<b>50% OFF + Free gift</b>', _ul('이미지는 하나로 통일해도 무방(랜딩페이지형)', 'SG·MY는 오리지널, PH는 콜라보 제품 → 3개국 통일하여 <b>오리지널로만 진행</b>')),
]
prodsec = ('<section id="pr"><h2><span class="n">0</span>제품 · 용량/호수 · 프로모션</h2>'
           '<p class="small"><b>읽는 법</b> — 이번 라이브에서 파는 제품과 행사 조건입니다(2026-10-15 전달받은 내용). 국가별 가격·사은품·행사 기간은 아직 받지 않았습니다(<a href="#ck">5장</a> 1~3번).</p>'
           '<div class="tbl"><table><tr><th>라인 (영상)</th><th>제품</th><th>용량 · 호수</th><th>프로모션</th></tr>'
           + ''.join(f'<tr><td><b>{a}</b></td><td>{b_}</td><td>{c}</td><td>{d}</td></tr>' for a, b_, c, d, _e in PROD)  # 비고 열은 사용자 요청으로 표시 안 함
           + '</table></div></section>')

# ── 1. AI 쇼호스트 캐릭터 시트 (2026-10-15 사용자: 최종 영상 앞에) ──
CS = [('5_에셋/character_sheet/R3/R3_sheet_turnaround.png', '전신·각도 (턴어라운드)'),
      ('5_에셋/character_sheet/R3/R3_sheet_expressions.png', '표정'),
      ('5_에셋/character_sheet/R3/R3_sheet_hands.png', '손 동작'),
      ('5_에셋/character_sheet/R3/R3_MF-01_9x16.png', '영상 첫 화면 (마스터 프레임, 9:16)')]
charsec = ('<section id="cs"><h2><span class="n">1</span>AI 쇼호스트 캐릭터 시트</h2>'
           '<p class="small"><b>읽는 법</b> — 세 편 모두 같은 AI 호스트 한 명이 진행합니다. 실존 인물이 아니라 이미지 생성 AI(OpenAI gpt-image-1.5)로 만든 캐릭터이고, '
           '아래 시트를 기준으로 얼굴·머리·옷을 고정했습니다. 마지막 장은 영상 생성(MiniMax H3)에 첫 화면으로 넣은 이미지입니다.</p>'
           '<div class="csgrid">' + ''.join(f'<figure class="sb"><img loading="lazy" src="../../{p}" alt="{c}"><figcaption>{c}</figcaption></figure>' for p, c in CS)
           + '</div></section>')

# ── 3. 라인별 활용 2차 콘텐츠 (팀 OneDrive '2차 활용 콘텐츠' 폴더, probe_secondary.py 실측) ──
import json as _json
from collections import Counter as _C


def _hms(t):
    t = int(round(t)); h, m, s_ = t // 3600, t % 3600 // 60, t % 60
    return (f'{h}시간 ' if h else '') + f'{m}분 {s_}초'


def _sec_line(key, title, product):
    d = _json.loads((ROOT / '5_에셋/secondary_content' / f'{key}.json').read_text(encoding='utf-8'))
    cc = _C((m.group(1) if (m := re.search(r'_([A-Z]{2})(?:[_ (\d)]*)\.\w+$', r['file'])) else '표기 없음') for r in d['files'])
    rows = ''.join(f'<tr><td>{i}</td><td style="word-break:break-all">{r["file"]}</td><td>{r["seconds"]:.1f}</td><td>{r["w"]}×{r["h"]}</td></tr>'
                   for i, r in enumerate(d['files'], 1))
    return (f'<tr><td><b>{title}</b><br><span class="small">{product}</span></td><td>{d["line"]}</td><td>{d["count"]}개</td>'
            f'<td><b>{d["total_seconds"]:,.1f}초</b><br><span class="small">({_hms(d["total_seconds"])})</span></td>'
            f'<td class="small">{" · ".join(f"{k} {v}" for k, v in cc.most_common())}</td></tr>',
            f'<details class="script"><summary>{title} — 파일 {d["count"]}개 목록 (파일명 · 길이 · 해상도)</summary><div class="tbl"><table>'
            f'<tr><th>#</th><th>파일명</th><th>길이(초)</th><th>해상도</th></tr>{rows}'
            f'<tr><td></td><td><b>합계</b></td><td><b>{d["total_seconds"]:,.1f}</b></td><td></td></tr></table></div></details>')


lc_row, lc_list = _sec_line('lipcheek', 'V2 립앤치크', 'Romantic Blush Lip &amp; Cheek')
zk_row, zk_list = _sec_line('zerokit', 'V3 클렌징밤 3종', 'Clean it Zero (제로키트)')
secsec = ('<section id="sec2"><h2><span class="n">3</span>라인별 활용 2차 콘텐츠</h2>'
          '<p class="small"><b>읽는 법</b> — 라이브 영상과 함께 쓸 수 있는 기존 영상(팀 OneDrive <code>AX팀/20. AI쇼핑라이브/2차 활용 콘텐츠</code> 폴더)을 라인별로 모았습니다. '
          '개수·길이·해상도는 파일을 직접 읽어 잰 값입니다(2026-10-15). "파일명 국가 표기"는 파일 이름 끝의 국가 코드(_PH, _MY 등)를 센 것으로, 실제 게시 국가인지는 확인하지 않았습니다(추정). '
          '이번 방송 대상 4개국(TH·MY·ID·VN) 중 파일명에 표기된 곳은 MY뿐입니다.</p>'
          '<div class="tbl"><table><tr><th>라인</th><th>폴더</th><th>영상 수</th><th>총 길이</th><th>파일명 국가 표기 (개수)</th></tr>'
          + lc_row + zk_row
          + '<tr><td><b>V1 프라이머 라인</b><br><span class="small">Prime Primer 4종</span></td><td>—</td><td colspan="3"><b>영상 부족</b> — 2차 활용 콘텐츠 폴더에 프라이머 라인 영상이 없습니다. '
            '<a href="#ck">5장</a> 13번으로 요청했습니다.</td></tr></table></div>'
          + lc_list + zk_list + '</section>')

# ── 조립 ──
hero = src.find('header', class_='hero')
legend_tags = clone(hero.find('p', class_='legend'))
doc = f'''<!doctype html><html lang="ko"><head>{''.join(str(c) for c in src.head.contents)}
<style>
.storyboard{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin:8px 0 22px}}
figure.sb{{margin:0}}figure.sb img{{width:100%;border-radius:8px;border:1px solid var(--line);display:block}}
figure.sb figcaption{{font-size:12px;line-height:1.35;margin-top:4px}}figure.sb b{{color:var(--pink)}}
details.script{{border:1px solid var(--line);border-radius:10px;padding:8px 12px;margin:8px 0;background:var(--surface)}}
details.script>summary{{cursor:pointer;font-weight:600}}
.csgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:8px 0 22px}}
</style></head><body><div class="wrap">
<nav class="toc"><b>목차</b>
<a href="#pr">0. 제품·프로모션</a><a href="#cs">1. AI 쇼호스트 캐릭터 시트</a><a href="#v">2. 최종 영상 3편</a><a href="#sec2">3. 라인별 활용 2차 콘텐츠</a><a href="#bn">4. 배너·그래픽 시안</a><a href="#ck">5. 실무자 확인 필요</a></nav>
<main>
<header class="hero">
<h1>바닐라코 × Shopee 11월 AI 쇼호스트 라이브 — 결과 공유</h1>
<p>2026-10-15 · 대상 Shopee TH · MY · ID · VN · 영어 1벌 · 제품별 독립 영상 3편 (1차 완성본)</p>
<p>프로모션: Clean It Zero 클렌징밤 3종 <b>50% OFF + Free gift</b> · Prime Primer 라인 <b>50% OFF + Free gift</b> · Romantic Blush Lip &amp; Cheek <b>Buy 2 Get 1</b></p>
{legend_tags}
</header>
<div class="callout"><b>한눈에</b> — AI로 만든 호스트가 영어로 제품을 소개하는 세로 라이브 영상 3편입니다. 화면 우측 상단에 "AI-generated host" 표시가 상시 노출됩니다. 국가별 가격·행사명은 아직 넣지 않았고(5장 1·6번 회신 후 반영), 화면 문구 중 <span class="tag t-r">RA</span> 표시는 RA·법무 검토가 필요한 표현입니다.</div>

{prodsec}
{charsec}
<section id="v"><h2><span class="n">2</span>최종 영상 3편</h2>
<p class="small"><b>읽는 법</b> — 이 페이지에서는 영상 파일을 재생할 수 없어(사내 대시보드가 영상 파일을 받지 않음), 장면이 바뀌는 지점마다 화면 한 장씩을 보여 드립니다. 이미지 아래 <b>시각</b>은 영상 안에서 그 장면이 시작되는 시점입니다. 영상 원본(mp4)은 담당자에게 요청해 주세요.</p>
{videos}
</section>

<!-- 2026-10-15 사용자: 대본 상세 삭제 -->
{secsec}
<section id="bn"><h2><span class="n">4</span>배너·그래픽 시안</h2>
{banner}
</section>

<section id="ck"><h2><span class="n">5</span>실무자 확인 필요</h2>
<p class="small"><b>읽는 법</b> — 한 줄 = 받아야 할 자료나 확인 하나. "현재 영상"은 자료 없이 지금 영상·배너에 어떻게 처리해 두었는지, "상세"는 해당 항목이 걸린 이미지 이름(4장 배너·그래픽 시안의 이미지 이름과 같음)입니다. 자료는 제작 담당자에게 전달해 주세요.</p>
{chk_tbl}
</section>
</main></div></body></html>'''
b = frag(doc)
b.title.string = '바닐라코 Shopee AI 라이브 — 결과 공유'

# 내부 링크 정리: 이 페이지에 없는 앵커는 글자만 남김, 표현 치환
for a in b.find_all('a', href=True):
    h = a['href']
    if h.startswith('#'):
        h = {'#s9': '#bn', '#s3': '#sc', '#s16': '#v', '#s13': '#ck'}.get(h, h)
        if b.find(id=h[1:]):
            a['href'] = h
            continue
    elif h.startswith('http'):
        continue
    a.name = 'span'; del a['href']
# 개발자용 장 번호·내부 문서 참조를 이 페이지 기준으로 바꾸거나 뺀다
SUBS = [('9-0', '4장 배너·그래픽'), ('(3장)', ''), ('4장 영역은 레퍼런스 1프레임 기준', '배치는 레퍼런스 화면 기준'),
        ('(9장 1080×1920)', '(1080×1920)'), ('(9장·USP 브리프 1-4 기준)', '(USP 브리프 기준)'), (' (3-0 시안)', ''), ('(3-0 시안)', ''), ('(3-0)', '(위 공통 대본)'), ('(16-2)', ''),
        ('(v2 13-2 원문, 펼치기)', '(펼치기)'), ('9장', '4장'), ('국가별 판매 사이즈 R1', '국가별 판매 사이즈(5장 1번)')]
for t in list(b.find_all(string=True)):
    v = str(t)
    if any(a in v for a, _ in SUBS) and t.parent.name not in ('style', 'script'):
        for a, c in SUBS:
            v = v.replace(a, c)
        t.replace_with(v)
# 대본 표의 "시간" 열은 계획 단계 값(1배속 기준 약 7분)이라 실제 완성본(1.25배속, 2.5~3.5분)과 달라 뺀다
for tb in b.select('details.script table'):
    rows = tb.find_all('tr')
    heads = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
    if '시간' in heads:
        k = heads.index('시간')
        for r in rows:
            cells = r.find_all(['th', 'td'], recursive=False)
            if len(cells) == len(heads):
                cells[k].decompose()
            else:  # 열 합친 줄(EC 등): 시간 모양 칸만 뺀다
                for c in cells:
                    if re.fullmatch(r'\d+:\d\d\s*[–-]\s*\d+:\d\d', c.get_text(strip=True)):
                        c.decompose()
for el in b.select('.dev-only, button.seek, .chap, script'):
    el.decompose()
# 2026-10-15 사용자: "읽는 법" 같은 설명 문단은 공유판에서 뺀다
for el in b.find_all('p'):
    if el.get_text(' ', strip=True).startswith('읽는 법'):
        el.decompose()

# 이미지 복사 (영문 이름, 평평하게)
for im in b.find_all('img', src=True):
    s = im['src']
    if (OUT / s).exists() or s.startswith(('http', 'data:')):
        continue
    rel = unquote(s)
    while rel.startswith('../'):
        rel = rel[3:]
    nm = flat_name(rel)
    shutil.copy2(ROOT / rel, OUT / nm)
    im['src'] = nm
    p = im.find_parent('a')
    if p is not None:
        p.unwrap()

(OUT / 'index.html').write_text(str(b), encoding='utf-8')
files = [p for p in OUT.iterdir() if p.is_file()]
bad = [i['src'] for i in b.find_all('img') if not (OUT / i['src']).exists()]
print('files', len(files), 'MB', round(sum(p.stat().st_size for p in files) / 1e6, 1), 'missing', bad[:3],
      'details', len(b.find_all('details')), 'RA', len(b.select('.tag.t-r')))
