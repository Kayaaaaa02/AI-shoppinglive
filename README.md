# AI 쇼호스트 라이브 — 자동 제작 워크플로우

제품명과 프로모션만 넣으면 **Product Spec MCP**(상품 기획서)와 **fnco-nas MCP**(브랜드 원본 이미지·영상)에서 정보와 소스를 가져와
대본 → 스토리보드 → 배너를 만들고, 사람 승인 뒤 캐릭터·목소리·호스트 영상(MiniMax H3)까지 이어 가는 코드입니다.
바닐라코 Shopee 11월 라이브 3편(프라이머·립앤치크·클렌징밤)을 만들며 쓴 스크립트를 제품에 묶이지 않게 정리했습니다.

## 1. 설치

```bash
pip install -r requirements.txt
python -m playwright install chromium     # 배너·카드를 PNG로 렌더할 때 필요
python -X utf8 ailive_config.py           # .env 자동 생성 + 어떤 키가 비었는지 확인 (값은 출력 안 함)
```

- Python 3.10 이상, **ffmpeg·ffprobe** 필요 (PATH에 있거나 `.env`의 `FFMPEG_PATH`·`FFPROBE_PATH`).
- Windows에서 한글 경로를 쓰므로 `python -X utf8`로 실행합니다.

## 2. API 키 (`.env`)

어떤 스크립트든 처음 실행하면 `ailive_config.py`가 `.env.example`을 복사해 저장소 루트에 **`.env`를 자동으로 만듭니다.**
생성된 `.env`를 열어 `=` 뒤에 값을 넣으세요. `.env`는 `.gitignore`로 저장소에 올라가지 않습니다.

