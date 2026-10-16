# -*- coding: utf-8 -*-
"""4단계: 대본(brief/script.json) + 받은 소스(assets_manifest.json) → 0_기획/storyboard.html
줄마다 화면 유형·대사·근거·RA·쓰일 누끼/시연 소스를 한 줄에 보여 준다. 소스가 비어 있으면 빨간 칸.
상단에 영상별 예상 길이와 호스트 영상(H3) 예상 비용(정가 추정, 청구서 아님)을 낸다.

python -X utf8 pipeline/build_storyboard.py --project <프로젝트 폴더>
"""
import argparse
import html
import json
import math
import re
from pathlib import Path

WPS = 2.4            # 1.25배속 기준 초당 단어 (POC h3_production.py와 같은 값, 목표값)
USD_PER_S = 0.13     # MiniMax-H3 2K 정가 추정 (POC run.json cost_basis)
ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True)
a = ap.parse_args()
P = Path(a.project).resolve()
script = json.loads((P / '0_기획/brief/script.json').read_text(encoding='utf-8'))
man_p = P / '5_에셋/이미지생성_소스/assets_manifest.json'
man = json.loads(man_p.read_text(encoding='utf-8')) if man_p.exists() else {}
by_key = {}
for m in man.values():
    by_key.setdefault((m['key'], m['role']), []).append(m)
E = html.escape


def words(t):
    return len(re.findall(r"[A-Za-z0-9']+", t or ''))


def secs(ln):
    w = words(ln.get('text'))
    vo = (ln.get('text') or '').startswith('V/O:') or ln['type'] in ('G', 'D')
    return w / WPS + (0.5 if vo else 2.0)


def thumb(key):
    ms = by_key.get((key, 'cutout'), [])
    if not ms:
        return f'<span class="miss">누끼 없음: {E(key)}</span>'
    m = ms[0]
    return f'<img loading="lazy" src="../{E(m.get("work") or m["local"])}" alt="{E(key)}" title="{E(m["filename"])}">'


def source_cell(ln):
    src = ln.get('source')
    if ln['type'] not in ('S', 'D'):
        return ''
    if not src:
        return '<span class="miss">시연 소스 없음</span>'
    hit = [m for m in man.values() if src.get('asset') and src['asset'] in (m['file_id'], Path(m['local']).stem, m['key'] + '__' + m['role'])]
    name = E(hit[0]['filename']) if hit else f'<span class="miss">받지 않은 소스: {E(str(src.get("asset")))}</span>'
    return f'{name}<br><small>{src.get("in", "?")}–{src.get("out", "?")}초</small>'


blocks, total_h3 = '', 0
for v in script['videos']:
    rows, t_all, t_h3 = '', 0.0, 0.0
    for ln in v['lines']:
        s = secs(ln); t_all += s
        is_h3 = not ((ln.get('text') or '').startswith('V/O:') or ln['type'] in ('G', 'D'))
        if is_h3 and ln.get('text'):
            t_h3 += max(6, min(15, math.ceil(words(ln['text']) / WPS + 2)))
        cuts = ''.join(thumb(k) for k in ln.get('cutouts', []))
        card = ln.get('card')
        card_s = f'<div class="card">{E(card.get("title", ""))}<br>{" → ".join(E(x) for x in card.get("steps", []))}</div>' if card else ''
        rows += (f'<tr><td class="id">{E(ln["id"])}</td><td><span class="t t-{E(ln["type"].replace("+", "").replace("→", ""))}">{E(ln["type"])}</span></td>'
                 f'<td>{E(ln.get("screen", ""))}{card_s}<div class="cuts">{cuts}</div>{source_cell(ln)}</td>'
                 f'<td class="say">{E(ln.get("text") or "")}<small>{words(ln.get("text"))}단어 · 약 {s:.0f}초</small></td>'
                 f'<td>{E(ln.get("basis") or "")}{" <b class=ra>RA</b>" if ln.get("ra") else ""}'
                 f'{"<br><small>" + E(ln["note"]) + "</small>" if ln.get("note") else ""}</td></tr>')
    total_h3 += t_h3
    blocks += (f'<section><h2>{E(v["id"])} · {E(v.get("title", ""))}</h2>'
               f'<p class="meta">헤드라인 <b>{E(v.get("headline", ""))}</b> · {len(v["lines"])}줄 · 예상 길이 약 {t_all / 60:.1f}분(1.25배속 말속도 추정) · '
               f'호스트 영상 클립 길이 합 {t_h3:.0f}초 → 정가 추정 ${t_h3 * USD_PER_S:.0f}</p>'
               f'<div class="tw"><table><tr><th>장면</th><th>화면</th><th>화면 구성 · 소스</th><th>대사 (영어)</th><th>근거 · RA</th></tr>{rows}</table></div></section>')

doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>스토리보드 — {E(P.name)}</title><style>
:root{{--bg:#fbf7f9;--sf:#fff;--ink:#1d1a1c;--mu:#6b6268;--ln:#eadde3;--pk:#e9579a;--bad:#c0392b;--bads:#fde5e2}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141113;--sf:#1e1a1d;--ink:#f1ecef;--mu:#a99fa5;--ln:#3a3237;--pk:#ff7fb6;--bad:#ff8a7a;--bads:#3d1c18}}}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--ink);font:14px/1.55 Pretendard,"Malgun Gothic",system-ui,sans-serif}}
h1{{font-size:22px;margin:0 0 6px}}h2{{font-size:18px;margin:0 0 4px}}section{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:16px;margin:16px 0}}
.meta,.lg{{color:var(--mu);font-size:13px}}.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:860px}}
th,td{{border-top:1px solid var(--ln);padding:8px;vertical-align:top;text-align:left}}th{{font-size:12px;color:var(--mu)}}
td.id{{font-weight:700;white-space:nowrap}}td.say{{max-width:380px}}td small{{display:block;color:var(--mu);font-size:12px}}
.t{{display:inline-block;border-radius:6px;padding:1px 7px;font-weight:700;font-size:12px;border:1px solid var(--ln)}}
.t-G,.t-GH,.t-D{{background:var(--pk);color:#fff;border-color:var(--pk)}}
.cuts img{{height:72px;width:auto;margin:6px 6px 0 0;background:repeating-conic-gradient(#0001 0 25%,#0000 0 50%) 0 0/12px 12px;border-radius:6px}}
.miss{{display:inline-block;margin-top:6px;background:var(--bads);color:var(--bad);border-radius:6px;padding:2px 8px;font-size:12px;font-weight:600}}
.card{{margin-top:6px;border:1px dashed var(--ln);border-radius:8px;padding:4px 8px;font-size:12px}}b.ra{{color:var(--bad)}}
</style></head><body>
<h1>스토리보드 — {E(P.name)}</h1>
<p class="lg"><b>읽는 법</b> — 화면 유형: H 호스트 · H+G 호스트+측면 카드 · S 호스트+하단 시연 창 · G 전체 화면 카드(V/O) · G+H 카드+호스트 음성 · D 공식 시연 영상(V/O) · B→H 분위기 컷→호스트.
빨간 칸 = 아직 받지 않은 누끼·시연 소스. <b class="ra">RA</b> = 표현 사전검토 대상. 길이는 단어 수 ÷ 초당 {WPS}단어로 계산한 추정값입니다.
호스트 영상 비용은 MiniMax-H3 2K 정가 ${USD_PER_S}/초 기준 추정이며 청구서가 아닙니다. 전체 클립 길이 합 {total_h3:.0f}초 → 약 ${total_h3 * USD_PER_S:.0f}.</p>
{blocks}</body></html>'''
out = P / '0_기획/storyboard.html'
out.write_text(doc, encoding='utf-8')
print('ok', out, f'h3 {total_h3:.0f}s ≈ ${total_h3 * USD_PER_S:.0f}')
