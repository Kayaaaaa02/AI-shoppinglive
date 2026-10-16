# Higgsfield 원화 비용·모델 출처 근거 — 2026-10-06

확인일: **2026-10-06**. 공식 문서·공식 개발사 저장소만 사용했다. 이 문서는 외부 가격·환율·모델 공개 범위 조사이며, 생성 요청·구매·설치·계정 변경은 수행하지 않았다. 개별 크레딧은 주 에이전트가 전달한 endpoint 견적이며 **실제 사용 내역 차감은 미확인**이다.

## HTML에 바로 사용할 결론

- 기본 표시: **“Higgsfield 표준 크레딧 환산 기준 원화 추정, 실제 결제액 아님”**.
- 공식 MCP 안내의 **20cr = $1**와 미 연준 H.10의 **2026-10-02 USD/KRW 1,345.75**를 적용하면 **1cr ≈ 67.2875원**이다.
- 충전 팩의 현재 결제 가격·할인과 사용자 구매 내역은 확인되지 않았다. 표준 환산을 “실제 충전 팩 구매 단가”라고 쓰지 않는다.
- MiniMax H3는 **Base 가중치 공개·일부 파이프라인 비공개**, Seedance 2.5 개발사는 **ByteDance Seed**다. 이번 연결 비용은 Higgsfield 서비스 호출의 견적이며 로컬 공개모델 실행 비용이 아니다.

## 크레딧 가격과 과금 경로

| 기준 | 공식 확인 | 해석 |
| --- | --- | --- |
| MCP 표준 환산 | 20cr / $1 | $0.05/cr. 실제 팩 구매 영수증과 다름 |
| Starter 플랜 | $15/월, 200cr | 전체 구독료를 크레딧에 배부하면 $0.075/cr. 기능 포함·전량 소진 가정 |
| 고정 충전 팩 | 100 / 200 / 500 / 1,000 / 2,000 / 4,000cr | 현재 USD 가격·할인은 checkout에만 표시 |
| 조절형 충전 팩 | 5,000–25,000cr, 1,000cr 단위 | 현재 USD 가격 확인 불가, 유효기간 90일 |
| 직접 Higgsfield API | 별도 선불 USD 잔액 | MCP 플랜 크레딧과 별도 상품·잔액 |

