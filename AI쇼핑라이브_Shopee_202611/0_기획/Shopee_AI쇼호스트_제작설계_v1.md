# Shopee 11월 AI 쇼호스트 — 영상 흐름·생성·일관성 제작 설계 v1

- 작성일: 2026-10-12 · 내부 제작 설계 초안 (승인 전)
- 상위 문서: `Shopee_AI쇼호스트_콘텐츠계획_v1.md`, `AI쇼핑라이브_제품USP_브리프_2026-10-12.md`
- 조건 [확정]
  - 11월 중 Shopee 방영 (송출·비디오 공용), 대상국 TH·MY·ID·VN
  - 영어 1벌 제작
  - 프로모션: 클렌징밤 3종 50% OFF + Free gift / 프라이머 라인 50% OFF + Free gift / Lip & Cheek Buy 2 Get 1
  - MiniMax API로 생성
- 표기
  - **[실측]** 파일을 직접 열어 확인한 사실
  - **[문서]** 공식 문서·사내 문서에서 확인한 사실
  - **[제안]** 작성자 설계
  - **[미확인]** 검증 전
  - **<RA/법무 사전검토>** 효능·표시 표현은 RA 검토 전까지 초안

---

## 0. 설계 근거

### 0-1. AL라이브 전자책 — 뷰티 카테고리 [문서: 전자책 p.16~17]
| 항목 | 전자책 내용 | 이번 설계에 반영한 방식 |
|---|---|---|
| 뷰티 공통 | "광고처럼 만드는 것", "즉흥적인 말 대신 검증된 워딩의 씬" | 모든 VO를 사전 확정 대본으로 만들고 RA 검토 후 고정한다. 애드리브·생성형 발화를 쓰지 않는다 |
| 12 기초 스킨케어 | 씬: ① 피부 고민 오프닝 ② 텍스처·흡수 시연과 성분 설명 ③ 아침·저녁 루틴 제안 | M1 클렌징밤: 하루 끝 고민 → 제형 변화 시연 → 저녁 루틴·사이즈 선택 |
| 13 색조 | 씬: ① 오늘의 룩 제안 ② 발색·비포애프터 분할 시연 ③ 퍼스널컬러·상황별 추천. 팁: 품절 컬러는 컬러칩 배너에 표시 | M3 립앤치크: 룩 제안 → 분할 발색 시연 → 쿨/웜/공용 트리오. 컬러칩 배너를 국가별 레이어로 운영 |
| 14 기능성 | "효능 표현 심의는 스크립트 단계에서 잡아두세요" | 대본 → RA 검토 → TTS 순서를 지킨다. RA 전 TTS 본생성 금지 |
| 운영 | "잘 만든 방송 한 편을 반복 재생", 가격·구성 변경은 배너·씬 교체 | 본편 1벌 + 국가별 배너 레이어 4벌. 가격·기간·사은품을 VO에 넣지 않는다 |

### 0-2. 레퍼런스 4편 분석 [실측: ffprobe, 2.5초 간격 컨택트시트, 장면 전환 검출, Banila 편 2fps 확대]
| 파일 | 길이 | 내용 |
|---|---|---|
| KakaoTalk_…639190 | 17.0s | manyo 공식스토어, 베트남어 Shopee Live (AI) |
| KakaoTalk_…644028 | 29.2s | LUNA 베트남 (AI) |
| KakaoTalk_…650231 | 35.3s | BANILA CO. LIVE (AI). Clean it Zero 헤드라인 "Da đẹp mood", "Sale up to 45%" |
| 베트남 쇼피 | 30.0s | BANILA CO 같은 방송. 후반에 Shopee 상품 목록 화면으로 넘어감 |

공통 사항 (4편 모두 884×1920 세로 화면 녹화):
- 방송 제목 앞에 "(AI)", "Streamer AI" 배지, "AI-GENERATED CONTENT" 라벨이 붙어 있다.
- 화면 구성: 고정 카메라 미디엄샷 1개. 여성 호스트가 상반신으로 테이블 뒤에 앉아 있고, 테이블 앞줄에 제품이 진열돼 있다. 배경은 브랜드 세트(Banila: 핑크 계단·선반 위 zero 밤 용기)다.
- 영상 자체 그래픽: 상단 헤드라인, 할인 배지, 하단 브랜드 로고
- 장면 전환 검출 결과(threshold 0.3): 방송 본편 안에서는 컷 전환이 검출되지 않았다. 검출된 전환은 녹화 끝의 화면 이동뿐이다.
- Banila 편 12초 구간을 2fps로 확인한 결과, 호스트는 손짓만 하고 **제품을 들거나 바르는 장면이 없다.**

