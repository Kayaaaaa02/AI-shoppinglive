"""제작설계 v2 → v3 본문 개정 (스토리보드·파이프라인·시연 소스·요청사항·POC).

v2 HTML은 그대로 두고 v3 파일을 새로 만든다. 이미지 섹션(4·5·6·9)은 build_v3_assets.py가 이어서 채운다.
python -X utf8 build_v3_text.py
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'Shopee_AI쇼호스트_제작설계_v2.html'
DST = HERE / 'Shopee_AI쇼호스트_제작설계_v3.html'

html = SRC.read_text(encoding='utf-8')


def put(sec_id, body):
    """<!-- n --> 주석부터 </section>까지 한 섹션을 통째로 교체."""
    global html
    pat = re.compile(r'<section id="%s">.*?\n</section>' % sec_id, re.S)
    assert pat.search(html), sec_id
    html = pat.sub(lambda m: body.strip('\n'), html, count=1)


R = '<span class="tag t-r">RA</span>'
X = lambda s='확인 필요': f'<span class="tag t-x">{s}</span>'
D = lambda s='문서': f'<span class="tag t-d">{s}</span>'
U = '<span class="tag t-u">사용자 요청</span>'
P = '<span class="tag t-p">제안</span>'
M = lambda s='실측': f'<span class="tag t-m">{s}</span>'


def row(*cells, vo_idx=4):
    out = []
    for i, c in enumerate(cells):
        cls = ' class="vo"' if i == vo_idx and c and not c.startswith('<') else ''
        out.append(f'<td{cls}>{c}</td>')
    return '    <tr>' + ''.join(out) + '</tr>'


def timeline(label, parts):
    divs = ''.join(f'<div style="flex:{f};background:{c}">{t}</div>' for t, f, c in parts)
    return f'  <div class="timeline" aria-label="{label}">{divs}</div>'


HEAD = '    <tr><th>#</th><th>시간</th><th>유형</th><th>화면 · 시연 소스</th><th>VO 초안 (영어)</th><th>근거·주의</th></tr>'

# ---------------------------------------------------------------- 0
put('s0', f'''<section id="s0">
  <h2><span class="n">0</span>v3 변경 사항 (2026-10-13)</h2>
  <p class="small">v2 → v3. 요청 14건을 반영했습니다. v2 파일은 비교용으로 그대로 둡니다(<code>Shopee_AI쇼호스트_제작설계_v2.html</code>).</p>
  <div class="tbl"><table>
    <tr><th>#</th><th>요청</th><th>v3 반영</th></tr>
    <tr><td>1</td><td>공통 오프닝·엔딩 길게, "좋은 기회", "문의 남기면 답변" 멘트</td><td>OC 8초 → 약 20초, EC 15초 → 약 30초. 기회 강조·질문 안내 문장 추가 (<a href="#s3">3-0</a>)</td></tr>
    <tr><td>2</td><td>Prime Primer 제품별 소개 보강</td><td>4종 각각 "무엇 → 제형 → 사용법 → 이런 분께" 4단 구성, 제품당 60~75초 (<a href="#s3">3-1</a>)</td></tr>
    <tr><td>3</td><td>Lip &amp; Cheek USP·살 이유</td><td>USP 5가지 + "왜 지금 사야 하는지(B2G1로 트리오 완성)" 장면 추가 (<a href="#s3">3-2</a>)</td></tr>
    <tr><td>4</td><td>클렌징밤 3종 유형별 특징 충분히</td><td>Original·Pore Clarifying·Calming 각 60초 단독 장면 + 피부 타입별 고르는 법 (<a href="#s3">3-3</a>)</td></tr>
    <tr><td>5</td><td>AL라이브 전자책 뷰티 내용 반영 확인</td><td>전자책 항목별 반영 점검표 신설 (<a href="#s1">1-1</a>)</td></tr>
    <tr><td>6</td><td>화면 레이아웃 품목별 1차 생성</td><td>V1·V2·V3 레이아웃 이미지 (<a href="#s4">4장</a>)</td></tr>
    <tr><td>7</td><td>캐릭터 시트 GPT 이미지, 20대 초반 K-pop 아이돌 느낌</td><td>GPT 이미지로 후보 생성 (<a href="#s5">5장</a>)</td></tr>
    <tr><td>8</td><td>MiniMax T2A 보이스 후보</td><td>후보 표 (<a href="#s6">6장</a>)</td></tr>
    <tr><td>9</td><td>립싱크 제외</td><td>립싱크 재현 테스트·LIPSYNC_LOCK·HeyGen 예비 경로 삭제. 호스트 장면은 MiniMax H3가 대사를 직접 말하는 방식 (<a href="#s7">7장</a>)</td></tr>
    <tr><td>10</td><td>시연은 받은 소스 활용</td><td>수령 체크리스트 → 받은 영상 파일을 장면별로 배정 (<a href="#s8">8장</a>)</td></tr>
    <tr><td>11</td><td>배너 폰트 수정, 11.11 등 이벤트 문구 제외, 제품·프로모션 정보 중심, 1080×1920, 립앤치크 호수별 발색</td><td><a href="#s9">9장</a></td></tr>
    <tr><td>12</td><td>실무진 요청사항 간략히</td><td>12행 → 핵심 8행, 세금 근거는 접어 둠 (<a href="#s13">13장</a>)</td></tr>
    <tr><td>13</td><td>POC 설명·studio04 대사 이탈 대응</td><td>POC가 무엇이었는지 설명, studio03 사용 확정, 대사 이탈 방지 하네스와 편집 삭제 단계 추가 (<a href="#s14">14장</a>)</td></tr>
    <tr><td>14</td><td>캐릭터 시트·스토리보드 확정 후 영상 생성</td><td>영상 생성은 아직 하지 않음. 확정 게이트를 <a href="#s11">11장</a> 맨 앞에 둠</td></tr>
  </table></div>
</section>''')

# ---------------------------------------------------------------- 1-1 전자책 점검표
EBOOK = f'''  <h3>1-1. AL라이브 전자책 — 뷰티 카테고리 반영 점검 {D('전자책 p.6·8·11·16~17·38 원문 확인')}</h3>
  <p class="small">원문: <code>OneDrive - F&amp;F\\AX팀\\20. AI쇼핑라이브\\AL라이브\\AL라이브_전자책_44개 카테고리 완전정복 가이드.pdf</code> (39쪽). 2026-10-13에 뷰티(12 기초·13 색조·14 기능성)와 공통 운영 쪽을 다시 읽고 v3 설계와 한 줄씩 대조했습니다.</p>
  <div class="tbl"><table>
    <tr><th>전자책 내용 (요약)</th><th>쪽</th><th>v3 반영 위치</th><th>상태</th></tr>
    <tr><td>뷰티는 "광고처럼 만드는 것" — 텍스처가 스며드는 장면을 광고 화보 감도로</td><td>16</td><td>D 시연은 공식 상세페이지 영상(광고 촬영본)만 사용, 1080×1920 시연 창 (4·8장)</td><td>✅</td></tr>
    <tr><td>즉흥 발언 대신 검증된 워딩의 씬 + 응대 시스템</td><td>16</td><td>VO 전량 사전 대본·RA 검토. 생성 중 대사 이탈은 ASR 가드로 잘라냄 (7·14장). 채팅 응대 FAQ 매뉴얼 (3장 각 영상 FAQ 장면)</td><td>✅</td></tr>
    <tr><td>기초: ① 피부 고민 오프닝 ② 텍스처·흡수 시연과 성분 ③ 아침·저녁 루틴</td><td>16</td><td>V3: C1 하루 끝 고민 → C2 셔벗→오일→유화 시연 → C3~C5 성분·특징 → 저녁 루틴. V1: P1 고민 → 제품별 텍스처 시연 → P7 아침 루틴</td><td>✅</td></tr>
    <tr><td>기초 팁: 피부 타입별(건성·지성·민감성) 답변 매뉴얼</td><td>16</td><td>V3 C6 "어떤 밤이 내 피부에?" 장면 + 채팅 FAQ. V1 P7 피부 타입별 사용량 팁</td><td>✅ (FAQ 문안 RA 대상)</td></tr>
    <tr><td>색조: ① 오늘의 룩 ② 발색·비포애프터 분할 시연 ③ 퍼스널컬러·상황별 추천</td><td>17</td><td>V2: L0 오늘의 룩 → L3 1겹/2겹 분할 → L5 호수별 립·치크 발색 → L6 퍼스널컬러 트리오 → L7 상황별 추천</td><td>✅ (v2에는 상황별 추천 없었음 → 추가)</td></tr>
    <tr><td>색조: 컬러별 씬을 만들어두고 배너만 바꿔 방송</td><td>13~17</td><td>호수별 발색 배너 1080×1920을 영상 G 화면에 그대로 사용 (9장)</td><td>✅</td></tr>
    <tr><td>색조 팁: 품절 컬러는 컬러칩 배너에 표시</td><td>17</td><td>호수별 배너에 SOLD OUT 레이어 자리 (국가 레이어 L5)</td><td>✅ (품절 정보 R6 대기)</td></tr>
    <tr><td>기능성: 핵심 포인트를 씬별로 쪼개 반복 노출, 효능 표현은 스크립트 단계에서</td><td>17</td><td>제품별 USP를 장면 단위로 분리, 혜택 문장은 O-·혜택 엔딩에서 반복. 효능 표현 RA를 TTS·생성 전 단계로 고정</td><td>✅</td></tr>
    <tr><td>운영: 잘 만든 한 편 반복 재생, 가격·구성 변경은 배너·씬 교체</td><td>8</td><td>제품별 영상 3편 루프, 가격·기간·사은품은 VO에 넣지 않고 배너·국가 레이어로만</td><td>✅</td></tr>
    <tr><td>운영: 실시간 응대 + 자동 안내 멘트</td><td>6·38</td><td>EC "질문은 채팅에 남겨주세요" 멘트. 실제 응대 주체·답변 시간은 {X('R8 확인')}</td><td>△ 응대 체계는 이 설계 범위 밖</td></tr>
    <tr><td>FAQ 씬: 자주 오는 질문 5개를 씬으로 (채팅 응대와 같은 답)</td><td>11</td><td>영상마다 FAQ 장면 1개(V1 P7·V2 L7·V3 C6). 질문 5개 목록은 채널 데이터 수령 후 확정</td><td>△ 질문 목록 {X('미수령')}</td></tr>
  </table></div>
  <p class="small">p.11 FAQ 씬 팁은 식품(건조식품) 항목에 있지만 응대형 방송 공통 팁이라 함께 반영했습니다.</p>
'''
html = re.sub(r'  <h3>1-1\. AL라이브 전자책.*?</table></div>\n', lambda m: EBOOK, html, count=1, flags=re.S)
html = html.replace('<div class="callout ok"><b>립싱크</b> — 공식 문서에서는 립싱크 전용 기능을 확인하지 못했지만 <span class="tag t-u">사용자 확인</span> MiniMax로 구현한 경험이 있습니다. 사용한 모델·입력 방식·파라미터를 <code>LIPSYNC_LOCK.md</code>에 적어 고정합니다 (<a href="#s7">7장</a>). 단가는 확인하지 않았으므로 비용은 산정하지 않았습니다.</div>',
                    f'<div class="callout ok"><b>립싱크 제외</b> {U} — 별도 립싱크 단계는 두지 않습니다. 호스트 장면은 MiniMax H3가 프롬프트의 대사를 직접 말하게 하고(POC에서 동작 확인, <a href="#s14">14장</a>), 음성 톤은 T2A 보이스 샘플을 <code>reference_audio</code>로 넣어 맞춥니다 (<a href="#s7">7장</a>).</div>')

# ---------------------------------------------------------------- 2 길이 갱신
html = html.replace('<td>50% OFF + Free gift</td><td>약 5분 20초</td>', '<td>50% OFF + Free gift</td><td>약 7분 50초</td>')
html = html.replace('<td>Buy 2 Get 1</td><td>약 4분 27초</td>', '<td>Buy 2 Get 1</td><td>약 7분 30초</td>')
html = html.replace('<td>MELT IT OFF</td><td>50% OFF + Free gift</td><td>약 4분 17초</td>', '<td>MELT IT OFF</td><td>50% OFF + Free gift</td><td>약 7분 25초</td>')
html = html.replace('<td>"여유 있는 자신감", 친구에게 사용법을 알려주는 톤. 과장 감탄사보다 시연과 혜택 안내</td>',
                    '<td>20대 초반, K-pop 아이돌 같은 밝고 또렷한 에너지 {U}. 친구에게 사용법을 알려주는 톤. 과장 감탄사보다 시연과 혜택 안내</td>'.replace('{U}', U))

# ---------------------------------------------------------------- 3 스토리보드
GREY, OC_C = '#8d7b86', '#8d7b86'
s3 = [f'''<section id="s3">
  <h2><span class="n">3</span>영상 흐름 — 제품별 독립 영상 3편 (v3 스토리보드)</h2>
  <p class="tl-legend">장면 유형 — <b>H</b> 호스트 미디엄샷(MiniMax H3가 대사를 직접 말함, 15초 이하 청크) · <b>D</b> 시연 클로즈업(<b>받은 공식 상세페이지 영상</b>, 8장) · <b>S</b> 분할(H 상단 + D 하단) · <b>G</b> 그래픽 카드·배너(9장 1080×1920) · <b>B</b> 무드 B-roll(MiniMax H3, 제품·인물 없음). <b>V/O</b> = 호스트가 화면에 없을 때 T2A 음성만.</p>
  <p class="small">VO는 전부 RA 검토 전 초안입니다. 효능은 세정·사용감·외관 표현으로만 썼고, 걸릴 소지가 있는 문장에는 {R}를 달았습니다. 판매량·순위·% 수치·SPF는 쓰지 않았습니다(9장·USP 브리프 1-4 기준). H 장면 대사는 한 청크 약 30단어(15초) 이하로 끊어 생성합니다.</p>

  <h3>3-0. 세 편 공통 — 한 번 만들어 3편에 재사용</h3>
  <div class="tbl"><table>
    <tr><th>#</th><th>길이</th><th>유형</th><th>화면</th><th>VO (영어, 3편 동일)</th><th>재사용 방식</th></tr>
    <tr><td><b>OC-1</b><br>공통 오프닝</td><td>약 6초</td><td>B→H</td><td>습한 거리 B-roll 3초 → 호스트 손 흔들며 인사</td><td class="vo">Hi everyone, welcome to BANILA CO Live! I'm your AI host today.</td><td rowspan="3">VO·H 클립 1회 생성 → 3편 동일 삽입. 헤드라인(PREP &amp; STAY / ADD SOME COLOR / MELT IT OFF)만 그래픽 레이어로 교체</td></tr>
    <tr><td><b>OC-2</b></td><td>약 8초</td><td>H</td><td>호스트, 기대감 표정</td><td class="vo">Today's promotion is a really great chance — so I hope you grab your favorites this time!</td></tr>
    <tr><td><b>OC-3</b></td><td>약 6초</td><td>H</td><td>호스트, 화면 아래 가리킴</td><td class="vo">Stay with me. I'll show you everything, step by step — and the deal is waiting below.</td></tr>
    <tr><td><b>EC-1</b><br>공통 엔딩</td><td>약 10초</td><td>H+G</td><td>호스트 + 장바구니 안내 카드</td><td class="vo">That's it for today! Remember, this deal is a great chance — I really hope you take it home this time.</td><td rowspan="3">VO·H 클립 1회 생성 → 3편 동일 삽입. EC-3 끝 프레임 = OC-1 첫 호스트 프레임(마스터 프레임)으로 루프</td></tr>
    <tr><td><b>EC-2</b></td><td>약 10초</td><td>H+G</td><td>장바구니 카드 강조 (손가락 탭 애니메이션)</td><td class="vo">Just tap the product card below to add it to your cart.</td></tr>
    <tr><td><b>EC-3</b></td><td>약 10초</td><td>H+G</td><td>"Questions? Leave them in the chat" 카드</td><td class="vo">Got a question? Leave it in the chat, and we'll get back to you. Thanks for watching — see you next live!</td></tr>
  </table></div>
  <ul>
    <li><b>요청 반영</b> {U}: "이번 프로모션이 좋은 기회이니 꼭 가져가셨으면" → OC-2·EC-1. "궁금한 내용은 문의 남기면 답변" → EC-3. 다만 할인 폭이 "역대 최대" 같은 비교 표현은 근거가 없어 쓰지 않았습니다.</li>
    <li>EC-3의 "we'll get back to you"는 실제로 답하는 담당이 있어야 쓸 수 있습니다 → 응대 주체·채널 확인 {X('R8')}. 확인 전에는 "Leave it in the chat"까지만 씁니다.</li>
    <li>OC·EC에는 제품명·가격·혜택을 넣지 않습니다. 세 편에 그대로 쓰고, 프로모션이 바뀌어도 다시 만들지 않기 위해서입니다.</li>
    <li>"AI-generated host" 표기는 화면에 상시 노출합니다.</li>
  </ul>
''']

# V1 ---------------------------------------------------------------
v1 = [
    ('OC', '0:00–0:20', 'B→H', '공통 오프닝 (3-0). 헤드라인 "PREP &amp; STAY"', None, None),
    ('O-P', '0:20–0:40', 'H+G', '호스트 + 4종 진열(누끼) + 혜택 배너', "Today it's all about Prime Primer — four products that help your makeup go on smooth and stay in place on hot, humid days. And the whole line is fifty percent off, with a free gift!", '혜택 숫자·사은품명은 배너·국가 레이어'),
    ('P1', '0:40–1:00', 'H', '호스트, 공감 표정', "Be honest — does your base slide off by lunch? Do your pores look bigger when it's hot? Then this routine is for you.", '고민 공감 오프닝 (전자책 기초 ①)'),
    ('P2', '1:00–1:20', 'G', '루틴 카드: Sun Base → Classic → (cushion) → Finish Powder → Setting Fixer', 'V/O: Here is the routine. Four steps, and each one has its own job. Let me show you one by one.', ''),
    ('P3-1', '1:20–1:40', 'H+G', '호스트 + 선 베이스 누끼 확대 (50ml 흰 튜브·실버 캡)', 'First, Prime Primer Sun Base. It is sun care and primer in one step — so on busy mornings, you can skip one layer.', f'{D("공식몰")} "선크림과 프라이머를 한 번에". SPF50+ PA++++는 국가별 등록 확인 전 말하지 않음 {R}'),
    ('P3-2', '1:40–2:05', 'S', '하단 D: <code>선베이스 바르는 영상.mp4</code> (1080², 10.4초) 루프', "Look at the texture. It's a watery essence. It spreads like a light lotion — no white cast, no sticky feeling.", f'{D("공식몰")} 수분 에센스 제형·로션처럼·백탁 없이·답답함 없이'),
    ('P3-3', '2:05–2:20', 'S', '하단 D: <code>선베이스 볼 광채.mp4</code> (6.8초)', 'And it feels cool when you put it on. Perfect for hot mornings, or when your sunscreen feels too heavy.', f'"cooling feel"까지만. 피부 온도 −15.74%·만족도 100% 미사용 {R}'),
    ('P4-1', '2:20–2:40', 'H+G', '호스트 + 클래식 누끼 (30ml 에어리스 펌프)', 'Next, the bestseller of the line — Prime Primer Classic. This is a cream primer, and it is the step right before your foundation.', f'{D("Product Spec v6")} "장기 스테디셀러". "bestseller"는 판매 근거 확인 전 → "the classic of the line"로 대체 가능 {R}'),
    ('P4-2', '2:40–3:10', 'S', '하단 D: <code>1_클래식 영상.mp4</code> (1080², 18.3초)', "Just one pea-sized drop. Press it in, like you're filling in your pores. See? The skin texture looks smoother, and pores look less visible.", f'{D()} 완두콩 크기·모공 채우듯. "look smoother / look less visible" 외관 표현만 {R}'),
    ('P4-3', '3:10–3:35', 'H', '호스트, 손가락 하나 들기', 'A little really goes a long way — too much can make your base slide. So one drop, and your cushion goes on smooth and sits nicely.', f'{D()} 소량 사용·과다 시 밀림 VOC. 지성 T존 보송 → "stays fresh-looking"만 {R}'),
    ('P4-4', '3:35–3:45', 'G', '사용법 카드: 1 pea-size → 2 press → 3 wait 30 sec → cushion', 'V/O: Pea-size, press, wait a moment, then your base.', '"잠시 뒤" 문서 표현 → 30초는 제안값 '+X('BM 확인')),
    ('P5-1', '3:45–4:05', 'H+G', '호스트 + 피니쉬 파우더 누끼 (12g)', "Now, Prime Primer Finish Powder. It's a translucent loose powder, so it won't change the shade of your cushion.", f'{D("Product Spec v8")} 투명 루스 파우더'),
    ('P5-2', '4:05–4:35', 'S', '하단 D: <code>피니쉬 파우더 영상.mp4</code> (19.5초) → <code>파우더 뜯어내기.mp4</code> (4.2초)', 'Tip — tap a little onto the lid first, then pick it up with your puff. Less mess, and you only use what you need.', f'{D()} 뚜껑에 덜어 퍼프 (가루 날림 방지)'),
    ('P5-3', '4:35–4:55', 'S', '하단 D: <code>파우더 비포.mp4</code> → <code>파우더 애프터.mp4</code> 분할 (4.5초 + 3.9초)', 'Before… and after. Shine looks blotted, and your skin looks soft-matte — not cakey.', f'비포·애프터 원본 영상 그대로(보정 없음 확인 {X()}). 유분 감소·8시간 모공 커버 수치 미사용 {R}'),
    ('P5-4', '4:55–5:05', 'H', '호스트', 'Use just a little. Press it on the T-zone, and you are done.', '과다 시 다크닝 Pain Point 대응'),
    ('P6-1', '5:05–5:25', 'H+G', '호스트 + 세팅 픽서 누끼 (100ml)', 'Last step — Prime Primer Setting Fixer. This is what keeps everything in place.', f'{D("Product Spec v6")}'),
    ('P6-2', '5:25–5:50', 'S', '하단 D: <code>프라임 프라이머 세팅픽서.mp4</code> (4.5초) 슬로 + <code>세팅 픽서 지속력.mp4</code> (6.2초)', 'Look at this mist — so fine, it falls evenly on your face. No big drops. Hold it about twenty centimeters away and spray twice.', f'{D()} 미세 분사·20cm·2회. <code>지속력.mp4</code>에 시간 수치 자막이 박혀 있으면 이 구간 제외 {X("번인 육안 확인")}'),
    ('P6-3', '5:50–6:10', 'H', '호스트, 퍼프 드는 손짓', 'Another tip — spray it on your puff, then press. Your makeup stays put on hot, humid days, and the finish is a soft semi-matte.', f'{D()} 퍼프 팁·세미매트. 24H·스웨트/워터프루프 시험은 쓰지 않음 {R}'),
    ('P6-4', '6:10–6:20', 'G', '이중 뚜껑 누끼 확대 카드', 'V/O: And it has a double cap, so it is easy to carry in your bag.', f'{D()} 이중 뚜껑'),
    ('P7', '6:20–7:00', 'H+G', 'FAQ 카드 2장 (피부 타입별)', 'Quick tips! Oily skin? Use Classic on your T-zone and set it with powder. Dry skin? Use less powder, and try the fixer on your puff. You can start with one, or build the whole routine.', f'전자책 피부 타입별 답변 매뉴얼. 병용 효과 주장 없음. 건성 픽서 자극 Pain Point 있음 → 문안 {R}'),
    ('P8', '7:00–7:20', 'G+H', '혜택 배너 (9장 V1 프로모션)', 'One more time: the whole Prime Primer line is fifty percent off today, with a free gift.', '국가 레이어: 가격·사은품'),
    ('EC', '7:20–7:50', 'H+G', '공통 엔딩 (3-0) → OC로 루프', None, None),
]
v2 = [
    ('OC', '0:00–0:20', 'B→H', '공통 오프닝 (3-0). 헤드라인 "ADD SOME COLOR"', None, None),
    ('O-L', '0:20–0:40', 'H+G', '호스트 + 혜택 배너', "Today it's all about color — Romantic Blush Lip &amp; Cheek. And it's buy two, get one today, so this is the day to build your set!", '국가 레이어: 기간·조건'),
    ('L0', '0:40–1:05', 'G+H', '"Today\'s look" 카드: 05호 립·치크 발색컷 (같은 색 톤온톤)', "Here's today's look: soft rosy cheeks and lips — all with one shade, 05. One stick, and your whole face matches.", '전자책 색조 ① 오늘의 룩. 05 = 문서 "최고 호응" 컬러'),
    ('L1', '1:05–1:45', 'H+G', '호스트 + 12색 진열(누끼) + USP 카드 ①', 'Why do people love it? Number one — it is one stick for your lips and your cheeks. Fewer things in your pouch, and a matching look in seconds.', f'{D("Product Spec v10")} USP① 멀티유즈·톤온톤'),
    ('L2', '1:45–2:25', 'D', '<code>8호 손바닥 그리기.gif</code> (1.7초) → <code>8호 손바닥 퍼뜨리기.gif</code> (2.9초) → 볼 발색', "Number two — the texture. It's a cream balm that melts with your body heat. Warm it on the back of your hand first, then tap it on with a puff. That way your base stays smooth.", f'{D()} 멜팅 밤·손등 워밍업 → 퍼프. 베이스 까짐 VOC(50건 중 10건+) 대응'),
    ('L3', '2:25–3:05', 'S', '좌 1겹 / 우 2겹 분할 (발색컷 <code>23호 발색_드로잉.mp4</code>·<code>23호 발색_블렌딩.mp4</code> 또는 받은 1회·2회 발색컷)', 'Number three — it is buildable. One layer looks sheer, like watercolor. Two layers — deeper color. And it does not clump when you layer it.', f'{D()} 빌더블·"수채화처럼"·쌓아도 뭉침 없는. 23호는 방송 12색이 아님 → 방송 컬러 소스로 교체 {X("방송 컬러 2겹 소스 확인")}'),
    ('L4', '3:05–3:30', 'D', '<code>립 발색_24호.mov</code> (7.7초) → 입술 톡톡', "For lips — a little lip balm first, then tap it on. Soft and natural.", f'각질 부각 VOC 대응. 24호는 방송 12색 아님 → 방송 컬러 소스로 교체 {X()}'),
    ('L4-2', '3:30–3:45', 'H+G', '스틱 누끼 확대 (잠금 캡)', 'Number four — it is a stick with a lock cap. No fingers, no tools — just throw it in your bag for quick touch-ups.', f'{D()} USP③ 스틱·잠금 캡·휴대'),
    ('L5', '3:45–5:15', 'G', '호수별 발색 배너 (립·치크 발색 1080×1920, 9장) 12색 순서대로, 호수당 약 7초', 'V/O (호수마다 1문장): 02, Pink Some — a light cool pink. 04, Flora — strawberry milk. 05, Laura Pink — our most-loved pink… (12색)', f'전자책 색조 ② 발색 분할. 영문 컬러명 미확정 → 번호만 말하고 이름은 확정 후 {X("R6 영문 컬러명")}. 품절 컬러 SOLD OUT 레이어'),
    ('L6', '5:15–6:05', 'G+H', '퍼스널컬러 트리오 카드 3장 (쿨 / 웜 / 공용)', 'Number five — find your trio! Cool tones, try 02, 05 and 09. Warm tones, 12, 17 and 18. Not sure? 04, 08 and 13 suit both.', f'{D("매장 컬러 가이드")} 전자책 색조 ③ 퍼스널컬러. 14·20 분류 근거 없음 {X("BM 확인")}'),
    ('L7', '6:05–6:40', 'H+G', '상황별 추천 카드 (Office / Date / Weekend)', 'For the office, try 07 or 08 — soft and natural. For a date, 05 or 13. For a cozy weekend look, 17.', f'전자책 색조 ③ 상황별 추천. 무드 분류(Milky·Muted·Mellow·Moody)는 문서 근거, 상황 매칭은 {P}'),
    ('L8', '6:40–7:00', 'G+H', 'Buy 2 Get 1 카드: 2개 담기 → 1개 무료 → 트리오 완성', 'And here is why today is the day: buy two, get one. So pick your trio — one for lips, one for cheeks, and one backup for your bag!', f'"살 이유" = B2G1로 트리오 완성. 무료 1개 선택 조건 {X("R3")}'),
    ('EC', '7:00–7:30', 'H+G', '공통 엔딩 (3-0) → OC로 루프', None, None),
]
v3 = [
    ('OC', '0:00–0:20', 'B→H', '공통 오프닝 (3-0). 헤드라인 "MELT IT OFF"', None, None),
    ('O-B', '0:20–0:40', 'H+G', '호스트 + 밤 3종 진열(누끼) + 혜택 배너', "Today it's all about Clean it Zero cleansing balm — three balms for three skin types. And they are all fifty percent off today, with a free gift!", '국가 레이어: 기간·사은품·가격'),
    ('C1', '0:40–1:05', 'B→H', '저녁 욕실 무드 B-roll → 호스트', 'End of a long, hot day. Sunscreen, base, maybe waterproof mascara… Now, let\'s melt it all off.', '전자책 기초 ① 고민 오프닝'),
    ('C2-1', '1:05–1:35', 'D', '<code>클린잇 제로 오리지널 밤 제형 스패출라.mp4</code> (1920², 20.3초)', 'V/O: Scoop it with the spatula. It looks like sherbet… and the moment it touches your skin, it melts into a silky oil.', f'{D("공식몰")} 셔벗 → 오일. 스패출러는 180/100/50ml 포함, 25ml 미포함 (자막 각주)'),
    ('C2-2', '1:35–2:05', 'D', '<code>클린잇 제로 오리지널 밤 제형 손등클렌징.mp4</code> (10.6초) → <code>…밤 제형.mp4</code> (5.2초)', 'V/O: Massage it over dry skin. Watch how the makeup melts away. Then add a little water — it turns milky — and rinse it off.', f'{D("공식몰")} 마른 얼굴 마사지 → 물 → 유화 → 헹굼. 배속 구간이면 "Time-lapse" 표기 {X("배속 여부")}'),
    ('C3-1', '2:05–2:25', 'H+G', '호스트 + 오리지널 누끼 (핑크 용기) + 카드 "ORIGINAL · All-in-one"', 'First, Clean it Zero Original — the all-in-one. It takes off everything, from sunscreen to waterproof makeup, in one step.', f'{D("공식몰")} "자외선 차단제부터 워터프루프까지 올인원 딥 클렌징". 99% 세정력·판매량 미사용 {R}'),
    ('C3-2', '2:25–2:45', 'H+G', '성분 카드: Acerola · Jojoba seed oil', 'It is made with acerola and jojoba seed oil, and it feels soft — not tight — after you rinse.', f'{D("공식몰")} ACEROLA+·호호바씨오일. 성분은 이름만, 효능(항산화·보습 %) 미사용. "not tight"는 사용감 {R}'),
    ('C3-3', '2:45–3:05', 'H', '호스트', 'If you are not sure where to start, or you wear a lot of makeup, Original is your everyday balm.', 'Original = 기본·데일리 포지션 '+P),
    ('C4-1', '3:05–3:25', 'H+G', '호스트 + 포어 클래리파잉 누끼 (그린 용기) + 카드 "PORE CLARIFYING · Fresh finish"', 'Next, Clean it Zero Pore Clarifying. This one is for oily and combination skin — it gives you a really fresh, clean finish.', f'{D("공식몰")} 지복합성 대상·산뜻한 마무리. 여드름성 피부·논코메도제닉·피지·블랙헤드 감소 미사용 {R}'),
    ('C4-2', '3:25–3:50', 'D+G', '<code>원본영상/손등.MP4</code> (16.8초) 일부 + 성분 카드: Tea tree · AHA · BHA · PHA · LHA', 'V/O: It has tea tree, plus a blend of AHA, BHA, PHA and LHA — so your skin feels smooth and refreshed after cleansing.', f'{D("공식몰")} Tea tree-EX·Pore-Peel Acid. 산 성분은 "feels smooth"까지만, 각질 12%·유분 27% 미사용 {R}'),
    ('C4-3', '3:50–4:05', 'H', '호스트', 'The balm is a natural green color from plants, with a fresh green tea scent.', f'{D("공식몰")} 식물유래 초록빛·인공색소 ZERO·그린티 향. "fragrance-free" 금지'),
    ('C5-1', '4:05–4:25', 'H+G', '호스트 + 카밍 누끼 (블루 용기) + 카드 "CALMING · Gentle"', 'And for sensitive-feeling skin — Clean it Zero Calming. It is a gentle, low-pH cleanser, close to your skin\'s natural pH.', f'{D("공식몰")} 초민감·미산성 포뮬러. "soothes redness" 등 진정 효능 미사용 {R}'),
    ('C5-2', '4:25–4:45', 'G', '성분 카드: Cica blend · Calming aroma (eucalyptus · bergamot · rosemary · chamomile)', 'V/O: It has a cica blend, and a calming aroma from essential oils like eucalyptus, bergamot and chamomile.', f'{D("공식몰")} Cica-Relief·CALMING AROMA 에센셜 오일. 붉어짐 27% 감소 미사용 {R}. 향 있음 → "fragrance-free" 금지'),
    ('C5-3', '4:45–5:05', 'H', '호스트', 'The soft blue color comes from plants, too. If your skin feels sensitive, this is the one to try.', f'{D("공식몰")} 식물유래 블루. 저자극 시험은 국내 시험 → 문구 미사용 {R}'),
    ('C6', '5:05–5:50', 'G+H', 'FAQ 카드 "Which balm is for me?" 3열 비교 (Original / Pore / Calming)', 'So, which one is yours? Wear a lot of makeup, or want an all-rounder — Original. Oily or combination skin — Pore Clarifying. Sensitive-feeling skin — Calming.', f'전자책 피부 타입별 답변 매뉴얼. 채팅 FAQ 같은 답 {R}'),
    ('C7', '5:50–6:15', 'G', '공통 3단계 카드: 1 dry hands, dry face → 2 massage → 3 add water, rinse with lukewarm water', 'V/O: Remember — dry hands, dry face. Massage, add a little water, then rinse with lukewarm water.', f'{D("공식몰")} STEP: 마른 얼굴·마사지·미온수 세안'),
    ('C8', '6:15–6:35', 'G', '사이즈 카드 (판매 사이즈만)', 'V/O: Pick the size that suits you — a small one for travel, or a big one for every day.', f'국가별 판매 사이즈 {X("R1")} — 숫자 미언급'),
    ('C9', '6:35–6:55', 'G+H', '혜택 배너 (9장 V3 프로모션)', 'One more time: all three Clean it Zero balms are fifty percent off today, with a free gift.', '국가 레이어'),
    ('EC', '6:55–7:25', 'H+G', '공통 엔딩 (3-0) → OC로 루프', None, None),
]


def table(rows):
    out = ['  <div class="tbl"><table>', HEAD]
    for r in rows:
        k, t, ty, scr, vo, note = r
        if vo is None:
            out.append(f'    <tr><td>{k}</td><td>{t}</td><td>{ty}</td><td colspan="3">{scr}</td></tr>')
        else:
            out.append(f'    <tr><td>{k}</td><td>{t}</td><td>{ty}</td><td>{scr}</td><td class="vo">{vo}</td><td>{note}</td></tr>')
    out.append('  </table></div>')
    return '\n'.join(out)


s3.append('  <h3>3-1. V1 Prime Primer — 아침 "Prep &amp; Stay" (약 7:50)</h3>')
s3.append(f'  <p class="small">{U} 제품별 소개 보강 — 4종 모두 <b>무엇인지 → 제형·시연 → 사용 팁 → 이런 분께</b> 순서로 60~75초씩. 근거: USP 브리프 2장(Product Spec v6·v8, 공식몰 product_no 1201).</p>')
s3.append(timeline('V1 타임라인', [('OC', 20, GREY), ('O-P', 20, '#c06a95'), ('P1·P2', 40, '#e9579a'), ('Sun Base', 60, '#e9579a'), ('Classic', 85, '#d24a8a'), ('Powder', 80, '#e9579a'), ('Fixer', 75, '#d24a8a'), ('FAQ', 40, '#c06a95'), ('P8', 20, '#c06a95'), ('EC', 30, GREY)]))
s3.append(table(v1))
s3.append('  <h3>3-2. V2 Romantic Blush Lip &amp; Cheek — 낮 "Add some color" (약 7:30)</h3>')
s3.append(f'''  <p class="small">{U} USP·살 이유 반영 — USP 5가지를 번호로 말해 기억하게 하고("Number one…five"), 마지막에 "왜 오늘 사야 하는지"를 B2G1 트리오로 연결합니다. 근거: USP 브리프 3장(Product Spec v10).</p>
  <div class="grid3">
    <div class="card"><h4>① 립·치크 한 자루</h4>입술과 볼을 같은 색으로, 톤온톤 룩을 몇 초 만에. 파우치 속 아이템이 줄어듦</div>
    <div class="card"><h4>② 체온에 녹는 크림 밤</h4>손등 워밍업 → 퍼프로 톡톡, 베이스가 까지지 않게</div>
    <div class="card"><h4>③ 빌더블</h4>1겹 수채화처럼 맑게, 2겹 선명하게, 쌓아도 뭉침 없음</div>
    <div class="card"><h4>④ 스틱 + 잠금 캡</h4>손·도구 없이, 가방 속 수정용</div>
    <div class="card"><h4>⑤ 12색 · 4무드</h4>Milky·Muted·Mellow·Moody, 퍼스널컬러 트리오·상황별 추천</div>
    <div class="card"><h4>살 이유 (오늘)</h4>Buy 2 Get 1 → 립용·치크용·가방용 트리오 완성</div>
  </div>''')
s3.append(timeline('V2 타임라인', [('OC', 20, GREY), ('O-L', 20, '#b8742e'), ('L0 룩', 25, '#d9822b'), ('L1–L4 USP', 180, '#d9822b'), ('L5 발색', 90, '#c96f1f'), ('L6 트리오', 50, '#d9822b'), ('L7', 35, '#d9822b'), ('L8', 20, '#b8742e'), ('EC', 30, GREY)]))
s3.append(table(v2))
s3.append('  <h3>3-3. V3 Clean it Zero 클렌징밤 3종 — 저녁 "Melt it off" (약 7:25)</h3>')
s3.append(f'''  <p class="small">{U} 유형별 특징 충분히 — 3종을 각각 <b>누구에게 → 성분 → 색·향·사용감 → 이런 분께</b> 순서의 단독 장면(약 60초)으로 나누고, 공통 시연(C2)과 "내 피부엔 어떤 밤?"(C6)을 따로 둡니다. 근거: USP 브리프 1장(공식몰 product_no 669·667·670, 2026-10-13 조회).</p>
  <div class="tbl"><table>
    <tr><th>구분</th><th>Original (핑크)</th><th>Pore Clarifying (그린)</th><th>Calming (블루)</th></tr>
    <tr><td>누구에게</td><td>메이크업 많이 하는 날, 처음 고르는 사람 · 올인원</td><td>지성·복합성, 산뜻한 마무리를 원하는 사람</td><td>민감하게 느껴지는 피부</td></tr>
    <tr><td>VO에 쓰는 성분</td><td>Acerola, jojoba seed oil</td><td>Tea tree, AHA·BHA·PHA·LHA</td><td>Cica blend, essential oils(eucalyptus·bergamot·rosemary·chamomile)</td></tr>
    <tr><td>색·향</td><td>—</td><td>식물유래 초록빛, 그린티 향</td><td>식물유래 블루, Calming aroma</td></tr>
    <tr><td>사용감 (VO)</td><td>sunscreen~waterproof까지 한 번에, 헹군 뒤 당기지 않음</td><td>fresh, clean finish · smooth and refreshed</td><td>gentle, low-pH (피부 pH와 유사)</td></tr>
    <tr><td>쓰지 않는 것 {R}</td><td>99%·1억 개·재구매 1위·항산화 6.98배·블랙헤드 %</td><td>여드름성 피부·논코메도제닉·피지·블랙헤드·각질 %</td><td>붉어짐 감소·진정 효능·% 수치</td></tr>
  </table></div>''')
s3.append(timeline('V3 타임라인', [('OC', 20, GREY), ('O-B', 20, '#1f5fb8'), ('C1', 25, '#2878e8'), ('C2 시연', 60, '#1f5fb8'), ('Original', 60, '#2878e8'), ('Pore', 60, '#1f5fb8'), ('Calming', 60, '#2878e8'), ('C6 FAQ', 45, '#1f5fb8'), ('C7·C8', 50, '#2878e8'), ('C9', 20, '#1f5fb8'), ('EC', 30, GREY)]))
s3.append(table(v3))
s3.append(f'''  <ul>
    <li><b>문장 패턴</b>: 영상별 오프닝 "Today it's all about ___", 혜택 엔딩 "One more time: ___". 혜택 문장에는 할인율만 넣고 가격·기간·사은품명은 배너로만 보여줍니다.</li>
    <li><b>길이</b>: 장면별 배정 시간의 합(계획값). T2A·H3 생성 후 실제 길이로 맞춥니다.</li>
    <li><b>컷다운</b> {P}: 영상별 60초 1편 — V1 OC-1+P4-2+P5-3+P6-2+P8+EC-2 / V2 OC-1+L0+L3+L6+L8+EC-2 / V3 OC-1+C2-1+C2-2+C6+C9+EC-2.</li>
    <li>VO 전체는 RA 검토 전입니다. 승인 전에는 T2A 본합성·H3 본생성을 하지 않습니다.</li>
  </ul>
</section>''')
put('s3', '\n'.join(s3))

# ---------------------------------------------------------------- 7 파이프라인 (립싱크 제외)
put('s7', f'''<section id="s7">
  <h2><span class="n">7</span>생성 파이프라인 (립싱크 제외)</h2>
  <h3>7-1. 호스트가 말하는 방식 — 립싱크 단계 없음 {U}</h3>
  <div class="callout ok">v2의 립싱크 재현 테스트(LS-1~3)·<code>LIPSYNC_LOCK.md</code>·HeyGen 예비 경로를 모두 뺐습니다. 호스트(H) 장면은 <b>MiniMax H3가 프롬프트에 적힌 대사를 직접 말하는 영상</b>으로 생성합니다. 목소리 톤을 맞추기 위해 확정한 T2A 보이스(6장)로 만든 짧은 샘플을 <code>reference_audio</code>로 함께 넣습니다. POC에서 이 방식으로 studio03이 대본대로 생성됐습니다 {M()} (<a href="#s14">14장</a>).</div>
  <div class="tbl"><table>
    <tr><th>장면 유형</th><th>소리</th><th>입 모양</th></tr>
    <tr><td>H (호스트 화면)</td><td>H3가 생성한 음성 (대사 = 확정 대본, 톤 = T2A 보이스 샘플 참조)</td><td>H3가 함께 생성 → 별도 정렬 없음</td></tr>
    <tr><td>D·G (호스트 없음)</td><td>T2A 음성 (V/O)</td><td>해당 없음</td></tr>
    <tr><td>S (분할)</td><td>상단 H 클립 음성</td><td>H3 생성</td></tr>
  </table></div>
  <p><b>대가</b>: H3가 대본에 없는 말을 섞을 수 있습니다(POC studio04 실측 사례). 그래서 생성 직후 <b>ASR 대사 가드</b>를 반드시 돌립니다 → 7-2의 6번 단계, 14장.</p>

  <h3>7-2. 단계별 실행</h3>
  <div class="tbl"><table>
    <tr><th>#</th><th>작업</th><th>입력</th><th>출력 위치</th></tr>
    <tr><td>1</td><td>캐릭터 시트 CS-00 후보 → 선정 → CS-01~04 (GPT 이미지)</td><td>5장 프롬프트</td><td><code>4_테스트/character/</code> → <code>5_에셋/character_sheet/</code></td></tr>
    <tr><td>2</td><td>세트 SET-00 + 마스터 프레임</td><td>CS-02 + 세트</td><td><code>5_에셋/set/</code>·<code>5_에셋/master_frame/</code></td></tr>
    <tr><td>3</td><td>T2A 보이스 후보 → voice_id 확정 → H3용 참조 샘플(≤15초)</td><td>6장</td><td><code>5_에셋/voice/</code></td></tr>
    <tr><td>4</td><td>대본 RA 승인 → D·G 장면 V/O를 T2A로 전량 합성</td><td>3장 확정 대본</td><td><code>2_나레이션/master/</code></td></tr>
    <tr><td>5</td><td>H 클립 생성 (H3, 9:16, 청크 ≤15초)</td><td>마스터 프레임 + 대사 + 참조 샘플</td><td><code>3_소스클립/host/</code></td></tr>
    <tr><td><b>6</b></td><td><b>ASR 대사 가드</b>: 대본과 다른 말 구간 검출 → 짧으면 편집에서 삭제, 길거나 중간이면 재생성</td><td>H 클립 + 대본</td><td><code>4_테스트/asr_guard/</code></td></tr>
    <tr><td>7</td><td>컷 검사: 클립 안 장면 전환(정적 샷 지시에도 발생 가능, POC studio03) → 허용 또는 재생성</td><td>H 클립</td><td><code>4_테스트/</code></td></tr>
    <tr><td>8</td><td>B-roll: H3 9:16, 6~10초 (습한 거리, 저녁 욕실, 제품·인물 없음)</td><td>프롬프트</td><td><code>3_소스클립/broll/</code></td></tr>
    <tr><td>9</td><td>시연 소스 배치·9:16 크롭 (8장 배정표)</td><td>받은 상세페이지 영상</td><td><code>3_소스클립/demo/</code></td></tr>
    <tr><td>10</td><td>채택 H 클립만 2K 재생성 (필요 시)</td><td>채택 task</td><td><code>3_소스클립/host_2k/</code></td></tr>
    <tr><td>11</td><td>배너·국가 레이어 (9장)</td><td>누끼·가격표</td><td><code>5_에셋/banner/</code></td></tr>
    <tr><td>12</td><td>편집: 영상 3편 × 국가 4벌 = 12본, 자막</td><td>전체</td><td><code>1_최종영상/{{V1|V2|V3}}/{{TH|MY|ID|VN}}/</code></td></tr>
  </table></div>

  <h3>7-3. H 클립 프롬프트 골격 {P}</h3>
<pre>9:16 vertical, static medium shot, livestream shopping host. One continuous take, no cuts.
Image 1: host (face, hair, outfit must match exactly).
A young woman in her early 20s seated behind a white table in a pink studio,
talking warmly to camera, natural small hand gestures at chest height, gentle nods.
She says exactly this line in English, and nothing else:
"&lt;확정 대사 1청크, 약 30단어 이하&gt;"
Then she stops speaking and smiles at the camera until the end.
Empty table surface: no products, no bottles, no text, no logos.
Soft even beauty lighting, no camera movement [Static shot].
No accessories, no rings, no watch. Hands stay below the chin.</pre>
  <p class="small">"exactly this line … nothing else", 대사 뒤 "stops speaking and smiles", 클립 길이 = 대사 길이 + 1초 — POC studio04에서 대사 사이·뒤에 생긴 이탈 발화를 줄이기 위한 문구입니다. 효과는 아직 검증 전 {X('추정')} (14장).</p>

  <h3>7-4. 생성 물량 (비용 산정 안 함)</h3>
  <div class="tbl"><table>
    <tr><th>구분</th><th>화면 시간</th><th>물량</th></tr>
    <tr><td>H (단독·S 상단 포함)</td><td>약 12분 {X('추정')}</td><td>청크 평균 12초 기준 약 60클립 + 재생성 여유. 공통 OC·EC 6클립은 1회만</td></tr>
    <tr><td>B-roll</td><td>약 20초</td><td>3~4클립</td></tr>
    <tr><td>D 시연</td><td>약 5분</td><td>받은 상세페이지 영상 (8장)</td></tr>
    <tr><td>G 그래픽·배너</td><td>약 5분</td><td>9장 배너 + 국가 4벌</td></tr>
  </table></div>
</section>''')

# ---------------------------------------------------------------- 8 시연 소스 배정
BASE = '5_에셋/이미지생성_소스'
put('s8', f'''<section id="s8">
  <h2><span class="n">8</span>시연 소스 — 받은 상세페이지 영상을 장면에 배정 {U}</h2>
  <p>별도 촬영·추가 수령 없이 <b>이미 받은 소스</b>(<code>{BASE}/</code>)로 D·S 장면을 채웁니다. 해상도·길이는 ffprobe로 잰 값입니다 {M()}. 화면 내용(번인 자막·워터마크·패키지 버전)은 아직 육안으로 보지 않았습니다 {X('미확인')} → 편집 전 컨택트시트로 확인합니다.</p>
  <div class="tbl"><table>
    <tr><th>장면</th><th>파일 (<code>{BASE}/</code> 아래)</th><th>해상도 · 길이</th><th>9:16 배치</th></tr>
    <tr><td>P3-2·3 선 베이스</td><td><code>2.프라임 라인/프라임 프라이머 선 베이스/상세페이지/선베이스 바르는 영상.mp4</code> · <code>선베이스 볼 광채.mp4</code></td><td>1080×1080 · 10.4초 / 6.8초</td><td>S 하단 정사각 창</td></tr>
    <tr><td>P4-2 클래식</td><td><code>…/프라임 프라이머 클래식/상세페이지/1_클래식 영상.mp4</code></td><td>1080×1080 · 18.3초</td><td>S 하단 정사각 창</td></tr>
    <tr><td>P5-2·3 피니쉬 파우더</td><td><code>…/피니쉬 파우더 12g/상세페이지/피니쉬 파우더 영상.mp4</code> · <code>GIF/영상/프라임 프라이머 파우더  뜯어내기.mp4</code> · <code>…파우더 비포.mp4</code> · <code>…파우더 애프터.mp4</code></td><td>1080² 19.5초 · 1920×1080 4.2 / 4.5 / 3.9초</td><td>정사각 창 / 비포·애프터 좌우 분할(가로 원본을 각각 크롭)</td></tr>
    <tr><td>P6-2 세팅 픽서</td><td><code>…/세팅 픽서 100ml/상세페이지/GIF/영상/프라임 프라이머 세팅픽서.mp4</code> · <code>…세팅 픽서 지속력.mp4</code></td><td>1920×1080 · 4.5초 / 6.2초</td><td>가로 창(16:9) 또는 중앙 크롭</td></tr>
    <tr><td>L2 립앤치크 워밍업</td><td><code>3.로맨틱 립앤치크/발색컷/4_gif/8호 손바닥 그리기.gif</code> · <code>8호 손바닥 퍼뜨리기.gif</code></td><td>2160² · 1.7초 / 2.9초</td><td>D 전체(정사각 확대)</td></tr>
    <tr><td>L3 1겹·2겹</td><td><code>…/4_gif/영상/23호 발색_드로잉.mp4</code> · <code>23호 발색_블렌딩.mp4</code> · <code>13호 립/치크 발색.gif</code></td><td>2160² 3.3초 · 1080² 2.6초 · 2160² 5.8초</td><td>좌우 분할. <b>23호는 방송 12색이 아님</b> → 13호 등 방송 컬러 우선</td></tr>
    <tr><td>L4 입술</td><td><code>…/4_gif/13호 립 발색.gif</code> (방송 컬러) · <code>립 발색_24호.mov</code></td><td>2160² · 5.8초 / 7.7초</td><td>D 전체. 24호는 방송 컬러 아님 → 13호 우선</td></tr>
    <tr><td>L5 호수별 발색</td><td><code>3.로맨틱 립앤치크/발색컷/</code> 립·치크 발색 정지컷 (호수별)</td><td>정지 이미지</td><td>호수별 발색 배너(9장)로 G 화면</td></tr>
    <tr><td>L1 텍스처 보조</td><td><code>3.로맨틱 립앤치크/제형/로맨틱 블러쉬 립 앤 치크 02 핑크썸 텍스처.mp4</code></td><td><b>2160×3840 (유일한 9:16)</b> · 10.4초</td><td>D 전체 화면</td></tr>
    <tr><td>C2-1 셔벗→오일</td><td><code>1.클렌징밤/클린 잇 제로 오리지널/3.제형/클린잇 제로 오리지널 밤 제형 스패출라.mp4</code></td><td>1920×1920 · 20.3초</td><td>정사각 창</td></tr>
    <tr><td>C2-2 마사지·헹굼</td><td><code>…/3.제형/클린잇 제로 오리지널 밤 제형 손등클렌징.mp4</code> · <code>…밤 제형.mp4</code></td><td>1920×1080 · 10.6초 / 5.2초</td><td>가로 창</td></tr>
    <tr><td>C4-2 포어</td><td><code>1.클렌징밤/2. 클린 잇 제로 포어 클래리파잉/상세페이지컷/원본영상/손등.MP4</code> (볼·입술 영상도 있음)</td><td>1920×1080 · 16.8초 (볼 47.3초, 입술 31.9초)</td><td>가로 창</td></tr>
    <tr><td>C5 카밍</td><td><b>시연 영상 없음</b> {M('목록 확인')}</td><td>—</td><td>누끼 + 성분 카드(G)로 대체</td></tr>
  </table></div>
  <ul>
    <li><b>음성</b>: 원본 영상 소리·BGM은 빼고 호스트 VO만 씁니다.</li>
    <li><b>배속</b>: 배속 구간이 있으면 "Time-lapse" 표기. 발색은 보정하지 않습니다.</li>
    <li><b>보조 소스</b>: 클렌징밤 오리지널은 POC 때 NAS에서 받은 공식 영상(제형·스패출라·손등, <code>banila-shopee-poc-20261006-v1/5_에셋/nas_clean_it_zero/</code>)도 같은 원본입니다. 손등 영상은 SHA-256 동일 확인 {M()}.</li>
    <li><b>패키지 버전</b>: 11월 판매 패키지와 같은지 확인 {X()}.</li>
  </ul>
</section>''')

# ---------------------------------------------------------------- 10 검수
html = html.replace('<tr><td>립싱크</td><td>지연 2프레임 이내, 오디오 = TTS 원본</td><td>LIPSYNC_LOCK 재적용 / 예비 경로</td></tr>',
                    '<tr><td>대사</td><td>ASR 대사 가드 통과 — 대본에 없는 말 0. 이탈 구간은 편집에서 삭제</td><td>삭제 컷 / 재생성</td></tr>\n    <tr><td>컷</td><td>H 클립 안 장면 전환 없음 (ffmpeg 장면 감지)</td><td>허용 판단 / 재생성</td></tr>')
html = html.replace('(task_id, 모델, 프롬프트, 레퍼런스, seed, 길이, LIPSYNC_LOCK 버전, 판정, 사유)', '(task_id, 모델, 프롬프트, 레퍼런스, seed, 길이, ASR 가드 판정, 판정, 사유)')

# ---------------------------------------------------------------- 11 제작 순서
put('s11', f'''<section id="s11">
  <h2><span class="n">11</span>제작 순서 — 확정 게이트 먼저 {U}</h2>
  <div class="callout warn"><b>영상 생성 게이트</b> — 캐릭터 시트(5장)와 스토리보드(3장)가 확정되기 전에는 영상(H3)을 생성하지 않습니다. 확정되면 영상 생성을 시작합니다.</div>
  <div class="tbl"><table>
    <tr><th>단계</th><th>작업</th><th>시작 조건</th><th>병행</th></tr>
    <tr><td>①</td><td>캐릭터 시트 후보 → <b>CS-00 확정</b></td><td>즉시 (후보 생성 완료, 5장)</td><td>②·③·④</td></tr>
    <tr><td>②</td><td>스토리보드 v3 → RA 검토 → <b>확정</b></td><td>즉시</td><td>①</td></tr>
    <tr><td>③</td><td>T2A 보이스 후보 청취 → voice_id 확정</td><td>즉시 (후보 6장)</td><td>①·②</td></tr>
    <tr><td>④</td><td>배너·레이아웃 1차 → 수정</td><td>즉시 (1차 생성 완료, 4·9장)</td><td>①~③</td></tr>
    <tr><td>⑤</td><td>CS-01~04 · 세트 · 마스터 프레임</td><td>① 확정</td><td>⑥</td></tr>
    <tr><td>⑥</td><td>V/O T2A 합성 (공통 OC·EC 먼저)</td><td>② 확정 + ③</td><td>⑤</td></tr>
    <tr><td>⑦</td><td><b>H 클립 생성 → ASR 대사 가드 → 컷 검사</b></td><td>①·② 확정 + ⑤ + ③</td><td>⑧</td></tr>
    <tr><td>⑧</td><td>시연 소스 컨택트시트 확인·크롭</td><td>즉시</td><td>①~⑦</td></tr>
    <tr><td>⑨</td><td>편집 3편 + 국가 레이어 4벌</td><td>⑦·⑧ + 가격표(R1)</td><td>—</td></tr>
    <tr><td>⑩</td><td>최종 검수 → 컷다운 1편씩</td><td>⑨</td><td>—</td></tr>
  </table></div>
  <p>영상 순서: V1 프라이머 → V2 립앤치크 → V3 클렌징밤. 세 편은 서로 의존하지 않아 병행 가능합니다. 보이스 확정 뒤에는 6일 이내 간격 유지 합성을 계속합니다(6장).</p>
</section>''')

# ---------------------------------------------------------------- 12 리스크
html = html.replace('<tr><td>립싱크 설정이 이번 캐릭터·15초 클립에서 재현되지 않음</td><td>청크를 더 짧게(4~8초) → 그래도 실패하면 HeyGen 예비 경로</td></tr>\n    <tr><td>모델이 음성을 다시 만들어 대사가 바뀜</td><td>ASR 대조 → 원본 TTS로 오디오 교체 후 입 모양 재확인</td></tr>',
                    '<tr><td>H3가 대본에 없는 말을 섞음 (POC studio04 실측)</td><td>프롬프트 "exactly this line" + 청크 ≤30단어 → ASR 대사 가드 → 짧은 구간은 편집 삭제, 아니면 재생성 (14장)</td></tr>\n    <tr><td>정적 샷 지시에도 클립 안에 컷 발생 (POC studio03 실측)</td><td>장면 감지로 검출 → 허용 여부 판단, 레이아웃이 깨지면 재생성</td></tr>')

# ---------------------------------------------------------------- 13 요청사항 간소화
TAX = re.search(r'  <h3 id="s13-tax">13-2\..*?(?=\n  <h3>13-3\.)', html, re.S).group(0)
TAX_BODY = TAX.split('\n', 1)[1]
put('s13', f'''<section id="s13">
  <h2><span class="n">13</span>실무진 요청사항 · 문의사항 (간략본)</h2>
  <p class="small">자료는 <code>5_에셋/이미지생성_소스/</code>에 넣어 주세요. 이미 받은 것(누끼·시연 영상·발색컷)은 뺐습니다. 담당은 제안입니다.</p>
  <div class="tbl"><table>
    <tr><th>#</th><th>요청</th><th>쓰이는 곳</th><th>담당</th></tr>
    <tr><td>R1</td><td><b>국가별 가격</b> — TH·MY·ID·VN, SKU별 정가·판매가·통화 · 클렌징밤 판매 사이즈</td><td>배너 가격 레이어, V3 C8</td><td>채널·영업</td></tr>
    <tr><td>R2</td><td><b>사은품</b> — 품명(영문)·누끼·소진 시 대체 여부</td><td>혜택 배너, 각 영상 혜택 장면</td><td>채널·영업</td></tr>
    <tr><td>R3</td><td><b>Buy 2 Get 1 조건</b> — 무료 1개 선택 범위·중복 할인·1인 한도</td><td>V2 L8, 배너</td><td>채널</td></tr>
    <tr><td>R4</td><td><b>표현 승인(RA)</b> — 3장 VO 초안 전체, SPF50+ PA++++ 국가별 표기 가능 여부</td><td>VO·자막·배너</td><td>RA</td></tr>
    <tr><td>R5</td><td><b>누락 누끼</b> — 클렌징밤 오리지널 PNG, 카밍 50ml 정면, 180ml 3종, 립앤치크 09·14·20호</td><td>진열·배너</td><td>디자인</td></tr>
    <tr><td>R6</td><td><b>립앤치크 표기</b> — 12색 영문 컬러명, 국가별 품절 컬러, B. by BANILA 표기 방식</td><td>V2 L5, 발색 배너</td><td>BM·채널</td></tr>
    <tr><td>R7</td><td><b>Shopee 규격</b> — 4개국 배너·라이브 커버 크기·용량·안전 영역</td><td>배너 전체</td><td>채널</td></tr>
    <tr><td>R8</td><td><b>채팅 응대</b> — EC "질문 남기면 답변" 멘트의 실제 응대 담당·채널, 자주 오는 질문 5개</td><td>EC-3, FAQ 장면</td><td>채널·CS</td></tr>
    <tr><td>T</td><td><b>세금 각주</b> — 국가별 판매 주체(로컬/크로스보더)와 화면 가격의 세금 포함 여부 (근거는 아래 펼치기)</td><td>배너 각주</td><td>현지 재무·채널</td></tr>
  </table></div>
  <p class="small">v2의 R7 배너 PSD·폰트, R11 시연 영상, R12 Product Spec 정정은 v3에서 빠졌습니다(폰트는 무료 라이선스로 대체, 시연은 받은 소스 사용). Product Spec 정정 사항은 USP 브리프 4장에 그대로 있습니다.</p>
  <details id="s13-tax"><summary><b>세금 각주 근거 자료 (v2 13-2 원문, 펼치기)</b></summary>
{TAX_BODY}
  </details>
</section>''')

# ---------------------------------------------------------------- 14 POC
POC = HERE.parents[1] / 'poc_20261006' / 'banila-shopee-poc-20261006-v1'  # 저장소에는 없음(실험 코드 제외)
u = lambda p: (POC / p).as_uri()
put('s14', f'''<section id="s14">
  <h2><span class="n">14</span>POC 결과 — 무엇을 시험했고, 무엇을 바꿨나</h2>
  <div class="callout"><b>POC가 무엇이었나</b> — 본 제작 전에 <b>"MiniMax API로 AI 호스트가 영어로 말하는 15초 영상을 만들 수 있는지"</b>를 클렌징밤으로 시험한 것입니다. 호스트 이미지 1장 + 목소리 참조 음성 + 대사를 넣으면, H3가 호스트가 대사를 말하는 영상(소리 포함)을 만들어 줍니다. 이번 v3의 H 장면이 바로 이 방식입니다. <b>studio</b>는 그때 스튜디오 배경 클립에 붙인 작업 번호입니다(studio01·02 다음이 03·04).</div>
  <div class="poc-vids">
    <figure><video controls preload="metadata" playsinline poster="{u('4_테스트/studio03/poster.jpg')}" src="{u('1_최종영상/studio03_final.mp4')}"></video>
      <b>studio03 · 텍스처 소개</b> <span class="tag t-m">사용 확정</span> <span class="tag t-u">사용자 확인</span><br>
      대사가 대본과 일치(ASR 실측). 3.60초·11.37초 화면 전환은 사용자 검토 결과 문제 없음.</figure>
    <figure><video controls preload="metadata" playsinline poster="{u('4_테스트/studio04/poster.jpg')}" src="{u('1_최종영상/studio04_final.mp4')}"></video>
      <b>studio04 · 사용법 안내</b> <span class="tag t-r">대사 이탈</span> <span class="tag t-u">사용자 확인</span><br>
      6.9–9.7초에 대본에 없는 말("BAAC… pylacety"로 전사됨). → 아래 하네스로 막고, 생기면 편집으로 덜어냅니다.</figure>
  </div>
  <h3>14-1. 대사 이탈 대응 — 하네스 + 편집 삭제 {U}</h3>
  <div class="tbl"><table>
    <tr><th>단계</th><th>무엇을</th><th>어떻게</th></tr>
    <tr><td>막기 (생성 전)</td><td>프롬프트 하네스</td><td>대사를 따옴표로 정확히 넣고 "says exactly this line, and nothing else", 대사 뒤 "stops speaking and smiles", 청크 ≤30단어, 클립 길이 = 대사 + 1초 (7-3)</td></tr>
    <tr><td>잡기 (생성 직후)</td><td>ASR 대사 가드 <code>5_에셋/scripts/asr_script_guard.py</code></td><td id="asr-guard-detail">음성 인식으로 단어 시점을 뽑아 대본과 맞추고, 대본에 없는 말 구간을 찾아 판정(통과 / 편집 삭제 / 재생성)</td></tr>
    <tr><td>덜어내기 (편집)</td><td>삭제 컷 목록</td><td>가드가 낸 "남길 구간" 목록대로 이탈 구간을 잘라냄. 잘린 자리는 B-roll·그래픽 컷어웨이로 덮어 화면 튐을 가림</td></tr>
    <tr><td>재생성 기준</td><td>—</td><td>이탈이 문장 중간에 있어 잘라내면 대사가 끊기거나, 이탈이 클립의 큰 비중을 차지할 때</td></tr>
  </table></div>
  <p class="small">POC 원본 폴더: <code>poc_20261006/banila-shopee-poc-20261006-v1</code> (저장소에는 포함하지 않음).</p>
</section>''')

# 목차 갱신
html = html.replace('<a href="#s0">0. v2 변경 사항</a>', '<a href="#s0">0. v3 변경 사항</a>')
html = html.replace('<a href="#s7">7. 생성 파이프라인·립싱크</a>', '<a href="#s7">7. 생성 파이프라인</a>')
html = html.replace('<a href="#s8">8. 시연 소스 수령</a>', '<a href="#s8">8. 시연 소스 배정</a>')
html = html.replace('<a href="#s14">14. POC 실측 · 결정 필요</a>', '<a href="#s14">14. POC 결과 · 대사 가드</a>')
html = html.replace('<title>Shopee AI쇼호스트 제작설계</title>', '<title>Shopee AI쇼호스트 제작설계 v3</title>')
html = html.replace('<h1>Shopee 11월 AI 쇼호스트 — 제작 설계 v2</h1>', '<h1>Shopee 11월 AI 쇼호스트 — 제작 설계 v3</h1>')
html = re.sub(r'<p>작성 2026-10-13 · 같은 날 개정.*?</p>',
              '<p>작성 2026-10-13 · v3 같은 날 개정(요청 14건: 스토리보드 보강·립싱크 제외·캐릭터 시트·보이스 후보·레이아웃·배너·POC 대사 가드) · 내부 제작 설계 (승인 전) · 이전 버전: <code>Shopee_AI쇼호스트_제작설계_v2.html</code></p>', html, count=1, flags=re.S)
html = html.replace('<span><span class="tag t-u">사용자 확인</span>담당자 답변</span>', '<span><span class="tag t-u">사용자 확인/요청</span>담당자 답변·지시</span>')

DST.write_text(html, encoding='utf-8')
assert 'LIPSYNC_LOCK 재적용' not in html
print('written', DST, len(html))
print('lipsync mentions left:', [m.start() for m in re.finditer('LIPSYNC|립싱크 재현|HeyGen', html)])