| 키 | 필요한 때 | 발급 | 쓰는 스크립트 |
|---|---|---|---|
| `MINIMAX_API_KEY` | 목소리(Voice Design·T2A)와 호스트 영상(MiniMax-H3) 생성 — **유료** | [MiniMax Open Platform](https://platform.minimax.io) API Keys | `minimax_voice.py`, `h3_production.py` (`lib/minimax_official_api.py`) |
| `OPENAI_API_KEY` | 새 호스트 캐릭터 이미지 생성(gpt-image-2.5-flare) — **유료**. 기본 호스트 R3를 재사용하면 필요 없음 | OpenAI 또는 사내 프록시 | `pipeline/gen_character.py` (Shopee 원본 `gen_r3_character.py`·`outpaint_master.py`) |
| `OPENAI_BASE_URL` | 사내 프록시를 쓸 때만 | — | 위와 같음 |
| `SECONDARY_CONTENT_DIR` | 선택. 2차 활용 콘텐츠 영상 목록을 잴 때 | 팀 OneDrive `AX팀/20. AI쇼핑라이브/2차 활용 콘텐츠` 로컬 경로 | `probe_secondary.py` |
| `FFMPEG_PATH`·`FFPROBE_PATH`·`KO_FONT_PATH` | 선택. 자동으로 못 찾을 때만 | — | 영상·이미지 스크립트 |

**무료로 돌아가는 단계**(접수·제품 정보·원본 소스·대본·스토리보드·배너)는 API 키 없이 됩니다.
유료 단계는 모두 먼저 요청 내용·견적만 보여 주고, `--confirm`(캐릭터) 또는 `submit`(H3)을 따로 실행해야 과금됩니다.

## 3. MCP (Claude Code에서 사용)

저장소의 `.mcp.json`에 두 서버가 등록돼 있어, 이 폴더에서 Claude Code를 열면 연결을 묻습니다(사내 계정 로그인 필요). 묻지 않으면 `/mcp`에서 두 서버를 승인하세요.

| MCP | 주소 | 쓰는 단계 |
|---|---|---|
| `product-spec` | `https://product-spec-mcp.hub.fnco.co.kr/mcp` | 1 제품 정보 — `search_product_specs` → `get_product_spec` → `get_spec_versions` · `get_spec_attachments` |
| `fnco-nas` | `https://docs.hub-dev.fnco.co.kr/mcp` | 2 원본 소스 — `find_sku` → `search_nas_assets` / `get_sku_assets` → `get_asset` |

## 4. 사용법

Claude Code에서 이 폴더를 열고 **"<제품명>으로 AI 라이브 스토리보드 만들어줘"** 라고 하면
`.claude/skills/ai-live-product/SKILL.md` 순서대로 0~5단계를 진행하고, 유료 단계 앞에서 견적을 보여 주고 멈춥니다.

직접 실행할 때:

```bash
python -X utf8 pipeline/new_project.py --name AI쇼핑라이브_<채널>_<YYYYMM> --products "제품A,제품B" --countries SG,MY --host R3
# (Claude가 MCP로 brief/product_brief.json, NAS 원본, brief/script.json, brief/banners.json 을 채움)
python -X utf8 pipeline/script_to_shotlist.py --project <프로젝트>
python -X utf8 pipeline/build_storyboard.py   --project <프로젝트>     # 0_기획/storyboard.html
python -X utf8 pipeline/build_banners.py      --project <프로젝트>     # 5_에셋/banner/common/*.png
# 유료 (승인 후)
AILIVE_ROOT=<프로젝트> python -X utf8 AI쇼핑라이브_Shopee_202611/5_에셋/scripts/h3_production.py prepare
```

단계 정의·다이어그램 원본은 `pipeline/stages.json`, 대본 규칙은 `pipeline/rules/script_grammar.md`.

## 5. 폴더

| 폴더 | 내용 |
|---|---|
| `ailive_config.py` · `.env.example` | API 키·도구 경로 설정 (`.env` 자동 생성) |
| `pipeline/` | 어떤 제품이든 쓰는 단계별 스크립트·규칙·형식 예시 |
| `lib/minimax_official_api.py` | MiniMax H3 제출 모듈 — 제출 잠금(`submission.lock`)·재POST 금지·키 비노출 |
| `AI쇼핑라이브_Shopee_202611/` | Shopee 11월 3편 제작 스크립트(`5_에셋/scripts/`, `0_기획/build_*.py`)와 재사용 자산(글꼴 Pretendard, 로고, 호스트 R3 시트·마스터 프레임, 참조 음성, 3편 shotlist) |
| `docs/` | 계획·리서치 문서 |
| `.claude/skills/ai-live-product/` | Claude Code 실행 순서 |

**새 프로젝트 폴더**(`new_project.py`가 만드는 `AI쇼핑라이브_<채널>_<YYYYMM>/`)는 미디어가 커서 기본으로 Git에서 제외됩니다. 팀과 나눌 것은 `0_기획/brief/*.json`·`storyboard.html` 정도이니, 필요하면 `.gitignore` 끝에 아래 세 줄을 추가하세요(`.gitignore`가 맨 위에서 전부 제외하므로 폴더를 단계별로 다시 허용해야 합니다).

```
!/<프로젝트>/
/<프로젝트>/*
!/<프로젝트>/0_기획/
```

**저장소에 없는 것**: 영상·원본 소스·생성 결과(약 12GB, 로컬 보관), 10월 6일 POC 실험 코드, 시험 프로젝트.
그래서 `AI쇼핑라이브_Shopee_202611/0_기획/build_*.py`(문서 빌드)와 `build_final_edit.py`(Shopee 3편 편집)는 원본 미디어가 있는 PC에서만 끝까지 돕니다.

## 6. 지켜야 할 것

- 제품은 생성하지 않습니다 — 공식 누끼·발색컷·시연 영상만 합성.
- 화면·대사 문구는 화장품 범위(세정·사용감·외관). 시험 수치·임상·순위·치료/미백/주름 효능 표현 금지, 애매하면 RA(법무) 표시.
- 가격·사은품·기간은 실무진 회신값만 씁니다.
- MiniMax H3 제출 기록(`3_소스클립/H3/<ID>/submission.lock`, `run.json`)은 지우지 마세요 — 중복 과금 방지용입니다.
