# ASR 대본 가드 — 대본에 없는 말 막기·잘라내기

배경: POC studio04(2026-10-13)에서 MiniMax H3가 대사 중간에 대본에 없는 말("BAAC… pylacety" 등)을 넣었습니다. 립싱크 단계를 빼고 영상 모델이 음성까지 만드는 구조라, **생성 단계(예방)**와 **검수·편집 단계(제거)** 두 겹으로 막습니다.

## 1. 예방 — 생성 프롬프트 규칙
- 대사는 **문장 2개 이하, 클립당 약 25단어 이하**로 나눈다(15초 클립 기준). 긴 대사일수록 이탈 위험이 클 것으로 추정(미검증).
- 프롬프트에 대사를 큰따옴표로 정확히 넣고 다음 문구를 붙인다:
  `She says exactly this line in English and nothing else: "<대사>". No extra words, no repeated phrases, no humming or filler sounds. After the line, she smiles silently.`
- 대사 끝에 **1~2초 무언 여유**(미소·끄덕임)를 지시해, 남는 시간에 모델이 말을 지어내지 않게 한다. (효과는 미검증. POC studio04의 이탈은 끝이 아니라 대사 중간 7.0–11.2초에 생겼다)
- 제품명·숫자는 철자대로 풀어 쓴다(`fifty percent`, `oh-two`).

## 2. 검수 — 생성 직후 자동 실행
```
python -X utf8 5_에셋/scripts/asr_script_guard.py <clip.mp4> --script "<대사>" --out 4_테스트/asr_guard/<장면> --apply
```
- ASR 2종(faster-whisper base·small)으로 받아 적고 대본과 단어 정렬 → 대본에 없는 말 구간을 찾음.
- 판정: **pass**(그대로 사용) / **cut-needed**(이탈 구간을 잘라낸 `_cut.mp4` 자동 생성) / **regenerate**(대본 단어가 빠졌거나 잘라낼 길이가 클립의 40% 초과).
- 임계값: 오인식 허용 유사도 0.5, 확정 = 두 모델 공통 + 구간 음량 −35dB 이상, 커버리지 0.9 이상, 1초 미만 남는 조각은 함께 컷.
- 한 모델만 잡은 구간은 `suspect` → 사람이 해당 초만 들어봄.

## 3. 편집
- cut-needed면 `_cut.mp4`(또는 guard.json의 `keep_segments_s`)를 편집 원본으로 쓰고, 잘린 지점은 그래픽 카드·시연 인서트로 덮어 화면 튐을 가린다.
- 컷본도 가드를 한 번 더 돌려 pass 확인.

## POC 실측 (2026-10-13)
| 클립 | 판정 | 내용 |
|---|---|---|
| studio03 | pass | 커버리지 1.0, 이탈 0 |
| studio04 | cut-needed | 이탈 7.00–11.16초(4.16초, 음량 −19.0dB, 두 모델 공통) → keep 0–6.92초 + 11.24–15.10초, 컷본 10.79초 |
| studio04 컷본 재검사 | pass | 커버리지 1.0, 확정 이탈 0 (small 단독 suspect 1건: 3.62초 "a"↔대본 "the", 오인식) |

참고: 이전 POC 보고의 이탈 구간 "6.9–9.7초"는 같은 ASR 결과를 사람이 읽어 잡은 범위였고, 가드는 뒤쪽 9.7–11.2초의 비대본 발화("Mataanjutu Mephas din" 등)까지 잡았습니다. ASR 결과는 실행마다 철자가 조금씩 달랐지만 구간은 같았습니다. 청취 확인은 아직 하지 않았습니다.