Higgsfield의 10월 2일 공식 안내는 MCP가 웹 계정의 플랜 크레딧을 표준 단가로 사용하고, 직접 API는 별도 USD 잔액을 사용한다고 구분한다. 플랜별 크레딧 배부 단가와 표준 환산은 다른 계산이다. 직접 MiniMax API의 영상 초당 요금도 이 MCP 원화 계산에 섞지 않았다. [공식 MCP/API 안내](https://higgsfield.ai/blog/automate-ai-video-n8n-make)

충전 팩 도움말(8월 3일)은 팩 크기를 공개하지만 현재 가격과 할인은 checkout에서 확인한다고 명시한다. 공개 pricing 페이지의 조회 결과에서는 결제용 가격표를 확보하지 못했다. 구독 크레딧이 먼저 소진되고 충전 팩은 90일 유효하다. [공식 충전 팩 도움말](https://higgsfield.ai/creator-hub/help-center/credits/how-credit-packs-work), [공식 pricing](https://higgsfield.ai/pricing)

Starter $15/200cr는 Higgsfield 공식 비교 글에서 직접 확인한 참고 플랜이다. 사용자의 실제 플랜·청구 단가라는 증거는 없다. 최신 공식 10월 안내 역시 지역별 플랜 차이를 명시하므로 계정별 결제 가격으로 확정하지 않는다. [Starter 포함량 근거](https://higgsfield.ai/blog/best-affordable-ai-video-generators), [10월 플랜 안내](https://higgsfield.ai/blog/new-ai-influencer)

## 환율과 견적 환산

미 연준 **2026-10-05 발표**의 최신 확인 관측일은 **2026-10-02**, 환율은 **1 USD = 1,345.75 KRW**이다. FRED DEXKOUS에서 같은 수치를 재확인했다. 이는 뉴욕 정오 매입 환율 참고값이며 카드 결제 환율이 아니다. 세금·해외결제 수수료·카드 환율 가산·할인은 제외했다. 합계를 정밀도로 계산한 뒤 원 단위로 반올림한다. [Federal Reserve H.10](https://www.federalreserve.gov/releases/h10/current/), [FRED DEXKOUS](https://fred.stlouisfed.org/series/DEXKOUS)

공식 표준 환산: `KRW = cr × ($1 / 20cr) × 1,345.75`.

| 항목 | 크레딧 | 표준 USD 환산 | 표준 원화 추정 | Starter 구독료 배부 시 참고값 |
| --- | ---: | ---: | ---: | ---: |
| 스튜디오 기준 이미지 | 1.5 | $0.075 | 101원 | 151원 |
| 기존 Seedance 2.5 스튜디오 30초 1080p | 360 | $18 | 24,224원 | 36,335원 |
| 기존 MiniMax H3 스튜디오 15초 2K | 30 | $1.5 | 2,019원 | 3,028원 |
| Seedance 2.5 홈쇼핑 15초 1080p | 180 | $9 | 12,112원 | 18,168원 |
| 기존 3개 항목 견적 합계 | 391.5 | $19.575 | 26,343원 | 39,515원 |
| 추가 4개 항목 조건부 시나리오 합계 | 241.5 | $12.075 | 16,250원 | 24,375원 |
| 기존 견적과 추가 시나리오 누적 | 633 | $31.65 | 42,593원 | 63,889원 |

**수치 상태:** 기존 이미지 1.5cr, Seedance 스튜디오 30초 1080p 360cr, H3 스튜디오 15초 2K 30cr는 주 에이전트가 전달한 endpoint 견적이다. 추가 241.5cr는 H3 재시도 30 + 홈 기준 이미지 1.5 + Seedance 홈 180 + H3 홈 30의 조건부 합계다. 홈 영상 180cr·30cr는 이 문서를 작성할 때 재확인 전이었다. 실제 생성 성공·차감·구매액으로 표시하지 않는다. 단위 환산을 달리해도 원래 견적 상태는 바뀌지 않는다.

## 모델 개발사와 공개 범위

| 모델 | 개발사 | 확인한 공개 범위 | HTML 권장 표기 |
| --- | --- | --- | --- |
| MiniMax H3 | MiniMax | H3-Base FL2VA·Ref2VA 가중치 공개, 로컬 Base는 768p. Context-IR·Regenerate-2K 및 초기 sparse-attention 구현은 현재 공개 범위에서 제외. 영어 포함 11개 대화 언어 명시 | “MiniMax · H3-Base 가중치 공개(Community License), 2K 전체 파이프라인 일부 비공개 · Higgsfield 유료 호출” |
| Seedance 2.5 | ByteDance Seed | 2026-07-31 출시, 음성·영상 공동 생성, 단일 최대 30초. 공식 사이트에서 API/서비스 접근 확인. 공개 가중치·오픈 모델 라이선스는 확인하지 못함 | “ByteDance Seed · Seedance 2.5 · Higgsfield 유료 호출, 공개 가중치 미확인” |

H3를 전체 비공개 모델로 분류하거나 2K 전체 파이프라인이 완전히 공개됐다고 분류하면 모두 부정확하다. 공개 가중치는 **MiniMax H3 Community License**를 따르며 지역·상업 이용 제한이 있는 별도 라이선스다. MIT/Apache처럼 제한 없는 오픈소스로 표기하지 않는다. [MiniMax 공식 저장소](https://github.com/MiniMax-AI/MiniMax-H3), [공식 가중치](https://huggingface.co/MiniMaxAI/MiniMax-H3), [라이선스 원문](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE), [공식 로컬 실행 문서](https://platform.minimax.io/docs/guides/local-deploy-h3)

Seedance의 개발사·출시일·음성 영상 공동 생성 기능은 개발사 공식 발표와 모델 페이지에서 확인했다. 공개 가중치가 없다는 영구적 단정은 하지 않는다. [ByteDance Seed 공식 출시 발표](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5), [공식 모델 페이지](https://seed.bytedance.com/en/seedance2_5)

## 생성 소요 시간과 미확인 정보

본 조사에서 실제 job 시간을 확인하지 않았다. 주 에이전트의 job 기록으로 `완료 시각 - 제출 시각`을 계산해 **“실측 대기+생성 시간”**으로 표시한다. 이 값은 순수 GPU 렌더 시간이 아니다. 업로드·견적 조회·다운로드·편집 시간은 따로 기록한다. 결과 영상 길이 15초/30초를 생성 대기 시간으로 사용하지 않는다. 공식 안내는 비동기 제출→대기열→완료→다운로드를 구분하며 모델별 보장 생성 시간은 제공하지 않는다. [공식 비동기 lifecycle 안내](https://higgsfield.ai/blog/automate-ai-video-n8n-make)

미확인: 현재 계정 checkout 충전 팩 가격·할인, 구매 영수증과 원화 카드 청구, 개별 ledger 차감, 실제 job 소요 시간, Higgsfield 모델 별칭의 정확한 backend checkpoint revision, Seedance 2.5 공개 가중치·라이선스. 기계 판독용 숫자·가정은 동일 이름의 JSON에 기록했다.

