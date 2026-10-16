# BANILA CO Shopee AI 진행자: 영어 음성·립싱크 후보 검토

확인일: 2026-10-02 KST. 범위: 공식 문서와 읽기 전용 모델 카탈로그 비교. 유료 생성, 구매, 설치, 실제 영상 품질 검증은 실행하지 않았다.

**조건부 권고: 승인한 영어 master audio를 먼저 고정하고, HeyGen Avatar IV/V와 Sync를 동일 입력으로 비교한다.** 15–45초 혜택 설명 클립을 제작해 상품 카드·승인된 원본 USP 영상과 편집한다. AI 진행자의 직접 시연이나 실제 사용 경험을 새로 만들어내는 방식은 이 평가의 제작 범위가 아니다. 현재 체크아웃에는 참고 index만 있고 실제 제작 이미지·영상은 확보되지 않았으므로 모델 채택도 아직 미정이다.

본 노트는 생성 엔진의 검토다. 사전 제작물을 Shopee에서 24시간 공개 반복 송출할 수 있다는 승인이나 플랫폼 적합성 판단을 의미하지 않는다. 송출 정책과 국가별 운영 조건은 부모 계획의 별도 확인 항목이다.

## 1. 최종 비교 후보

| 평가 항목 | HeyGen Avatar IV / V | Sync: sync-3 / lipsync-2-pro |
|---|---|---|
| 주요 역할 | 승인된 이미지·등록 아바타를 새 영어 음원에 맞춰 진행자 영상으로 렌더 | 승인된 진행자 영상의 입 모양을 새 음원에 맞춤. sync-3는 이미지 입력도 지원 |
| 외부 master audio | v3 Audio to Video에 `audio_url` 또는 `audio_asset_id` 사용. script와 동시 사용하지 않음. MP3/WAV 업로드 지원. [공식 입력 문서](https://developers.heygen.com/audio-to-video) | 영상 또는 이미지 + 외부 WAV/MP3를 URL/asset로 전달. API는 음성 입력과 립싱크 생성을 분리할 수 있음. [공식 API 개요](https://sync.so/docs/api-reference/api-overview), [sync-3 입력](https://sync.so/docs/models/sync-3) |
| 영어 발음·운율 통제 | 직접 script→TTS도 가능하지만, 가격·브랜드 발음을 먼저 검수한 외부 음원을 쓰는 경로를 권고. 음원 품질과 시각적 말하기 품질을 별도 평가 | 립싱크 엔진이 영어 발음을 교정하는 것으로 간주하지 않음. 같은 검수 음원으로 입·얼굴 성능을 평가 |
| 고정 진행자 | IV는 `studio_avatar`, `digital_twin`, `photo_avatar`, image/prompt 지원. V는 eligible `digital_twin` look에 한정되며 `supported_api_engines`에 `avatar_v`가 있어야 함. [IV](https://developers.heygen.com/avatar-iv), [V](https://developers.heygen.com/avatar-v) | 2/pro는 입력 영상에서 자연스럽게 말하는 동작이 필요. 정지 얼굴이나 말하지 않는 구간을 그대로 넣는 경로는 부적합. sync-3는 무음 입을 열 수 있지만 원래 말하기 스타일과 같은 결과가 보장되지는 않음. [입력 caveats](https://sync.so/docs/models/lipsync) |
| 반복 생산/API | v3 batch 최대 100개, 비동기 job 상태·webhook, PAYG 동시 작업 10개. [Batch](https://developers.heygen.com/batch-videos), [Limits](https://developers.heygen.com/docs/usage-limits) | 일반 API 비동기 처리·webhook. Creator 동시 3개/5분, Growth 6개/10분, Scale 15개/30분. Batch는 Scale+에서 최대 500개, 최소 20개, 문서상 24시간 turnaround. [API 개요](https://sync.so/docs/api-reference/api-overview), [가격/플랜](https://sync.so/pricing) |
| 15–45초 운영 단위 | 이번 모듈 길이는 공개 제한보다 충분히 짧음. Audio to Video 문서의 최대 30분과 Limits의 audio input 10분 항목이 상충하므로 장편 최대치를 확정 계약 사양으로 인용하지 않음 | 모듈 길이는 유료 플랜 한도 이내. 2/pro에는 컷이 잦은 완성 편집본 대신 말하는 얼굴이 계속 보이는 독립 shot을 입력 |
| 상업 사용·동의 | 공식 FAQ는 적법한 입력을 전제로 상업 배포 허용. 실인물 digital twin은 동의 절차 필요. photo에 API 동의 단계가 없어도 초상 사용 허락은 필요. [배포 FAQ](https://help.heygen.com/en/articles/9380615-digital-twin-faq), [동의](https://developers.heygen.com/docs/avatar-consent) | 유료 모든 subscription tier에 상업 사용·광고 사용 권한 안내. 원본 얼굴·음성·영상 권리와 필요한 동의는 이용자가 확보. [상업 권한](https://support.sync.so/articles/2618163041-commercial-usage-rights-across-sync-so-subscription-plans), [약관](https://sync.so/terms) |
| 실제 품질 판단 | V/IV의 자연스러움·identity 우열은 이번 자료 조사로 검증하지 않음 | sync-3/2-pro의 자연스러움·identity 우열은 이번 자료 조사로 검증하지 않음 |

V는 현재 공식 v3 API에 존재한다. 웹 전용 후보로 제외하지 않는다. 반대로 V가 합성 캐릭터 또는 임의 photo look에 항상 적용된다고 가정하지 않는다. eligible look과 동의 상태를 실제 계정에서 확인한 뒤 선택한다. [Avatar V API](https://developers.heygen.com/avatar-v)

## 2. 비용 계산: 채택한 새 영상 분량 기준

2026-10-02에 공식 페이지를 직접 열어 확인한 USD 기준이다. 검색 캐시의 과거 단가를 쓰지 않았다. HeyGen 도움말은 2026-09-16 업데이트라고 표시한다. [HeyGen API 최신 표](https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained)

| 렌더 경로 | 공개 단가 | 30초 1회 생성 산술값 |
|---|---:|---:|
| HeyGen IV Photo | $2.31 / 생성 분 | $1.155 |
| HeyGen IV Digital Twin / Studio | $4.83 / 생성 분 | $2.415 |
| HeyGen V Digital Twin | $7.20 / 생성 분 | $3.60 |
| Sync lipsync-2, Creator 기준 25fps | $0.05 / 초 = $3.00 / 분 | $1.50 |
| Sync lipsync-2-pro, Creator 기준 25fps | $0.08325 / 초 = $4.995 / 분 | $2.4975 |
| Sync sync-3, Creator 기준 25fps | $0.13340 / 초 = $8.004 / 분 | $4.002 |

Sync Creator에는 $19/월 subscription이 별도로 붙는다. 표의 초당 단가는 25fps 기준이며 실제 frame 수·tier·할인에 따라 달라진다. Scale은 subscription $249/월과 사용 할인 구조이므로 소량 테스트에 자동 선택하지 않는다. [Sync 가격표](https://sync.so/pricing)

계산식:

```text
U = 최종 채택한 신규 AI 진행자 영상의 분량(분)
f = 총 유료 생성 분량 / 최종 채택 분량
C_render = U × f × 해당 엔진의 분당 단가
C_total = C_render + 음성 생성/녹음 + 아바타 생성/동의 제작
          + 월 subscription/계약 비용 + 편집·QA + 보관·송출 + 세금
```

`f`는 실패, 추가 take, 미채택 결과, 변경된 프로모션의 재생성을 포함한 실측 값이다. 1.0/1.3/1.6은 초기 예산의 민감도 시나리오이며 검증된 평균이 아니다. 24시간 재생하는 이미 채택된 파일을 반복한다고 새 립싱크 생성비가 매번 발생하는 구조로 계산하지 않는다. 24시간 전체가 신규 제작이면 U가 증가한다. 반복 송출 가능 여부는 별도 플랫폼 검토다.

예: U=60분, f=1.3이면 78분 생성이다. IV Digital Twin은 $376.74, V는 $561.60, Sync pro는 $389.61 + Creator $19, sync-3는 $624.31 + Creator $19의 렌더 산술값이다. 동일 품질이라는 가정은 없고 음성·원본 제작·QA·송출비는 제외했다. API/엔진/해상도별 실제 계정 청구액과 환불 조건은 제작 전에 재확인한다.

HeyGen 공개 표에는 Starfish TTS $0.12/음성 분, Digital Twin 생성 $2.13/call도 있으나 실제 custom twin API 생성 권한은 도움말과 최신 개발 문서 사이 차이가 있어 계정 확인 항목이다. 아바타 생성 권한·API 렌더 권한·웹 요금제를 하나로 간주하지 않는다. [공식 가격/권한 안내](https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained), [동의 access levels](https://developers.heygen.com/docs/avatar-consent)

## 3. 비교 실험과 채택 조건

아래는 **실행 전 프로젝트 제안 기준**이다. 공급사 성능 보장이나 완료된 측정 결과가 아니다.

1. 영어 음성을 먼저 고른다. 브랜드가 승인한 BANILA CO 발음, 제품 이름, 통화·숫자·쿠폰·조건을 음성만으로 검수한다. neutral English의 명료도와 억양을 우선 보고 실제 목표 국가의 영어 청취자에게 확인한다. 승인 master WAV와 checksum을 보관하고 립싱크 업체가 음성을 다시 만들게 하지 않는다.
2. 공정한 동일 입력 비교를 두 트랙으로 나눈다. 이미지 트랙은 같은 승인 portrait + 같은 master audio로 HeyGen IV image와 Sync sync-3 image를 비교한다. 동의 받은 실인물 영상 트랙은 같은 진행자 원본 shot에서 V digital twin과 Sync video 입력을 구성한다. 학습/입력 구조가 달라 완전 동일 조건이라고 부르지는 않는다. 2/pro는 talking-motion source를 확보한 경우에만 추가한다.
3. 15초·30초·45초에서 각 3–5문장, 정면 shot을 우선 시험한다. 코드·가격·최소 구매액·할인 cap, /p b m f v/가 포함된 말, 문장 사이 쉼, 미소 뒤 말하기를 넣는다. 얼굴·메이크업·치아·빛·의상은 동일하게 유지한다.
4. 업체명을 숨기고 평가 순서를 무작위로 배치한다. 5명 영어 청취자의 음성 자연스러움·입 움직임·얼굴 유지·표정·반복 시청 피로를 각각 5점 평가하고 각 오류를 timestamp로 적는다. 브랜드 담당자가 제품 카드와 가격·쿠폰·조건·발음을 별도로 대조한다.
5. 시작 목표: 혜택·숫자·발음의 중대한 오류 0건, 평균 자연스러움 4/5 이상, 5명 중 4명 이상 채택 가능 판정. 립싱크는 frame 단위로 점검하고 주요 입 닫힘/열림 구간에서 25fps 기준 약 2frame(80ms) 이내를 검토 목표로 둔다. 지속적인 어긋남, 얼굴 drift, 치아·입 주변 flicker는 실패 처리한다. 숫자 오류는 평균 점수로 상쇄하지 않는다.

30초 실험용 대본 예시 — **가상의 수치이며 판매 혜택으로 사용 금지**:

> Welcome to BANILA CO on Shopee.
> The bundle includes one full-size item and two minis.
> The price is twenty-nine Singapore dollars and ninety cents.
> Use code B A N I L A one zero for ten percent off, capped at five dollars, with a minimum spend of forty dollars.
> Check the product card for the current terms and availability.

실제 제작에서는 수치·구성을 승인된 SKU와 프로모션 데이터로 대체한다. 생성 전 발음용 문자열과 화면 표시 문자열을 구분하고, 양쪽이 같은 값을 나타내는지 대조한다. 최종 영상 길이·자막·입 모양은 승인한 음원에 맞추고 편집 후 말속도 변형으로 입·음성 싱크를 깨뜨리지 않는다.

재현은 새로 생성한 영상이 byte 단위로 같다는 뜻이 아니다. source checksum, master audio checksum, script/offer version, avatar/look/model ID, 입력 payload, job ID, 평가표, 채택 MP4를 보관해 같은 제작 조건을 다시 제출할 수 있게 한다. 네트워크 retry는 같은 action의 idempotency key를 재사용하고, 품질 개선을 위한 새 take는 별도 action으로 기록한다. [HeyGen batch idempotency](https://developers.heygen.com/batch-videos), [Sync idempotency](https://sync.so/docs/api-reference/guides/idempotency)

## 4. 사전 제작과 실시간 대화는 별도 제품

이번 비교 경로는 비동기 렌더가 완료된 파일을 검수해 편성하는 사전 제작이다. HeyGen LiveAvatar는 별도 realtime API와 FULL/LITE 대화 구조를 가진다. Avatar IV/V 영상 생성 API와 같은 과금·세션·기능으로 취급하지 않는다. [LiveAvatar 공식 구분](https://developers.heygen.com/live-avatar), [API 가격의 streaming 구분](https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained)

실시간 고객 질문 대응은 초기 범위에서 자동 약속·할인 답변까지 확대하지 않는다. 승인된 FAQ/상품 데이터 기반 문답과 운영자 핸드오프를 별도 단계로 검증한다. 사전 제작물은 댓글에 실제로 응답한 것처럼 말하거나 방금 받은 질문·재고를 확인했다고 표현하지 않도록 대본을 설계한다.

## 5. 보류한 후보·남은 확인

Synthesia는 이번 우선 비교에서 보류한다. 실제 배우 stock은 프로모션 제한이 있고, photo Personal/Express-2/Synthetic은 공식 표상 Video API 미지원이다. Custom Studio(Express-1)는 API 가능하나 별도 제작비 $1,000/아바타와 외부 음원 Enterprise 요건이 있어 초기 실험의 부담이 크다. Studio나 Personal을 마케팅에 쓰는 경우에도 승인된 얼굴·음성 및 해당 계약을 확인한다. [아바타 공식 비교](https://help.synthesia.io/en/articles/15197011-which-avatar-type-is-right-for-me), [외부 음원 요건](https://docs.synthesia.io/docs/script), [외부 음원 API](https://docs.synthesia.io/reference/upload-script-audio)

Higgsfield의 읽기 전용 model search에서는 native audio/audio references 중심 영상 모델을 확인했지만, 정확한 승인 master audio를 변경 없이 전달하고 15–45초 고정 진행자로 생산하는 전용 avatar/lipsync 경로를 충분히 검증하지 못했다. 지원하지 않는다는 단정은 하지 않으며 이번 두 후보 benchmark에 추가하지 않는다. 커넥터 검색 확인: 2026-10-02, `models_search(query="avatar"/"lipsync"/"audio lipsync", type="video")`. 크레딧을 사용하지 않았다.

브랜드 원본을 외부에 업로드할 때 Sync의 일반 약관은 content 사용 권한을 넓게 정하고 있으며 zero data retention은 공식 help상 Enterprise 옵션이다. 중요 원본의 학습·보관·2차 활용 조건은 실제 계약에서 확인할 항목이다. [Sync 약관](https://sync.so/terms), [데이터 보관 옵션](https://support.sync.so/articles/3861799718-what-are-your-data-retention-policies-and-can-we-opt-out-of-data-collection)

종료 조건: 동일 음원 실험에 통과한 엔진 1개, 최종 진행자 1개, 발음·혜택 오류가 없는 승인 클립, 실측 재생성 배수와 비용. 그 전에는 품질 1위·최저 비용·24시간 공개 운영 승인으로 표기하지 않는다.
