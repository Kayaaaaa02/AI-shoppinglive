import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import re
# -*- coding: utf-8 -*-
"""v3 HTML(설계 + 15·16장 진행 기록) → v4 정리본.

v4 = 완성본 3편이 나온 뒤의 상태 문서. 끝난 후보 비교·확정 게이트·계획 단계 표를 지우고
현재 상태 요약을 맨 앞에 둔다. v3 파일은 비교용으로 그대로 둔다.
빌드 순서: build_v3_text → build_v3_assets → build_v3_production → build_v3_final → build_v4
"""
import html
import json
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / 'Shopee_AI쇼호스트_제작설계_v3.html'
OUT = HERE / '개발자용' / 'Shopee_AI쇼호스트_제작설계_v4.html'  # 2026-10-15 사용자: 개발자용(로컬, 영상 재생) / 공유용(dcsai) 분리
FFPROBE = cfg.FFPROBE

b = BeautifulSoup(SRC.read_text(encoding='utf-8'), 'html.parser')


def frag(html):
    return BeautifulSoup(html, 'html.parser')


def sec(sid):
    s = b.find('section', id=sid)
    assert s is not None, sid
    return s


def h3_of(s, prefix):
    hs = [h for h in s.find_all('h3', recursive=False) if h.get_text(strip=True).startswith(prefix)]
    assert len(hs) == 1, (prefix, len(hs))
    return hs[0]


def drop_block(h3):
    """h3와, 다음 h3/h2 전까지의 형제 요소를 지운다."""
    n = h3.find_next_sibling()
    while n is not None and n.name not in ('h3', 'h2'):
        nxt = n.find_next_sibling()
        n.decompose()
        n = nxt
    h3.decompose()


def clear_after_h2(s):
    for c in list(s.find_all(recursive=False)):
        if c.name != 'h2':
            c.decompose()


def set_h2(s, title):
    h2 = s.find('h2')
    n = h2.find('span', class_='n')
    h2.clear()
    h2.append(n)
    h2.append(frag(title))


