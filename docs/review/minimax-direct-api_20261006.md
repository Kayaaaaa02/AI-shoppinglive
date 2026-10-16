# MiniMax H3 직접 생성 조사 — 2026-10-06

최신 요청은 [MiniMaxAI/MiniMax-H3 공개 모델](https://huggingface.co/MiniMaxAI/MiniMax-H3)을 로컬에 설치하여 기존 Seedance/Higgsfield MiniMax 영상과 비교하는 것입니다. H3는 영상과 음성을 함께 만드는 모델이며, 별도 TTS만 생성하는 데모는 이 요청을 충족하지 않습니다. 이 문서는 공식 자료 조사 결과이며 설치·가중치 다운로드·유료 생성은 실행하지 않았습니다.

## 로컬 설치에 먼저 적용되는 조건

현행 공개 [LICENSE I.5·II](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)는 대한민국을 허용 범위에서 제외하고 별도 사용권 문의를 안내합니다. 공식 [H3 사용권 신청](https://platform.minimax.io/h3-license) 경로가 있습니다. 공개 가중치를 한국에서 실행하기 전에 별도 허용을 확인해야 합니다. 기존 Higgsfield 결과나 별도 공식 API 계약의 권한까지 이 공개 가중치 약관만으로 단정하지 않습니다.

[공식 배포 안내](https://platform.minimax.io/docs/guides/local-deploy-h3)의 소비자용 공개 사례는 RTX 4090 24 GB에서 INT8와 레이어 오프로딩을 사용하여 GPU 메모리 약 18 GB를 관측한 설정입니다. 안내 자체가 이 사례를 upstream 구성으로 분류하며 MiniMax 하드웨어 검증으로 보장하지 않습니다. 따라서 현 RTX 4080 16 GB·RAM 64 GB의 성공 경로는 확인되지 않았습니다. 16 GB에서 모든 구현이 절대 불가능하다는 뜻은 아닙니다. 같은 안내의 2 GPU vLLM 오프로딩 설정은 가용 RAM 200 GiB 이상, 384 GiB 권장을 제시합니다.

공개된 것은 **768p H3-Base FL2VA/Ref2VA**입니다. 영상과 동기화 스테레오 음성을 생성하지만 Context-IR과 2K 재생성 모듈은 공개되지 않았습니다. [모델 카드](https://huggingface.co/MiniMaxAI/MiniMax-H3)

## 별도 공식 API 경로

공식 API도 확인했습니다. `POST https://api.minimax.io/v2/video_generation`에 `MiniMax-H3`, `2K`, 정수 `duration: 15`를 제출할 수 있습니다. API Key를 Bearer 헤더에 넣으며 계정의 API 이용 권한·잔액을 사용합니다. Token Plan 구독 키와 pay-as-you-go API 키는 구분됩니다. [생성 문서](https://platform.minimax.io/docs/api-reference/video-generation-v2-create), [유료 서비스 약관](https://platform.minimax.io/protocol/paid-agreement)

아래는 검증된 형식의 **미제출 템플릿**입니다. 실제 키·이미지 데이터·생성 완료값은 포함하지 않습니다.

```json
{
  "model": "MiniMax-H3",
  "content": [
    {"type": "text", "text": "<영상 장면과 발화 대사 프롬프트>"},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,<BASE64>"}, "role": "first_frame"}
  ],
  "resolution": "2K",
  "duration": 15,
  "ratio": "adaptive"
}
```

`image_url`는 `{url: ...}` 객체입니다. 공개 URL·`mm_file://`·Data URI를 지원합니다. 첫 프레임 모드의 비율은 이미지로 결정됩니다. 인물 참고만 사용하려면 `role: reference_image`로 바꾸며 이 경우 `9:16`을 지정할 수 있습니다. 첫/마지막 프레임과 참고 자료 모드는 함께 섞을 수 없습니다. 별도 `character_id`, `voice_id`, `generate_audio` 필드는 선언되어 있지 않습니다. [실제 OpenAPI 스키마](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json)

생성 응답의 `task_id`로 `GET https://api.minimax.io/v2/query/video_generation/{task_id}`를 조회하고 `task.status=succeeded`일 때 `task.content.url`에서 MP4를 받습니다. 조회 대상은 최근 7일이며 다운로드 URL은 유효 시간이 있어 바로 저장해야 합니다. 정확한 URL 만료 시간은 공개 스키마에 없으며 만료 후 다시 조회하여 새 URL을 받을 수 있습니다. [조회 문서](https://platform.minimax.io/docs/api-reference/video-generation-v2-query), [스키마](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json)

H3는 영상·스테레오 음성 잠재표현을 함께 예측하며 영어·한국어 대화를 지원합니다. 별도 TTS 생성 비용을 붙이는 방식이 아닙니다. 브랜드의 실제 발음과 입 모양·연기 품질은 생성 후 검수해야 합니다. [공식 연구 설명](https://www.minimax.io/blog/minimax-h3), [모델 카드](https://huggingface.co/MiniMaxAI/MiniMax-H3)

## 공식 목록가

| 설정 | 15초 출력 가격 | 추가 입력 비용 |
|---|---:|---|
| H3 2K | $1.95 | 오디오 무료, 첫 5장 무료, 입력 영상 $0.13/초 |
| H3 768P | $1.20 | 오디오 무료, 첫 5장 무료, 입력 영상 $0.08/초 |

출력은 각각 $0.13/초·$0.08/초입니다. 한 장의 홈 앵커와 텍스트를 사용하고 입력 영상 없이 한 번 생성하는 조건입니다. 표에 생성 오디오의 별도 할증은 없으며 오디오 on/off 과금 필드도 확인되지 않았습니다. 세금·결제 수수료·환율·계정 할인과 재생성 비용은 별도입니다. Higgsfield 크레딧을 직접 API 달러와 같은 단위로 취급하지 않습니다. [공식 가격표](https://platform.minimax.io/docs/pricing/overview)

보장된 공통 H3 무료 체험 크레딧 수량은 공개 FAQ·가격표·약관에서 확인되지 않았습니다. [개발자 프로그램](https://platform.minimax.io/contact-us)은 API 크레딧을 안내하지만 공개된 고정 금액이나 자동 지급 조건이 없으므로 계정 확인 전 무료 생성을 가정할 수 없습니다.

생성 요청을 보내지 않았으므로 실제 생성 시간·과금·영상 품질은 측정값이 없습니다. 로컬 실행은 한국 사용권과 적합한 하드웨어 경로가 아직 미확인입니다. API 형식은 로컬 설치를 대신 완료했다는 증거가 아닙니다.