**참고하되 넘어설 지점 [제안]**
- 그대로 가져올 것: 세트·제품 진열형 레이아웃, 상단 헤드라인·할인 배지, AI 표기
- 보완할 것
  - 단일 샷만 반복된다. 이번 방송은 14분 규모라 시연 컷·분할 화면·컬러칩 화면으로 리듬을 만든다.
  - 시연이 없다. 제형·발색 시연을 실물 영상으로 넣는다.
  - 레퍼런스 텍스트는 베트남어다. 이번 방송은 영어 1벌 + 국가별 가격 레이어로 만든다.
- 음성(언어·톤)은 확인하지 않았다 [미확인].

**Shopee UI 안전 영역 [실측: Banila 편 1프레임 기준, 확정 아님]**
| 영역 | 화면 높이 대비 위치 |
|---|---|
| 상단 Shopee UI (제목, 팔로우, Streamer AI, 우측 보상 칼럼) | 0~약 33% |
| 좌측 상품 썸네일 카드 | 약 24~38% |
| 하단 채팅·상품 팝업·입력창 | 약 78~100% |

→ **얼굴과 핵심 정보는 세로 38~78% 구간**에 둔다. 이번 레이아웃(3장)은 이 값을 기준으로 설계했다.

### 0-3. MiniMax API 기능 확인 [문서: platform.minimax.io, 2026-10-12 조회]
| 용도 | 모델·엔드포인트 | 확인된 사양 |
|---|---|---|
| 호스트·세트 이미지 | `image-01` T2I / I2I (`/v1/image_generation`) | `subject_reference` type=`character`(인물), 정면 단일 인물사진 권장, JPG/PNG <10MB. 9:16=720×1280 또는 width/height 512~2048(8의 배수). `seed`로 재현. n 1~9. 프롬프트 1500자 |
| 영상 | `MiniMax-H3` (`/v2/video_generation`) | text / image(first·last frame) / reference 입력. 768P·2K, 4~15초, ratio 9:16 지원. reference_image 최대 9장, reference_video 3개, reference_audio 3개(총 15초 이하, WAV/MP3) |
| 영상(빠른) | `MiniMax-H3-Max` | 480P·768P, 5~15초 |
| 업스케일 | Video Regeneration | 768P H3 결과를 2K로 재생성 |
| 음성 | `speech-2.8-hd` 등 T2A | 1회 10,000자 미만. voice_setting(speed 0.5~2, vol, pitch −12~12, emotion), language_boost=English, pronunciation_dict, 쉼 표기 `<#x#>`, 자막 타임스탬프(sentence/word), WAV 44.1kHz 등 |
| 보이스 생성 | Voice Design (`/v1/voice_design`) | 설명 프롬프트 + preview_text(500자)로 voice_id 생성 |
| 보이스 보존 | 공통 규칙 | 클론·디자인 보이스는 임시다. **168시간(7일) 안에 합성에 쓰이지 않으면 삭제된다** |

[미확인 — 테스트로 판정할 항목]
- H3 결과물에 **음성과 립싱크가 생성되는지**: 공식 문서는 오디오를 '입력'으로만 설명한다. 예시 문구 "Voice timbre follows reference audio"만 있다.
- **MiniMax H3 Max Lip Sync**(이미지+오디오 → 말하는 영상)는 외부 집계 사이트(fal, eachlabs 등)에만 나온다. 공식 API 문서에서는 확인되지 않았다.
- 여러 클립에 걸친 인물 일관성: 문서는 "생성된 영상 한 편 안의 일관성"만 언급한다.
- 제품·로고·글자 재현력: 문서에 언급이 없다.
- 단가: 영상 `usage`가 초 단위로 과금된다는 것만 확인했다. 금액은 미확인이라 비용 산정을 하지 않았다.

---

## 1. 방송 콘셉트

**한 줄 [제안]:** "Hot day, fresh face — Prep, Stay, Melt it off."
덥고 습한 하루를 기준으로 세 묶음을 하나의 흐름으로 연결한다.
- 아침 **Prep & Stay**: 프라이머 라인
- 낮의 **Color**: 립앤치크
- 저녁 **Melt it off**: 클렌징밤

**방송 순서 [제안]:** 오프닝 → M2 프라이머 → M3 립앤치크 → M1 클렌징밤 → 클로징
- 하루 흐름(아침 → 낮 → 저녁)대로 배치했다.
- 자료가 아직 없는 클렌징밤을 마지막 모듈에 두면, 앞 모듈부터 제작에 들어갈 수 있다.
- 모듈은 독립적으로 만든다. 순서는 편집에서 바꿀 수 있다.

