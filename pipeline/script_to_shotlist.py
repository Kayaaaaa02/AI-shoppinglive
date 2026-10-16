# -*- coding: utf-8 -*-
"""3단계 뒤: brief/script.json → 5_에셋/production/shotlist.json (생성 단위).
POC의 5_에셋/scripts/build_shotlist.py와 같은 규칙을 대본 JSON에서 바로 적용한다.
- kind=h3 : 호스트가 화면에서 말함 (유형에 H 또는 S가 있고 'V/O:'가 아님). 30단어 넘는 줄은 문장 경계로 나눔
- kind=vo : T2A 음성만 (G·D 유형 또는 'V/O:')
검사: 30단어 초과 청크, 근거(basis) 없는 줄, 남은 [자리표시] → 오류로 중단

python -X utf8 pipeline/script_to_shotlist.py --project <프로젝트 폴더>
"""
import argparse
import json
import re
from pathlib import Path

MAX_WORDS = 30
ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True)
a = ap.parse_args()
P = Path(a.project).resolve()
script = json.loads((P / '0_기획/brief/script.json').read_text(encoding='utf-8'))


def words(t):
    return len(re.findall(r"[A-Za-z0-9']+", t))


def chunks(text):
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    out, cur = [], ''
    for s in sents:
        if cur and words(cur + ' ' + s) > MAX_WORDS:
            out.append(cur); cur = s
        else:
            cur = (cur + ' ' + s).strip()
    if cur:
        out.append(cur)
    return out


shots, errors = [], []
for v in script['videos']:
    for ln in v['lines']:
        t = ln.get('text') or ''
        if not t:
            continue
        if not ln.get('basis'):
            errors.append(f"{v['id']} {ln['id']}: basis(근거) 없음")
        if re.search(r'\[[^\]]+\]', t):
            errors.append(f"{v['id']} {ln['id']}: 자리표시 남음 → {t}")
        vo = t.startswith('V/O:') or ln['type'] in ('G', 'D')
        t = t.replace('V/O:', '').strip()
        base = dict(video=v['id'], scene=ln['id'], type=ln['type'], screen=ln.get('screen', ''),
                    cutouts=ln.get('cutouts', []), source=ln.get('source'), card=ln.get('card'), ra=ln.get('ra', False))
        if vo:
            shots.append(dict(base, id=f"{v['id']}_{ln['id']}", kind='vo', text=t, words=words(t), gesture=''))
            continue
        parts = chunks(t)
        for i, c in enumerate(parts):
            if words(c) > MAX_WORDS:
                errors.append(f"{v['id']} {ln['id']}: 한 문장이 {words(c)}단어 — 나눠 쓰기")
            sid = f"{v['id']}_{ln['id']}" + (f"_{i + 1}" if len(parts) > 1 else '')
            shots.append(dict(base, id=sid, kind='h3', text=c, words=words(c), gesture=ln.get('gesture', '')))

if errors:
    raise SystemExit('대본 검사 실패:\n- ' + '\n- '.join(errors))
out = P / '5_에셋/production/shotlist.json'
out.write_text(json.dumps(shots, ensure_ascii=False, indent=1), encoding='utf-8')
h3 = [s for s in shots if s['kind'] == 'h3']
print(f"shotlist {len(shots)}줄 = h3 {len(h3)} · vo {len(shots) - len(h3)} → {out}")
