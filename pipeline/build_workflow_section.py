# -*- coding: utf-8 -*-
"""stages.json → workflow_section.html (개발용 제작설계 HTML 맨 위 A장).
- 단계 × 역할(사람·Claude 지침·MCP·생성 모델/프롬프트·스크립트) 다이어그램
- MCP 호출 목록, 프롬프트 원문 — 프롬프트는 실제 실행 스크립트에서 빌드할 때마다 읽어 온다(문서와 코드가 어긋나지 않게)
build_v4.py가 이 파일이 있으면 페이지 맨 위에 넣는다.
python -X utf8 pipeline/build_workflow_section.py
"""
import ast
import html
import json
from pathlib import Path

import workflow_diagram as wd

HERE = Path(__file__).resolve().parent
HUB = HERE.parent
POC = HUB / 'AI쇼핑라이브_Shopee_202611/5_에셋/scripts'
d = json.loads((HERE / 'stages.json').read_text(encoding='utf-8'))
E = html.escape


def src_of(path, name):
    """파일에서 `name = ...` 대입문을 찾아 문자열 상수면 값, 아니면 소스 원문을 돌려준다."""
    text = Path(path).read_text(encoding='utf-8')
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == name for t in node.targets):
            try:
                return ast.literal_eval(node.value), 'value'
            except Exception:
                return ast.get_source_segment(text, node), 'code'
    raise KeyError(f'{name} not in {path}')


def rel(p):
    return Path(p).resolve().relative_to(HUB.parent).as_posix()


# ── 참조 카탈로그 ──
MCP = {
    'PS_SEARCH': ('product-spec', 'search_product_specs', 'query = 제품 한글명 · 영문명 · 라인명 (limit ≤ 30), 못 찾으면 category로 목록', '제품마다 첫 호출'),
    'PS_GET': ('product-spec', 'get_product_spec', '찾은 문서 1건', 'USP · 용량 · 제형 · 사용법 · 주의 문구 읽기'),
    'PS_VER': ('product-spec', 'get_spec_versions', '같은 문서', '최신 버전 번호를 근거(basis)로 기록'),
    'PS_ATT': ('product-spec', 'get_spec_attachments', '같은 문서', '첨부 이미지·자료가 필요할 때'),
    'PS_MATCH': ('product-spec', 'get_product_match · list_categories', '(인자 미확인 — 호출 전 스키마 확인)', '이름 검색으로 안 잡힐 때'),
    'NAS_FIND': ('fnco-nas', 'find_sku', 'query = 제품명 조각, brand = "B"(바닐라코)', '품번 후보 · confirmed_assets 확인'),
    'NAS_SEARCH': ('fnco-nas', 'search_nas_assets', 'query = "<제품> 누끼" · has_alpha="1" · reviewed_only · path_prefix · kind="video"(시연) · limit 2~3', '누끼·발색컷·상세컷·시연 영상 후보 (미리보기 1시간 링크)'),
    'NAS_SKU': ('fnco-nas', 'get_sku_assets', 'prdt_cd · usage = 누끼|발색컷|상세컷 · kind', 'confirmed_assets > 0 인 품번일 때'),
    'NAS_GET': ('fnco-nas', 'get_asset', 'file_id', '내려받기 직전 원본 링크(5분) 새로 받기 → nas_download.py'),
}
GUIDE = {
    'SKILL': ('Claude 지침', '.claude/skills/ai-live-product/SKILL.md', '단계별 실행 순서·멈출 곳(유료 승인)'),
    'GRAMMAR': ('Claude 지침', 'fnco_ai-shoppinghost/pipeline/rules/script_grammar.md', '대본 장면 순서·화면 유형·문장 길이·근거·RA'),
    'HOOK_VERIFY': ('훅 · 매 요청', '~/.claude/hooks/no_fabrication_guard.py', '실측한 것만 사실로, 나머지는 미확인/추정'),
    'HOOK_FDA': ('훅 · 매 요청', '~/.claude/hooks/fda_ftc_guard.py', '화장품 범위 표현, 의약품 클레임 금지, RA 태그'),
    'HOOK_LOCK': ('훅 · 조건부', '~/.claude/hooks/product_lock_guard.py', '요청에 제품어 + 생성어가 있을 때 — 제품은 생성하지 않고 실물 누끼 합성'),
}
h3_prompt, _ = src_of(POC / 'h3_production.py', 'PROMPT')
vd_prompt, _ = src_of(POC / 'minimax_voice.py', 'PROMPT_A1')
vd_preview, _ = src_of(POC / 'minimax_voice.py', 'PREVIEW')
ref_text, _ = src_of(POC / 'minimax_voice.py', 'REF_TEXT')
op_prompt, _ = src_of(HERE / 'gen_character.py', 'OUTPAINT')
cand, _ = src_of(HERE / 'gen_character.py', 'CAND')
jobs, _ = src_of(HERE / 'gen_character.py', 'JOBS')
same, _ = src_of(HERE / 'gen_character.py', 'SAME')
real, _ = src_of(HERE / 'gen_character.py', 'REAL')
MODEL = {
    'TPL_BANNER': ('템플릿', 'HTML/CSS → Playwright (모델 없음)', 'POC banner/template/build_banners.py 의 promo()·info()',
                   '문구는 brief/banners.json 에서. 생성 프롬프트 없음 — 제품은 누끼 그대로', None),
    'IMG_CAND': ('유료', 'OpenAI gpt-image-2.5-flare · images.generate · 1024×1536 · high', rel(HERE / 'gen_character.py') + ' CAND',
                 '새 호스트일 때만. {identity}{wardrobe}{set} = brief/host_spec.json', cand),
    'IMG_SHEET': ('유료', 'OpenAI gpt-image-2.5-flare · images.edit · input_fidelity high · 레퍼런스 = 사람이 고른 후보', rel(HERE / 'gen_character.py') + ' SAME + REAL + JOBS',
                  '시트 3장(각도·표정·손) + 마스터 프레임. 각 JOBS 문장 앞에 SAME·REAL이 붙음', '\n\n'.join([same, real, jobs])),
    'IMG_OUTPAINT': ('유료', 'OpenAI gpt-image-2.5-flare · images.edit + mask', rel(HERE / 'gen_character.py') + ' OUTPAINT (master916 단계)',
                     '마스터 프레임을 9:16으로 넓힐 때 빈 영역만 채움', op_prompt),
    'VOICE_DESIGN': ('유료', 'MiniMax /v1/voice_design', rel(POC / 'minimax_voice.py') + ' PROMPT_A1 · PREVIEW',
                     '새 목소리일 때만 1회 → voice_id', f'prompt: {vd_prompt}\n\npreview_text: {vd_preview}'),
    'T2A_REF': ('유료', 'MiniMax /v1/t2a_v2 · speech-2.8-hd', rel(POC / 'minimax_voice.py') + ' REF_TEXT',
                'H3에 넣을 목소리 참조 샘플(대본에 없는 문장 — H3가 따라 말하지 않게)', ref_text),
    'T2A_VO': ('유료', 'MiniMax /v1/t2a_v2 · speech-2.8-hd · speed 1.25 · emotion happy · English · 32kHz mono',
               rel(POC / 'minimax_voice.py') + ' t2a()', 'text = shotlist.json 의 vo 줄 그대로 (프롬프트 없이 대사만)', None),
    'H3_HOST': ('유료', 'MiniMax-H3 · /v2/video_generation · 2K · 9:16 · 음성 동시 생성', rel(POC / 'h3_production.py') + ' PROMPT',
                '{gesture}·{text} = shotlist.json 의 h3 줄. reference_image = 마스터 프레임, reference_audio = host_reference.wav, '
                'duration = 단어수 ÷ 2.4 + 2초 (6~15초)', h3_prompt),
    'ASR': ('로컬', 'faster-whisper base · small (두 모델)', rel(POC / 'asr_script_guard.py'),
            '프롬프트 없음(initial_prompt 없음). 받아 적은 말을 대본과 대조해 이탈 구간 검출', None),
}
TAG = {'유료': 'paid', '로컬': 'local', '템플릿': 'local'}