**호스트 페르소나 [제안]**
| 항목 | 내용 |
|---|---|
| 역할 | BANILA CO 공식 스토어의 **AI 호스트**. 스스로 AI임을 밝힌다. 실존 인물·전문가·실사용자를 사칭하지 않는다 |
| 태도 | 브랜드 기준 "여유 있는 자신감", 친구에게 사용법을 알려주는 톤. 과장 감탄사를 줄이고 시연과 혜택 안내에 집중한다 |
| 영어 | 쉬운 단어, 한 문장 12단어 안팎, 핵심어 반복. 말 속도는 기본보다 약간 느리게 (5장) |
| 하지 않는 것 | 제품을 직접 바르는 장면. 호스트 자신의 피부·화장을 제품 결과처럼 말하는 것. "I've used this for years" 같은 사용 경험 발화 |

---

## 2. 영상 흐름 — 장면별 상세 (풀버전 약 14분)

### 2-0. 장면 유형 정의
| 코드 | 화면 | 제작 방식 |
|---|---|---|
| **H** | 호스트 미디엄샷. 세트·테이블 앞 제품 진열 | MiniMax 생성 호스트 + 제품 진열은 실물 누끼 합성 |
| **D** | 시연 클로즈업 (제형, 발림, 발색, 분사) | **실물 촬영**. 생성하지 않는다 |
| **S** | 분할 화면 (호스트 상단 + 시연 하단, 또는 좌우 비교) | H + D 편집 합성 |
| **G** | 그래픽 카드 (혜택, 컬러칩, 사이즈표, 루틴 순서) | 편집 그래픽. 국가별 레이어 |
| **B** | 무드 B-roll (덥고 습한 거리, 저녁 욕실 무드) | MiniMax H3 생성 가능. 제품은 등장시키지 않는다 |

### 2-1. 오프닝 (0:00–0:40)
| # | 시간 | 유형 | 화면 | VO 초안 (영어) | 자막·그래픽 |
|---|---|---|---|---|---|
| O1 | 0:00–0:08 | B→H | 습한 거리 B-roll 3초 → 호스트 미소 | "Hi everyone, welcome to BANILA CO Live! I'm your AI host today." | 상단 헤드라인 "PREP · STAY · MELT IT OFF" / "AI-generated host" 상시 |
| O2 | 0:08–0:25 | H | 호스트가 화면 좌우 카드를 손으로 가리킴 | "Hot and humid outside? Today I'll show you three easy steps — prep your skin, keep your makeup in place, and melt it all off at night." | 3단계 아이콘 |
| O3 | 0:25–0:40 | G+H | 혜택 카드 3장이 차례로 등장 | "And today's deals: fifty percent off our Clean it Zero balms and our Prime Primer line, both with a free gift. Plus — Lip & Cheek, buy two, get one!" | 국가별 레이어: 기간, 사은품 구성, 가격 |

### 2-2. M2 Prime Primer 라인 (0:40–5:40) — 아침 "Prep & Stay"
전자책 기초·색조 씬 구조 적용: 고민 → 시연 → 루틴.

| # | 시간 | 유형 | 화면 | VO 초안 | 근거·주의 |
|---|---|---|---|---|---|
| P1 | 0:40–1:00 | H | 호스트 | "Let's start with the morning. Does your base slide off by lunch? Do your pores show more when it's hot?" | 고민 공감 |
| P2 | 1:00–1:20 | G | 루틴 순서 카드 `Sun base → Classic → Cushion → Finish Powder → Setting Fixer` | "Here's the Prime Primer routine — four steps, each with one job." | 선베이스 [자료 대기] |
| P3 | 1:20–1:50 | H | 호스트 + 선베이스 누끼 확대 | [자료 대기] 선베이스 제품명·SPF/PA·특징 | 자료 받은 뒤 작성 |
| P4 | 1:50–2:40 | S | 상단 호스트 / 하단 손등 시연: 완두콩 크기 → 문지르기 → 반쪽 비교 | "Prime Primer Classic. Just a pea-sized amount. Press it in like you're filling the pores — see how the skin texture looks smoother?" / "A little goes a long way — too much can make your base slide." | [문서] 소량 사용, 모공 채우듯 바르기, 과다 사용 시 밀림 VOC. "smooths the look of" 외관 표현만 <RA/법무 사전검토> |
| P5 | 2:40–3:30 | S | 하단: 쿠션 위 피니쉬 파우더. 뚜껑에 덜기 → 퍼프 → 반쪽 얼굴 비교 | "Next, Prime Primer Finish Powder. It's translucent, so it won't change your cushion shade. Tap a little into your puff — shine looks blotted, skin looks soft-matte." | [문서] 투명 파우더, 가루 날림 방지 사용법. 시험 수치 미사용 <RA/법무 사전검토> |
| P6 | 3:30–4:20 | S | 하단: 세팅 픽서 미세 분사 슬로모션, 20cm 거리, 퍼프에 뿌리는 팁, 이중 뚜껑 | "Last step — Prime Primer Setting Fixer. Look at this fine mist. Spray from about 20 centimeters. It helps your makeup stay in place — great for hot, humid days." | [문서] 20cm, 퍼프 팁, 이중 뚜껑. "24H"·"sweat-proof" 수치 표현은 RA 판정 전 미사용 |
| P7 | 4:20–4:50 | H | 호스트, 테이블의 4종 진열 | "So — prep, set, fix. You can pick just one, or build the whole routine." | 4종을 함께 쓴 효과는 주장하지 않는다 |
| P8 | 4:50–5:40 | G+H | 혜택 카드, 장바구니 안내 | "The whole Prime Primer line is fifty percent off today, with a free gift. Tap the product card below to add it to your cart." | 국가별 레이어: 가격, 사은품 |

