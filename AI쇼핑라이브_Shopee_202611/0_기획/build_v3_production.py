"""v3 HTML에 15장 '본생성 진행'을 넣는다. build_v3_text.py → build_v3_assets.py 다음에 실행.
python -X utf8 build_v3_production.py
데이터: 3_소스클립/H3/*/run.json · 4_테스트/h3_qa/qa_summary.json · 5_에셋/production/* · 2_나레이션/*
"""
import json, re, html as H
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DST = HERE / 'Shopee_AI쇼호스트_제작설계_v3.html'
doc = DST.read_text(encoding='utf-8')

X = lambda s='확인 필요': f'<span class="tag t-x">{s}</span>'
M = lambda s='실측': f'<span class="tag t-m">{s}</span>'
U = '<span class="tag t-u">사용자 요청</span>'
P = '<span class="tag t-p">제안</span>'
R = '<span class="tag t-r">RA</span>'


def img(rel, cap):
    return (f'<figure class="shot"><a href="../{rel}"><img loading="lazy" src="../{rel}" alt="{H.escape(cap)}"></a>'
            f'<figcaption>{cap}</figcaption></figure>')


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


cfg = json.loads((ROOT / '3_소스클립/H3/config.json').read_text(encoding='utf-8'))
shots = {s['id']: s for s in json.loads((ROOT / '5_에셋/production/shotlist_v3.json').read_text(encoding='utf-8'))}
changes = json.loads((ROOT / '5_에셋/production/shotlist_v3_changes.json').read_text(encoding='utf-8'))
qa_path = ROOT / '4_테스트/h3_qa/qa_summary.json'
qa = json.loads(qa_path.read_text(encoding='utf-8')) if qa_path.exists() else {}
voice = json.loads((ROOT / '2_나레이션/voice/voice_state.json').read_text(encoding='utf-8'))
vo_log = json.loads((ROOT / '2_나레이션/vo/vo_log.json').read_text(encoding='utf-8'))

runs = {}
for sid in cfg['jobs']:
    f = ROOT / '3_소스클립/H3' / sid / 'run.json'
    runs[sid] = json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}

VERD = {'pass': ('통과', 't-m'), 'trim-tail': ('끝 군말 자름', 't-m'), 'cut-needed': ('중간 이탈 자름', 't-x'),
        'regenerate': ('재생성', 't-r'), 'guard-error': ('가드 오류', 't-r'), 'prepared': ('잔액 충전 대기', 't-x'),
        'visual-regenerate': ('재생성(화면)', 't-r')}
vis_path = ROOT / '4_테스트/h3_qa/visual_review.json'
vis = json.loads(vis_path.read_text(encoding='utf-8')) if vis_path.exists() else {'issues': {}}
counts = {}
rows = []
for sid, job in cfg['jobs'].items():
    r = runs.get(sid, {}); q = qa.get(sid, {})
    st = r.get('status', '—')
    v = q.get('verdict')
    if sid in vis['issues'] and st == 'prepared':
        v = None; st = 'prepared'
    key_ = v or st
    counts[key_] = counts.get(key_, 0) + 1
    k_ = v or st
    vtxt = f'<span class="tag {VERD[k_][1]}">{VERD[k_][0]}</span>' if k_ in VERD else st
    if sid in vis['issues']:
        vtxt += f'<br><span class="small">1차 결과 탈락: {H.escape(vis["issues"][sid]["issue"])}</span>'
    keep = q.get('keep_segments_s') or []
    kept = round(sum(e - s for s, e in keep), 2) if keep else ''
    gdir = ROOT / '4_테스트/h3_qa' / sid
    cut = next(gdir.glob('*_cut.mp4'), None) if gdir.exists() else None
    native = ROOT / '3_소스클립/H3' / sid / 'native.mp4'
    links = []
    if native.exists(): links.append(f'<a href="../{rel(native)}">원본</a>')
    if cut: links.append(f'<a href="../{rel(cut)}">편집본</a>')
    if (gdir / 'contact.jpg').exists(): links.append(f'<a href="../{rel(gdir / "contact.jpg")}">프레임</a>')
    rows.append(f'<tr><td><code>{sid}</code></td><td>{job["duration"]}</td><td class="vo">{H.escape(shots[sid]["text"])}</td>'
                f'<td>{vtxt}</td><td>{q.get("script_coverage", "")}</td><td>{kept}</td><td>{" · ".join(links)}</td></tr>')

