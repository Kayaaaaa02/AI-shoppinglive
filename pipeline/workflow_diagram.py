# -*- coding: utf-8 -*-
"""A-0 아키텍처 다이어그램 (SVG, 상자 + 화살표, 위→아래 흐름). build_workflow_section.py가 불러 쓴다.
가운데 = 작업 단계 0~10, 오른쪽 = 그 단계가 부르는 외부 시스템(MCP·Claude 지침·생성 API)과 보내는 프롬프트, 왼쪽 = 사람 입력·산출물.
라이브러리 없는 인라인 SVG라 로컬 HTML·아티팩트에서 같게 보이고, 색은 페이지 토큰(var(--…))이라 라이트·다크 모두 맞는다.
상자를 누르면 아래 상세(#wf-…)로 이동.
"""
import html

E = html.escape
W = 780
SX, SW, SH = 196, 190, 50            # 단계 상자
RX, RW = 478, 292                    # 오른쪽 외부 시스템 상자
LX, LW = 8, 168                     # 왼쪽 상자
STEP = 74
Y0 = 70


def ycen(row):
    return Y0 + row * STEP + SH / 2


def box(x, y, w, h, lines, cls='nd', href=None):
    out = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
    n = len(lines)
    ty = y + h / 2 - (n - 1) * 7.5 + 4
    for i, ln in enumerate(lines):
        out += f'<text class="{"t" if i == 0 else "s"}" x="{x + w / 2}" y="{ty}" text-anchor="middle">{E(ln)}</text>'
        ty += 16 if i == 0 else 15
    return f'<a href="{href}">{out}</a>' if href else out


def arrow(x1, y1, x2, y2, label='', dashed=False, ly=None):
    s = f'<line class="ar{" dash" if dashed else ""}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ah)"/>'
    if label:
        s += f'<text class="lb" x="{(x1 + x2) / 2}" y="{(ly if ly is not None else min(y1, y2) - 6)}" text-anchor="middle">{E(label)}</text>'
    return s


STAGES = [  # (번호, 이름, 보조, 유료)
    (0, '접수', 'new_project.py', False), (1, '제품 정보', 'product_brief.json', False),
    (2, '원본 소스', 'nas_download.py · 누끼 실측', False), (3, '대본', 'script.json → shotlist.json', False),
    (4, '스토리보드', 'storyboard.html · 견적', False), (5, '배너', 'build_banners.py', False),
    None,  # 승인 게이트 자리
    (6, '캐릭터 시트', '기본 R3 재사용(무료)', True), (7, '목소리', 'minimax_voice.py', True),
    (8, '호스트 영상', 'h3_production.py', True), (9, '검수', 'qa_h3.py · 육안', False),
    (10, '편집', 'build_final_edit.py *', False),
]
# 오른쪽 외부 시스템: (행, 줄들, 클래스, 링크, 화살표 방향 'in'=시스템→단계 / 'out'=단계→시스템, 화살표 글)
RIGHT = [
    (1, ['Product Spec MCP', 'search_product_specs → get_product_spec', '→ get_spec_versions · attachments'], 'ext', '#wf-PS_SEARCH', 'in', '근거 문서'),
    (2, ['fnco-nas MCP', 'find_sku → search_nas_assets / get_sku_assets', '→ get_asset (원본 5분 링크)'], 'ext', '#wf-NAS_FIND', 'in', '원본 파일'),
    (7, ['OpenAI gpt-image-2.5-flare', '① CAND 후보 → ② 시트(SAME+REAL+JOBS) → ③ 9:16', 'R3 재사용이면 호출 없음'], 'api paid', '#wf-IMG_CAND', 'out', '프롬프트'),
    (8, ['MiniMax 음성 (speech-2.8-hd)', 'Voice Design PROMPT_A1 (새 목소리만)', 'REF_TEXT → 참조 음성 · V/O 대사 그대로 1.25배'], 'api paid', '#wf-VOICE_DESIGN', 'out', '프롬프트'),
    (9, ['MiniMax-H3 · 2K · 9:16', 'PROMPT {gesture}{text} + 마스터 프레임', '+ host_reference.wav · 단어÷2.4+2초'], 'api paid', '#wf-H3_HOST', 'out', '프롬프트'),
    (10, ['faster-whisper base · small (로컬)', '프롬프트 없음', '받아 적은 말 ↔ 대본 대조'], 'api local', '#wf-ASR', 'out', '클립'),
]