### 2-3. M3 Lip & Cheek (5:40–9:40) — 낮 "Color"
전자책 색조 씬: ① 오늘의 룩 ② 발색 분할 시연 ③ 퍼스널컬러 추천

| # | 시간 | 유형 | 화면 | VO 초안 | 근거·주의 |
|---|---|---|---|---|---|
| L1 | 5:40–6:00 | H | 호스트 + 12색 스틱 진열(누끼) | "Now let's add some color. One stick — for your lips and your cheeks." | [문서] 립·치크 겸용 |
| L2 | 6:00–6:40 | D | 손등 → 퍼프 → 볼 톡톡 (실물 모델) | "Here's the trick: warm it on the back of your hand first, then tap it on with the puff. That way your base stays smooth." | [문서] 베이스 까짐 VOC 대응 사용법 |
| L3 | 6:40–7:20 | S | 좌: 1회 / 우: 2회 레이어링 발색 비교 | "One layer — sheer and natural. Two layers — deeper color. You choose." | [문서] 빌더블. 지속력 표현 금지 |
| L4 | 7:20–7:40 | D | 입술: 립밤 → 톡톡 | "For lips, a little lip balm first, then tap." | [문서] 각질 부각 VOC 대응 |
| L5 | 7:40–8:50 | G+H | 컬러칩 차트 12색 (쿨/웜/공용/기타) + 호스트 손짓 | "Find your trio! Cool tones — try 02, 05 and 09. Warm tones — 12, 17 and 18. Not sure? 04, 08 and 13 suit both." | [문서] 매장 컬러 가이드. 14·20은 분류 근거 없음 [BM 확인]. 영어 컬러명은 확정 후 자막 표기. 품절 컬러 표시 레이어 |
| L6 | 8:50–9:40 | G+H | Buy 2 Get 1 카드: 2색 담기 → 1색 무료 애니메이션 | "Lip & Cheek is buy two, get one today. So build your trio — lips, cheeks, and a backup for your bag." | 국가별 레이어: 적용 조건 |

### 2-4. M1 Clean It Zero 클렌징밤 3종 (9:40–13:40) — 저녁 "Melt it off"
전자책 기초 씬: ① 고민 ② 텍스처 시연 ③ 저녁 루틴

| # | 시간 | 유형 | 화면 | VO 초안 | 근거·주의 |
|---|---|---|---|---|---|
| C1 | 9:40–10:00 | B→H | 저녁 욕실 무드 B-roll → 호스트 | "End of a long, hot day. Primer, powder, fixer, color… now let's melt it all off." | 앞 모듈과 연결 |
| C2 | 10:00–11:00 | D | 스패출러로 떠내기 → 손바닥 → 얼굴에서 오일로 녹음 → 물을 더해 우윳빛 유화 → 헹굼 | "Scoop it with the spatula. It feels like sherbet… and it melts into oil on your skin. Massage gently, add a little water — it turns milky. Then rinse." | [문서: 브랜드 표현] 샤베트 → 오일 → 유화 → 헹굼. 압축 편집 시 "Time-lapse" 자막. 워터프루프 제거 표현은 [확인 필요] |
| C3 | 11:00–12:10 | G+H | 3종 비교 카드 (Original / Pore / Calming) | [자료 대기] 3종 차이 | Original을 'fragrance-free'로 쓰지 않는다 [문서: CLAIMS]. Pore·Calming의 효능 표현은 자료·RA 확인 후 작성 |
| C4 | 12:10–12:50 | G | 사이즈 카드 25 / 50 / 100 / 180ml | "Four sizes — mini for travel, up to the big one for daily use." | 국가별 판매 사이즈 레이어 [확인 필요] |
| C5 | 12:50–13:40 | G+H | 혜택 카드 | "Clean it Zero balms are fifty percent off today, with a free gift." | 국가별 레이어 |

### 2-5. 클로징 (13:40–14:10)
| # | 시간 | 유형 | 화면 | VO 초안 |
|---|---|---|---|---|
| E1 | 13:40–14:10 | H+G | 호스트 + 3개 혜택 요약 카드 | "One more time: fifty percent off Prime Primer and Clean it Zero, with free gifts, and Lip & Cheek buy two, get one. Tap the cart below. Thanks for watching — see you next live!" |

