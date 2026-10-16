---
name: ai-live-product
description: 새 제품으로 AI 쇼호스트 라이브 영상을 만들 때 사용. 제품명·프로모션을 받으면 Product Spec MCP·NAS MCP로 정보와 원본 소스를 가져와 대본 → 스토리보드 → 배너를 자동으로 만들고, 승인 후 캐릭터·목소리·호스트 영상(MiniMax H3)까지 이어 간다. "AI 라이브 만들어줘", "쇼호스트 영상 새 제품", "라이브 스토리보드" 같은 요청에 사용.
---

# AI 쇼호스트 라이브 — 새 제품 워크플로우

이 저장소 루트에서 실행한다(아래 경로는 모두 저장소 루트 기준). 단계 정의는 `pipeline/stages.json`.
MCP 연결은 저장소의 `.mcp.json`(product-spec, fnco-nas), API 키는 저장소 루트 `.env`(처음 실행 때 `ailive_config.py`가 자동 생성 — README 참고).

## 지켜야 할 것 (먼저)

- 유료 단계(캐릭터 생성·Voice Design·T2A·H3 submit)는 **견적을 보여 주고 사용자 승인 후**. `submission.lock` 삭제·재POST 금지.
- 제품은 생성하지 않는다. NAS 공식 누끼·발색컷·시연 영상만 합성. 축소본만 보고 제품을 판정하지 않는다.
- 문구는 화장품 범위(세정·사용감·외관). 시험 수치·임상·순위·치료/미백/주름/모공 축소 효능 금지. 애매하면 RA 표시.
- Product Spec에 없는 정보는 '없음'으로 적는다. 가격·사은품·기간은 실무진 회신값만.
- `.env`는 읽어서 출력하지 않는다.

## 단계 (`P` = 새 프로젝트 폴더)

**0. 접수** — 제품명·브랜드·채널·국가·프로모션을 확인하고
`python -X utf8 pipeline/new_project.py --name <프로젝트> --products "A,B" --channel Shopee --countries SG,MY --promo "..." --host R3`

**1. 제품 정보 (Product Spec MCP)** — 제품마다 `search_product_specs(query=한글명·영문명·라인명)` → `get_product_spec` → `get_spec_versions`(최신 버전 번호 기록) → 필요하면 `get_spec_attachments`.
결과를 `P/0_기획/brief/product_brief.json` (형식 `pipeline/schema/product_brief.example.json`). 사실마다 source·버전, 쓰지 말아야 할 표현은 `do_not_say`/`cautions`.
도구가 안 보이면 `.mcp.json` 승인 여부(`/mcp`)를 확인하게 안내하고, 그래도 안 되면 공식몰 상세페이지를 보조 출처로 쓰되 brief에 그 사실을 적는다.

**2. 원본 소스 (NAS MCP)**
1. `find_sku(query, brand="B")`로 품번 후보. `confirmed_assets`가 0이면 폴더 검색으로.
2. `search_nas_assets(query="<제품명> 누끼", has_alpha="1", reviewed_only=True)` → 없으면 reviewed_only 끄고 다시. 발색컷·상세컷·`kind="video"` 시연 영상도 같은 방식.
3. 콜라보(`Collaboration`)·기획세트·구버전(`meta.lifecycle`≠current)은 요청이 없으면 제외. `preview_url`(1시간)로 제품·용량·호수 확인.
   - 응답은 자산 1건에 수천 토큰(서명 URL) → `limit` 2~3, 제품 폴더를 찾으면 `path_prefix`로 좁힌다.
   - `reviewed_only=True` 결과도 `nas_path`로 제품 폴더인지 확인(엉뚱한 사은품이 섞일 수 있음).
   - 단상자·기획세트 이미지는 국문 문구·배지·SPF가 인쇄돼 있을 수 있다 → 용기 단독 누끼 우선.
4. 고른 file_id마다 **내려받기 직전에** `get_asset(file_id)`로 새 `original.url`(5분)을 받아 `sel.json`(형식은 nas_download.py 맨 위) →
   `python -X utf8 pipeline/nas_download.py --project P --sel sel.json` → `assets_manifest.json` + `product_lock.json`. 내려받은 뒤 sel.json의 url은 지운다.

**3. 대본** — `pipeline/rules/script_grammar.md`대로 `P/0_기획/brief/script.json` (형식 `pipeline/schema/script.example.json`) →
`python -X utf8 pipeline/script_to_shotlist.py --project P` (근거 없는 줄·30단어 초과·[자리표시]가 있으면 멈춤).

**4. 스토리보드** — `python -X utf8 pipeline/build_storyboard.py --project P` → `P/0_기획/storyboard.html`. 빨간 칸(소스 없음)을 채우고, 사용자에게 링크와 예상 비용(호스트 클립 길이 합 × $0.13/초, 정가 추정)을 보여 준다.

**5. 배너** — `P/0_기획/brief/banners.json` (promo의 `line`은 48자 이내) → `python -X utf8 pipeline/build_banners.py --project P`. 결과 PNG를 원본 크기로 확인.

**6. 캐릭터 (기본: R3 재사용, 무료)** — 새 호스트가 필요할 때만 `brief/host_spec.json` → `pipeline/gen_character.py candidates` → 승인 → `--confirm` → 사람이 1장 고름 → `sheets --ref ... --confirm` → `master916 --confirm` → intake.json `host.anchor` 갱신. 이미지 모델 **gpt-image-2.5-flare**.

**7~9. 목소리·호스트 영상·검수 (유료, 승인 후)** — 프로젝트를 `AILIVE_ROOT`로 지정:
```
AILIVE_ROOT=<P> python -X utf8 AI쇼핑라이브_Shopee_202611/5_에셋/scripts/minimax_voice.py vo <P>/5_에셋/production/shotlist.json
AILIVE_ROOT=<P> python -X utf8 AI쇼핑라이브_Shopee_202611/5_에셋/scripts/h3_production.py prepare        # 무료: 클립 수·예상 비용
AILIVE_ROOT=<P> python -X utf8 AI쇼핑라이브_Shopee_202611/5_에셋/scripts/h3_production.py submit pending  # 승인 후
AILIVE_ROOT=<P> python -X utf8 AI쇼핑라이브_Shopee_202611/5_에셋/scripts/h3_production.py resume all --wait 1800
AILIVE_ROOT=<P> python -X utf8 AI쇼핑라이브_Shopee_202611/5_에셋/scripts/qa_h3.py all
```
(PowerShell은 `$env:AILIVE_ROOT="<P>"` 먼저.) voice_id는 `2_나레이션/voice/voice_state.json` — 만료됐으면 사용자에게 알리고 Voice Design 재실행 여부를 묻는다.

**10. 편집** — `build_final_edit.py`는 아직 Shopee 3편 전용. 새 제품은 스토리보드·배너·호스트 클립까지 만들고 편집 일반화가 필요하다고 보고한다.

## 끝나면

사용자에게: 만든 파일 위치, 스토리보드 경로, 빈 소스·확인 필요 항목, RA 표시 문장 수, 유료 단계 견적.