# 바로 보기 갤러리: 영상별로 완료 클립을 대본 순서대로 (편집본이 있으면 편집본)
REJ_WHY = {'V3_O-B_1': '8.7초부터 화면이 줌인됨 (육안)', 'V3_O-B_2': '2.4초부터 배경이 남색으로 바뀜 (육안)',
           'V1_P4-3_2': '문장 중간에 대본에 없는 말 (ASR 가드)', 'V2_L4-2_2': '문장 중간에 대본에 없는 말 (ASR 가드)',
           'V3_C1': '문장 중간에 대본에 없는 말 (ASR 가드)', 'V3_C3-1': '문장 중간에 대본에 없는 말 (ASR 가드)',
           'V3_C6_2': '문장 중간에 대본에 없는 말 (ASR 가드)'}
VNAME = {'COMMON': '공통 오프닝·엔딩', 'V1': 'V1 Prime Primer', 'V2': 'V2 Romantic Blush Lip & Cheek', 'V3': 'V3 Clean it Zero'}
gal = []
for vid, vname in VNAME.items():
    ids_v = [k for k in cfg['jobs'] if shots[k]['video'] == vid]
    ok = [k for k in ids_v if runs.get(k, {}).get('generation_completed')]
    cards = []
    for k in ok:
        q = qa.get(k, {}); gdir = ROOT / '4_테스트/h3_qa' / k
        cut = next(gdir.glob('*_cut.mp4'), None) if gdir.exists() else None
        src = cut or (ROOT / '3_소스클립/H3' / k / 'native.mp4')
        v = q.get('verdict', '')
        tag = f'<span class="tag {VERD[v][1]}">{VERD[v][0]}</span>' if v in VERD else ''
        which = '편집본' if cut else '원본'
        cards.append(f'<div class="vc"><video controls preload="metadata" playsinline src="../{rel(src)}#t=0.1"></video>'
                     f'<div class="vm"><code>{k}</code> {tag} <span class="small">{which}</span></div>'
                     f'<div class="vt">{H.escape(shots[k]["text"])}</div></div>')
    rej_cards = []
    for d in sorted((ROOT / '4_테스트/h3_rejected').glob('*__*')):
        k = d.name.split('__')[0]
        if k in ids_v and (d / 'native.mp4').exists():
            rej_cards.append(f'<div class="vc rej"><video controls preload="metadata" playsinline src="../{rel(d / "native.mp4")}#t=0.1"></video>'
                         f'<div class="vm"><code>{k}</code> <span class="tag t-r">탈락 → 재생성함</span></div>'
                         f'<div class="vt">{H.escape(REJ_WHY.get(k, ""))}</div></div>')
    miss = [k for k in ids_v if k not in ok]
    miss_txt = f'<p class="small">아직 없음 {len(miss)}개 (잔액 충전 대기): ' + ', '.join(f'<code>{k}</code>' for k in miss) + '</p>' if miss else ''
    rej_txt = (f'<details><summary>탈락한 1차본 {len(rej_cards)}개 (참고용 · 영상에는 쓰지 않음)</summary><div class="vgrid">{"".join(rej_cards)}</div></details>' if rej_cards else '')
    gal.append(f'<h4>{vname} — {len(ok)}/{len(ids_v)}</h4>' + (f'<div class="vgrid">{"".join(cards)}</div>' if cards else '') + rej_txt + miss_txt)