- 반복 재생용 연결: E1 마지막 프레임과 O1 첫 호스트 프레임은 같은 마스터 프레임에서 시작·종료한다(4-2 참고).
- **컷다운 [제안]:** 각 모듈의 핵심 시연 + 혜택으로 45~60초 3편을 만든다 (P4~P6 / L2·L3·L5 / C2+C5).

---

## 3. 화면 레이아웃 (9:16, 납품 1080×1920) [제안]

| 레이어 (아래→위) | 내용 | 위치 (세로 %) |
|---|---|---|
| L0 세트 | 생성 세트 플레이트 (핑크 스튜디오, 비어 있는 선반) | 전체 |
| L1 호스트 | 생성 호스트 클립. 얼굴 중심을 약 50% 위치에 고정 | 머리 꼭대기 약 38%, 테이블 상판 약 74% |
| L2 테이블 진열 | 실물 누끼 제품 합성 (모듈별 진열 교체) | 약 68~78% |
| L3 시연 창 (S 유형) | 하단 D 영상 또는 좌우 분할 | 약 50~78% |
| L4 그래픽 | 헤드라인(상단 고정, Shopee UI 아래), 혜택 배지, 컬러칩 | 헤드라인 약 34~40%, 카드 약 40~76% |
| L5 국가 레이어 | 가격, 기간, 사은품, 품절 컬러 표시 (TH/MY/ID/VN 4벌) | 카드 안 지정 박스 |
| L6 고지 | "AI-generated host", 시험 조건 고지(수치 사용 시), "Time-lapse" | 약 76~78% 소형 |

- 영어 자막: VO 자동 타임스탬프(5장)로 만든다. 2줄 이하, 약 70~76% 구간에 배치한다.
- 위치값은 Banila 레퍼런스 1프레임 실측 기준이다. 실제 Shopee 화면에 올려 다시 확인한다.

---

## 4. 캐릭터 일관성 설계 (MiniMax)

### 4-1. 캐릭터 시트 — 만들 이미지 목록
같은 seed 계열로 생성하고, **마스터 포트레이트 1장**을 모든 후속 생성의 `subject_reference`로 쓴다.

| ID | 이미지 | 용도 | 생성 |
|---|---|---|---|
| CS-00 | 마스터 포트레이트: 정면, 무표정에 가까운 미소, 어깨 위, 균일 조명, 단색 배경 | 모든 생성의 기준 얼굴 | image-01 T2I, 후보 9장(n=9) → 1장 선정 |
| CS-01 | 3/4 좌 · 3/4 우 · 측면 | 각도 일관성 검수 기준 | image-01 I2I + subject_reference=CS-00 |
| CS-02 | 상반신 착석, 의상 확정본 (정면) | 의상·헤어 고정 기준 | I2I |
| CS-03 | 표정 세트 6종: 미소 / 설명 중(입 약간 벌림) / 놀람(가벼움) / 끄덕임 / 오른쪽 가리킴 / 왼쪽 가리킴 | 장면별 시작 프레임 | I2I |
| CS-04 | 손 제스처 4종: 양손 모음 / 한 손 펼침 / 화면 쪽 가리킴 / 하트 손 | 손 기형 검수 기준 | I2I |
| MF-01~03 | **마스터 프레임**: 세트 플레이트 + 호스트 상반신 + 빈 테이블 (9:16, 얼굴 높이 약 50%) | H3 생성의 first/last frame | I2I (세트 + 인물 합성 후 정리) |

### 4-2. 캐릭터 사양 고정값 — "Host Lock" (CS-00 선정 후 실측해 숫자를 채운다)
| 항목 | 기록할 값 | 예시 형식 (값 아님) |
|---|---|---|
| 얼굴 | 피부톤 hex(볼·이마), 눈 모양, 쌍꺼풀 유무, 눈썹 형태 | `skin #RRGGBB` |
| 헤어 | 길이(어깨/쇄골/가슴), 가르마 위치, 앞머리 유무, 색 hex, 웨이브 유무 | "쇄골 아래 5cm, 5:5 가르마" |
| 메이크업 | 베이스 마무리, 볼·입술 색 hex. 립앤치크 판매 색과 혼동되지 않는 뉴트럴 | 호스트 화장을 제품 결과로 쓰지 않는다 |
| 의상 | 1벌로 고정. 상의 종류·색 hex·넥라인. 로고·패턴 없음 | 핑크 계열은 배경과 명도 차이를 둔다 |
| 액세서리 | **없음** (반지·시계·귀걸이 금지). 프레임마다 모양이 바뀌는 위험을 없앤다 | 레퍼런스에 반지·시계가 있었지만 쓰지 않는다 |
| 손톱 | 짧은 길이, 누드 단색 hex | 시연 손 모델과 색을 맞춘다 |
| 프레이밍 | 머리 꼭대기 약 38%, 눈 높이 약 46%, 어깨 폭은 화면 폭의 약 55% | 마스터 프레임 기준 |