st = d['stages']

mcp_rows = ''.join(f'<tr id="wf-{k}"><td><b>{E(v[0])}</b><br><code>{E(v[1])}</code></td><td>{E(v[2])}</td><td>{E(v[3])}</td>'
                   f'<td>{", ".join(s["id"] for s in st if k in s["lanes"]["mcp"])}</td></tr>' for k, v in MCP.items())
guide_rows = ''.join(f'<tr id="wf-{k}"><td>{E(v[0])}</td><td><code>{E(v[1])}</code></td><td>{E(v[2])}</td>'
                     f'<td>{", ".join(s["id"] for s in st if k in s["lanes"]["guide"])}</td></tr>' for k, v in GUIDE.items())
prompt_blocks = ''
for k, (fee, model, where, when, text) in MODEL.items():
    used = ', '.join(s['id'] for s in st if k in s['lanes']['model'])
    body = f'<pre class="pt">{E(text)}</pre>' if text else '<p class="small">— 모델에 보내는 프롬프트 문장 없음</p>'
    prompt_blocks += (f'<details id="wf-{k}" class="pd"><summary><span class="c c-m c-{TAG[fee]}">{E(k)}</span> 단계 {used} · {E(model)}</summary>'
                      f'<p class="small"><b>어디서</b> <code>{E(where)}</code><br><b>언제·무엇을 채우나</b> {E(when)}</p>{body}</details>')

rows = ''.join(f'<tr><td><b>{E(s["id"])}</b></td><td>{E(s["name"])}<br><span class="small">{E(s["who"])} · {E(s["fee"])}</span></td>'
               f'<td>{E(s["do"])}</td><td><code>{E(s["tool"])}</code></td><td><code>{E(s["out"])}</code></td></tr>' for s in st)
gates = ''.join(f'<li>{E(g)}</li>' for g in d['gates'])
status = ''.join(f'<tr><td>{E(a)}</td><td>{E(b)}</td></tr>' for a, b in d['status'])