rc_path = ROOT / '4_테스트/h3_preview/V1_roughcut.mp4'
rc_idx = json.loads((ROOT / '4_테스트/h3_preview/_roughcut_index.json').read_text(encoding='utf-8')) if rc_path.exists() else []
rc_rows = ''.join(f'<tr><td>{int(x["start_s"]//60)}:{x["start_s"]%60:04.1f}</td><td><code>{x["id"]}</code></td><td>{x["kind"]}</td><td class="vo">{H.escape(x["text"])}</td></tr>' for x in rc_idx)
RC = (f'''<div class="rc"><video controls preload="metadata" playsinline src="../{rel(rc_path)}#t=0.1"></video>
  <div><p><b>V1 러프컷 (검토용, {rc_idx[-1]["start_s"] + rc_idx[-1]["seconds"]:.0f}초)</b> — 오프닝 → V1 → 엔딩을 대본 순서로 이어 붙였습니다. <b>합성 전</b>이라 화면에는 호스트만 나오고 레이아웃·배너·제품·자막은 없습니다.
  V/O 줄은 마스터 정지화면 위에 "V/O · 시연 소스 자리" 라벨, 아직 없는 클립은 회색 "미생성" 카드(2초)로 넣었습니다. 클립 사이 전환은 단순 컷입니다.</p>
  <details><summary>타임라인 ({len(rc_idx)}구간)</summary><div class="tbl"><table><tr><th>시작</th><th>ID</th><th>종류</th><th>대사</th></tr>{rc_rows}</table></div></details>
  <p class="small">만드는 법: <code>python -X utf8 5_에셋/scripts/build_roughcut.py</code> → <code>4_테스트/h3_preview/</code></p></div></div>''' if rc_idx else '')

done = sum(1 for r in runs.values() if r.get('generation_completed'))
PILOT2 = ('COMMON_OC-1', 'V2_L6_1')
done_batch = sum(1 for k, r in runs.items() if r.get('generation_completed') and k not in PILOT2)
done_secs = sum(cfg['jobs'][k]['duration'] for k, r in runs.items() if r.get('generation_completed') and k not in PILOT2)
rej_dirs = [d for d in (ROOT / '4_테스트/h3_rejected').glob('*__*') if (d / 'run.json').exists()]
rej_secs = sum(int(json.loads((d / 'run.json').read_text(encoding='utf-8'))['inputs']['duration']) for d in rej_dirs)
pend_ids = [k for k, r in runs.items() if r.get('status') == 'prepared']
pend = len(pend_ids); pend_secs = sum(cfg['jobs'][k]['duration'] for k in pend_ids)
secs = sum(j['duration'] for j in cfg['jobs'].values())
summary = ' · '.join(f'{VERD.get(k, (k,))[0]} {n}' for k, n in sorted(counts.items(), key=lambda x: -x[1]))

chg = ''.join(f'<tr><td>{c["id"]}</td><td class="vo">{H.escape(c["before"])}</td><td class="vo">{H.escape(c["after"])}</td><td>{H.escape(c["why"])}</td></tr>' for c in changes)
vo_rows = ''.join(f'<tr><td><code>{k}</code></td><td class="vo">{H.escape(v["text"])}</td><td>{v["seconds"]}</td>'
                  f'<td><audio controls preload="none" src="../2_나레이션/vo/{k}.wav"></audio></td></tr>' for k, v in vo_log.items())