- **인물 권리 [제안 원칙]:** 실존 인물 사진을 레퍼런스로 쓰지 않는다. 생성 얼굴이 특정 연예인·인플루언서와 닮았는지 내부 확인한다. 4개국 시청자가 친숙하게 느낄 아시아계 외모로 설계하되 특정 국적을 표방하지 않는다.

### 4-3. 세트 일관성
- **SET-00 세트 플레이트**: image-01 T2I, 9:16, 사람·제품 없음
  - 핑크 톤 도시적 스튜디오(브랜드 기준), 배경 선반은 비워 둔다. 제품은 L2에서 실물 합성한다.
  - 테이블 상판 높이는 화면의 약 74%.
  - 핑크 hex 2~3개를 Host Lock 문서에 기록한다.
- 모든 H 클립은 같은 마스터 프레임에서 출발하므로 세트가 바뀌지 않는다. 배경이 흔들리는 클립은 SET-00 정지 플레이트로 교체 합성한다. 이를 위해 호스트 뒤 배경을 단순하게 설계한다.

### 4-4. 제품 처리 원칙
- 화면의 모든 제품은 **실물 누끼 합성(L2) 또는 실물 촬영(D)**으로 넣는다.
- 생성 프롬프트에는 "empty table surface, no products, no bottles, no text"를 넣어 제품이 생성되지 않게 한다.
- 호스트가 제품을 드는 생성 컷은 이번 범위에서 **만들지 않는다.** 레퍼런스도 손짓만 쓰며, 이 방식이 제품 변형 위험을 0으로 만든다.
- 제품 실측 자료(Product Lock)는 누끼 합성 크기·색 검수 기준으로 쓴다 (콘텐츠계획 8장).

---

## 5. 음성 일관성 설계 (MiniMax T2A)

### 5-1. 보이스 확정
| 단계 | 작업 | 고정값 |
|---|---|---|
| V1 | Voice Design 후보 3개 생성 | 프롬프트 예: "Warm, bright female voice in her late 20s, clear neutral international English, friendly and confident like a beauty advisor, medium pitch, smooth, not breathy, not childish" (+ 변형 2개) |
| V2 | 같은 preview_text로 비교 청취 | preview_text 고정: 브랜드명·숫자·제품명이 모두 들어간 문장 (예: "Hi everyone, welcome to BANILA CO Live! Prime Primer Classic, fifty percent off, buy two, get one.") |
| V3 | 1개 선정 → voice_id 기록 | voice_id, 디자인 프롬프트, 생성일, 담당자를 `5_에셋/voice/VOICE_LOCK.md`에 기록 |

- **클론 보이스는 쓰지 않는다 [제안]:** 성우 계약·권리·본인 인증이 필요하다. 디자인 보이스로 충분하다.

### 5-2. 합성 파라미터 고정 (전 문장 동일)
| 파라미터 | 값 [제안] | 이유 |
|---|---|---|
| model | `speech-2.8-hd` | 최신 HD. 감탄 태그 지원 |
| language_boost | `English` | 영어 고정 |
| speed | 0.95 | 4개국 모두 영어가 제2언어인 시청자가 많다는 가정 |
| pitch | 0 | 바꾸지 않는다 |
| vol | 1.0 | 믹싱에서 조정한다 |
| emotion | 전 구간 `happy`로 시작해 테스트 | 장면마다 바꾸면 톤이 흔들린다. 바꿔야 하면 시연 설명 구간만 `calm`으로 한정 |
| audio_setting | WAV, 44100Hz, mono | 편집 원본 |
| 쉼 | 문장 사이 `<#0.4#>`, 혜택 전 `<#0.6#>` | 리듬 통일 |
| subtitle_enable | true, `word` | 영어 자막과 립싱크 정렬에 사용 |

**pronunciation_dict [제안, 청취 후 확정]**
- BANILA CO, Clean it Zero, Prime Primer, Lip & Cheek
- 숫자 컬러 "oh-two"(02) 등 읽는 방식 통일
- 브랜드 공식 발음은 BM에 확인한다 [확인 필요].

### 5-3. 보이스 보존 (7일 삭제 규칙 대응) [문서 규칙 기반 제안]
1. 보이스 확정 당일에 **전 대본 VO를 한 번에 합성**해 WAV 마스터로 저장한다 (`2_나레이션/master/`). 이후 보이스가 삭제돼도 완성 음원은 남는다.
2. 수정 대응: 프로젝트 기간 동안 **최소 6일 간격으로 짧은 문장 합성**을 실행해 voice_id를 유지한다. 담당자와 일정을 VOICE_LOCK에 기록한다.
3. 보이스가 삭제되면 같은 디자인 프롬프트로 다시 만들어도 같은 목소리가 보장되지 않는다. 이 경우 수정 문장만 새 보이스로 만들지 않고 해당 모듈 전체를 다시 합성한다.