def svg():
    H = Y0 + len(STAGES) * STEP + SH + 40
    p = [f'<text class="hd" x="{SX + SW / 2}" y="40" text-anchor="middle">작업 단계</text>',
         f'<text class="hd" x="{RX + RW / 2}" y="40" text-anchor="middle">외부 시스템 · 보내는 프롬프트</text>',
         f'<text class="hd" x="{LX + LW / 2}" y="40" text-anchor="middle">사람</text>']
    # 유료 구간 배경
    p.append(f'<rect class="band" x="{SX - 14}" y="{Y0 + 7 * STEP - 12}" width="{W - SX + 4}" height="{3 * STEP + 2}" rx="12"/>'
             f'<text class="lb" x="{W - 12}" y="{Y0 + 7 * STEP - 18}" text-anchor="end">유료 구간 — 승인 후에만</text>')
    for row, st in enumerate(STAGES):
        y = Y0 + row * STEP
        if st is None:
            cx, cy = SX + SW / 2, y + SH / 2
            p.append(f'<polygon class="gate" points="{cx},{cy - 26} {cx + 108},{cy} {cx},{cy + 26} {cx - 108},{cy}"/>'
                     f'<text class="t" x="{cx}" y="{cy - 2}" text-anchor="middle">사람 승인</text>'
                     f'<text class="s" x="{cx}" y="{cy + 13}" text-anchor="middle">스토리보드·견적 보고 유료 실행</text>')
            continue
        i, n, sub, paid = st
        p.append(box(SX, y, SW, SH, [f'{i}  {n}', sub], 'nd paid' if paid else 'nd'))
    # 세로 화살표
    for row in range(len(STAGES) - 1):
        top = Y0 + row * STEP + (SH if STAGES[row] else SH / 2 + 26)
        nxt = Y0 + (row + 1) * STEP + (0 if STAGES[row + 1] else SH / 2 - 26)
        p.append(arrow(SX + SW / 2, top, SX + SW / 2, nxt - 3))
    # 왼쪽: 입력·산출물·사람 확인
    p.append(box(LX, Y0 - 4, LW, SH + 8, ['사용자 입력', '제품명·채널·국가·프로모션'], 'nd user'))
    p.append(arrow(LX + LW, ycen(0), SX - 3, ycen(0)))
    for row, txt in ((2, '미리보기로 제품·호수 확인'), (3, '대본·RA 문장 확인'), (5, '배너 원본 크기 확인'), (7, '후보 1장 선택'), (10, '컨택트시트 육안')):
        p.append(f'<text class="lb" x="{SX - 10}" y="{ycen(row) + 4}" text-anchor="end">{E(txt)}</text>')
    p.append(box(LX, Y0 + 11 * STEP + SH + 6, LW, SH, ['1_최종영상/', '완성본 mp4'], 'nd user'))
    p.append(arrow(SX, ycen(11) + 10, LX + LW + 3, Y0 + 11 * STEP + SH + 6 + SH / 2))
    # 오른쪽: Claude 지침 (3~5행에 걸침)
    cy0, cy1 = Y0 + 3 * STEP - 6, Y0 + 5 * STEP + SH + 6
    p.append(box(RX, cy0, RW, cy1 - cy0, ['Claude Code · ai-live-product 스킬', 'SKILL.md — 단계 순서·유료 전 멈춤',
                                          'rules/script_grammar.md — 대본 규칙', '훅(매 요청): no_fabrication · fda_ftc',
                                          '훅(제품+생성어): product_lock', '1·2단계 MCP 호출도 Claude가 이 지침으로'], 'ai', '#wf-SKILL'))
    for row, lab in ((3, '대본 규칙'), (5, '문구 가드')):
        p.append(arrow(RX, ycen(row), SX + SW + 3, ycen(row), lab, dashed=True))
    # 오른쪽: MCP·API
    for row, lines, cls, href, way, lab in RIGHT:
        y = Y0 + row * STEP - 7
        p.append(box(RX, y, RW, SH + 14, lines, cls, href))
        cy = ycen(row)
        if way == 'in':
            p.append(arrow(RX, cy, SX + SW + 3, cy, lab))
        else:
            p.append(arrow(SX + SW, cy, RX - 3, cy, lab))
    p.append(f'<text class="lb" x="{SX}" y="{H - 6}">* 편집은 아직 Shopee 3편 전용 (영상용 카드 내용이 스크립트 안)</text>')
    return (f'<svg class="wfd" viewBox="0 0 {W} {H}" role="img" aria-label="자동 제작 워크플로우 아키텍처 다이어그램">'
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path class="ahp" d="M0,0 L10,5 L0,10 z"/></marker></defs>' + ''.join(p) + '</svg>')


CSS = '''
.wfd-wrap{overflow-x:auto;margin:12px 0;border:1px solid var(--line);border-radius:12px;background:var(--bg);padding:6px}
svg.wfd{display:block;width:100%;max-width:780px;min-width:600px;height:auto;margin:0 auto;font-family:inherit}
svg.wfd .nd{fill:var(--surface);stroke:var(--line);stroke-width:1.5}
svg.wfd .nd.paid{fill:var(--pink-soft);stroke:var(--pink)}
svg.wfd .nd.user{fill:var(--bg);stroke:var(--muted);stroke-dasharray:4 3}
svg.wfd .ext{fill:var(--ok-soft);stroke:var(--ok);stroke-width:1.5}
svg.wfd .ai{fill:var(--blue-soft);stroke:var(--blue);stroke-width:1.5}
svg.wfd .api.paid{fill:var(--pink-soft);stroke:var(--pink);stroke-width:1.5}
svg.wfd .api.local{fill:var(--code);stroke:var(--line);stroke-width:1.5}
svg.wfd .gate{fill:var(--warn-soft);stroke:var(--warn);stroke-width:1.5}
svg.wfd .band{fill:none;stroke:var(--pink);stroke-width:1;stroke-dasharray:6 4;opacity:.7}
svg.wfd .hd{fill:var(--muted);font-size:12px;font-weight:700;letter-spacing:.04em}
svg.wfd .t{fill:var(--ink);font-size:13.5px;font-weight:700}
svg.wfd .s{fill:var(--muted);font-size:11.5px}
svg.wfd .lb{fill:var(--muted);font-size:11px}
svg.wfd .ar{stroke:var(--muted);stroke-width:1.6;fill:none}
svg.wfd .ar.dash{stroke-dasharray:5 4}
svg.wfd .ahp{fill:var(--muted)}
svg.wfd a:hover rect{stroke-width:2.5}
'''