S15 = f'''<section id="s15">
  <h2><span class="n">15</span>본생성 진행 — R3 확정 · v3 대본 그대로 {U}</h2>
  <h3 id="s15-0">15-0. 생성된 영상 바로 보기 — 완료 {done}/{len(cfg['jobs'])}클립</h3>
  <p class="small"><b>읽는 법</b> — 카드마다 재생 버튼을 누르면 바로 봅니다. <span class="tag t-m">통과</span> 원본 그대로 사용 · <span class="tag t-m">끝 군말 자름</span> 대사를 다 말한 뒤 붙은 말을 잘라낸 <b>편집본</b>을 보여 줍니다(원본은 15-5 표의 링크). 판정은 음성 인식(ASR) 자동 검사 + 5프레임 육안 결과이고, 사람이 끝까지 듣는 확인은 아직 안 했습니다 {X('미실시')}. 모든 클립은 합성 전 원소스(호스트만)이고, 합성한 완성본은 <a href="#s16">16장</a>에 있습니다.</p>
  {''.join(gal)}

  <div class="callout"><b>결정 (2026-10-14)</b> — 캐릭터 <b>R3</b>(둥근 얼굴·소프트브라운 웨이브), 대본은 <b>v3 3장 그대로</b>. 보이스는 청취 전이라 6장 1순위 <b>A(Voice Design A-1)</b>로 진행했습니다 {P} — 바꾸면 H3 클립을 다시 만들어야 합니다.</div>

  <h3>15-1. 캐릭터 시트 · 마스터 프레임 (gpt-image-1.5, R3 정면을 레퍼런스로)</h3>
  <div class="shots wide">
    {img('5_에셋/character_sheet/R3/R3_sheet_turnaround.png', '각도: 정면 · 3/4 좌 · 3/4 우 · 측면')}
    {img('5_에셋/character_sheet/R3/R3_sheet_expressions.png', '표정 6종 (마지막 칸 가리키는 손이 팔과 이어지는지 애매 — 육안)')}
    {img('5_에셋/character_sheet/R3/R3_sheet_hands.png', '손 제스처 4종 (손가락 5개, 육안)')}
  </div>
  <div class="shots">{img('5_에셋/character_sheet/R3/R3_MF-01_9x16.png', 'MF-01 마스터 (H3 첫 프레임, 1080×1920) — 눈 높이 26%, 테이블 87%')}</div>
  <p class="small">마스터는 세 번 만들었습니다 {M()}: ① gpt-image 아웃페인트 → 얼굴이 바뀌고 배경이 어두워져 폐기 ② 머리 위 여백을 넣어 눈 높이 46%로 맞춘 판 → H3가 빈 벽에 <b>세로 줄무늬</b>를 그리거나 <b>줌인</b>함(파일럿 v1) → 폐기 ③ gpt-image 원래 구도(눈 26%)를 9:16으로 자른 판 → 줌·줄무늬 없음(파일럿 v2). 그래서 합성 단계에서 호스트를 340px 아래로 내리고, 비는 위쪽은 마스터 프레임 벽을 흐리게 늘여 채웠습니다(16장). 폐기본: <code>4_테스트/character/R3_rejected/</code></p>

  <h3>15-2. 보이스 A — 들어 보시고 바꿀지 알려주세요</h3>
  <div class="tbl"><table>
    <tr><th>파일</th><th>내용</th><th>재생</th></tr>
    <tr><td>Voice Design 미리듣기</td><td class="vo">{H.escape(voice['preview_text'])}</td><td><audio controls preload="none" src="../2_나레이션/voice/A1_design_preview.mp3"></audio></td></tr>
    <tr><td>H3 reference ({voice['reference_seconds']:.1f}초)</td><td class="vo">{H.escape(re.sub('<#[0-9.]+#>', '', voice['reference_text']))}</td><td><audio controls preload="none" src="../2_나레이션/voice/host_reference.wav"></audio></td></tr>
  </table></div>
  <p class="small">voice_id는 <code>2_나레이션/voice/voice_state.json</code>에 있습니다. T2A로 바로 합성했으므로 공식 FAQ 기준 영구 보존 대상입니다(Voice Design 보이스에도 적용되는지는 {X('1주 뒤 확인')}). reference 문장은 대본에 없는 중립 문장으로 만들어, H3가 따라 읽지 않게 했습니다.</p>

  <h3>15-3. 장면 → 생성 단위</h3>
  <p>호스트가 화면에서 말하는 줄(H·S·H+G·G+H) = <b>H3 클립 {len(cfg['jobs'])}개</b>, 화면 밖 목소리(D·G·"V/O") = <b>T2A {len(vo_log)}줄</b>. 한 클립 대사는 문장 경계에서 22단어 이하로 나눴고, 클립 길이는 <code>단어 수 ÷ 1.9 + 2초</code>(6~15초)입니다 — 파일럿 실측 말 속도 1.9~2.1단어/초 {M()}. H3는 대사 뒤 남는 시간을 대본에 없는 말로 채우는 경향이 있어(파일럿 OC-1), 길이를 대사에 맞춰 줄였습니다. 총 {secs}초.</p>
  <div class="tbl"><table>
    <tr><th>장면</th><th>v3 대본</th><th>생성에 쓴 문장</th><th>이유</th></tr>{chg}
  </table></div>

  <h3>15-4. 파일럿 3회 — 무엇이 깨졌고 어떻게 고쳤나 {M()}</h3>
  <div class="tbl"><table>
    <tr><th>회차</th><th>결과</th><th>조치</th></tr>
    <tr><td>v0 (15초 고정)</td><td>OC-1: 대사(5.7초) 뒤 9초 동안 대본에 없는 말. L6: 실제론 대본대로 말했지만 ASR이 "oh-five"를 "05"로 적어 가드가 오판</td><td>클립 길이를 대사에 맞춤 · 가드에 숫자 표기 통일 + <b>trim-tail</b> 판정 추가(대본을 다 말한 뒤의 군말은 길이와 무관하게 잘라냄)</td></tr>
    <tr><td>v1 (여백 마스터)</td><td>OC-1: 배경 세로 줄무늬 + 대사 중간 이탈 / L6_1: 구도가 줌인됐다 돌아옴</td><td>마스터를 gpt-image 원래 구도로 교체, 프롬프트에 "삼각대 고정·줌 없음" 강화, "BANILA CO" → "Banila Co"</td></tr>
    <tr><td>v2</td><td>두 클립 모두 구도 고정·줄무늬 없음, 대본 커버리지 100%, 끝 군말만 → trim-tail 편집본 OC-1 6.08초 / L6_1 13.42초</td><td>본생성 진행</td></tr>
  </table></div>
  <p class="small">파일럿 원본: <code>4_테스트/h3_pilot_v0/</code>, <code>4_테스트/h3_pilot_v1/</code>. 가드 수정 전 버전 백업: <code>4_테스트/asr_guard/asr_script_guard_v1_backup.py</code>.</p>

  <h3>15-5. H3 클립 결과 — 완료 {done}/{len(cfg['jobs'])} · {summary}</h3>
  <p class="small"><b>읽는 법</b> — 판정은 ASR 대사 가드(14장) 자동 결과입니다. <span class="tag t-m">통과</span> 그대로 사용 · <span class="tag t-m">끝 군말 자름</span> 대본을 다 말한 뒤 붙은 말을 잘라낸 편집본 사용 · <span class="tag t-x">중간 이탈 자름</span> 중간 구간을 뺀 편집본(이음새 확인 필요) · <span class="tag t-r">재생성</span> 대본 단어가 빠지거나 이탈이 길어 다시 생성. 커버리지 = 대본 단어 중 들린 비율(0~1). 남긴 길이 = 편집본 길이(초). 사람이 듣는 최종 확인은 {X('미실시')}.</p>
  <div class="tbl"><table>
    <tr><th>ID</th><th>요청 길이(초)</th><th>대사</th><th>판정</th><th>커버리지</th><th>남긴 길이(초)</th><th>파일</th></tr>
    {''.join(rows)}
  </table></div>

  <h3>15-6. V/O (T2A, 보이스 A) — {len(vo_log)}줄</h3>
  <p class="small">ASR 검사 결과 모두 대본대로 합성된 것으로 판단 {M('실측+판단')}: 1~2초짜리 호수 음성은 Whisper가 짧은 음성을 못 듣거나 반복 기재하는 오류가 있어, 12개를 0.6초 간격으로 이어 붙인 파일(<code>2_나레이션/vo/sequence/V2_L5_shades_all.wav</code>)로 다시 확인 → 12개 모두 순서대로 인식. "cica"→"seeker" 등은 인식 오차. 결과: <code>4_테스트/vo_qa/</code></p>
  <details><summary>V/O 23줄 듣기</summary><div class="tbl"><table><tr><th>ID</th><th>문장</th><th>초</th><th>재생</th></tr>{vo_rows}</table></div></details>

  <h3>15-7. 비용 (정가 기준 추정 — 청구서 아님)</h3>
  <div class="tbl"><table>
    <tr><th>항목</th><th>내용</th><th>추정</th></tr>
    <tr><td>H3 파일럿</td><td>v0 15초×2, v1 9+14초, v2 9+14초</td><td>약 ${0.13*(30+23+23):.2f}</td></tr>
    <tr><td>H3 본생성 (생성 완료분)</td><td>{done_batch}클립 {done_secs}초 + 검수 탈락 후 재생성한 {len(rej_dirs)}클립의 1차분 {rej_secs}초 (파일럿 v2 제외)</td><td>약 ${0.13*(done_secs+rej_secs):.2f}</td></tr>
    <tr><td>H3 잔액 부족 실패</td><td>34클립 — 공급자 응답 <code>1008 insufficient balance</code>, usage 비어 있음 → 과금 안 된 것으로 추정 {X('콘솔 확인')}. 이후 잔액 충전 뒤 다시 생성함</td><td>$0 (추정)</td></tr>
    {f'<tr><td>H3 남은 생성</td><td>{pend}클립 {pend_secs}초</td><td>약 ${0.13*pend_secs:.2f}</td></tr>' if pend else ''}
    <tr><td><b>H3 합계</b></td><td>파일럿 76초 + 본생성 {done_secs}초 + 탈락 1차분 {rej_secs}초 = {76+done_secs+rej_secs}초</td><td><b>약 ${0.13*(76+done_secs+rej_secs):.2f}</b></td></tr>
    <tr><td>gpt-image-1.5</td><td>R3 후보 3 + 시트 3 + 마스터 1 + 아웃페인트 1 (high)</td><td>{X('금액 미확인')}</td></tr>
    <tr><td>MiniMax Voice Design · T2A</td><td>미리듣기 1 + reference 1 + V/O 23줄</td><td>{X('금액 미확인')} (Voice Design 미리듣기 $30/100만 자 기준 1달러 미만)</td></tr>
  </table></div>
  <p class="small">H3 단가 $0.13/초는 POC 기록의 공식 가격표 기준값입니다. 실제 청구액은 MiniMax 콘솔에서 확인 {X()}.</p>

  {f'<div class="callout warn"><b>{pend}클립이 아직 생성 전입니다.</b> <code>python -X utf8 5_에셋/scripts/h3_production.py submit pending</code> → <code>resume all --wait 1500</code> → <code>qa_h3.py all</code></div>' if pend else ''}
</section>'''