### 5-4. VO 분할 규칙
- H 장면의 VO는 **문장 경계에서 4~15초 청크**로 자른다. H3 클립 길이와 reference_audio 상한 15초에 맞춘다.
- 파일명: `VO_{모듈}{장면}_{청크}_v{버전}.wav` (예: `VO_P4_02_v1.wav`)

---

## 6. 영상 생성 파이프라인

### 6-1. 립싱크 방식 결정 — 1주차 게이트 테스트 [제안]
최종 오디오는 **RA를 통과한 TTS 마스터와 반드시 같아야** 한다. 생성 모델이 대사를 바꿔 말하면 문안 검토가 무효가 된다.

| 경로 | 방법 | 장점 | 확인할 것 |
|---|---|---|---|
| **A (우선)** | 마스터 프레임 + TTS 청크 → 이미지+오디오 립싱크 모델 (MiniMax H3 Max Lip Sync 등) | 오디오가 TTS 원본 그대로 | 공식 MiniMax API 제공 여부 [미확인], 15초 한도, 얼굴 일관성 |
| **B** | H3 I2V (first=last=마스터 프레임, 무음 말하기·손짓) → 별도 립싱크 툴로 TTS를 입힘 | 몸짓 품질은 H3, 오디오는 원본 | 외부 툴 선정·보안 검토 |
| **C (예비)** | H3 reference-to-video: reference_image(CS) + reference_audio(TTS 청크) + 대사를 프롬프트에 명시 | MiniMax 단독 | 음성이 출력되는지, 대사가 원문과 같은지(ASR 대조), 입 모양 일치 [모두 미확인] |

**판정 기준 [제안]** (같은 문장 3개로 경로별 시험)
- 오디오와 원본 TTS 일치 (경로 C는 ASR 전사 대조, 1단어라도 다르면 탈락)
- 입 모양 지연: 육안 2프레임 이내
- 얼굴이 CS-00과 일치
- 15초 클립 끝 프레임이 마스터 프레임에 복귀

### 6-2. 단계별 실행
| 단계 | API·작업 | 입력 | 출력 위치 |
|---|---|---|---|
| 1 | image-01 T2I `n=9`, 9:16 | 호스트 기본 프롬프트 + seed 기록 | `4_테스트/character/` |
| 2 | 후보 선정 → CS-00 | 내부 리뷰 | `5_에셋/character_sheet/CS-00.png` |
| 3 | image-01 I2I + subject_reference(CS-00) | CS-01~04 프롬프트 | `5_에셋/character_sheet/` |
| 4 | image-01 T2I 세트 | SET-00 프롬프트 | `5_에셋/set/` |
| 5 | 마스터 프레임 합성·정리 (세트 + 호스트 + 빈 테이블) | CS-02, SET-00 | `5_에셋/master_frame/MF-01~03.png` |
| 6 | Voice Design → voice_id | 5-1 | `5_에셋/voice/VOICE_LOCK.md` |
| 7 | **게이트 테스트** (경로 A/B/C) | MF-01 + VO 3문장 | `4_테스트/lipsync/` |
| 8 | 대본 RA 승인 → T2A 전량 합성 | 확정 대본 | `2_나레이션/master/` |
| 9 | H 클립 본생성 (확정 경로) | MF + VO 청크 | `3_소스클립/host/` |
| 10 | B-roll 생성: H3 T2V 9:16, 6~10초 (습한 거리, 저녁 욕실 무드, 제품·인물 없음) | 프롬프트 | `3_소스클립/broll/` |
| 11 | D 시연 실촬영 (손 모델, 실제품) | 촬영 리스트 6-4 | `3_소스클립/demo/` |
| 12 | 768P 결과 중 채택 컷만 2K 재생성 (Video Regeneration) | 채택 task | `3_소스클립/host_2k/` |
| 13 | 편집: 레이어 L0~L6, 자막, 국가별 레이어 4벌 | 전체 | `1_최종영상/` |

**H 클립 프롬프트 골격 [제안, 경로 B 기준]**
```
9:16 vertical, static medium shot, livestream shopping host.
Image 1: host (face, hair, outfit must match exactly).
A young woman seated behind a white table in a pink studio, talking warmly to camera,
natural small hand gestures at chest height, gentle nods, blinking naturally.
Empty table surface: no products, no bottles, no text, no logos.
Soft even beauty lighting, no camera movement [Static shot].
No accessories, no rings, no watch. Hands stay below the chin.
```

