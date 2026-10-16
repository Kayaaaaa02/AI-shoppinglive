"""v3 HTML에 생성 결과(레이아웃·캐릭터 시트·보이스 후보·배너·ASR 가드)를 넣는다. build_v3_text.py 다음에 실행.
python -X utf8 build_v3_assets.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DST = HERE / 'Shopee_AI쇼호스트_제작설계_v3.html'
html = DST.read_text(encoding='utf-8')

X = lambda s='확인 필요': f'<span class="tag t-x">{s}</span>'
M = lambda s='실측': f'<span class="tag t-m">{s}</span>'
U = '<span class="tag t-u">사용자 요청</span>'
P = '<span class="tag t-p">제안</span>'
R = '<span class="tag t-r">RA</span>'


def img(rel, cap, w=''):
    return (f'<figure class="shot"><a href="../{rel}"><img loading="lazy" src="../{rel}" alt="{cap}"{w}></a>'
            f'<figcaption>{cap}</figcaption></figure>')


CSS = ('.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin:12px 0}'
       '.shots.wide{grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}'
       '.shot{margin:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--bg)}'
       '.shot img{display:block;width:100%;height:auto}.shot figcaption{font-size:12px;color:var(--muted);padding:6px 8px}')
html = re.sub(r'<style id="v3-assets">.*?</style>\n?', '', html, flags=re.S)
html = html.replace('</head>', f'<style id="v3-assets">{CSS}</style>\n</head>', 1)

# ---------------------------------------------------------------- 4 레이아웃
LAYOUT = f'''  <h3>4-1. 품목별 레이아웃 1차 {U} <span class="tag t-p">1차안 · 합성 전</span></h3>
  <p class="small">1080×1920. 위 도식의 영역(%)을 그대로 박스로 그렸습니다. 호스트는 회색 실루엣 자리표시(캐릭터 확정 후 교체), 제품은 공식 누끼를 비율 그대로 배치했습니다(변형 0, 생성 아님). 실제 합성은 캐릭터·영상 확정 후 진행합니다. 원본 템플릿: <code>5_에셋/banner/template/</code></p>
  <div class="shots">
    {img('5_에셋/layout/V1_layout.png', 'V1 Prime Primer — 시연 창(지문·파우더 비포애프터), 루틴 카드')}
    {img('5_에셋/layout/V2_layout.png', 'V2 Lip &amp; Cheek — 시연 창(워밍업→퍼프), 발색 칩 카드')}
    {img('5_에셋/layout/V3_layout.png', 'V3 Clean it Zero — 시연 창(스패출러→오일→유화), 밤 고르기 카드')}
  </div>
  <p class="small">확인 필요: Shopee 상단 UI(0~33%)와 하단 채팅(78~100%)은 레퍼런스 1프레임 기준이라, 실제 Shopee 화면에 올려 겹침을 다시 봐야 합니다 {X()}.</p>
'''
html = re.sub(r'(<section id="s4">.*?)(\n</section>)', lambda m: m.group(1) + '\n' + LAYOUT + m.group(2), html, count=1, flags=re.S)

# ---------------------------------------------------------------- 5 캐릭터
log = json.loads((ROOT / '4_테스트/character/generation_log.json').read_text(encoding='utf-8'))
calls = log if isinstance(log, list) else log.get('calls', log.get('entries', []))
model = sorted({c.get('model') for c in calls if isinstance(c, dict) and c.get('model')}) or ['gpt-image-1.5']
real = json.loads((ROOT / '4_테스트/character/CS-00R_real/generation_log.json').read_text(encoding='utf-8'))
S5 = f'''<section id="s5">
  <h2><span class="n">5</span>캐릭터 일관성 — GPT 이미지 캐릭터 시트 {U}</h2>
  <p>요청: <b>20대 초반, K-pop 아이돌 느낌</b>. OpenAI <code>{', '.join(model)}</code>(quality high)로 정면 후보 4안(CS-00 A~D, 1024×1536)을 만들고, 각 후보를 레퍼런스로 넣어 시트(1536×1024)를 만들었습니다. 호출 {len(calls)}회, 비용은 응답에 금액이 없어 {X('미확인')}. 기록: <code>4_테스트/character/generation_log.json</code></p>
  <h3>5-0. 실사 피부 재생성 — A안 기반 3명 (CS-00R) {U} <span class="tag t-p">최신 · 선택 대기</span></h3>
  <p class="small">피드백: “너무 인위적, 피부 표현 더 리얼하게, 1번(A안)을 다양화해서 3명”. A안 프롬프트의 <i>luminous dewy skin</i>·<i>soft even beauty lighting</i>(보정된 광고 피부를 유도)을 빼고, <b>무보정 촬영 조건</b>(85mm·f/2.8·창가 자연광)과 <b>실제 피부 요소</b>(코·볼 모공, 잔털, 미세한 톤 차이, 작은 점, 좌우 비대칭)를 넣었습니다. 헤어 기본형·크림 니트·핑크 배경은 A안 그대로, 얼굴은 3명 각각 다르게 지정했습니다. <code>{', '.join(model)}</code> quality high, 1024×1536, 호출 {len(real)}회(비용 금액 {X('미확인')}). 기록: <code>4_테스트/character/CS-00R_real/generation_log.json</code></p>
  <div class="shots" style="grid-template-columns:1fr">{img('4_테스트/character/CS-00R_real/CS-00R_compare.jpg', '이전 A안 ↔ R1·R2·R3 (아래 줄 = 볼·코 확대)')}</div>
  <div class="tbl"><table>
    <tr><th>안</th><th>지정한 얼굴·헤어</th><th>확대 육안 (원본 기준)</th><th>참고</th></tr>
    <tr><td><b>R1</b></td><td>부드러운 계란형·쌍꺼풀·웜뉴트럴 톤 / 다크브라운 생머리·시스루뱅 (A안과 가장 가까움)</td><td>코·볼 모공, 옅은 주근깨, 입술 주름 보임. 보정 광택 없음</td><td>R2와 얼굴 인상이 비슷한 편 {X('육안 판단')}</td></tr>
    <tr><td><b>R2</b></td><td>갸름한 턱선·속쌍꺼풀·뉴트럴 톤 / 흑발 생머리·옆으로 넘긴 앞머리</td><td>모공·잔털·옅은 주근깨 보임, 볼 홍조 자연스러움</td><td>흑발이라 핑크 배경 대비가 가장 강함</td></tr>
    <tr><td><b>R3</b></td><td>둥근 얼굴·처진 눈매(강아지상)·골드베이지 톤 / 소프트브라운 끝 웨이브</td><td>주근깨가 셋 중 가장 많이 보임, 피부 질감 가장 강함</td><td>주근깨 양은 시트 단계에서 줄일 수 있음 {X('추정')}</td></tr>
  </table></div>
  <p class="small">아직 안 한 것: 손 확대 검수(정면 컷이라 손 없음), 실존 인물 닮음 확인 {X('미확인')}. 선택하시면 이 얼굴을 레퍼런스로 각도·표정·손 시트(5-1)를 같은 실사 조건으로 만듭니다. 아래 CS-00 A~D는 이전 1차안(보정 피부)입니다.</p>
  <div class="callout"><b>공통 프롬프트 요지</b> — 가상 인물(실존 인물 레퍼런스 없음), 20대 초반 한국 여성, K-pop 아이돌 비주얼(촉촉한 피부, 뉴트럴 피치 메이크업), 단색 핑크 배경, 액세서리·글자·제품 없음. A~D는 헤어·의상만 다름. 시트 = 정면·3/4·측면, 미소·말하기·놀람·가리키기, 전신 1컷, 손 제스처.</div>
  <div class="shots wide">{img('5_에셋/character_sheet/CS-00_contact_sheet.jpg', '후보(왼쪽) ↔ 시트(오른쪽) 4안 비교')}</div>
  <div class="tbl"><table>
    <tr><th>안</th><th>스타일</th><th>시트 일관성 (육안, 원본 크기)</th><th>문제점</th></tr>
    <tr><td><b>A</b></td><td>긴 생머리·시스루뱅·크림 니트</td><td>8컷 얼굴·헤어·의상 일관, 액세서리·글자 없음</td><td>3/4 우측 각도 없음(말하는 3/4 컷 2장), 가리키는 컷 손이 몸과 이어지는지 애매 {X('추정')}</td></tr>
    <tr><td><b>B</b></td><td>어깨 레이어드·라벤더 스퀘어넥</td><td>반신 컷 일관</td><td>마지막 패널 손만 떠 있음, 전신 얼굴 작아 판정 어려움, 넥라인이 후보보다 깊음</td></tr>
    <tr><td><b>C</b></td><td>하이 포니테일·스카이블루 크롭 가디건</td><td>얼굴·헤어 일관</td><td>크롭 상의로 배 노출(후보부터), 가리키는 팔 어색, 손 인셋이 인물에 겹침</td></tr>
    <tr><td><b>D</b></td><td>C컬 미디엄·흰 퍼프소매 블라우스</td><td>얼굴·헤어 일관</td><td>블라우스가 시트에서 연핑크로 바뀐 것으로 보임 {X('추정')}, 전신 맨발</td></tr>
  </table></div>
  <p><b>제안</b> {P}: 방송 화면(상반신, 테이블 뒤)에서 문제가 적은 <b>A</b> 또는 <b>D</b>. C는 크롭 상의 노출, B는 넥라인 때문에 SEA 4개국 방송 의상으로는 보수적으로 제외를 권합니다. 손가락 확대 검수와 실존 인물 닮음 확인은 아직 하지 않았습니다 {X('미확인')}.</p>
  <h3>5-1. 확정 후 할 일</h3>
  <div class="tbl"><table>
    <tr><th>ID</th><th>이미지</th><th>용도</th></tr>
    <tr><td>CS-00</td><td>선정안 정면 (위 후보)</td><td>모든 후속 생성의 기준 얼굴</td></tr>
    <tr><td>CS-01</td><td>3/4 좌·우·측면 (따로 생성)</td><td>각도 검수 기준</td></tr>
    <tr><td>CS-02</td><td>상반신 착석, 의상 확정본</td><td>의상·헤어 고정, 마스터 프레임 재료</td></tr>
    <tr><td>CS-03</td><td>표정 6종</td><td>장면별 시작 프레임</td></tr>
    <tr><td>CS-04</td><td>손 제스처 4종</td><td>손 기형 검수 기준</td></tr>
    <tr><td>MF-01~03</td><td>세트 + 호스트 상반신 + 빈 테이블 (얼굴 높이 약 50%)</td><td>H3 첫 프레임</td></tr>
  </table></div>
  <h3>5-2. Host Lock — 숫자로 고정 (CS-00 확정 후 실측)</h3>
  <p class="small">피부톤·헤어·의상 hex, 앞머리·가르마 위치, 프레이밍(머리 꼭대기 약 38%, 눈 높이 약 46%)을 CS-00에서 픽셀 실측해 <code>5_에셋/character_sheet/HOST_LOCK.md</code>에 기록합니다. 액세서리 없음, 손톱 짧은 누드 단색, 호스트 화장을 제품 결과로 말하지 않음.</p>
  <h3>5-3. 세트·제품</h3>
  <ul>
    <li><b>SET-00</b>: 사람·제품 없는 핑크 스튜디오, 빈 테이블 상판 약 74%.</li>
    <li><b>제품은 생성하지 않습니다.</b> 진열·배너는 공식 누끼 합성, 시연은 받은 공식 영상(8장).</li>
    <li>Product Lock 스크립트(<code>product_lock.py</code>·<code>composite_product.py</code>·<code>PACKAGING_LOCK.md</code>)는 <code>fnco_influencer_seeding_crawler/experiments/ai_influencer_test/</code>에 있습니다.</li>
  </ul>
</section>'''
html = re.sub(r'<section id="s5">.*?\n</section>', lambda m: S5, html, count=1, flags=re.S)

# ---------------------------------------------------------------- 6 보이스
S6 = f'''<section id="s6">
  <h2><span class="n">6</span>음성 일관성 — MiniMax T2A 보이스 후보 {U}</h2>
  <p>후보는 MiniMax 공식 문서에서 고른 것으로, <b>아직 아무것도 듣지 않았습니다</b> {X('청취 전')}. 시스템 보이스의 성격 설명은 이름에서 짐작한 것입니다 {X('추정')}. 상세: <code>5_에셋/voice/voice_candidates_v1.md</code></p>
  <div class="tbl"><table>
    <tr><th>후보</th><th>방식</th><th>voice_id / 설명 프롬프트</th><th>메모</th></tr>
    <tr><td><b>A (1순위)</b></td><td>Voice Design</td><td><i>Bright, youthful female voice in her early twenties, like a friendly K-pop idol hosting a live beauty show in English. Clear, neutral international English with crisp consonants, easy for non-native listeners. Warm, upbeat and confident, medium-high pitch, smooth and clean, not breathy, not childish, not exaggerated.</i></td><td>전용 보이스. 생성 후 7일 안에 T2A로 1회 합성 필요</td></tr>
    <tr><td>B</td><td>Voice Design</td><td>A + 조금 더 차분하고 부드럽게 (스킨케어 설명 톤)</td><td>시연 설명 구간용</td></tr>
    <tr><td>C</td><td>Voice Design</td><td>A + 조금 더 활기차고 장난스럽게 (팬 라이브 오프닝 톤)</td><td>오프닝·혜택 구간용</td></tr>
    <tr><td>D</td><td>시스템</td><td><code>English_radiant_girl</code></td><td></td></tr>
    <tr><td>E</td><td>시스템</td><td><code>English_Upbeat_Woman</code></td><td>20대 초반보다 나이 들게 들릴 수 있음 {X('추정')}</td></tr>
    <tr><td>F</td><td>시스템</td><td><code>English_LovelyGirl</code></td><td>너무 귀엽게 들릴 수 있음 {X('추정')}</td></tr>
  </table></div>
  <p class="small">예비 시스템 보이스: <code>English_PlayfulGirl</code> · <code>English_Kind-heartedGirl</code> · <code>English_captivating_female1</code> · <code>English_ConfidentWoman</code>. 출처: <a href="https://platform.minimax.io/docs/faq/system-voice-id">MiniMax 시스템 보이스 목록</a> · <a href="https://platform.minimax.io/docs/api-reference/voice-design-design">Voice Design API</a> · <a href="https://platform.minimax.io/docs/api-reference/speech-t2a-http">T2A API</a></p>
  <h3>6-1. 고르는 방법</h3>
  <ol>
    <li>A·B·C는 Voice Design 미리듣기(3개 합계 약 $0.02 — 문서 단가 $30/100만 자 기준 계산), D·E·F는 T2A로 같은 비교 문장 5개(오프닝·숫자·시연·컬러 번호·엔딩)를 합성 → 나란히 청취. <b>유료 호출이라 실행 전 확인받습니다.</b></li>
    <li>1개 선정 → <code>5_에셋/voice/VOICE_LOCK.md</code>에 voice_id·프롬프트·생성일 기록.</li>
    <li>선정 보이스로 H3 참조 샘플(≤15초)을 만들어 모든 H 클립에 같은 파일을 씁니다(7장).</li>
  </ol>
  <h3>6-2. 합성 파라미터 {P}</h3>
  <div class="tbl"><table>
    <tr><th>파라미터</th><th>값</th><th>이유</th></tr>
    <tr><td>model</td><td><code>speech-2.8-hd</code></td><td>최신 HD</td></tr>
    <tr><td>language_boost</td><td><code>English</code></td><td>영어 고정</td></tr>
    <tr><td>speed / pitch / vol</td><td>0.95 / 0 / 1.0</td><td>영어가 제2언어인 시청자 가정</td></tr>
    <tr><td>emotion</td><td><code>happy</code> (시연 설명만 <code>calm</code>)</td><td>장면마다 바꾸면 톤이 흔들림</td></tr>
    <tr><td>쉼</td><td>문장 사이 <code>&lt;#0.4#&gt;</code>, 혜택 전 <code>&lt;#0.6#&gt;</code></td><td>리듬 통일</td></tr>
    <tr><td>subtitle</td><td>enable, <code>word</code></td><td>자막 타이밍</td></tr>
  </table></div>
  <p><b>pronunciation_dict</b>: BANILA CO, Clean it Zero, Prime Primer, Romantic Blush Lip &amp; Cheek, 컬러 번호("oh-two") 읽기 통일. 공식 발음은 BM 확인 {X()}.</p>
  <h3>6-3. 보이스 보존 — v2 내용 정정</h3>
  <p>MiniMax 공식 FAQ: voice_id는 생성 후 <b>7일 안에 T2A로 한 번 합성하면 영구 보존</b>됩니다(<a href="https://platform.minimax.io/docs/faq/about-apis.md">API FAQ</a>). 그래서 v2의 "6일마다 유지 합성"은 필요 없습니다. 다만 FAQ가 Voice Design 보이스에도 똑같이 적용된다고 명시하지는 않아, 생성 1주일 뒤 voice_id가 남아 있는지 한 번 확인합니다 {X()}.</p>
</section>'''
html = re.sub(r'<section id="s6">.*?\n</section>', lambda m: S6, html, count=1, flags=re.S)
html = html.replace('보이스 확정 뒤에는 6일 이내 간격 유지 합성을 계속합니다(6장).', '보이스는 생성 7일 안에 T2A로 1회 합성해 보존합니다(6-3).')
html = html.replace('<tr><td>보이스 7일 삭제</td><td>전량 선합성 + 6일 이내 유지 합성</td></tr>', '<tr><td>보이스 7일 삭제</td><td>생성 7일 안에 T2A 1회 합성(공식 FAQ: 이후 영구 보존), 1주일 뒤 존재 확인</td></tr>')

# ---------------------------------------------------------------- 9 배너
FONT = f'''  <h3>9-2. 폰트 — v3 확정 {U}</h3>
  <div class="tbl"><table>
    <tr><th>용도</th><th>폰트</th><th>라이선스</th><th>이유</th></tr>
    <tr><td>할인 숫자·헤드라인·라벨·본문</td><td><b>Poppins</b> 500 / 600 / 700 / 800</td><td>SIL OFL 1.1 (google/fonts, 라이선스 파일 동봉)</td><td>10월 배너 "up to 60% off"와 같은 계열의 기하학 산세리프. 영상 크기에서도 잘 읽힘</td></tr>
    <tr><td>강조 문구 ("+ Free Gift", 카드 제목)</td><td><b>Playfair Display Italic</b></td><td>SIL OFL 1.1</td><td>레퍼런스의 세리프 이탤릭 느낌</td></tr>
    <tr><td>BANILA CO 로고</td><td>폰트로 대체하지 않음</td><td>—</td><td>공식 로고 파일 미수령 → 로고 자리 비움</td></tr>
  </table></div>
  <p class="small">v2의 손글씨(Gaegu)·Bodoni·Montserrat 후보는 위계를 단순하게 하려고 뺐습니다. 폰트 파일: <code>5_에셋/banner/fonts/</code></p>
'''
html = re.sub(r'  <h3>9-2\. 폰트 분석.*?(?=  <h3>9-3\.)', lambda m: FONT, html, count=1, flags=re.S)

B = '5_에셋/banner/common/'
BANNER = f'''  <h3>9-4. 1080×1920 배너 1차 — 영상 G 화면 겸용 {U}</h3>
  <ul>
    <li><b>바뀐 점</b>: v2의 1200×1608 롱배너·1200×1438 카드배너·1500×1500 썸네일 구성 대신, 영상에 그대로 넣을 수 있는 <b>1080×1920 세로 배너</b>로 만들었습니다.</li>
    <li><b>이벤트 문구 제외</b>: "11.11"·이벤트명·날짜·가격·세금 문구를 모두 뺐습니다. 행사명이 정해지지 않았기 때문입니다.</li>
    <li><b>제품명은 헤드라인에서 제외</b>: 큰 헤드라인은 프로모션(50% OFF · BUY 2 GET 1)과 제품 정보만 씁니다. 제품명은 위쪽 작은 라벨과 카드 이름에만 남겼습니다. 제품명을 아예 빼야 하면 알려 주세요 {X('해석 확인')}.</li>
    <li><b>문구 기준</b>: 문구는 세정·사용감·외관 범위로만 썼습니다. 판매량·순위·% 수치·여드름/피지/붉어짐·"fragrance-free"는 넣지 않았습니다. 걸릴 소지가 있는 문장은 <code>banner_copy.csv</code>에 RA로 표시했습니다.</li>
  </ul>
  <div class="shots">
    {img(B+'BNR_V1_PrimePrimer_promo.png', 'V1 프로모션 — 50% OFF + Free Gift, 4종 누끼')}
    {img(B+'BNR_V1_PrimePrimer_info.png', 'V1 제품 정보 — 4종 각 3줄 (일부 RA)')}
    {img(B+'BNR_V2_LipCheek_promo.png', 'V2 프로모션 — BUY 2 GET 1 FREE')}
    {img(B+'BNR_V2_LipCheek_info.png', 'V2 USP — 립+치크 · 빌더블 · 사용법')}
    {img(B+'BNR_V2_LipCheek_shades_1.png', 'V2 호수별 발색 ① Milky·Muted — 02 04 05 07 08 09')}
    {img(B+'BNR_V2_LipCheek_shades_2.png', 'V2 호수별 발색 ② Mellow·Moody — 12 13 14 17 18 20')}
    {img(B+'BNR_V3_CleanItZero_promo.png', 'V3 프로모션 — 50% OFF + Free Gift, 3종')}
    {img(B+'BNR_V3_CleanItZero_info.png', 'V3 고르기 — Original · Pore · Calming (일부 RA)')}
  </div>
  <div class="tbl"><table>
    <tr><th>항목</th><th>결과</th></tr>
    <tr><td>립앤치크 호수별 발색</td><td>참고 이미지 <code>립앤치크 2.png</code>, <code>립앤치크 3_16-18.png</code>(OneDrive 2607_TICTOK POC)의 호수 + 입술·볼 배치를 따랐습니다. 발색은 받은 공식 발색컷을 잘라 썼고 생성하지 않았습니다(<code>banner/src_swatch/</code>). 한 장에 6색씩 2장. 영문 컬러명은 Product Spec에 없어 번호·무드·추천 톤만 표기 {X('R6')}. 14·20호는 문서에 추천 톤이 없어 비움</td></tr>
    <tr><td>제품 비율</td><td>모든 누끼의 렌더 비율을 원본과 비교했을 때 최대 오차는 0.12%(픽셀 반올림)였습니다 {M()}. 늘이거나 줄여 변형한 이미지는 없습니다</td></tr>
    <tr><td>자동 검사</td><td>폰트 로딩 실패·이미지 누락·캔버스 밖으로 넘친 글자 없음 {M()} (<code>template/render_check.json</code>)</td></tr>
    <tr><td>남은 점</td><td>사은품이 정해지지 않아 일반 "FREE GIFT" 아이콘만 넣었습니다(R2). 오리지널 밤 누끼는 1000px 저해상도라 고해상도 원본이 필요합니다(R5). 클렌징밤 3종 용기를 같은 높이로 놓아 실제 크기 차이가 보이지 않습니다. 선베이스 "SPF50+"·픽서 "24H"는 패키지에 인쇄된 문구지만 국가별 RA 확인이 필요합니다 {R}. V3 프로모션 배너는 마지막 수정 후 육안 재확인을 하지 못했습니다</td></tr>
  </table></div>
  <p class="small">재생성: <code>python -X utf8 5_에셋/banner/template/build_banners.py</code> · 문구 전체: <code>5_에셋/banner/common/banner_copy.csv</code> · 국가별 가격 레이어는 R1 수령 후 <code>5_에셋/banner/{{TH|MY|ID|VN}}/</code>에 추가합니다.</p>
'''
html = re.sub(r'  <h3>9-4\. 11월 배너 세트.*?(?=  <h3>9-7\.)', lambda m: BANNER, html, count=1, flags=re.S)
html = html.replace('<h2><span class="n">9</span>배너 제작 설계 (영문) · 이미지 생성 계획</h2>', '<h2><span class="n">9</span>배너 (영문, 1080×1920)</h2>')
html = html.replace('<a href="#s9">9. 배너·이미지 생성 계획</a>', '<a href="#s9">9. 배너 1080×1920</a>')
html = html.replace('<tr><td>제품명</td><td>9-3 표기와 일치 (Product Spec 기준)</td></tr>', '<tr><td>제품명</td><td>9-3 표기와 일치 (Product Spec 기준), 헤드라인에는 넣지 않음</td></tr>')
html = html.replace('<tr><td>안전 영역</td><td>Shopee 업로드 규격 확인 후 잘림 없음</td></tr>', '<tr><td>안전 영역</td><td>영상 삽입 시 Shopee 상단 UI·하단 채팅에 핵심 문구가 가리지 않음 (R7 규격 확인 후)</td></tr>')

# ---------------------------------------------------------------- 14 ASR 가드 결과
g4 = json.loads((ROOT / '4_테스트/asr_guard/studio04/guard.json').read_text(encoding='utf-8'))
GUARD = f'''<td id="asr-guard-detail">음성 인식 모델 2개(base·small)로 단어 시점을 뽑아 대본과 맞춥니다. 두 모델이 모두 잡고 음량이 −35dB 이상인 구간만 "대본에 없는 말"로 확정합니다. 판정 기준은 아래와 같습니다.
      <ul>
        <li><b>통과</b>: 대본 단어를 90% 이상 말했고, 확정된 이탈 구간이 없음</li>
        <li><b>편집 삭제</b>: 이탈 구간이 있음. 그 구간을 잘라낸 <code>_cut.mp4</code>를 함께 출력</li>
        <li><b>재생성</b>: 대본 단어를 90% 미만 말했거나, 잘라낼 구간이 클립의 40%를 넘음</li>
        <li><b>사람 청취</b>: 모델 하나만 잡은 구간은 사람이 들어보고 판단</li>
      </ul>
      설명서: <code>5_에셋/scripts/ASR_GUARD.md</code></td>'''
html = re.sub(r'<td id="asr-guard-detail">.*?</td>', lambda m: GUARD, html, count=1, flags=re.S)
TEST = f'''  <h3>14-2. 가드 시험 결과 — POC 클립 {M()}</h3>
  <div class="tbl"><table>
    <tr><th>클립</th><th>판정</th><th>내용</th></tr>
    <tr><td>studio03</td><td><span class="tag t-m">통과</span></td><td>대본 단어 전부 말함(100%), 이탈 구간 없음</td></tr>
    <tr><td>studio04</td><td><span class="tag t-r">편집 삭제</span></td><td>이탈 구간 <b>7.00–11.16초</b>(4.16초, 평균 −19.0dB)를 두 모델이 모두 잡음. 0–6.92초와 11.24–15.10초만 남긴 컷본은 <b>10.79초</b>입니다. 처음 POC 보고(6.9–9.7초)보다 이탈이 약 11.2초까지 이어졌습니다</td></tr>
    <tr><td>studio04 컷본 재검사</td><td><span class="tag t-m">통과</span></td><td>대본 단어 전부 말함(100%), 확정 이탈 없음. 3.62초 "the"를 small 모델이 "a"로 들은 의심 1건은 인식 오류로 판단</td></tr>
  </table></div>
  <p class="small">사람이 직접 듣지는 않았습니다 {X('청취 전')}. 컷본: <code>4_테스트/asr_guard/studio04/studio04_final_cut.mp4</code>. 가드 1차 버전에 정렬 방향을 반대로 읽어 studio04를 통과시키는 버그가 있었고, 고친 뒤 세 경우를 모두 다시 돌려 위 결과를 확인했습니다.</p>
'''
html = html.replace('  <p class="small">POC 원본 폴더:', TEST + '  <p class="small">POC 원본 폴더:', 1)
html = html.replace('6.9–9.7초에 대본에 없는 말("BAAC… pylacety"로 전사됨).', '7.0–11.2초에 대본에 없는 말("BAAC… pylacety" 등으로 전사됨, 가드 실측).')


for a,b in [('<a href="#s13-tax">13-2 세금 문의</a>','<a href="#s13-tax">13장 T 세금 각주</a>'),('브랜드 표기 방식을 확인합니다 (<a href="#s13">13-1</a>)','브랜드 표기 방식을 확인합니다 (<a href="#s13">13장 R6</a>)'),('국가별 통화 기호, 13-2 확정 각주','국가별 통화 기호, 13장 T 확정 각주'),('13-2 문의 결과로 확정.','13장 T 문의 결과로 확정.')]:
    html = html.replace(a, b)

DST.write_text(html, encoding='utf-8')
print('ok', len(html), 'verdict04', g4.get('verdict'))
