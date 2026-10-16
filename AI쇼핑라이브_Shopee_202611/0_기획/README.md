# 0_기획 — 제작설계 HTML 두 가지

> Git 저장소에는 이 폴더의 `build_*.py`와 md 문서만 있습니다. HTML 결과물·`공유용/`·`개발자용/`은 원본 미디어가 있는 제작 PC에만 있습니다.

| 구분 | 위치 | 누가 보나 | 내용 |
|---|---|---|---|
| **개발자용** | `개발자용/Shopee_AI쇼호스트_제작설계_v4.html` | 제작 담당(로컬) | 전체 작업본. 영상·음성 재생, 구간 이동 버튼, 생성 파이프라인·스크립트·파일 경로, 비용(17장, "실제 사용분 / 테스트·폐기" 구분 17-3 포함) |
| **공유용** | `공유용/dcsai_bundle/index.html` → https://dcsai.fnf.co.kr/server/quick-dashboard/shopee-ai-live-plan | 공유 대상 | 한 장짜리: ① 최종 영상 3편(장면별 화면) ② 대본(토글) ③ 배너·그래픽 시안 ④ 실무자 확인 필요. 작업 플로우·비용·스크립트는 넣지 않음 |

## 다시 만들기 (순서)

1. 개발자용: `python -X utf8 0_기획/build_v4.py` (v3 빌드 결과를 읽어 `개발자용/`에 씀)
2. 공유용: `python -X utf8 5_에셋/scripts/build_share_page.py` (개발자용에서 필요한 부분만 골라 `공유용/dcsai_bundle/`에 씀, 이전 묶음은 `4_테스트/_old_dcsai_qd_*`로 이동)
3. 배포: `cd 0_기획/공유용 && dcs-ai-cli app update shopee-ai-live-plan --path ./dcsai_bundle` (주소 유지)

공유용은 개발자용에서 자동 생성되므로 직접 고치지 않는다.

## dcsai(Quick Dashboard) 제약 — 실측

- mp4·wav·mp3는 올릴 수 없다 → 최종 영상은 장면별 대표 화면으로 보여 준다.
- 한글 파일 경로, 하위 폴더 파일, 이전과 같은 이름으로 다시 올린 파일은 깨졌다 → 영문 이름 + 빌드마다 새 이름 + 한 폴더에 평평하게.

## 그 밖의 파일

- `Shopee_AI쇼호스트_제작설계_v1.md`, `_v2.html`: 이전 버전(비교용)
- `Shopee_AI쇼호스트_제작설계_v3.html`: 개발자용 v4를 만드는 중간 결과물(`build_v3_*.py` 출력) — 지우지 말 것
- `5_에셋/scripts/build_dcsai_bundle.py`: 이전 방식(개발자용 전체를 영상만 빼고 올림). `build_share_page.py`로 대체됨