- 장면별 변수: 시작 표정(CS-03), 손 제스처(가리키는 방향 = 그래픽 카드가 나올 쪽), 클립 길이(VO 청크 길이 + 0.5초)

### 6-3. 생성 물량 추정 [제안, 비용 산정 안 함]
| 구분 | 화면 시간 | 클립 |
|---|---|---|
| H (단독·S 상단 포함) | 약 7.5분 | 평균 12초 기준 약 38개 + 재생성 여유 |
| B-roll | 약 20초 | 3~4개 |
| D 실촬영 | 약 4.5분 분량 | 촬영 리스트 6-4 |
| G 그래픽 | 약 2분 | 편집 제작 |

### 6-4. D 시연 실촬영 리스트 (손 모델 1명, 세로 4K, 동일 조명·배경)
1. 프라이머 클래식: 완두콩 크기 덜기 → 손등 요철 → 반쪽 비교
2. 피니쉬 파우더: 뚜껑에 덜기 → 퍼프 → 반쪽 얼굴(유분 있는 상태 → 보송)
3. 세팅 픽서: 정면·측면 분사 (고속 촬영), 퍼프 분사, 이중 뚜껑 열기
4. 선베이스: [자료 대기]
5. 립앤치크: 손등 워밍 → 퍼프 → 볼 / 1회·2회 레이어링 / 립밤 → 입술
6. 립앤치크 12색 스와치: 같은 피부·같은 조명에서 1회·2회, 컬러칩 그래픽 원본
7. 클렌징밤 3종: 떠내기 → 오일 변화 → 유화 → 헹굼, 3종 각각 용기 오픈 컷
8. 제품 누끼: 전 SKU (Product Lock 기준)

- 시연 결과는 보정·배속 조건을 기록한다. 배속 컷에는 "Time-lapse"를 표기한다.
- ⚠ 기존 공식 시연 영상을 재사용하려면 사용 권리 확인이 필요하다.

---

## 7. 검수 기준 [제안]
| 대상 | 기준 | 불합격 시 |
|---|---|---|
| 호스트 얼굴 | CS-00과 나란히 확대 비교. 눈·코·입·헤어라인 차이 없음 | 재생성 |
| 헤어·의상 | Host Lock 값과 일치. 액세서리가 생기면 탈락 | 재생성 |
| 손 | 손가락 수·관절, 제스처가 화면 밖으로 나가지 않음 | 재생성 |
| 테이블 | 생성 제품·글자가 없음 | 재생성 또는 마스킹 |
| 립싱크 | 지연 2프레임 이내, 오디오는 TTS 원본 | 경로 재적용 |
| 연결 | 클립 시작·끝이 마스터 프레임과 맞음 | 크로스페이드 6~8프레임 또는 재생성 |
| 제품 합성 | Product Lock 비율·색 기준 | 누끼 재배치 |
| 문안 | RA 승인본과 VO·자막 일치. 국가 레이어 가격·기간 일치 | 수정 |
| 표기 | AI 호스트, 시험 조건(수치 사용 시), Time-lapse | 추가 |

생성 기록은 `4_테스트/generation_log.csv`에 남긴다 (task_id, 모델, 프롬프트, 레퍼런스, seed, 길이, 판정, 사유).

---

## 8. 일정 [제안 — 11월 방영일 확정 전 가정]
| 주차 | 기간 | 작업 |
|---|---|---|
| W1 | 10/13–10/19 | 캐릭터 시트·세트·보이스 확정. **립싱크 게이트 테스트**. 대본 v1 (클렌징밤·선베이스 자료 수령 시 반영) |
| W2 | 10/20–10/26 | RA 검토 → VO 전량 합성. D 실촬영. H 클립 본생성 시작 |
| W3 | 10/27–11/02 | H 클립 완료, 2K 재생성, 편집, 국가별 레이어 4벌 |
| W4 | 11/03–11/09 | 최종 검수, 컷다운 3편, 업로드 준비 |

방영일을 알려주면 이 일정을 역산해 다시 맞춘다.

## 9. 리스크와 대응
| 리스크 | 대응 |
|---|---|
| 공식 MiniMax API에 립싱크가 없음 | 게이트 테스트에서 경로 B(외부 립싱크)로 전환. 외부 툴은 보안·약관 검토 |
| 클립 간 얼굴 변화 | 같은 마스터 프레임에서 시작·종료, 검수 기준 적용, 불합격 재생성 |
| 보이스 7일 삭제 | 전량 선합성 + 6일 간격 유지 합성 |
| 제품 변형 | 제품 생성 금지, 실물 합성만 사용 |
| 클렌징밤·선베이스 자료 지연 | 모듈 순서상 마지막 제작. 자료 없이는 해당 장면 VO를 만들지 않는다 |
| 동남아 광고 표현 기준 미확인 | 외관·사용감 표현으로 한정하고 RA 판정 후 고정 |
