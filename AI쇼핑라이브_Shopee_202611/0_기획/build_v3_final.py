"""v3 HTML에 16장 '최종 편집본'을 넣는다. build_v3_production.py 다음에 실행.
python -X utf8 build_v3_final.py
데이터: 1_최종영상/*.mp4 · 4_테스트/edit_seg/<V>/edit_log.json · 5_에셋/edit_gfx/* · 5_에셋/banner/common/* · 5_에셋/logo/*
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import csv, json, re, subprocess, html as H
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DST = HERE / 'Shopee_AI쇼호스트_제작설계_v3.html'
FP = cfg.FFPROBE
doc = DST.read_text(encoding='utf-8')
X = lambda s='확인 필요': f'<span class="tag t-x">{s}</span>'
M = lambda s='실측': f'<span class="tag t-m">{s}</span>'
U = '<span class="tag t-u">사용자 요청</span>'
R = '<span class="tag t-r">RA</span>'


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def img(p, cap):
    r = rel(p)
    return f'<figure class="shot"><a href="../{r}"><img loading="lazy" src="../{r}" alt="{H.escape(cap)}"></a><figcaption>{cap}</figcaption></figure>'


def dur(p):
    return float(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout.strip() or 0)


MODE = {'H': '호스트', 'H+G': '호스트 + 측면 카드', 'S': '호스트 + 시연 창', 'G': '전체 화면 카드 (V/O)', 'G+H': '전체 화면 카드 (호스트 음성)', 'D': '공식 시연 영상 전체 화면 (V/O)'}
NAMES = {'V1': 'V1 Prime Primer', 'V2': 'V2 Romantic Blush Lip & Cheek', 'V3': 'V3 Clean it Zero'}
_meta = json.loads((ROOT / '4_테스트/edit_seg/final_meta.json').read_text(encoding='utf-8'))
FILES, SPEED = _meta['files'], _meta['speed']   # 완성본은 1.25배속 → 시작 시각도 배속 기준

vids, demo_rows = [], {}
for v, name in NAMES.items():
    f = ROOT / '1_최종영상' / FILES[v]
    lp = ROOT / '4_테스트/edit_seg' / v / 'edit_log.json'
    log = json.loads(lp.read_text(encoding='utf-8')) if lp.exists() else []
    t, rows = 0.0, ''
    for x in log:
        ts = t / SPEED
        rows += (f'<tr><td>{int(ts // 60)}:{ts % 60:04.1f}</td><td><code>{x["id"]}</code></td><td>{MODE.get(x["mode"], x["mode"])}</td>'
                 f'<td>{H.escape(x.get("card") or x.get("graphic") or "")}</td><td class="vo">{H.escape(" / ".join(c[2] for c in x.get("captions", [])))}</td></tr>')
        t += x.get('out_seconds', 0)
        if x.get('demo'):
            demo_rows[x['id']] = x['demo']
    if f.exists():
        player = f'<video controls preload="metadata" playsinline src="../{rel(f)}#t=0.1"></video>'
        meta = f'{dur(f):.0f}초 ({SPEED}배속) · {len(log)}줄 · <code>{rel(f)}</code>'
    else:
        player = '<div class="small">아직 이어붙이지 않음 (생성 미완료 클립 대기)</div>'
        meta = f'{len(log)}줄 합성됨'
    vids.append(f'<div class="fv">{player}<div><b>{name}</b><br><span class="small">{meta}</span>'
                f'<details><summary>타임라인 (줄별 화면 유형 · 자막)</summary><div class="tbl"><table><tr><th>시작</th><th>ID</th><th>화면</th><th>그래픽</th><th>자막</th></tr>{rows}</table></div></details></div></div>')

fl = []
for v in NAMES:
    lp = ROOT / '4_테스트/edit_seg' / v / 'edit_log.json'
    for x in (json.loads(lp.read_text(encoding='utf-8')) if lp.exists() else []):
        if x.get('flashes_replaced') and x['id'] not in [r[0] for r in fl]:
            fl.append((x['id'], x['flashes_replaced']))
flash_tbl = ''.join(f'<tr><td><code>{k}</code></td><td>{", ".join(f"프레임 {a}~{b} (+{d})" for a, b, d in v)}</td></tr>' for k, v in fl)

demo_tbl = ''.join(f'<tr><td><code>{k}</code></td><td>{"<br>".join(H.escape(Path(d[0] if isinstance(d, (list, tuple)) else d).name) for d in v)}</td></tr>' for k, v in demo_rows.items())

ra = []
for fcsv in (ROOT / '5_에셋/edit_gfx/edit_gfx_copy.csv', ROOT / '5_에셋/banner/common/banner_copy.csv'):
    if fcsv.exists():
        for r in list(csv.reader(open(fcsv, encoding='utf-8-sig')))[1:]:
            if r[-1].startswith('RA') and (r[0], r[-2]) not in [(a, b) for a, b in ra]:
                ra.append((r[0], r[-2]))
ra_tbl = ''.join(f'<tr><td><code>{H.escape(a)}</code></td><td class="vo">{H.escape(b)}</td></tr>' for a, b in ra)

vis = json.loads((ROOT / '4_테스트/h3_qa/visual_review.json').read_text(encoding='utf-8'))
regen = ['V3_O-B_1', 'V3_O-B_2', 'V1_P4-3_2', 'V2_L4-2_2', 'V3_C1', 'V3_C3-1', 'V3_C6_2']
qa = json.loads((ROOT / '4_테스트/h3_qa/qa_summary.json').read_text(encoding='utf-8'))
FIRST = {'V3_O-B_1': '8.7초부터 화면 줌인 (육안)', 'V3_O-B_2': '2.4초부터 배경이 남색으로 바뀜 (육안)'}
VK = {'pass': '통과', 'trim-tail': '끝 군말 자름', 'cut-needed': '중간 이탈 자름', 'regenerate': '재생성'}
regen_tbl = ''.join(f'<tr><td><code>{k}</code></td><td>{FIRST.get(k, "문장 중간에 대본에 없는 말 (ASR 가드)")}</td>'
                    f'<td>{VK.get(qa.get(k, {}).get("verdict"), qa.get(k, {}).get("verdict", "대기"))}</td></tr>' for k in regen)

banners = sorted((ROOT / '5_에셋/banner/common').glob('BNR_*.png'))
gfx_g = sorted((ROOT / '5_에셋/edit_gfx').glob('g_*.png'))
cards = sorted((ROOT / '5_에셋/edit_gfx').glob('card_*.png'))

S16 = f'''<section id="s16">
  <h2><span class="n">16</span>최종 편집본 — 배너 · 시연 · 카드 · 자막 합성 {U}</h2>
  <div class="callout"><b>요청 (2026-10-15)</b> — ① 클렌징밤 편에서 보인 "빛 반짝임" 보완 ② 나머지 클립 생성 ③ 배너·시연 장면 등 편집 완료 ④ 폰트는 Pretendard ⑤ 바닐라코 로고는 정식 로고 사용.</div>
  <p class="small"><b>읽는 법</b> — 아래 영상은 합성까지 끝난 1차 완성본입니다(1080×1920, 30fps, 원본 음성 = 호스트 H3 음성 + T2A V/O, 배경음악 없음). 화면 유형: {" · ".join(f"<b>{k}</b> {v}" for k, v in MODE.items())}. Shopee 앱 화면(상단 UI·하단 채팅)은 영상 위에 앱이 그리므로 영상에는 넣지 않았고, 핵심 내용은 4장 안전 영역(세로 34~76%)에만 두었습니다.</p>

  <h3>16-0. 완성본 3편</h3>
  {''.join(vids)}

  <h3>16-1. 빛 반짝임 — 원인과 조치 {M()}</h3>
  <p>프레임마다 평균 밝기(YAVG, 0~255)를 재서 앞뒤 9프레임 중앙값보다 2 넘게 튀는 곳을 찾았습니다. 첫 27클립 중 COMMON_OC-1(+10.0)·OC-2(+14.1)·V1_P1_2(+11.4)·V1_P5-4(+5.0)가 모두 <b>4.96초(24fps 기준 119~120번째 프레임)</b>에서 2~3프레임 하얗게 떴습니다. 위치가 클립과 무관하게 같아 H3가 약 5초 단위로 이어 생성하는 경계에서 생기는 것으로 추정합니다 {X('추정')}.</p>
  <ul>
    <li><b>생성 단계</b>: 남은 35클립과 재생성 7클립 프롬프트에 "조명·노출 일정, 번쩍임·깜빡임·화이트밸런스 변화 없음" 조항을 추가했습니다.</li>
    <li><b>편집 단계</b>: 모든 호스트 클립을 같은 방법으로 재고, 튄 프레임을 직전 프레임으로 교체했습니다(ffmpeg freezeframes, 2~3프레임 = 0.1초 내외 정지). OC-2 편집본을 다시 재보니 튐 0 {M()}.</li>
  </ul>
  <details><summary>교체한 프레임 ({len(fl)}클립)</summary><div class="tbl"><table><tr><th>클립</th><th>교체 구간 (밝기 튐)</th></tr>{flash_tbl}</table></div></details>

  <h3>16-2. 정식 로고</h3>
  <div class="shots">{img(ROOT / '5_에셋/logo/_check.png', '추출한 로고 — 핑크(#FBD3D9, 원본 색) / 흰색')}</div>
  <p class="small">로컬과 사내 NAS 검색(로고·logo·BANILA CI)에서 바닐라코 로고 단독 파일(AI·SVG·PNG)은 찾지 못했습니다. 그래서 NAS의 공식 영상 <code>BANILACO_CLEANSING_BALM_ASMR_logo.mp4</code>(file_id 2239a722a6de) 마지막 흰 화면의 로고(503×61px)를 배경만 투명하게 뽑아 썼습니다 — 글자 모양은 원본 픽셀 그대로이고 폰트로 다시 쓰지 않았습니다. 영상·배너에서는 이보다 작게(높이 22~30px) 쓰므로 확대 손실은 없습니다. 원본 핑크는 밝아 연한 배경에서 안 보여, 진한 핑크(#E9579A) 알약 위에 흰색으로 올렸습니다. <b>정식 벡터 로고 파일을 받으면 교체</b>합니다 {X('로고 원본 요청')}. 파일: <code>5_에셋/logo/</code></p>

  <h3>16-3. 배너 v2 — Pretendard + 정식 로고</h3>
  <p class="small">9장 배너의 Poppins·Playfair를 Pretendard(SIL OFL, <code>5_에셋/banner/fonts/</code>)로 바꾸고 상단에 로고를 넣었습니다. 레이아웃·문구·누끼는 그대로입니다. 이전판: <code>4_테스트/banner_v1_poppins/</code>. 립앤치크는 B. by BANILA 브랜드라 BANILA CO 로고를 쓸지 {X('R6 브랜드 표기')}.</p>
  <div class="shots">{''.join(img(p, p.stem) for p in banners)}</div>

  <h3>16-4. 영상용 그래픽</h3>
  <p class="small">배너는 상단 0~33%(Shopee UI 자리)에 핵심 문구가 있어 영상에 그대로 넣으면 가려집니다. 그래서 영상용은 같은 디자인으로 <b>34~68% 안에 내용을 둔 판</b>을 따로 만들었습니다. 제품은 공식 누끼, 발색은 공식 발색컷만 썼습니다(생성 아님). 파일: <code>5_에셋/edit_gfx/</code> · 재생성 <code>python -X utf8 5_에셋/scripts/build_edit_gfx.py</code></p>
  <details><summary>전체 화면 카드 {len(gfx_g)}장</summary><div class="shots">{''.join(img(p, p.stem) for p in gfx_g)}</div></details>
  <details><summary>측면 카드 {len(cards)}장 (투명 PNG, 호스트 위에 얹음)</summary><div class="shots">{''.join(img(p, p.stem) for p in cards)}</div></details>

  <h3>16-5. 시연 소스 배정 (공식 상세페이지 영상, 원본 소리 제거)</h3>
  <p class="small">28개 소스를 6프레임 시트로 육안 확인했고 번인 자막·워터마크는 보지 못했습니다 {M('육안')}. 배속은 쓰지 않았습니다(원속, 짧으면 반복). <b>프라이머 시연 영상(선베이스·클래식·파우더)에는 실제 모델 얼굴이 나옵니다</b> — 해외(TH·MY·ID·VN) Shopee 사용 범위 확인 필요 {X('모델 초상권')}. 23·24호(방송 12색 아님) 소스는 쓰지 않고 08·13호로 바꿨습니다. 카밍 밤은 시연 영상이 없어 카드로 대체.</p>
  <div class="tbl"><table><tr><th>줄</th><th>소스 파일</th></tr>{demo_tbl}</table></div>

  <h3>16-6. 이번에 다시 만든 호스트 클립 (7개)</h3>
  <div class="tbl"><table><tr><th>클립</th><th>1차 문제</th><th>재생성 판정</th></tr>{regen_tbl}</table></div>
  <p class="small">재생성 판정은 같은 가드 결과입니다. <b>V3_C6_2</b>의 "중간 이탈"은 대사를 마친 뒤 6.7초부터라 끝만 잘랐습니다(화면 튐 없음). <b>V3_C3-1</b>은 두 번 모두 문장 사이에 대본에 없는 말이 끼어, 2차본에서 4.5~5.9초를 잘라냈습니다. 남긴 구간에 대본 두 문장이 순서대로 온전히 들어 있음을 단어 타임스탬프로 확인했지만 {M()}, 4.4초에 점프컷이 생깁니다 — 보시고 거슬리면 대사를 두 클립으로 나눠 다시 만들겠습니다 {X('사람 확인')}.</p>

  <h3>16-7. 화면 문구 중 RA 검토 대상 {R}</h3>
  <div class="tbl"><table><tr><th>그래픽</th><th>문구</th></tr>{ra_tbl}</table></div>

  <h3>16-8. 남은 일 · 확인 요청</h3>
  <div class="tbl"><table><tr><th>#</th><th>항목</th><th>누가</th></tr>
    <tr><td>1</td><td>완성본 3편을 처음부터 끝까지 보고 듣는 확인 — 보이스 A 톤 포함 (자막 타이밍은 음성 구간을 글자 수 비율로 나눈 근사값) {X('미실시')}</td><td>담당자</td></tr>
    <tr><td>2</td><td>V3_C3-1 점프컷(4.4초) 허용 여부 — 안 되면 대사를 두 클립으로 나눠 재생성 (유료)</td><td>담당자</td></tr>
    <tr><td>3</td><td>화면 문구 RA 대상 {len(ra)}개(16-7)와 대본 RA 표시 문장(3장) 검토 — 결과에 따라 해당 클립·카드만 다시 만듦 {R}</td><td>RA</td></tr>
    <tr><td>4</td><td>정식 로고 원본(AI·SVG·PNG) — 받으면 추출본과 교체</td><td>BM</td></tr>
    <tr><td>5</td><td>립앤치크(B. by BANILA) 편에 BANILA CO 로고를 쓰는 게 맞는지 (R6)</td><td>BM</td></tr>
    <tr><td>6</td><td>프라이머 시연 영상 속 모델의 해외(TH·MY·ID·VN) 사용 범위 (초상권)</td><td>BM·법무</td></tr>
    <tr><td>7</td><td>실제 Shopee 라이브 화면에 올려 상단 UI·하단 채팅과 겹침 확인 (4장 영역은 레퍼런스 1프레임 기준) {X()}</td><td>채널</td></tr>
    <tr><td>8</td><td>국가별 가격·사은품·행사명 레이어 — R1~R3 회신 후 제작</td><td>채널·영업 → 제작</td></tr>
  </table></div>
  <p class="small">V3 C1의 욕실 B-roll은 만들지 않고 호스트 화면으로 대체했습니다.</p>
</section>'''

doc = re.sub(r'\n<section id="s16">.*?\n</section>', '', doc, flags=re.S)
doc = doc.replace('\n</main>', '\n' + S16 + '\n</main>', 1)
if 'href="#s16"' not in doc:
    doc = doc.replace('<a href="#s15">15. 본생성 진행</a>', '<a href="#s15">15. 본생성 진행</a>\n  <a href="#s16">16. 최종 편집본</a>', 1)
doc = re.sub(r'<style id="v3-final">.*?</style>\n?', '', doc, flags=re.S)
doc = doc.replace('</head>', '<style id="v3-final">.fv{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:18px;margin:14px 0 22px;align-items:start}'
                  '.fv video{width:100%;aspect-ratio:9/16;background:#000;border-radius:8px}#s16 td code{white-space:nowrap}'
                  '.fv>div{min-width:0}@media(max-width:700px){.fv{grid-template-columns:minmax(0,1fr)}.fv video{max-width:300px}}</style>\n</head>', 1)
DST.write_text(doc, encoding='utf-8')
print('ok s16', [v.split('<b>')[1].split('</b>')[0] for v in vids], 'flash clips', len(fl), 'RA', len(ra))