def dur(p):
    r = subprocess.run([FFPROBE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return float(r.stdout.strip())


T_OK = '<span class="tag t-m">완료</span>'
T_WAIT = '<span class="tag t-x">확인 대기</span>'
T_TODO = '<span class="tag t-x">회신 대기</span>'

# ── 머리말 ──
b.title.string = 'Shopee AI쇼호스트 제작설계 v4'
hero = b.find('header', class_='hero')
hero.find('h1').string = 'Shopee 11월 AI 쇼호스트 — 제작 설계 v4'
hero.find_all('p')[0].replace_with(frag(
    '<p>작성 2026-10-13 · <b>v4 2026-10-15</b>: 완성본 3편 제작 완료를 반영하고, 끝난 후보 비교·계획 단계 내용을 지웠습니다 · '
    '이전 버전(비교용): <code>Shopee_AI쇼호스트_제작설계_v3.html</code></p>'))

# ── 0. 현재 상태 ──
finals = [('V1 Prime Primer', '1_최종영상/V1_PrimePrimer_AI라이브_v2.mp4'),
          ('V2 Romantic Blush Lip &amp; Cheek', '1_최종영상/V2_RomanticBlushLipCheek_AI라이브_v2.mp4'),
          ('V3 Clean it Zero', '1_최종영상/V3_CleanItZero_AI라이브_v2.mp4')]
fin_rows = ''.join(f'<tr><td>{n}</td><td>{dur(ROOT / p):.0f}초</td><td><a href="../{p}"><code>{p}</code></a></td></tr>'
                   for n, p in finals)
qa = json.loads((ROOT / '4_테스트/h3_qa/qa_summary.json').read_text(encoding='utf-8'))
n_clip = len(qa)

s0 = sec('s0')
set_h2(s0, '현재 상태 (2026-10-15)')
clear_after_h2(s0)
s0.append(frag(f'''
  <div class="callout ok"><b>완성본 3편 1차 제작 완료.</b> 1080×1920 · 30fps · 영어 1벌 · 국가별 가격 레이어 없음. 영상은 <a href="#s16">16장</a>에서 바로 재생됩니다.</div>
  <div class="tbl"><table><tr><th>영상</th><th>길이 {'<span class="tag t-m">실측</span>'}</th><th>파일</th></tr>{fin_rows}</table></div>
  <div class="tbl"><table>
    <tr><th>단계</th><th>상태</th><th>결과</th><th>보는 곳</th></tr>
    <tr><td>캐릭터</td><td>{T_OK}</td><td>R3 확정 → 시트·마스터 프레임</td><td><a href="#s5">5장</a></td></tr>
    <tr><td>대본</td><td>{T_OK}</td><td>v3 그대로 (일부 문장은 근거 부족으로 바꿔 생성)</td><td><a href="#s3">3장</a> · <a href="#s15">15-3</a></td></tr>
    <tr><td>보이스</td><td>{T_WAIT}</td><td>A로 생성 완료, 사람 청취 확인 전</td><td><a href="#s15">15-2</a></td></tr>
    <tr><td>호스트 영상 (MiniMax H3)</td><td>{T_OK}</td><td>{n_clip}/{n_clip}클립, 탈락 7클립 재생성 포함</td><td><a href="#s15">15-0 · 15-5</a></td></tr>
    <tr><td>화면 밖 목소리 (T2A V/O)</td><td>{T_OK}</td><td>23줄</td><td><a href="#s15">15-6</a></td></tr>
    <tr><td>빛 반짝임 보완</td><td>{T_OK}</td><td>프롬프트 조항 + 튄 프레임 교체</td><td><a href="#s16">16-1</a></td></tr>
    <tr><td>로고</td><td>{T_WAIT}</td><td>공식 영상에서 추출해 사용, 원본 파일 받으면 교체</td><td><a href="#s16">16-2</a></td></tr>
    <tr><td>배너 8종 · 영상용 그래픽</td><td>{T_OK}</td><td>Pretendard + 로고</td><td><a href="#s16">16-3 · 16-4</a></td></tr>
    <tr><td>시연 소스 배정</td><td>{T_OK}</td><td>공식 상세페이지 영상, 원본 소리 제거</td><td><a href="#s16">16-5</a></td></tr>
    <tr><td>RA 검토</td><td>{T_WAIT}</td><td>화면 문구 RA 대상 + 대본 RA 표시 문장</td><td><a href="#s16">16-7</a> · <a href="#s3">3장</a></td></tr>
    <tr><td>국가별 가격·사은품 레이어</td><td>{T_TODO}</td><td>R1~R3 회신 후 제작</td><td><a href="#s13">13장</a></td></tr>
  </table></div>
  <p class="small">전체 제작 구조(어떤 모델·스크립트가 어떤 순서로 도는지)는 <a href="#s7">7-0 아키텍처·워크플로우</a>에 한 장으로 정리했습니다.</p>
  <p class="small">확인 요청 목록은 <a href="#s16">16-8</a>, 받아야 할 자료는 <a href="#s13">13장</a>에 모았습니다. <b>2026-10-15 말 속도</b>: 완성본·미리보기 영상은 1.25배속으로 다시 만들었고(음높이 유지), 앞으로 생성은 T2A speed 1.25 · H3 대사 속도 약 160단어/분으로 바꿨습니다(H3 실제 속도는 다음 생성 때 실측).</p>
  <details><summary>v4에서 지운 내용 (v3 파일에는 남아 있음)</summary><ul class="small">
    <li>0장 v3 변경 요청 14건 표 → 이 현재 상태 요약으로 교체</li>
    <li>4-1 레이아웃 1차안(회색 실루엣) → 16장 완성본으로 대체</li>
    <li>5장 캐릭터 후보 비교(1차 A~D, 실사 R1~R3), 확정 후 할 일, Host Lock 수치 기록 계획(실행하지 않음 — 클립마다 5프레임 육안 검수로 대신함)</li>
    <li>6장 보이스 비교 청취 절차 → 옵션 표(목소리·조절값)와 실제 쓴 설정으로 다시 정리</li>
    <li>15-1 캐릭터 시트·마스터 프레임 → 5장으로 옮김, 15-0 클립 낱개 카드 → 장면별로 합친 영상(펼치면 낱개)</li>
    <li>7-3 프롬프트 골격(실제 프롬프트는 <code>5_에셋/scripts/h3_production.py</code>), 7-4 생성 물량 추정(실제 {n_clip}클립)</li>
    <li>8장 시연 소스 배정 계획 → 16-5 실제 배정</li>
    <li>9-2 Poppins·Playfair 폰트 → Pretendard로 바꿈, 9-4 1차 배너 이미지(16-3과 중복)</li>
    <li>11장 확정 게이트 → 진행 현황 표</li>
    <li>14장 POC 설명(studio03·04)과 POC 가드 시험 결과 → 대사 이탈 대응 방법만 남김</li>
    <li>16-7 RA 문구 표 → 9-0 이미지마다 아래에 표시, 16-3·16-4 이미지 → 9-0으로 모음</li>
    <li>15장 V1 러프컷(합성 전·미생성 자리표시 포함) → 16장 완성본, 15-8 남은 일 → 16-8로 합침</li>
  </ul></details>'''))

# ── 3. 끝난 조건 문장 ──
for li in sec('s3').find_all('li'):
    if 'VO 전체는 RA 검토 전입니다' in li.get_text():
        li.replace_with(frag('<li>VO는 RA 검토 전에 영상으로 만들었습니다(사용자 지시). RA 결과에 따라 표시 문장이 든 클립만 다시 만듭니다 <span class="tag t-r">RA</span></li>'))

# ── 4. 1차 레이아웃 삭제 ──
s4 = sec('s4')
drop_block(h3_of(s4, '4-1.'))
s4.append(frag('<p class="small">위 영역은 레퍼런스 1프레임 기준의 계획값입니다. 실제 합성 위치(호스트 340px 아래로, 시연 창 x20·y880, 카드 34~68%)는 <a href="#s16">16장</a>.</p>'))

# ── 5. 캐릭터: 후보 비교 삭제 ──
s5 = sec('s5')
set_h2(s5, '캐릭터 — R3 확정 <span class="tag t-u">사용자 확인</span>')
r3_keep = h3_of(s5, '5-3.')
for c in list(s5.find_all(recursive=False)):
    if c.name == 'h2':
        continue
    if c is r3_keep:
        break
    c.decompose()
r3_keep.string = '5-1. 세트·제품'
r3_keep.insert_before(frag(
    '<p>2026-10-14 <b>R3</b>(둥근 얼굴·처진 눈매·소프트브라운 끝 웨이브, 실사 피부 표현)로 확정했습니다. '
    'gpt-image-1.5로 정면 후보를 만든 뒤, R3 정면을 레퍼런스로 각도·표정·손 시트와 H3 첫 프레임(마스터)을 만들었습니다(아래). '
    '가상 인물이며 실존 인물 레퍼런스는 쓰지 않았습니다. 실존 인물 닮음 확인은 하지 않았습니다 <span class="tag t-x">미확인</span>.</p>'
    '<p class="small">후보 기록: <code>4_테스트/character/</code> (CS-00 A~D, CS-00R R1~R3)</p>'))

# ── 6. 음성: 후보 삭제 ──
s6 = sec('s6')
set_h2(s6, '음성 — 보이스 A로 진행')
for c in list(s6.find_all(recursive=False)):
    if c.name == 'h3' and c.get_text(strip=True).startswith('6-3.'):
        break
    if c.name != 'h2':
        c.decompose()
h63 = h3_of(s6, '6-3.')
h63.string = '6-2. 보이스 보존'
h63.insert_before(frag('''
  <p>MiniMax Voice Design으로 만든 전용 보이스 <b>A</b>를 썼습니다. 설명 프롬프트: <i>Bright, youthful female voice in her early twenties, like a friendly K-pop idol hosting a live beauty show in English…</i>
  아직 사람이 듣고 확정하지 않았습니다 <span class="tag t-x">청취 전</span> — 바꾸면 H3 호스트 클립 전부를 다시 만들어야 합니다. 미리듣기는 <a href="#s15">15-2</a>.</p>
  <h3>6-1. 실제 쓴 T2A 설정 <span class="tag t-m">실측</span></h3>
  <div class="tbl"><table>
    <tr><th>항목</th><th>값</th></tr>
    <tr><td>model</td><td><code>speech-2.8-hd</code></td></tr>
    <tr><td>language_boost</td><td>English</td></tr>
    <tr><td>speed / pitch / vol</td><td>0.95 / 0 / 1 (지금까지) → 앞으로 speed <b>1.25</b></td></tr>
    <tr><td>emotion</td><td>happy (시연 설명 줄은 calm)</td></tr>
    <tr><td>출력</td><td>wav 32kHz mono</td></tr>
  </table></div>
  <p class="small">출처: <code>5_에셋/scripts/minimax_voice.py</code>. 발음 사전은 쓰지 않았고, 호수 숫자는 대본에 "oh-five"처럼 발음대로 적었습니다(15-3).</p>'''))

# ── 7. 프롬프트 골격·물량 추정 삭제 ──
s7 = sec('s7')
drop_block(h3_of(s7, '7-3.'))
drop_block(h3_of(s7, '7-4.'))
s7.append(frag('<p class="small">실제 H3 프롬프트(조명 고정 조항 포함)는 <code>5_에셋/scripts/h3_production.py</code>, 실제 물량은 호스트 클립 {0}개·V/O 23줄(15-3).</p>'.format(n_clip)))

# ── 8. 시연 배정 계획 → 16-5 ──
s8 = sec('s8')
set_h2(s8, '시연 소스')
clear_after_h2(s8)
s8.append(frag('<p>이미 받은 공식 상세페이지 영상(<code>5_에셋/이미지생성_소스/</code>)만 썼습니다. 원본 소리는 빼고, 배속·발색 보정은 하지 않았습니다. 장면별 실제 배정과 확인 결과는 <a href="#s16">16-5</a>.</p>'))

# ── 9. 폰트·1차 배너 ──
s9 = sec('s9')
h92 = h3_of(s9, '9-2.')
h92.string = '9-2. 폰트 — Pretendard (2026-10-15 변경)'
for c in list(h92.find_next_siblings()):
    if c.name == 'h3':
        break
    c.decompose()
h92.insert_after(frag('''<div class="tbl"><table>
    <tr><th>용도</th><th>폰트</th><th>라이선스</th></tr>
    <tr><td>배너·영상 그래픽·자막 전부</td><td>Pretendard Medium / SemiBold / Bold / ExtraBold / Black</td><td>SIL OFL 1.1 (라이선스 파일 동봉)</td></tr>
    <tr><td>BANILA CO 로고</td><td>폰트로 쓰지 않음 — 공식 영상에서 추출한 로고 이미지 (16-2)</td><td>—</td></tr>
  </table></div>
  <p class="small">사용자 요청으로 v3의 Poppins·Playfair Display를 Pretendard로 바꿨습니다. 폰트 파일: <code>5_에셋/banner/fonts/</code></p>'''))
h94 = h3_of(s9, '9-4.')
h94.string = '9-4. 1080×1920 배너 — 만든 기준 (완성 이미지는 16-3)'
for c in list(h94.find_next_siblings()):
    if c.name == 'h3':
        break
    if c.name == 'div' and 'shots' in (c.get('class') or []):
        c.decompose()

# ── 11. 확정 게이트 → 진행 현황 ──
s11 = sec('s11')
set_h2(s11, '진행 현황')
clear_after_h2(s11)
s11.append(frag(f'''<div class="tbl"><table>
    <tr><th>단계</th><th>작업</th><th>상태</th></tr>
    <tr><td>①</td><td>캐릭터 후보 → R3 확정</td><td>{T_OK}</td></tr>
    <tr><td>②</td><td>스토리보드 v3 확정</td><td>{T_OK} (RA 검토는 {T_WAIT})</td></tr>
    <tr><td>③</td><td>보이스 A 생성</td><td>{T_OK} (사람 청취 {T_WAIT})</td></tr>
    <tr><td>④</td><td>배너 8종 (v2 Pretendard)</td><td>{T_OK}</td></tr>
    <tr><td>⑤</td><td>시트 · 마스터 프레임</td><td>{T_OK}</td></tr>
    <tr><td>⑥</td><td>V/O T2A 23줄</td><td>{T_OK}</td></tr>
    <tr><td>⑦</td><td>H3 클립 {n_clip}개 → ASR 대사 가드 → 육안 검수 → 탈락분 재생성</td><td>{T_OK}</td></tr>
    <tr><td>⑧</td><td>시연 소스 확인·배정</td><td>{T_OK}</td></tr>
    <tr><td>⑨</td><td>편집 3편 (영어 1벌)</td><td>{T_OK}</td></tr>
    <tr><td>⑩</td><td>국가 레이어 4벌 (TH·MY·ID·VN)</td><td>{T_TODO} R1~R3</td></tr>
    <tr><td>⑪</td><td>사람 최종 검수 → 60초 컷다운 1편씩</td><td>{T_WAIT}</td></tr>
  </table></div>'''))

# ── 3. 장면마다 영상 + 대본은 토글 ──
prev = json.loads((ROOT / '4_테스트/html_preview/index.json').read_text(encoding='utf-8'))
s3 = sec('s3')


def player(src, cap):
    return frag(f'<div class="fv"><video controls preload="metadata" playsinline src="../{src}#t=0.1"></video><div>{cap}</div></div>')


def fold_last_tbl(h3, label):
    tbls = []
    for c in h3.find_next_siblings():
        if c.name in ('h3', 'h2'):
            break
        if c.name == 'div' and 'tbl' in (c.get('class') or []):
            tbls.append(c)
    t = tbls[-1]
    d = b.new_tag('details')
    sm = b.new_tag('summary')
    sm.string = label
    d.append(sm)
    t.insert_before(d)
    d.append(t.extract())


SPEED_F = json.loads((ROOT / '4_테스트/edit_seg/final_meta.json').read_text(encoding='utf-8'))['speed']
CH_NAME = {'OC': '공통 오프닝', 'EC': '공통 엔딩', 'O-P': '오프닝', 'O-L': '오프닝', 'O-B': '오프닝',
           'P1': '고민 공감', 'P2': '루틴 4단계', 'P3': 'Sun Base', 'P4': 'Classic', 'P5': 'Finish Powder', 'P6': 'Setting Fixer',
           'P7': '피부 타입 팁', 'P8': '혜택', 'L0': '오늘의 룩', 'L1': 'USP① 립·치크 한 자루', 'L2': 'USP② 텍스처',
           'L3': 'USP③ 빌더블', 'L4': '립 바르기 · USP④ 스틱', 'L5': '호수별 발색 12색', 'L6': 'USP⑤ 퍼스널컬러 트리오',
           'L7': '상황별 추천', 'L8': 'Buy 2 Get 1', 'C1': '하루 끝 고민', 'C2': '제형 시연', 'C3': 'Original',
           'C4': 'Pore Clarifying', 'C5': 'Calming', 'C6': '내 피부엔 어떤 밤?', 'C7': '사용법 3단계', 'C8': '사이즈', 'C9': '혜택'}


def mmss(t):
    return f'{int(t // 60)}:{t % 60:04.1f}'


def chapters_html(chs):
    """chs = [(시작초, 라벨)] → 누르면 같은 카드의 영상이 그 지점으로 이동하는 버튼 목록"""
    return ('<div class="chap"><span class="small">구간 (누르면 그 지점으로 이동)</span><ol>'
            + ''.join(f'<li><button type="button" class="seek" data-t="{t:.2f}"><b>{mmss(t)}</b> {html.escape(lab)}</button></li>' for t, lab in chs)
            + '</ol></div>')


def final_chapters(vid):
    """편집 세그먼트 실제 길이(out_seconds)를 누적해 장면별 시작 시각을 낸다."""
    log = json.loads((ROOT / f'4_테스트/edit_seg/{vid}/edit_log.json').read_text(encoding='utf-8'))
    t, out, last = 0.0, [], None
    for r in log:
        sid = r['id'].split('_', 1)[1]
        if sid.startswith(('OC', 'EC')):
            key = sid[:2]
        elif sid.startswith('O-'):
            key = sid.split('_')[0]
        else:
            key = sid.split('-')[0].split('_')[0]
        if key != last:
            out.append((t / SPEED_F, f'{key} {CH_NAME.get(key, "")}'.strip()))
            last = key
        t += r['out_seconds']
    return out, t / SPEED_F


h30 = h3_of(s3, '3-0.')
tbl30 = next(c for c in h30.find_next_siblings() if c.name == 'div' and 'tbl' in (c.get('class') or []))
rows = tbl30.find_all('tr')
head = str(rows[0])
oc_rows = ''.join(str(r) for r in rows if r.find('td') and r.find('td').get_text(strip=True).startswith('OC'))
ec_rows = ''.join(str(r) for r in rows if r.find('td') and r.find('td').get_text(strip=True).startswith('EC'))
assert oc_rows.count('<tr') == 3 and ec_rows.count('<tr') == 3
blocks = ''
for part, title, rws in (('OC', '공통 오프닝 — OC-1~3', oc_rows), ('EC', '공통 엔딩 — EC-1~3', ec_rows)):
    cm = prev['common'][part]
    chs = [(c['start'], c['id'].replace('COMMON_', '')) for c in cm['clips']]
    blocks += (f'<h4>{title}</h4><div class="fv"><video controls preload="metadata" playsinline src="../{cm["file"]}#t=0.1"></video>'
               f'<div><b>{title}</b> ({cm["seconds"]:.0f}초)<br><span class="small">완성본(V1)에서 해당 구간만 이어 붙인 것입니다. '
               f'상단 헤드라인은 V1용이고, V2·V3에서는 헤드라인{"과 엔딩 카드" if part == "EC" else ""}만 바뀝니다.</span>'
               f'{chapters_html(chs)}</div></div>'
               f'<details><summary>대본 보기 ({title})</summary><div class="tbl"><table>{head}{rws}</table></div></details>')
tbl30.replace_with(frag(blocks))

# 자막·AI 표기 (확정 결과만)
ul30 = h30.find_next_sibling('ul')
ul30.insert_after(frag(f'''
  <h4>자막 — B 외곽선 36px (확정)</h4>
  <div class="callout ok"><b>선택 반영 (2026-10-15 사용자)</b> — 자막은 <b>B(외곽선, 상자 없음)</b>로 바꿨습니다. 글자 크기는 기존 자막(42px)보다 15% 작은 <b>36px</b>입니다(42×0.85=35.7). 글꼴 Pretendard ExtraBold, 흰 글자에 진한 테두리(#2B1F25) 3px와 아래쪽 그림자를 넣었고, 줄 간격은 시안 B의 비율대로 47px입니다. 위치는 그대로입니다(자막 아래 끝 약 1458px). 완성본 3편을 다시 렌더했습니다.</div>
  <div class="shots"><figure class="shot"><a href="../4_테스트/caption_proposal/applied_caption_B36.jpg"><img loading="lazy" src="../4_테스트/caption_proposal/applied_caption_B36.jpg" alt="자막 B 반영 결과"></a><figcaption><b>반영 결과</b> — 완성본에서 뽑은 프레임 (왼쪽부터 호스트 화면 · 호스트+측면 카드 · 전체 화면 카드)</figcaption></figure></div>
  <h4>"AI-generated host" 배지 — 우측 상단 (확정)</h4>
  <div class="callout ok"><b>선택 반영 (2026-10-15 사용자)</b> — <b>배지 2(화이트 + 핑크 테두리)</b>를 우측 상단 맨 위(y 48px)에 두고, 제품 헤드라인(BANILA CO | 제품명)도 그 바로 아래(y 116px)로 함께 올렸습니다. 자막 아래에 있던 작은 "AI-generated host" 문구는 이 배지로 바꿨습니다. 완성본 3편(16장)에 적용해 다시 렌더했습니다. 이 자리는 Shopee 앱 상단 UI(세로 0~33%) 안이라 시청자 수·닫기 버튼 등에 가려질 수 있습니다 <span class="tag t-x">실제 앱 화면에서 확인 필요</span>.</div>
  <div class="shots"><figure class="shot"><a href="../4_테스트/caption_proposal/applied_badge2_top.jpg"><img loading="lazy" src="../4_테스트/caption_proposal/applied_badge2_top.jpg" alt="반영 결과"></a><figcaption><b>반영 결과</b> — V1 완성본에서 뽑은 프레임 (호스트 화면)</figcaption></figure></div>
  <p class="small">2026-10-16 사용자 요청으로 자막·배지 후보 시안 비교는 지웠습니다(시안 이미지는 <code>4_테스트/caption_proposal/</code>에 남아 있음).</p>'''))

# 3-1~3-3 완성본 + 구간
for pre, (name, path), vid in zip(('3-1.', '3-2.', '3-3.'), finals, ('V1', 'V2', 'V3')):
    h = h3_of(s3, pre)
    chs, _ = final_chapters(vid)
    h.insert_after(player(path, f'<b>{name} 완성본</b> ({dur(ROOT / path):.0f}초)<br><span class="small">'
                              f'<code>{path}</code> · 줄별 화면 유형·자막은 <a href="#s16">16-0</a></span>{chapters_html(chs)}'))
    fold_last_tbl(h, '대본 보기 (장면별 VO 초안 · 근거·주의)')

# 16-0 완성본에도 같은 구간 버튼 + 타임라인 시작 시각을 누르면 이동
for fv in sec('s16').find_all('div', class_='fv'):
    src = fv.find('video')['src']
    vid = next((v for v, (_, pth) in zip(('V1', 'V2', 'V3'), finals) if pth in src), None)
    if not vid:
        continue
    chs, _ = final_chapters(vid)
    fv.find('video').find_next_sibling('div').find('details').insert_before(frag(chapters_html(chs)))
    for tr in fv.find_all('tr')[1:]:
        td = tr.find('td')
        m_, s_ = td.get_text(strip=True).split(':')
        td.string = ''
        td.append(frag(f'<button type="button" class="seek" data-t="{int(m_) * 60 + float(s_):.2f}"><b>{m_}:{s_}</b></button>'))

# ── 5. 캐릭터 시트를 5장으로 옮김 (15-1에서) ──
s15 = sec('s15')
h151 = h3_of(s15, '15-1.')
moved = []
for c in list(h151.find_next_siblings()):
    if c.name in ('h3', 'h2'):
        break
    moved.append(c.extract())
h151.insert_after(frag('<p class="small">캐릭터 시트·마스터 프레임은 <a href="#s5">5장</a>으로 옮겼습니다.</p>'))
h51 = h3_of(s5, '5-1. 세트')
hs = frag('<h3>캐릭터 시트 · 마스터 프레임 (gpt-image-1.5, R3 정면을 레퍼런스로)</h3>')
h51.insert_before(hs)
for c in moved:
    h51.insert_before(c)

# ── 6. 음성 옵션 ──
VOPT = [('A', 'Voice Design (전용)', '설명 문장으로 새로 만든 목소리 — 20대 초반·밝음·또렷한 국제 영어 (아래 프롬프트)', '<span class="tag t-u">사용 중</span> 생성·합성 완료'),
        ('B', 'Voice Design (전용)', 'A + "조금 더 차분하고 부드럽게" (스킨케어 설명 톤)', '안 만듦'),
        ('C', 'Voice Design (전용)', 'A + "조금 더 활기차고 장난스럽게" (팬 라이브 오프닝 톤)', '안 만듦'),
        ('D', 'MiniMax 기본 보이스', '<code>English_radiant_girl</code>', '안 들어 봄'),
        ('E', 'MiniMax 기본 보이스', '<code>English_Upbeat_Woman</code> — 20대 초반보다 나이 들게 들릴 수 있음 (이름으로 짐작)', '안 들어 봄'),
        ('F', 'MiniMax 기본 보이스', '<code>English_LovelyGirl</code> — 너무 귀엽게 들릴 수 있음 (이름으로 짐작)', '안 들어 봄'),
        ('예비', 'MiniMax 기본 보이스', '<code>English_PlayfulGirl</code> · <code>English_Kind-heartedGirl</code> · <code>English_captivating_female1</code> · <code>English_ConfidentWoman</code>', '안 들어 봄')]
vrows = ''.join(f'<tr><td><b>{a}</b></td><td>{b_}</td><td>{c}</td><td>{d}</td></tr>' for a, b_, c, d in VOPT)
h61 = h3_of(s6, '6-1.')
h61.insert_before(frag(f'''
  <h3>보이스 옵션 — 고를 수 있는 목소리</h3>
  <div class="tbl"><table><tr><th>옵션</th><th>종류</th><th>목소리</th><th>상태</th></tr>{vrows}</table></div>
  <p class="small"><b>읽는 법</b> — Voice Design = 문장 설명으로 우리만 쓰는 목소리를 새로 만드는 방식(만든 뒤 7일 안에 한 번 합성해야 보존). 기본 보이스 = MiniMax가 제공하는 목소리로 voice_id만 지정하면 됨. 기본 보이스 설명은 이름에서 짐작한 것이고 들어 보지 않았습니다 <span class="tag t-x">미확인</span>. 다른 옵션으로 바꾸면 V/O 23줄과 H3 호스트 클립 62개를 다시 만들어야 합니다(H3가 이 목소리를 참조해 말하기 때문). 출처: <code>5_에셋/voice/voice_candidates_v1.md</code></p>
  <h3>목소리 조절 옵션 (T2A) <span class="tag t-d">문서</span></h3>
  <div class="tbl"><table><tr><th>옵션</th><th>고를 수 있는 값</th><th>지금 값</th></tr>
    <tr><td>speed (말 속도)</td><td>0.5 ~ 2</td><td><b>1.25</b> (2026-10-15 변경 · 이미 만든 V/O 23줄은 0.95로 합성 → 완성본에서 1.25배속)</td></tr>
    <tr><td>pitch (음높이)</td><td>−12 ~ 12</td><td>0</td></tr>
    <tr><td>vol (음량)</td><td>0 초과 ~ 10</td><td>1</td></tr>
    <tr><td>emotion (감정)</td><td>happy · sad · angry · fearful · disgusted · surprised · calm · fluent · whisper (fluent·whisper는 speech-2.6 계열만)</td><td>happy / 시연 설명 줄 calm</td></tr>
    <tr><td>쉼</td><td>문장 안에 <code>&lt;#0.4#&gt;</code>처럼 0.01~99.99초</td><td>안 씀</td></tr>
    <tr><td>발음 사전</td><td>단어별 발음 지정 (IPA 표기 가능)</td><td>안 씀 — 숫자는 대본에 발음대로 적음</td></tr>
  </table></div>
  <p class="small">출처: MiniMax T2A API 문서(2026-10-13 조회, <code>voice_candidates_v1.md</code>에 기록).</p>'''))
h61.string = '6-1. 실제 쓴 T2A 설정'
for h_ in s6.find_all('h3', recursive=False):
    t_ = h_.get_text(strip=True)
    if t_.startswith('보이스 옵션'):
        h_.string = '6-1. 보이스 옵션 — 고를 수 있는 목소리'
    elif t_.startswith('목소리 조절'):
        h_.clear(); h_.append(frag('6-2. 목소리 조절 옵션 (T2A) <span class="tag t-d">문서</span>'))
    elif t_.startswith('6-1. 실제'):
        h_.clear(); h_.append(frag('6-3. 실제 쓴 T2A 설정 <span class="tag t-m">실측</span>'))
    elif t_.startswith('6-2. 보이스 보존'):
        h_.string = '6-4. 보이스 보존'

# ── 7. 파이프라인 접기 ──
s7 = sec('s7')
d7 = b.new_tag('details')
sm7 = b.new_tag('summary')
sm7.string = '펼쳐 보기 — 계획 당시(v2~v3) 단계표 · 립싱크 제외 결정 (실제와 다른 점은 위 7-0 마지막 표)'
d7.append(sm7)
for c in list(s7.find_all(recursive=False)):
    if c.name != 'h2':
        d7.append(c.extract())
s7.append(d7)

# ── 7-0. 현재 아키텍처·워크플로우 (2026-10-16 사용자 요청, 스크립트·실행 기록 기준) ──
set_h2(s7, '생성 파이프라인 — 아키텍처·워크플로우')
ARCH_STAGES = [  # (번호, 단계, 도구/모델, 과금, 산출물)
    ('A', '대본 → 생성 단위', '<code>build_v3_text.py</code> → <code>build_shotlist.py</code>', '로컬',
     f'<code>5_에셋/production/shotlist_v3.json</code> — 85줄 = 호스트 말하기(h3) {n_clip} · 화면 밖 목소리(vo) 23'),
    ('B', '캐릭터·마스터 프레임', 'OpenAI <b>gpt-image-1.5</b> (R3 정면 사진을 레퍼런스로 편집) · <code>gen_r3_character.py</code> · <code>outpaint_master.py</code>', '유료',
     '<code>5_에셋/character_sheet/R3/</code> — 시트 + <code>R3_MF-01_9x16.png</code>(모든 호스트 클립의 첫 프레임)'),
    ('C', '목소리', 'MiniMax <b>Voice Design</b> 1회 → voice_id · <b>speech-2.8-hd</b> T2A (영어, 속도 1.25, 32kHz mono) · <code>minimax_voice.py</code>', '유료',
     '<code>2_나레이션/voice/host_reference.wav</code>(H3 톤 참조용, 대본에 없는 문장) · <code>2_나레이션/vo/</code> V/O 23개'),
    ('D', '호스트 영상', 'MiniMax <b>MiniMax-H3</b> (2K · 9:16 · 클립별 4~15초 · 음성 동시 생성) · <code>h3_production.py</code> prepare → submit → resume', '유료',
     f'<code>3_소스클립/H3/&lt;ID&gt;/native.mp4</code> + <code>run.json</code> — {n_clip}클립'),
    ('E', '검수', '<code>qa_h3.py</code> = ASR 대사 가드(<b>faster-whisper</b> base·small 두 모델) + 5프레임 컨택트시트 육안', '로컬',
     '<code>4_테스트/h3_qa/</code> — 통과 / 끝 군말 자름(<code>*_cut.mp4</code>) / 탈락 → <code>requeue-rejected</code>로 재생성'),
    ('F', '그래픽', 'HTML/CSS → <b>Playwright</b> 캡처 · Pretendard · 공식 누끼·발색컷만 배치(제품 생성 없음) · <code>build_banners.py</code> · <code>build_edit_gfx.py</code>', '로컬',
     '<code>5_에셋/banner/</code> 배너 · <code>5_에셋/edit_gfx/</code> 전체화면 카드 g_ 24 · 측면 카드 · 오버레이'),
    ('G', '최종 편집', '<b>ffmpeg</b> + PIL · <code>build_final_edit.py</code>', '로컬',
     '<code>1_최종영상/V1·V2·V3_*_v2.mp4</code> (1080×1920 · 30fps · H.264)'),
    ('H', '문서·공유', '<code>build_v3_*.py</code> → <code>build_v4.py</code> (이 문서) · <code>build_share_page.py</code> → <code>dcs-ai-cli app update</code>', '로컬',
     '개발자용 HTML(영상 재생) · dcsai 공유판(영상 대신 장면별 프레임 — QD가 mp4·wav·mp3 업로드를 막음)'),
]
_flow = ''.join(
    f'<div class="ar-st{" paid" if fee == "유료" else ""}"><b>{k}</b><span>{name}</span><em>{fee}</em></div>' + ('<i>→</i>' if k != 'H' else '')
    for k, name, _, fee, _ in ARCH_STAGES)
_rows = ''.join(f'<tr><td><b>{k}</b></td><td>{name}</td><td>{tool}</td><td>{fee}</td><td>{out}</td></tr>'
                for k, name, tool, fee, out in ARCH_STAGES)
ARCH = f'''
<h3>7-0. 현재 아키텍처·워크플로우 (2026-10-16) <span class="tag t-m">실측</span> <span class="tag t-u">사용자 요청</span></h3>
<p class="small">스크립트(<code>5_에셋/scripts/</code>, <code>0_기획/</code>)와 실행 기록(<code>run.json</code>·<code>voice_state.json</code>·<code>shotlist_v3.json</code>)을 읽고 정리했습니다.
<b>유료</b> = 외부 API 호출로 과금되는 단계(분홍), <b>로컬</b> = 이 PC에서만 도는 단계. 모든 유료 제출은 사람 확인 후 실행합니다.</p>
<div class="ar-in"><b>입력</b> 브랜드 제공 자료 <code>5_에셋/이미지생성_소스/</code>(누끼·발색컷·상세페이지 영상) · 제품 USP 브리프 · 10월 더블데이 배너 레퍼런스 · 실무진 회신(13장)</div>
<div class="ar-flow">{_flow}</div>
<div class="ar-split">
 <div><b>호스트가 나오는 줄 (h3, {n_clip}개)</b><br>A 대본 → <b>B 마스터 프레임</b> + <b>C 참조 목소리</b> → D MiniMax-H3가 얼굴·입·목소리를 한 번에 생성 → E 검수 → G 편집. <span class="small">립싱크 단계 없음(7-1).</span></div>
 <div><b>호스트가 안 나오는 줄 (vo, 23개)</b><br>A 대본 → C T2A 목소리만 생성 → G 편집에서 F 그래픽 카드(G 화면) 또는 공식 시연 영상(D 화면) 위에 얹음.</div>
</div>
<div class="tbl"><table><tr><th>#</th><th>단계</th><th>도구·모델 / 스크립트</th><th>과금</th><th>산출물</th></tr>{_rows}</table></div>
<h4>G 최종 편집 안에서 하는 일</h4>
<ol class="small">
 <li>대본 줄 순서대로 화면 유형별 합성 — H 호스트+헤드라인+AI 고지+자막 · H+G 측면 카드 · S 시연 창 · G/G+H 전체화면 카드 · D 공식 시연 영상 전체화면(원본 소리 제거)</li>
 <li>호스트 레이어를 340px 내려 얼굴을 화면 약 44% 높이에 두고, 위 빈 곳은 마스터 프레임 벽으로 채움</li>
 <li>빛 번쩍임 프레임을 직전 프레임으로 교체(deflash, 16-1)</li>
 <li>자막: Pretendard ExtraBold 36px, 상자 없는 외곽선(#2B1F25, 3px) + 그림자</li>
 <li>음량 정규화 loudnorm −16 LUFS → 세그먼트마다 1.25배속(영상 setpts·음성 atempo, 음높이 유지) → 이어 붙여 libx264 CRF 20</li>
</ol>
<h4>안전장치</h4>
<ul class="small">
 <li>H3 제출: <code>submission.lock</code> · 응답이 불명확하면 다시 POST하지 않음 · 키는 파일에서만 읽고 명령·로그에 남기지 않음 (POC <code>official_api.py</code>의 Runner 재사용)</li>
 <li>제품: 생성하지 않음 — 공식 누끼·발색컷·상세페이지 영상만 합성 (PRODUCT LOCK)</li>
 <li>문구: 화장품 범위(세정·사용감·외관)로 제한, 걸릴 소지가 있으면 RA 표시(9-0·3장)</li>
</ul>
<h4>계획(7-2)과 실제가 다른 점</h4>
<div class="tbl"><table><tr><th>계획 당시</th><th>실제</th></tr>
<tr><td>세트 SET-00·마스터 프레임을 따로 만들기</td><td>R3 캐릭터 사진을 9:16으로 아웃페인트한 MF-01 한 장을 모든 클립의 첫 프레임으로 사용</td></tr>
<tr><td>H 클립 → <code>3_소스클립/host/</code>, 채택분만 2K 재생성</td><td>처음부터 2K로 생성해 <code>3_소스클립/H3/</code>에 저장 (host·host_2k 단계 없음)</td></tr>
<tr><td>B-roll(H3) · 시연 소스 9:16 크롭본 → <code>broll/</code>·<code>demo/</code></td><td>B-roll 생성 안 함. 시연은 받은 원본 영상을 편집 단계에서 바로 잘라 씀 (두 폴더는 비어 있음)</td></tr>
<tr><td>영상 3편 × 국가 4벌 = 12본</td><td>영어 공통 3본만 완성. 국가별 가격·사은품 레이어는 실무진 회신 대기(13장)</td></tr>
<tr><td>컷 검사 별도 단계</td><td>E 검수의 5프레임 컨택트시트 육안 확인으로 대신함</td></tr>
</table></div>'''
d7.insert_before(frag(ARCH))
b.head.append(frag('<style>.ar-in{border:1px dashed var(--line);border-radius:10px;padding:8px 12px;margin:10px 0;font-size:13px}'
                   '.ar-flow{display:flex;flex-wrap:wrap;align-items:stretch;gap:6px;margin:10px 0}'
                   '.ar-flow i{align-self:center;font-style:normal;color:var(--muted)}'
                   '.ar-st{flex:1 1 92px;border:1px solid var(--line);border-radius:10px;padding:8px;text-align:center;font-size:13px;display:flex;flex-direction:column;gap:2px}'
                   '.ar-st b{font-size:16px}.ar-st em{font-style:normal;font-size:11px;color:var(--muted)}'
                   '.ar-st.paid{background:rgba(233,87,154,.12);border-color:#E9579A}'
                   '.ar-split{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;margin:10px 0}'
                   '.ar-split>div{border:1px solid var(--line);border-radius:10px;padding:10px;font-size:13px}</style>'))

# ── 15-0. 같은 장면 클립을 한 영상으로, 펼치면 클립 각각 ──
SCN = {'OC': '공통 오프닝', 'EC': '공통 엔딩', 'O-P': '오프닝', 'P1': '고민 공감', 'P3': 'Sun Base', 'P4': 'Classic',
       'P5': 'Finish Powder', 'P6': 'Setting Fixer', 'P7': '피부 타입 팁', 'P8': '혜택',
       'O-L': '오프닝', 'L0': '오늘의 룩', 'L1': 'USP① 립·치크 한 자루', 'L3': 'USP③ 빌더블', 'L4': 'USP④ 스틱·잠금 캡',
       'L6': 'USP⑤ 퍼스널컬러 트리오', 'L7': '상황별 추천', 'L8': 'Buy 2 Get 1',
       'O-B': '오프닝', 'C1': '하루 끝 고민', 'C3': 'Original', 'C4': 'Pore Clarifying', 'C5': 'Calming',
       'C6': '내 피부엔 어떤 밤?', 'C9': '혜택'}
cards_by_id = {}
for vc in s15.find_all('div', class_='vc'):
    if 'rej' in (vc.get('class') or []):
        continue
    code = vc.find('code')
    if code:
        cards_by_id[code.get_text(strip=True)] = vc
grids = s15.find_all('div', class_='vgrid', recursive=False)
assert len(grids) == 4, len(grids)
for g, vid in zip(grids, ('COMMON', 'V1', 'V2', 'V3')):
    new = []
    for gr in [x for x in prev['groups'] if x['video'] == vid]:
        chap = ''.join(f'<button type="button" class="seek" data-t="{c["start"]:.2f}"><b>{int(c["start"] // 60)}:{c["start"] % 60:04.1f}</b> {c["id"]}</button> ' for c in gr['clips'])
        inner = ''.join(str(cards_by_id[c['id']]) for c in gr['clips'])
        new.append(f'<div class="vc"><video controls preload="metadata" playsinline src="../{gr["file"]}#t=0.1"></video>'
                   f'<div class="vm"><b>{gr["scene"]} {SCN.get(gr["scene"], "")}</b> <span class="small">클립 {len(gr["clips"])}개 · {gr["seconds"]:.0f}초</span></div>'
                   f'<div class="vt small">{chap}</div>'
                   f'<details class="each"><summary>클립 각각 보기</summary>{inner}</details></div>')
    g.replace_with(frag(f'<div class="vgrid">{"".join(new)}</div>'))
p150 = h3_of(s15, '15-0.').find_next_sibling('p')
p150.replace_with(frag(
    '<p class="small"><b>읽는 법</b> — 같은 장면의 호스트 클립을 대본 순서대로 한 영상으로 이었습니다(720×1280 미리보기, 완성본과 같이 1.25배속). '
    '카드 아래 시간 버튼은 각 클립이 시작하는 지점이고, 누르면 그 지점으로 이동합니다. <b>클립 각각 보기</b>를 열면 클립별 영상과 판정이 나옵니다 — '
    '<span class="tag t-m">통과</span> 원본 그대로 · <span class="tag t-m">끝 군말 자름</span> 대사 뒤에 붙은 말을 잘라낸 편집본 · '
    '<span class="tag t-x">중간 이탈 자름</span> 중간 구간을 뺀 편집본(낱개 클립은 원본 파일을 1.25배속으로 재생). 합성 전 원소스(호스트만)이며 빛 반짝임 프레임 교체 전입니다 — 교체·합성한 완성본은 '
    '<a href="#s16">16장</a>. 사람이 끝까지 듣는 확인은 <span class="tag t-x">미실시</span>. 만드는 법: '
    '<code>python -X utf8 5_에셋/scripts/build_html_previews.py</code></p>'))
b.head.append(frag('<style id="v4">details.each{margin-top:6px}details.each>summary{font-size:12px;cursor:pointer}'
                   'details.each .vc{border:0;padding:6px 0 0;border-top:1px dashed rgba(128,128,128,.3);border-radius:0;margin-top:6px}'
                   '#s7>details>summary,#s3 details>summary{cursor:pointer;font-weight:600;margin:6px 0}'
                   '.chap{margin-top:10px}.chap ol{list-style:none;margin:4px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:6px}'
                   'button.seek{font:inherit;font-size:12.5px;border:1px solid rgba(233,87,154,.45);background:rgba(233,87,154,.08);color:inherit;'
                   'border-radius:999px;padding:3px 10px;cursor:pointer}button.seek:hover{background:rgba(233,87,154,.2)}button.seek b{color:#E9579A}'
                   'td button.seek{padding:1px 8px}figure.alpha img{background:#9a8f95}.ra{font-size:12px}#s5>details>summary{cursor:pointer;font-weight:600}</style>'))
b.body.append(frag('<script>document.addEventListener("click",function(e){var x=e.target.closest("button.seek");if(!x)return;'
                   'var c=x.closest(".fv,.vc");var v=c&&c.querySelector("video");if(!v)return;v.currentTime=parseFloat(x.dataset.t);'
                   'var p=v.play();if(p&&p.catch)p.catch(function(){});v.scrollIntoView({block:"nearest",behavior:"smooth"});});'
                   'document.querySelectorAll("details.each video").forEach(function(v){v.defaultPlaybackRate=1.25;v.playbackRate=1.25;'
                   'v.addEventListener("loadedmetadata",function(){v.playbackRate=1.25;});});</script>'))

# ── 2026-10-15 2차 요청 ──
import csv as _csv

# 5. 캐릭터 → 토글
s5 = sec('s5')
d5 = b.new_tag('details')
sm5 = b.new_tag('summary')
sm5.string = '펼쳐 보기 — R3 확정 내용 · 캐릭터 시트 · 마스터 프레임 · 세트·제품'
d5.append(sm5)
for c in list(s5.find_all(recursive=False)):
    if c.name != 'h2':
        d5.append(c.extract())
s5.append(d5)

# RA 문구: 이미지 이름별
RA = {}
for fcsv, ki, ti in ((ROOT / '5_에셋/edit_gfx/edit_gfx_copy.csv', 0, 1), (ROOT / '5_에셋/banner/common/banner_copy.csv', 0, 2)):
    for r in list(_csv.reader(open(fcsv, encoding='utf-8-sig')))[1:]:
        if r[-1].startswith('RA') and r[ti] not in RA.setdefault(r[ki], []):
            RA[r[ki]].append(r[ti])
RA_N = sum(len(v) for v in RA.values())


def ra_line(stem):
    k = stem
    if stem.startswith('overlay_headline'):
        k = 'headline'
    xs = RA.get(k, [])
    if not xs:
        return '<span class="small" style="opacity:.7">RA 대상 문구 없음</span>'
    return '<span class="tag t-r">RA</span> ' + ' · '.join(f'<span class="ra">{html.escape(x)}</span>' for x in xs)


def fig(p, cls=''):
    r_ = p.relative_to(ROOT).as_posix()
    return (f'<figure class="shot {cls}"><a href="../{r_}"><img loading="lazy" src="../{r_}" alt="{p.stem}"></a>'
            f'<figcaption><b>{p.stem}</b><br>{ra_line(p.stem)}</figcaption></figure>')


bnr = sorted((ROOT / '5_에셋/banner/common').glob('BNR_*.png'))
gfx_g = sorted((ROOT / '5_에셋/edit_gfx').glob('g_*.png'))
cards = sorted((ROOT / '5_에셋/edit_gfx').glob('card_*.png'))
ovs = sorted((ROOT / '5_에셋/edit_gfx').glob('overlay_*.png'))
s9 = sec('s9')
h91 = h3_of(s9, '9-1.')
h91.insert_before(frag(f'''
  <h3>9-0. 만든 배너·그래픽 전체 — {len(bnr) + len(gfx_g) + len(cards) + len(ovs)}장 (이미지 아래 RA 표시)</h3>
  <div class="callout warn"><b>배너와 영상 화면이 왜 다른가</b> — 배너 8종은 10-13에 10월 더블데이 Shopee 배너(헤드라인·할인이 맨 위)를 기준으로 <b>단독 배너</b>로 먼저 만들었습니다. 10-15에 영상에 넣으려고 보니 위쪽 0~33%는 Shopee 앱 UI가 덮는 자리라(4장), 배너를 고치지 않고 <b>영상용 카드를 따로</b> 34~68% 안에 다시 그렸습니다. 그 결과 같은 제품·문구가 두 가지 레이아웃으로 갈렸습니다. 처음부터 4장 안전 영역 하나로 디자인했어야 했고, 계획에서 이 점을 놓쳤습니다.<br>
  <b>다시 만들 때 제안</b> <span class="tag t-p">제안</span> — 영상 카드 레이아웃(안전 영역 34~68%) 하나로 통일하고, 배너 8종도 같은 틀로 다시 렌더 → 배너 = 영상 G 화면 그대로. 단독 배너가 따로 필요한 지면(Shopee 배너 규격, R7)이 있으면 그 규격을 받은 뒤 같은 디자인으로 크기만 맞춥니다. 방향을 정해 주시면 진행합니다.</div>
  <p class="small"><b>읽는 법</b> — 이미지 아래 <span class="tag t-r">RA</span>는 RA·법무 사전검토가 필요한 화면 문구(총 {RA_N}개)입니다. 효능은 세정·사용감·외관 범위로만 썼고, 걸릴 소지가 있는 문구만 표시했습니다. 제품은 공식 누끼, 발색은 공식 발색컷이며 생성하지 않았습니다. 이미지를 누르면 원본 크기로 봅니다.</p>
  <h4>① 배너 8종 (단독 배너 레이아웃, 1080×1920)</h4>
  <div class="shots">{''.join(fig(p) for p in bnr)}</div>
  <h4>② 영상 전체 화면 카드 {len(gfx_g)}장 (영상 G 화면, 내용 34~68%)</h4>
  <p class="small">2026-10-15 다시 디자인 — 레퍼런스 <code>10월 더블데이 배너(RM).jpg</code>의 노트·스크랩북 톤(스프링 노트, 찢은 메모지 제목, 핑크 테이프·형광펜, 모눈종이 칸, 핑크 숫자 블록)으로 바꿨습니다. 로고는 핑크 둥근 테두리를 없애고 검정으로 넣었습니다. V1 P4-4·V3 C7은 제품을 왼쪽 네모 칸 안에 넣고 단계 4개를 오른쪽에 세웠습니다. 영상 3편도 새 카드로 다시 렌더했습니다.<span class="dev-only"> 이전 카드: <code>4_테스트/gfx_before_scrapbook/</code></span></p>
  <div class="shots">{''.join(fig(p) for p in gfx_g)}</div>
  <h4>③ 측면 카드 {len(cards)}장 · 오버레이 {len(ovs)}장 (투명 PNG — 호스트 화면 위에 얹음, 여기서는 회색 바탕에 표시)</h4>
  <div class="shots">{''.join(fig(p, 'alpha') for p in cards + ovs)}</div>
  <p class="small">파일: <code>5_에셋/banner/common/</code> · <code>5_에셋/edit_gfx/</code> · 문구 목록 <code>banner_copy.csv</code> · <code>edit_gfx_copy.csv</code></p>'''))

# 16. 배너·그래픽 이미지는 9-0으로, RA 표는 삭제
s16 = sec('s16')
for pre in ('16-3.', '16-4.', '16-7.'):
    h_ = h3_of(s16, pre)
    keep = pre != '16-7.'
    title = {'16-3.': '16-3. 배너 v2 — Pretendard + 정식 로고', '16-4.': '16-4. 영상용 그래픽'}.get(pre)
    nxt = h_.find_next_sibling()
    while nxt is not None and nxt.name not in ('h3', 'h2'):
        n2 = nxt.find_next_sibling(); nxt.decompose(); nxt = n2
    if keep:
        h_.insert_after(frag('<p class="small">이미지 전체와 RA 표시는 <a href="#s9">9-0</a>으로 옮겼습니다.'
                             + (' 배너는 Poppins·Playfair → Pretendard(SIL OFL)로 바꾸고 상단에 로고를 넣었습니다. 이전판: <code>4_테스트/banner_v1_poppins/</code>.' if pre == '16-3.' else
                                ' 배너는 위쪽 0~33%에 핵심 문구가 있어 영상에는 같은 디자인으로 34~68% 안에 둔 판을 따로 만들었습니다(9-0 설명). 재생성 <code>python -X utf8 5_에셋/scripts/build_edit_gfx.py</code>') + '</p>'))
    else:
        h_.decompose()
for td in s16.find_all('td'):
    if '16-7' in td.get_text():
        td.clear()
        td.append(frag(f'화면 문구 RA 대상 {RA_N}개(<a href="#s9">9-0</a> 이미지 아래 표시)와 대본 RA 표시 문장(3장) 검토 — 결과에 따라 해당 클립·카드만 다시 만듦 <span class="tag t-r">RA</span>'))
rd = s16.find('p', class_='small')
rd.append(frag(' <b>2026-10-15 사용자 요청으로 완성본 전체를 1.25배속</b>(음높이 유지, 세그먼트마다 배속 후 연결)했습니다. 1배속 이전판: <code>4_테스트/final_v1_1x/</code>.'))

# 13. 실무진 요청 상세
R13 = [
    ('R1', '국가별 가격', 'TH·MY·ID·VN 각각, SKU별 <b>정가 · 판매가 · 통화 · 할인율</b> — 프라이머 4종, 립앤치크 12색, 클렌징밤 3종 × 국가별 판매 사이즈(25/50/100/180ml 중 무엇을 파는지)', '엑셀·CSV 한 장 (국가 | SKU | 용량 | 정가 | 판매가 | 통화)', '배너·혜택 카드의 국가 레이어(지금 비어 있음), V3 C8 사이즈 카드', '할인율(50% OFF · Buy 2 Get 1)만 표기, 가격 숫자 없음', '채널·영업'),
    ('R2', '사은품', '품명(영문), <b>고해상도 누끼 PNG</b>, 증정 조건(구매액·품목), 소진 시 대체품과 안내 문구', '이미지 + 한 줄 설명', '혜택 카드·배너의 "+ FREE GIFT" 자리 (지금은 일반 선물 아이콘)', '일반 "FREE GIFT" 아이콘만', '채널·영업'),
    ('R3', 'Buy 2 Get 1 조건', '무료 1개를 고르는 범위(12색 중 아무거나? 같은 가격대만?), 다른 할인과 중복 여부, 1인 구매 한도, 기간', '문장', 'V2 L8 카드·배너, 대사 "buy two, get one"', '"Buy 2 Get 1"만 표기, 조건 문구 없음', '채널'),
    ('R4', 'RA 표현 승인', '① 대본의 RA 표시 문장(3장) ② 화면 문구 RA 대상(9-0 이미지 아래) ③ 패키지 인쇄 문구 SPF50+ PA++++·24H의 국가별 표기 가능 여부 ④ "AI-generated host" 고지 문구·위치', '승인 / 수정 문구', '대사·자막·배너·카드 전부', '이미 영상에 들어가 있음 → 수정 나오면 해당 클립·카드만 재생성', 'RA'),
    ('R5', '누락 누끼', '클렌징밤 오리지널 <b>고해상도</b> PNG(지금 1000px), 카밍 50ml 정면, 180ml 3종, 립앤치크 09·14·20호 단품', '투명 PNG, 긴 변 2000px 이상', '진열·배너·카드', '있는 누끼로 대체 (오리지널은 저해상도)', '디자인'),
    ('R6', '립앤치크 표기', '12색 <b>영문 컬러명</b>(지금 번호만), 국가별 품절 컬러, B. by BANILA 편에 BANILA CO 로고를 써도 되는지', '표 + 예/아니오', 'V2 L5 발색 카드·배너, V2 로고', '번호만 · BANILA CO 로고 사용 중', 'BM·채널'),
    ('R7', 'Shopee 규격', '4개국 <b>라이브 화면 캡처 각 1장</b>(앱 UI가 덮는 범위 확인용), 배너·라이브 커버 크기·용량·형식, AI 생성 콘텐츠 표기 규정', '캡처 + 규격 문서', '안전 영역·AI 배지 위치(3-0 시안)·배너 크기', '레퍼런스 1프레임 실측값(상단 0~33%, 하단 78~100%)으로 배치', '채널'),
    ('R8', '채팅 응대', 'EC "질문은 채팅에 남겨 주세요" 뒤 실제 응대 담당·채널·응답 시간, 자주 오는 질문 5개', '문장', 'EC-3 멘트, FAQ 장면', '"Leave it in the chat"까지만 말함 (답변 약속 문구 뺌)', '채널·CS'),
    ('R9', '정식 로고 원본', 'BANILA CO 로고 AI·SVG·PNG', '벡터 파일', '배너·카드·영상 전체의 로고', '공식 영상 엔드카드에서 추출한 로고 사용(16-2)', 'BM'),
    ('R10', '시연 영상 모델 초상권', '프라이머 시연 영상(선베이스·클래식·파우더)에 나오는 모델의 해외 4개국 Shopee 사용 가능 여부', '예/아니오', 'V1 P3·P4·P5 시연 창', '사용 중 — 불가면 해당 구간을 카드로 대체', 'BM·법무'),
    ('R11', '행사명·방송 일정', '11월 행사명(확정 시), 국가별 방송 일정', '문장', '배너 상단 문구', '행사명·날짜 문구 없음', '채널'),
]
rows13 = ''.join(f'<tr><td style="white-space:nowrap"><b>{a}</b></td><td><b>{b_}</b></td><td>{c}</td><td>{d}</td><td>{e}</td><td>{f}</td><td>{g}</td></tr>' for a, b_, c, d, e, f, g in R13)
s13 = sec('s13')
set_h2(s13, '실무진 요청사항 · 문의사항 (상세)')
t13 = s13.find('div', class_='tbl', recursive=False)
t13.replace_with(frag(f'''<p class="small"><b>읽는 법</b> — 한 줄 = 받아야 할 자료 하나. "받기 전까지"는 자료 없이 지금 영상·배너에 어떻게 처리해 두었는지입니다. 담당은 제안이며, 자료는 <code>5_에셋/이미지생성_소스/</code>에 넣어 주시면 됩니다. 세금 각주(T)는 아래 펼치기.</p>
  <div class="tbl"><table><tr><th>#</th><th>요청</th><th>구체적으로 필요한 것</th><th>형식</th><th>쓰이는 곳</th><th>받기 전까지</th><th>담당</th></tr>{rows13}
  <tr><td><b>T</b></td><td><b>세금 각주</b></td><td>국가별 판매 주체(현지 로컬 셀러 / Shopee 크로스보더)와 Shopee 화면 가격이 세금 포함가인지</td><td>문장 + 결제 화면 캡처</td><td>배너 가격 각주</td><td>각주 자리 비움</td><td>현지 재무·채널</td></tr></table></div>'''))
for p_ in s13.find_all('p', class_='small', recursive=False):
    if 'v2의 R7' in p_.get_text() or p_.get_text(strip=True).startswith('자료는'):
        p_.decompose()

# 14. POC 설명 삭제 → 대사 이탈 대응만
s14 = sec('s14')
set_h2(s14, '대사 이탈 대응 — ASR 대사 가드')
for c in list(s14.find_all(recursive=False)):
    if c.name == 'h2':
        continue
    if c.name == 'h3' and c.get_text(strip=True).startswith('14-1.'):
        break
    c.decompose()
drop_block(h3_of(s14, '14-2.'))
h141 = h3_of(s14, '14-1.')
h141.clear(); h141.append(frag('14-1. 막기 → 잡기 → 덜어내기'))

# ── 17. 영상 생성 비용 (맨 아래) — 생성 기록(run.json · usage)에서 다시 집계 ──
# 단가: platform.minimax.io/docs/pricing/overview · developers.openai.com/api/docs/pricing (2026-10-15 조회)
H3_RATE = 0.13            # MiniMax-H3 2K, $/초
T2A_RATE = 100 / 1e6      # speech-2.8-hd, $/자
VD_VOICE = 3.0            # Voice Design, 보이스 1개(처음 T2A에 쓸 때 과금)
VD_PREVIEW = 60 / 1e6     # Voice Design 미리듣기 합성, $/자
IMG = {'ti': 5, 'ii': 8, 'to': 10, 'io': 32}  # gpt-image-1.5, $/100만 토큰

h3_tasks = {}
for f in ROOT.rglob('run.json'):
    r = json.loads(f.read_text(encoding='utf-8'))
    if r.get('task_id'):
        h3_tasks[r['task_id']] = (f.relative_to(ROOT).as_posix(), r)
by_vid, n_fail, s_fail = {}, 0, 0
for path, r in h3_tasks.values():
    d = r['settings']['duration']
    if r.get('status') == 'failed':
        n_fail += 1; s_fail += d
        continue
    if not r.get('generation_completed'):
        continue
    if 'h3_pilot_v' in path:
        key = '파일럿'
    else:
        key = r['scene'].split('_')[0]  # COMMON / V1 / V2 / V3
    kind = 'rej' if 'h3_rejected' in path else 'use'
    v = by_vid.setdefault(key, {'use': [0, 0], 'rej': [0, 0]})
    v[kind][0] += 1; v[kind][1] += d
h3_secs = sum(v['use'][1] + v['rej'][1] for v in by_vid.values())
h3_cost = h3_secs * H3_RATE
n_use = sum(v['use'][0] for k, v in by_vid.items() if k != '파일럿')
s_use = sum(v['use'][1] for k, v in by_vid.items() if k != '파일럿')
s_rej = sum(v['rej'][1] for v in by_vid.values())
s_pil = by_vid.get('파일럿', {'use': [0, 0]})['use'][1]

img_rows, img_files = [], []
for f in ROOT.rglob('generation_log.json'):
    for e in json.loads(f.read_text(encoding='utf-8')):
        u = e.get('usage')
        if not u:
            continue
        i_, o_ = u.get('input_tokens_details') or {}, u.get('output_tokens_details') or {}
        img_rows.append((i_.get('image_tokens', 0) * IMG['ii'] + i_.get('text_tokens', 0) * IMG['ti']
                         + o_.get('image_tokens', u['output_tokens']) * IMG['io'] + o_.get('text_tokens', 0) * IMG['to']) / 1e6)
        img_files.append(Path(str(e.get('file', '')).replace('\\', '/')).name)
img_cost = sum(img_rows)
# 제작에 실제 쓴 이미지: R3 얼굴이 된 후보(CS-00R_3) + R3 시트 3장 + 마스터 원본(9:16 크롭해 H3 첫 프레임). 아웃페인트 결과(R3_MF-01_9x16 덮어쓰기 전 판)는 폐기(15-1)
IMG_USED = {'CS-00R_3.png', 'R3_sheet_turnaround.png', 'R3_sheet_expressions.png', 'R3_sheet_hands.png', 'R3_MF-01_master.png'}
img_used = sum(c for c, f in zip(img_rows, img_files) if f in IMG_USED)
n_img_used = sum(1 for f in img_files if f in IMG_USED)

vstate = json.loads((ROOT / '2_나레이션/voice/voice_state.json').read_text(encoding='utf-8'))
vo_chars = sum(x['usage_characters'] for x in json.loads((ROOT / '2_나레이션/vo/vo_log.json').read_text(encoding='utf-8')).values())
import ast as _ast
_ri = vstate['reference_info']
ref_chars = (_ri if isinstance(_ri, dict) else _ast.literal_eval(_ri))['usage_characters']
prev_chars = len(vstate['preview_text'])
voice_cost = VD_VOICE + prev_chars * VD_PREVIEW + (ref_chars + vo_chars) * T2A_RATE
total = h3_cost + img_cost + voice_cost

VNAME = {'COMMON': '세 편 공통 (오프닝·엔딩)', 'V1': 'V1 Prime Primer', 'V2': 'V2 Romantic Blush Lip &amp; Cheek',
         'V3': 'V3 Clean it Zero', '파일럿': '파일럿 v0·v1 (시험 생성, 폐기)'}
FIN = {'V1': '1_최종영상/V1_PrimePrimer_AI라이브_v2.mp4', 'V2': '1_최종영상/V2_RomanticBlushLipCheek_AI라이브_v2.mp4',
       'V3': '1_최종영상/V3_CleanItZero_AI라이브_v2.mp4'}
vrows = ''
for k in ('COMMON', 'V1', 'V2', 'V3', '파일럿'):
    v = by_vid.get(k)
    if not v:
        continue
    s_ = v['use'][1] + v['rej'][1]
    fin = f'{dur(ROOT / FIN[k]):.0f}초' if k in FIN else ('3편에 재사용' if k == 'COMMON' else '—')
    rej = f'{v["rej"][0]}클립 {v["rej"][1]}초' if v['rej'][0] else '—'
    vrows += (f'<tr><td>{VNAME[k]}</td><td>{v["use"][0]}클립 {v["use"][1]}초</td><td>{rej}</td>'
              f'<td>{s_}초</td><td>${s_ * H3_RATE:.2f}</td><td>{fin}</td></tr>')

S17 = f'''<section id="s17">
<h2><span class="n">17</span>영상 생성 비용 — 정가 기준 추정 <span class="tag t-u">사용자 요청</span></h2>
<p class="small"><b>읽는 법</b> — 금액은 모두 <b>미국 달러, 공식 정가 × 실제 생성량</b>으로 계산한 추정입니다. 청구서 금액이 아닙니다 <span class="tag t-x">MiniMax · OpenAI 콘솔에서 확인 필요</span>. 생성량은 생성 기록 파일에서 셌습니다 <span class="tag t-m">실측</span>: 호스트 영상은 작업마다 남긴 <code>run.json</code> {len(h3_tasks)}건(성공 {len(h3_tasks) - n_fail} · 실패 {n_fail}), 이미지는 <code>generation_log.json</code>의 토큰 수, 목소리는 공급자가 돌려준 글자 수(<code>usage_characters</code>). 단가는 2026-10-15에 공식 가격표에서 확인했습니다.</p>
<div class="callout"><b>총 생성 비용 약 ${total:.2f}</b> — 호스트 영상(MiniMax H3) ${h3_cost:.2f} · 캐릭터 이미지(gpt-image-1.5) ${img_cost:.2f} · 목소리(MiniMax Voice Design·T2A) ${voice_cost:.2f}. 편집·합성·자막·1.25배속 재렌더는 이 PC에서 ffmpeg로 처리해 비용이 없습니다.</div>

<h3>17-1. 영상별 — 호스트 영상(H3) 생성분</h3>
<p class="small">H3 = MiniMax-H3 영상 모델, 2K 출력 <b>초당 $0.13</b>. 요청한 클립 길이(초)만큼 과금되는 것으로 계산했습니다. "다시 만든 것의 1차분" = 대사 가드 검수에서 떨어져 다시 생성한 클립의 처음 버전(돈은 나갔지만 영상에는 안 씀).</p>
<div class="tbl"><table>
<tr><th>영상</th><th>완성본에 쓴 클립</th><th>다시 만든 것의 1차분</th><th>생성 합계</th><th>비용</th><th>완성본 길이</th></tr>
{vrows}
<tr><td><b>합계</b></td><td></td><td></td><td><b>{h3_secs}초</b></td><td><b>${h3_cost:.2f}</b></td><td></td></tr>
</table></div>
<p class="small">생성 실패 {n_fail}건({s_fail}초)은 빠져 있습니다. 공급자가 <code>1008 insufficient balance</code>(잔액 부족)로 돌려주고 사용량이 비어 있어 과금되지 않은 것으로 봤습니다 <span class="tag t-x">추정 · 콘솔 확인</span>. 세 편 공통 구간은 한 번 만들어 3편에 함께 씁니다.</p>

<h3>17-2. 항목별</h3>
<div class="tbl"><table>
<tr><th>항목</th><th>생성량 (실측)</th><th>단가 (정가)</th><th>추정 비용</th></tr>
<tr><td>호스트 영상 — MiniMax-H3 2K</td><td>{h3_secs}초 (성공한 생성 전부)</td><td>$0.13 / 초</td><td>${h3_cost:.2f}</td></tr>
<tr><td>캐릭터 이미지 — gpt-image-1.5 (high)</td><td>{len(img_rows)}장: 후보 7 · 시트 7 · 마스터 1 · 아웃페인트 1</td><td>이미지 입력 $8 · 이미지 출력 $32 · 글 입력 $5 · 글 출력 $10 (100만 토큰당)</td><td>${img_cost:.2f}</td></tr>
<tr><td>목소리 만들기 — Voice Design</td><td>보이스 A 1개 + 미리듣기 {prev_chars}자</td><td>보이스당 $3 (처음 T2A에 쓸 때) · 미리듣기 $60 / 100만 자</td><td>${VD_VOICE + prev_chars * VD_PREVIEW:.2f}</td></tr>
<tr><td>목소리 합성 — T2A speech-2.8-hd</td><td>H3용 reference {ref_chars}자 + 화면 밖 목소리(V/O) 23줄 {vo_chars:,}자</td><td>$100 / 100만 자</td><td>${(ref_chars + vo_chars) * T2A_RATE:.2f}</td></tr>
<tr><td><b>합계</b></td><td></td><td></td><td><b>${total:.2f}</b></td></tr>
</table></div>
<div class="dev-only">
<h3>17-3. 완성본에 실제 쓴 것 vs 테스트·폐기 <span class="tag t-u">개발자용</span></h3>
<p class="small">17-2 합계는 이번 작업에서 생성한 것 전부(시험 생성·버린 것 포함)입니다. 아래는 그 합계를 둘로 나눈 것입니다. 배너 8종·영상용 카드·그래픽은 HTML 템플릿을 브라우저로 캡처하고 실물 누끼를 합성해 만들어 <b>생성 비용이 없습니다</b>(OpenAI 이미지 API를 부르는 스크립트는 <code>gen_r3_character.py</code>·<code>outpaint_master.py</code> 두 개뿐 — 확인함).</p>
<div class="tbl"><table>
<tr><th>항목</th><th>완성본에 실제 쓴 것</th><th>테스트·폐기</th></tr>
<tr><td>호스트 영상 (H3)</td><td>{n_use}클립 {s_use}초 = <b>${s_use * H3_RATE:.2f}</b></td><td>시험 생성 {s_pil}초 ${s_pil * H3_RATE:.2f} + 검수 탈락 후 다시 만든 클립의 처음 버전 {s_rej}초 ${s_rej * H3_RATE:.2f} = <b>${(s_pil + s_rej) * H3_RATE:.2f}</b></td></tr>
<tr><td>캐릭터 이미지 (gpt-image-1.5)</td><td>R3 얼굴이 된 후보 1 + 시트 3 + 마스터 1 = {n_img_used}장 <b>${img_used:.2f}</b></td><td>이전 캐릭터 후보·시트 8 + R3 탈락 후보 2 + 버린 아웃페인트 1 = {len(img_rows) - n_img_used}장 <b>${img_cost - img_used:.2f}</b></td></tr>
<tr><td>목소리 (Voice Design · T2A)</td><td>보이스 1개 + 음성 합성 전부 <b>${voice_cost - prev_chars * VD_PREVIEW:.2f}</b></td><td>미리듣기 {prev_chars}자 ${prev_chars * VD_PREVIEW:.2f}</td></tr>
<tr><td><b>합계</b></td><td><b>약 ${s_use * H3_RATE + img_used + voice_cost - prev_chars * VD_PREVIEW:.2f}</b></td><td><b>약 ${(s_pil + s_rej) * H3_RATE + img_cost - img_used + prev_chars * VD_PREVIEW:.2f}</b></td></tr>
</table></div>
<p class="small">"완성본에 실제 쓴 것"의 캐릭터 시트 3장은 화면에 직접 나오지 않지만 캐릭터 고정 레퍼런스로 썼습니다. 정가 기준 추정이며 청구서 금액이 아닙니다.</p>
</div>
<p class="small">포함하지 않은 것: 10월 6일 POC(별도 폴더 <code>fnco_ai-shoppinghost/poc_20261006/banila-shopee-poc-20261006-v1/</code>) 비용, 대본·기획에 쓴 AI 대화 비용. 다시 만들 때 참고: 호스트 클립 1개(평균 약 {h3_secs / max(1, sum(v["use"][0] + v["rej"][0] for v in by_vid.values())):.0f}초)를 다시 생성하면 약 ${H3_RATE * h3_secs / max(1, sum(v["use"][0] + v["rej"][0] for v in by_vid.values())):.2f}입니다.</p>
</section>'''
b.find('section', id='s16').insert_after(frag('\n' + S17))
# 15-7은 17장으로 안내만
h157 = h3_of(sec('s15'), '15-7.')
n = h157.find_next_sibling()
while n is not None and n.name not in ('h3', 'h2'):
    nxt = n.find_next_sibling()
    n.decompose()
    n = nxt
h157.insert_after(frag('<p>비용 표는 맨 아래 <a href="#s17">17장</a>으로 옮겼습니다(생성 기록에서 다시 집계, 이미지·목소리 금액 포함).</p>'))
toc = b.find('nav', class_='toc')
if not toc.find('a', href='#s17'):
    toc.find('a', href='#s16').insert_after(frag('\n  <a href="#s17">17. 영상 생성 비용</a>'))


# ── 4·15. 토글로 접기 (2026-10-15 사용자) ──
for sid_, lab_ in (('s4', '펼쳐 보기 — 레이아웃 계획값(영역 그림 · 레이어 표 L0~L6)'),
                   ('s15', '펼쳐 보기 — 생성 클립 바로 보기 · 캐릭터 시트 · 보이스 · 파일럿 · 클립 검수 결과 · V/O')):
    s_ = sec(sid_)
    d_ = b.new_tag('details')
    sm_ = b.new_tag('summary')
    sm_.string = lab_
    d_.append(sm_)
    for c in list(s_.find_all(recursive=False)):
        if c.name != 'h2':
            d_.append(c.extract())
    s_.append(d_)
b.head.append(frag('<style>#s4>details>summary,#s15>details>summary{cursor:pointer;font-weight:600}#s17 td:last-child,#s17 td:nth-child(5){white-space:nowrap}</style>'))

# ── 목차 ──
NAV = {'s0': '0. 현재 상태', 's3': '3. 완성본 3편 · 대본 ★', 's5': '5. 캐릭터 (R3)', 's6': '6. 음성 (보이스 A)', 's7': '7. 아키텍처·워크플로우', 's8': '8. 시연 소스', 's9': '9. 배너·그래픽 전체',
       's11': '11. 진행 현황', 's13': '13. 실무진 요청 (상세)', 's14': '14. 대사 이탈 대응', 's16': '16. 최종 편집본 ★'}
for a in b.find('nav', class_='toc').find_all('a'):
    k = a['href'].lstrip('#')
    if k in NAV:
        a.string = NAV[k]

# ── 생성 POC 줄이기 (2026-10-16 사용자: "쓸데없는 내용 삭제해 너무 길어") ──
# 남기는 것: 결과물(영상·대본·배너·캐릭터·음성·비용)과 남은 확인 요청. 지우는 것: 끝난 과정 기록·다른 장과 겹치는 것·계획 단계 설명.
# 지운 내용은 v3 파일(Shopee_AI쇼호스트_제작설계_v3.html)에 남아 있다.
for sid_ in ('s1', 's2', 's4', 's8', 's11', 's12'):
    sec(sid_).decompose()
for sid_, prefixes in (('s9', ('9-1.', '9-2.', '9-4.', '9-7.', '9-8.')),
                       ('s15', ('15-1.', '15-2.', '15-3.', '15-4.', '15-6.', '15-7.')),
                       ('s16', ('16-1.', '16-2.', '16-3.', '16-4.', '16-6.')),
                       ('s6', ('6-1.', '6-2.'))):
    s_ = sec(sid_)
    for pre in prefixes:
        hs_ = [h for h in s_.find_all('h3') if h.get_text(strip=True).startswith(pre)]
        assert len(hs_) == 1, (sid_, pre, len(hs_))
        drop_block(hs_[0])
# 15-5 클립별 검수 표는 접어 둔다 (요약 문단만 보이게)
h155 = [h for h in sec('s15').find_all('h3') if h.get_text(strip=True).startswith('15-5.')][0]
d155 = b.new_tag('details'); sm155 = b.new_tag('summary'); sm155.string = '클립별 검수 결과 표 펼쳐 보기'; d155.append(sm155)
n_ = h155.find_next_sibling()
while n_ is not None and n_.name not in ('h3', 'h2'):
    nx_ = n_.find_next_sibling()
    if n_.name in ('div', 'table', 'details'):
        d155.append(n_.extract())
    n_ = nx_
h155.insert_after(d155)
for d_ in sec('s0').find_all('details'):
    if d_.find('summary') and d_.find('summary').get_text(strip=True).startswith('v4에서 지운 내용'):
        d_.decompose()
# ── 생성 POC 결과만 남기기 2 (2026-10-16 사용자: "실무진 요청 삭제", 배너 "폰트 바꿨다 이런 내용 왜 넣어 — 요약", "전체 읽고 불필요한 내용 삭제") ──
sec('s13').decompose()


def _drop_text(s_, starts):
    """섹션 안에서 글이 starts 중 하나로 시작하는 블록(p·div)을 지운다."""
    for el_ in list(s_.find_all(['p', 'div'])):
        if el_.decomposed:
            continue
        t_ = el_.get_text(' ', strip=True)
        if any(t_.startswith(x) for x in starts):
            el_.decompose()


# 0장: 결과 표 2개만
s0_ = sec('s0')
vid_tbl = s0_.find('div', class_='tbl').extract()
for c_ in list(s0_.find_all(recursive=False)):
    if c_.name != 'h2':
        c_.decompose()
s0_.append(frag(f'<div class="callout ok"><b>완성본 3편</b> — 1080×1920 · 30fps · 영어 1벌 · 1.25배속(음높이 유지) · 국가별 가격 레이어 없음. 재생은 <a href="#s16">16장</a>.</div>'))
s0_.append(vid_tbl)
s0_.append(frag(f"""<div class="tbl"><table><tr><th>항목</th><th>상태</th><th>결과</th><th>보는 곳</th></tr>
<tr><td>캐릭터</td><td>{T_OK}</td><td>R3 · 시트·마스터 프레임</td><td><a href="#s5">5장</a></td></tr>
<tr><td>대본</td><td>{T_OK}</td><td>3편 + 공통 오프닝·엔딩</td><td><a href="#s3">3장</a></td></tr>
<tr><td>보이스</td><td>{T_WAIT}</td><td>보이스 A, 사람 청취 확정 전</td><td><a href="#s6">6장</a></td></tr>
<tr><td>호스트 영상 (MiniMax H3)</td><td>{T_OK}</td><td>{n_clip}/{n_clip}클립 (탈락 7클립 재생성 포함)</td><td><a href="#s15">15장</a></td></tr>
<tr><td>화면 밖 목소리 (T2A)</td><td>{T_OK}</td><td>23줄</td><td><a href="#s16">16장</a></td></tr>
<tr><td>배너·영상용 그래픽</td><td>{T_OK}</td><td>배너 8 · 전체화면 카드 24 · 측면 카드 18 · 오버레이 5</td><td><a href="#s9">9장</a></td></tr>
<tr><td>로고</td><td>{T_WAIT}</td><td>공식 영상에서 추출해 사용 — 원본 파일 받으면 교체</td><td>—</td></tr>
<tr><td>RA 검토</td><td>{T_WAIT}</td><td>화면 문구 17개 + 대본 RA 표시 문장</td><td><a href="#s9">9장</a> · <a href="#s3">3장</a></td></tr>
<tr><td>국가별 가격·사은품 레이어</td><td>{T_TODO}</td><td>실무진 회신 후 제작</td><td><a href="#s16">16-8</a></td></tr>
</table></div>"""))

# 5장: 시행착오 기록 빼고 결과만
s5_ = sec('s5')
_drop_text(s5_, ('마스터는 세 번 만들었습니다', 'Product Lock 스크립트', '후보 기록'))
for p_ in s5_.find_all('p'):
    if p_.get_text(strip=True).startswith('2026-10-14'):
        p_.clear()
        p_.append(frag('<b>R3</b>(둥근 얼굴·처진 눈매·소프트브라운 끝 웨이브, 실사 피부)로 확정. R3 정면을 레퍼런스로 각도·표정·손 시트와 H3 첫 프레임(마스터)을 만들었습니다(gpt-image-1.5 — 이후 새 호스트는 2.5). '
                       '가상 인물이며 실존 인물 닮음 확인은 하지 않았습니다 <span class="tag t-x">미확인</span>. 편집에서는 호스트를 340px 내려 얼굴을 화면 약 44% 높이에 둡니다.'))

h51 = [h for h in s5_.find_all('h3') if h.get_text(strip=True).startswith('5-1.')]
if h51:
    drop_block(h51[0])
(s5_.find('details') or s5_).append(frag('<p class="small"><b>세트·제품</b> — 사람·제품 없는 핑크 스튜디오 세트. 제품은 생성하지 않고 진열·배너는 공식 누끼 합성, 시연은 공식 상세페이지 영상(16-5).</p>'))

# 6장: 최종 설정 + 미리듣기
s6_ = sec('s6')
for c_ in list(s6_.find_all(recursive=False)):
    if c_.name != 'h2':
        c_.decompose()
s6_.append(frag(f"""<p>MiniMax Voice Design으로 만든 전용 <b>보이스 A</b> (영어, 밝은 20대 초반 여성 톤). 사람 청취 확정 전 {T_WAIT} — 바꾸면 H3 호스트 클립 전부를 다시 만들어야 합니다.</p>
<div class="tbl"><table><tr><th>항목</th><th>값</th></tr>
<tr><td>모델</td><td>speech-2.8-hd · English</td></tr>
<tr><td>속도</td><td>생성 0.95 → 완성본 편집에서 1.25배속 (다음 생성부터 speed 1.25로 바로)</td></tr>
<tr><td>감정</td><td>happy (시연 설명 줄 calm)</td></tr>
<tr><td>출력</td><td>wav 32kHz mono</td></tr>
<tr><td>보존</td><td>voice_id는 <code>2_나레이션/voice/voice_state.json</code>. 생성 7일 안에 T2A로 쓰면 영구 보존(MiniMax FAQ) — Voice Design 보이스에도 해당하는지 <span class="tag t-x">확인 필요</span></td></tr>
</table></div>
<div class="tbl"><table><tr><th>미리듣기</th><th>문장</th><th>재생</th></tr>
<tr><td>Voice Design 샘플</td><td class="vo">Hi everyone, welcome to BANILA CO Live! Today's deals are really good, so don't miss this chance. Scoop a little balm, massage it in, and watch it melt into oil.</td><td><audio controls preload="none" src="../2_나레이션/voice/A1_design_preview.mp3"></audio></td></tr>
<tr><td>H3 참조 음성</td><td class="vo">I always love these little moments with you. Let's take it slow, look closely, and have some fun together, okay? I think you're going to like this one.</td><td><audio controls preload="none" src="../2_나레이션/voice/host_reference.wav"></audio></td></tr>
</table></div>"""))

# 9장: 최종 배너 구성 요약 + 이미지 + 짧은 제품명 표
s9_ = sec('s9')
_drop_text(s9_, ('배너와 영상 화면이 왜 다른가', '다시 만들 때 제안', '2026-10-15 다시 디자인', '읽는 법', '10월 Shopee 배너에는', 'Product Spec 안에서 브랜드 표기', '립앤치크는 B. By BANILA', '영문 컬러명은 Product Spec에 없습니다', '파일:'))
h90 = [h for h in s9_.find_all('h3') if h.get_text(strip=True).startswith('9-0.')][0]
h90.clear(); h90.append(frag('9-0. 만든 배너·그래픽 — 55장'))
h90.insert_after(frag("""<div class="tbl"><table><tr><th>구성</th><th>내용</th></tr>
<tr><td>종류</td><td>① 배너 8종(단독 배너) · ② 영상 전체 화면 카드 24장 · ③ 측면 카드 18장 · 오버레이 5장 — 모두 1080×1920</td></tr>
<tr><td>디자인</td><td>10월 더블데이 배너 톤(노트·스크랩북: 스프링 노트, 찢은 메모지 제목, 핑크 테이프·형광펜, 모눈 칸) · 검정 로고 · 폰트 Pretendard</td></tr>
<tr><td>영상 카드 안전 영역</td><td>세로 34~68% (위 0~33%는 Shopee 앱 UI가 덮는 자리)</td></tr>
<tr><td>제품·발색</td><td>공식 누끼·공식 발색컷만 비율 유지로 배치 — 생성하지 않음</td></tr>
<tr><td>문구</td><td>세정·사용감·외관 범위. RA 사전검토 대상 17개는 이미지 아래 <span class="tag t-r">RA</span> 표시</td></tr>
<tr><td>파일</td><td><code>5_에셋/banner/common/</code> · <code>5_에셋/edit_gfx/</code> · 문구 목록 <code>banner_copy.csv</code> · <code>edit_gfx_copy.csv</code></td></tr>
</table></div>"""))
h93 = [h for h in s9_.find_all('h3') if h.get_text(strip=True).startswith('9-3.')][0]
drop_block(h93)
s9_.append(frag("""<h3>9-1. 제품명 표기 (Product Spec 기준, 2026-10-13 조회)</h3>
<div class="tbl"><table><tr><th>제품</th><th>배너·VO 표기</th><th>근거</th></tr>
<tr><td>프라이머 클래식</td><td>Prime Primer Classic</td><td>Product Spec v6</td></tr>
<tr><td>세팅 픽서 100ml</td><td>Prime Primer Setting Fixer</td><td>Product Spec v6</td></tr>
<tr><td>피니쉬 파우더 12g</td><td>Prime Primer Finish Powder</td><td>Product Spec v8</td></tr>
<tr><td>선 베이스</td><td>Prime Primer Sun Base (SPF 표기는 국가별 등록 확인 후)</td><td>공식몰 상세 (Spec 미등록)</td></tr>
<tr><td>립앤치크 12색</td><td>Romantic Blush Lip &amp; Cheek · 컬러는 번호만(영문 컬러명 없음)</td><td>Product Spec v10</td></tr>
<tr><td>클렌징밤 3종</td><td>Clean it Zero Cleansing Balm Original / Pore Clarifying / Calming</td><td>공식몰 상세 (Spec 미등록)</td></tr>
</table></div>
<p class="small">브랜드명은 제품명에 넣지 않고 로고로만 표기합니다.</p>"""))

# ── 3장 영상 흐름 + 16장 최종 편집본 합치기 (2026-10-16 사용자) ──
s3_, s16_ = sec('s3'), sec('s16')
set_h2(s3_, '완성본 3편 · 대본')
# 편별 플레이어: 16-0의 것(구간 + 줄별 화면·자막 표)으로 바꾼다
fv16 = [d for d in s16_.find_all('div', class_='fv', recursive=False)]
for pre, fvn in zip(('3-1.', '3-2.', '3-3.'), fv16):
    h_ = [h for h in s3_.find_all('h3', recursive=False) if h.get_text(strip=True).startswith(pre)][0]
    old_ = h_.find_next_sibling('div', class_='fv')
    old_.replace_with(fvn.extract())
# 경위 메모 빼기
for el_ in list(s3_.find_all(['p', 'ul'], recursive=False)):
    t_ = el_.get_text(' ', strip=True)
    if t_.startswith(('사용자 요청', '요청 반영', '2026-10-16 사용자 요청으로', 'VO는 전부 RA 검토 전 초안')):
        el_.decompose()
for d_ in s3_.find_all('div', class_='callout'):
    if d_.get_text(strip=True).startswith('선택 반영'):
        d_.decompose()
s3_.insert(2, frag('<p class="small">대본 VO는 RA 검토 전 초안 — 효능은 세정·사용감·외관 표현만, 걸릴 소지가 있는 문장은 <span class="tag t-r">RA</span>. '
                   '완성본: 1080×1920 · 30fps · 1.25배속 · 호스트 H3 음성 + T2A V/O · 배경음악 없음.</p>'))
# 자막·배지 확정 블록은 토글로 (2026-10-16 사용자)
h4c = [h for h in s3_.find_all('h4') if h.get_text(strip=True).startswith('자막 — B')]
if h4c:
    d_ = b.new_tag('details'); sm_ = b.new_tag('summary'); sm_.string = '자막·"AI-generated host" 배지 — 확정 결과 보기'; d_.append(sm_)
    n_ = h4c[0]
    while n_ is not None and n_.name in ('h4', 'div', 'p'):
        nx_ = n_.find_next_sibling(); d_.append(n_.extract()); n_ = nx_
    nx_.insert_before(d_) if nx_ is not None else s3_.append(d_)

# 16-5 시연 소스 배정, 16-8 남은 일 → 3-4, 3-5
for pre, new_t in (('16-5.', '3-4. 시연 소스 배정 (공식 상세페이지 영상, 원본 소리 제거)'), ('16-8.', '3-5. 남은 일 · 확인 요청')):
    h_ = [h for h in s16_.find_all('h3', recursive=False) if h.get_text(strip=True).startswith(pre)][0]
    blk_ = [h_]
    n_ = h_.find_next_sibling()
    while n_ is not None and n_.name not in ('h3', 'h2'):
        blk_.append(n_); n_ = n_.find_next_sibling()
    h_.string = new_t
    for el_ in blk_:
        s3_.append(el_.extract())
# 3-4 시연 소스 배정은 제목만 남기고 본문을 토글로 (2026-10-16 사용자)
h34 = [h for h in s3_.find_all('h3') if h.get_text(strip=True).startswith('3-4.')][0]
d34 = b.new_tag('details'); sm34 = b.new_tag('summary'); sm34.string = '줄별 시연 소스 파일 보기'; d34.append(sm34)
n_ = h34.find_next_sibling()
while n_ is not None and n_.name not in ('h3', 'h2'):
    nx_ = n_.find_next_sibling(); d34.append(n_.extract()); n_ = nx_
h34.insert_after(d34)
# 3-5 남은 일도 같은 방식으로 토글 (2026-10-16 사용자)
h35 = [h for h in s3_.find_all('h3') if h.get_text(strip=True).startswith('3-5.')][0]
d35 = b.new_tag('details'); sm35 = b.new_tag('summary'); sm35.string = '확인 요청 목록 보기'; d35.append(sm35)
n_ = h35.find_next_sibling()
while n_ is not None and n_.name not in ('h3', 'h2'):
    nx_ = n_.find_next_sibling(); d35.append(n_.extract()); n_ = nx_
h35.insert_after(d35)
s16_.decompose()
for a_ in b.find_all('a', href='#s16'):
    if a_.find_parent('nav'):
        a_.decompose()  # 목차의 16장 항목은 없앤다 (3장 항목은 그대로)
        continue
    a_['href'] = '#s3'
    t_ = a_.get_text()
    a_.string = {'16-8': '3-5', '16-5': '3-4', '16-0': '3장'}.get(t_, '3장' if '16' in t_ else t_)

# ── 탭 나누기 (2026-10-16 사용자: "아키텍쳐 탭이랑 생성 poc 탭으로") ──
# 아키텍처 = 다른 제품에도 그대로 쓰는 구조·방법 / 생성 POC = 이번 Shopee 3편 제작 기록
WF = ROOT.parent / 'pipeline' / 'workflow_section.html'  # pipeline/build_workflow_section.py 출력 (어떤 제품이든 자동 제작)
main_ = b.find('main')
if WF.exists():
    main_.append(frag(WF.read_text(encoding='utf-8')))
ARCH_IDS = ['s14', 's10']  # 2026-10-16 사용자: 7장은 자동 제작 워크플로우(sW)에 합침 — sW가 메인
if WF.exists():
    # 7장 7-0에서 A와 겹치지 않는 'Shopee 3편 실제 실행 기록'만 sW 맨 끝 참고로 옮기고 7장은 지운다
    s7_ = sec('s7')
    h70 = [h for h in s7_.find_all('h3') if h.get_text(strip=True).startswith('7-0.')][0]
    keep_ = []
    n_ = h70.find_next_sibling()
    while n_ is not None and n_.name != 'details':
        nx_ = n_.find_next_sibling(); keep_.append(n_.extract()); n_ = nx_
    ref_ = frag('<h3>A-7. 참고 — Shopee 3편에서 실제로 돈 방식 (구 7장)</h3>'
                '<details class="pd"><summary>펼쳐 보기 — 단계별 도구·산출물, 최종 편집 안에서 하는 일, 계획과 실제가 다른 점</summary></details>')
    det_ = ref_.find('details')
    for el_ in keep_:
        if el_.name == 'div' and 'ar-flow' in (el_.get('class') or []):
            continue  # 흐름 그림은 A-0 다이어그램과 겹침
        det_.append(el_)
    sec('sW').append(ref_)
    s7_.decompose()
    for a_ in b.find_all('a', href='#s7'):
        a_['href'] = '#sW'
        if '7-0' in a_.get_text():
            a_.string = 'A. 자동 제작 워크플로우'
tab_arch, tab_poc = b.new_tag('div', id='tab-arch'), b.new_tag('div', id='tab-poc')
tab_arch['class'], tab_poc['class'] = 'tabpane', 'tabpane'
sw_ = sec('sW').extract() if WF.exists() else None
if sw_ is not None:
    tab_arch.append(sw_)
for sid_ in ARCH_IDS:
    tab_arch.append(sec(sid_).extract())
for s_ in list(main_.find_all('section', recursive=False)):
    tab_poc.append(s_.extract())
hero_ = main_.find('header', class_='hero').extract()
tab_poc.insert(0, hero_)
main_.insert(0, tab_poc)
main_.insert(0, tab_arch)
main_.insert(0, frag('<div class="tabs" role="tablist">'
                        '<button type="button" role="tab" id="tb-arch" data-tab="arch">① 아키텍처 · 워크플로우 <span>어떤 제품이든 쓰는 자동 제작 구조</span></button>'
                        '<button type="button" role="tab" id="tb-poc" data-tab="poc">② 생성 POC <span>Shopee 11월 3편 — 실제로 만든 영상·배너·캐릭터·대본</span></button></div>'))
# 목차도 탭별로
toc_ = b.find('nav', class_='toc')
links_ = {a['href'].lstrip('#'): a for a in toc_.find_all('a')}
for a_ in links_.values():
    a_.extract()
for c_ in list(toc_.children):
    if getattr(c_, 'name', None) != 'b':
        c_.extract()
NAVW = {'sW': 'A. 어떤 제품이든 — 자동 제작', 's7': '7. 아키텍처·워크플로우 (이번 제작)', 's14': '14. 대사 이탈 대응', 's10': '10. 검수 기준'}
g_arch = frag('<div class="tocg" data-tab="arch"></div>').div
g_poc = frag('<div class="tocg" data-tab="poc"></div>').div
for sid_ in ARCH_IDS:
    a_ = links_.get(sid_) or frag(f'<a href="#{sid_}"></a>').a
    a_.string = NAVW[sid_]
    g_arch.append(a_)
for s_ in tab_poc.find_all('section', recursive=False):
    if s_['id'] in links_:
        g_poc.append(links_[s_['id']])
if sw_ is not None:
    g_arch.insert(0, frag('<a class="top-wf" href="#sW">A. 자동 제작 워크플로우 ★</a>'))
toc_.append(g_arch); toc_.append(g_poc)
b.head.append(frag('<style>section,h3,details{scroll-margin-top:96px}.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 20px;position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding:8px 0}'
                   '.tabs button{flex:1 1 220px;text-align:left;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:12px;padding:12px 16px;font:600 16px/1.3 inherit;cursor:pointer}'
                   '.tabs button span{display:block;font-weight:400;font-size:12px;color:var(--muted)}'
                   '.tabs button[aria-selected="true"]{border-color:var(--pink);background:var(--pink-soft)}'
                   '.tabs button:focus-visible{outline:2px solid var(--pink);outline-offset:2px}</style>'))
b.body.append(frag('''<script>(function(){
var arch=document.getElementById('tab-arch'),poc=document.getElementById('tab-poc');
function show(t,noScroll){arch.hidden=t!=='arch';poc.hidden=t!=='poc';
 document.querySelectorAll('.tabs button').forEach(function(x){x.setAttribute('aria-selected',x.dataset.tab===t)});
 document.querySelectorAll('.tocg').forEach(function(g){g.hidden=g.dataset.tab!==t});
 try{localStorage.setItem('tab',t)}catch(e){}}
function tabOf(id){var el=id&&document.getElementById(id);return el&&arch.contains(el)?'arch':(el&&poc.contains(el)?'poc':null)}
document.querySelectorAll('.tabs button').forEach(function(x){x.addEventListener('click',function(){show(x.dataset.tab);window.scrollTo(0,0)})});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(!a)return;
 var t=tabOf(a.getAttribute('href').slice(1));if(t&&(t==='arch'?arch:poc).hidden){show(t)}});
var h=location.hash.slice(1),t=h==='arch'||h==='poc'?h:tabOf(h),saved=null;try{saved=localStorage.getItem('tab')}catch(e){}
show(t||saved||'arch');
})();</script>'''))

# 개발자용 표시 (공유용 묶음에서는 .dev-only 를 지운다)
(b.find('main') or b.body).insert(0, frag('<div class="callout dev-only"><b>개발자용</b> — 로컬 파일·영상 재생·생성 스크립트·테스트 비용까지 담은 내부 작업본입니다. '
                                          '외부 공유는 dcsai 공유판(<code>0_기획/공유용/dcsai_bundle/</code>, 사내 링크)을 쓰세요.</div>'))
_tabs = main_.find('div', class_='tabs').extract(); main_.insert(0, _tabs)
b.head.append(frag('<style>nav.toc a.top-wf{color:var(--ink);font-weight:700;background:var(--pink-soft);margin-bottom:6px}</style>'))
# 0_기획/개발자용/ 으로 한 단계 깊어졌으므로 '../X' → '../../X'
for t in b.find_all(['a', 'img', 'video', 'audio', 'source']):
    for at in ('href', 'src'):
        v = t.get(at)
        if v and v.startswith('../'):
            t[at] = '../' + v
OUT.parent.mkdir(exist_ok=True)
_html = str(b)
# 2026-10-15 사용자: overlay_V3_C4-2(성분 칩) 삭제 → 대본 표의 화면 설명도 맞춘다
_html = re.sub(r'(<td>C4-2</td>(?:<td>[^<]*</td>)?)<td>D\+G</td><td><code>원본영상/손등\.MP4</code> \(16\.8초\) 일부 \+ 성분 카드: Tea tree · AHA · BHA · PHA · LHA</td>',
               r'<td>D</td><td><code>원본영상/손등.MP4</code> (16.8초) 일부 (성분 카드는 2026-10-15 요청으로 삭제)</td>', _html)
OUT.write_text(_html, encoding='utf-8')
print('ok', OUT.name, OUT.stat().st_size)