CSS = f'''<style>
.c{{display:block;border-radius:6px;padding:3px 6px;text-decoration:none;color:var(--ink);border:1px solid var(--line);line-height:1.3;overflow-wrap:anywhere}}
.c small{{display:block;font-size:10px;color:var(--muted)}}
.c-h{{background:var(--bg);border-style:dashed}}
.c-g{{background:var(--blue-soft);border-color:transparent}}.c-hook{{background:var(--warn-soft)}}
.c-mcp{{background:var(--ok-soft);border-color:transparent}}
.c-m.c-paid{{background:var(--pink-soft);border-color:var(--pink)}}.c-m.c-local{{background:var(--code)}}
.lgd{{display:flex;flex-wrap:wrap;gap:6px;font-size:12px;margin:6px 0}}.lgd .c{{display:inline-block}}
{wd.CSS}
details.pd{{border:1px solid var(--line);border-radius:10px;padding:6px 10px;margin:6px 0}}details.pd summary{{cursor:pointer;font-size:13px}}
details.pd summary .c{{display:inline-block;margin-right:6px}}
pre.pt{{white-space:pre-wrap;font-size:12px;background:var(--code);border-radius:8px;padding:10px;max-height:420px;overflow:auto}}
</style>'''

doc = f'''<section id="sW">{CSS}<h2><span class="n">A</span>어떤 제품이든 — 자동 제작 워크플로우 <span class="tag t-u">사용자 요청</span> <span class="small">{E(d["version"])}</span></h2>
<p>{E(d["summary"])}</p>
<div class="callout ok"><b>시작하는 법</b> — 이 저장소를 연 폴더에서 Claude Code에 <b>"&lt;제품명&gt;으로 AI 라이브 스토리보드 만들어줘"</b>라고 요청하면 <code>ai-live-product</code> 스킬이 0~5단계를 진행하고, 유료 단계(6~8) 앞에서 견적을 보여 주고 멈춥니다.<br>
<b>필요한 입력</b>: 제품명(여러 개 가능) · 판매 채널·국가·언어 · 프로모션 문구(없으면 숫자 없이 진행) · 호스트(기본 R3 재사용).</div>
<h3>A-0. 아키텍처 다이어그램</h3>
<p class="small"><b>읽는 법</b> — 가운데 = 작업 단계(위→아래), 오른쪽 = 그 단계가 부르는 MCP·Claude 지침·생성 API, 왼쪽 = 사람이 확인하는 지점. 0~5는 무료, 사람 승인 뒤 6~8(점선 구간)이 유료입니다. 아래 상자 안 글자가 그 API에 보내는 프롬프트입니다. 상자를 누르면 호출 인자·프롬프트 원문(A-1~A-3)으로 이동합니다.</p>
<div class="lgd"><span class="c c-mcp">MCP 서버</span><span class="c c-g">Claude 지침·훅</span><span class="c c-h">사람 입력·산출물</span><span class="c c-m c-paid">유료 단계·생성 API</span><span class="c c-m c-local">로컬 처리</span><span class="c c-hook">승인 게이트</span></div>
<div class="wfd-wrap">{wd.svg()}</div>
<h3>A-1. MCP 호출 — 무엇을, 어떤 인자로, 언제</h3>
<div class="tbl"><table><tr><th>MCP · 도구</th><th>넣는 값</th><th>언제·왜</th><th>단계</th></tr>{mcp_rows}</table></div>
<p class="small">Product Spec MCP: <code>https://product-spec-mcp.hub.fnco.co.kr/mcp</code> · fnco-nas: <code>https://docs.hub-dev.fnco.co.kr/mcp</code> — 둘 다 저장소 <code>.mcp.json</code>에 등록. NAS 응답은 자산 1건에 서명 URL이 붙어 수천 토큰이라 limit을 작게 씁니다.</p>
<h3>A-2. Claude가 따르는 지침과 훅</h3>
<div class="tbl"><table><tr><th>종류</th><th>파일</th><th>내용</th><th>단계</th></tr>{guide_rows}</table></div>
<h3>A-3. 생성 모델에 들어가는 프롬프트 — 원문 (실행 스크립트에서 자동으로 읽어 옴)</h3>
<p class="small">중괄호 <code>{{...}}</code>는 실행할 때 채워지는 자리입니다. 대본(3단계)은 생성 모델이 아니라 Claude가 A-2 지침대로 씁니다.</p>
{prompt_blocks}
<h3>A-4. 단계 상세</h3>
<div class="tbl"><table><tr><th>#</th><th>단계</th><th>하는 일</th><th>도구·MCP</th><th>산출물</th></tr>{rows}</table></div>
<h3>A-5. 지키는 규칙</h3><ul class="small">{gates}</ul>
<h3>A-6. 지금 상태</h3><div class="tbl"><table><tr><th>범위</th><th>상태</th></tr>{status}</table></div>
<script>document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[href^="#wf-"]');if(!a)return;
var t=document.getElementById(a.getAttribute('href').slice(1));if(t&&t.tagName==='DETAILS')t.open=true;}});</script>
</section>'''
(HERE / 'workflow_section.html').write_text(doc, encoding='utf-8')
print('ok', HERE / 'workflow_section.html', len(doc))