doc = re.sub(r'\n<section id="s15">.*?\n</section>', '', doc, flags=re.S)
doc = doc.replace('\n</main>', '\n' + S15 + '\n</main>', 1)
if 'href="#s15"' not in doc:
    doc = doc.replace('<a href="#s14">14. POC 결과 · 대사 가드</a>', '<a href="#s14">14. POC 결과 · 대사 가드</a>\n  <a href="#s15">15. 본생성 진행</a>', 1)
doc = re.sub(r'<style id="v3-prod">.*?</style>\n?', '', doc, flags=re.S)
doc = doc.replace('</head>', '<style id="v3-prod">#s15 audio{height:32px;max-width:220px}#s15 td code{white-space:nowrap}'
                   '.vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;margin:8px 0 18px}'
                   '.vc{background:var(--card,#fff);border:1px solid rgba(128,128,128,.25);border-radius:10px;padding:8px;min-width:0}'
                   '.vc.rej{border-color:#d33}.vc video{width:100%;aspect-ratio:9/16;background:#000;border-radius:6px;display:block}'
                   '.vm{margin:6px 0 4px;font-size:12px;display:flex;flex-wrap:wrap;gap:4px;align-items:center}.vt{font-size:12.5px;line-height:1.45}'
                   '.rc{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:18px;margin:10px 0 20px;align-items:start}'
                   '.rc video{width:100%;aspect-ratio:9/16;background:#000;border-radius:8px}'
                   '@media(max-width:700px){.rc{grid-template-columns:1fr}.rc video{max-width:300px}.vgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}</style>\n</head>', 1)
DST.write_text(doc, encoding='utf-8')
print('ok s15', done, '/', len(cfg['jobs']), summary)
