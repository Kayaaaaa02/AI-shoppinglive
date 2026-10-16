# -*- coding: utf-8 -*-
"""2차 활용 콘텐츠(팀 OneDrive) 영상 목록·길이 실측 → 5_에셋/secondary_content/<라인>.json
2026-10-15 사용자: 공유판 '라인별 활용 2차 콘텐츠' 표(파일명·총 초수)용.
python -X utf8 5_에셋/scripts/probe_secondary.py
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(cfg.require('SECONDARY_CONTENT_DIR'))  # .env — 팀 OneDrive 'AX팀/20. AI쇼핑라이브/2차 활용 콘텐츠'
OUT = ROOT / '5_에셋' / 'secondary_content'
FP = cfg.FFPROBE
LINES = {'lipcheek': '립앤치크', 'zerokit': '제로키트'}


def probe(p):
    r = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration',
                        '-of', 'json', str(p)], capture_output=True, text=True, encoding='utf-8', stdin=subprocess.DEVNULL)
    j = json.loads(r.stdout or '{}')
    st = (j.get('streams') or [{}])[0]
    return float(j.get('format', {}).get('duration') or 0), st.get('width'), st.get('height')


OUT.mkdir(parents=True, exist_ok=True)
for key, folder in LINES.items():
    rows = []
    for f in sorted((SRC / folder).rglob('*')):
        if f.is_file() and f.suffix.lower() in ('.mp4', '.mov'):
            d, w, h = probe(f)
            rows.append({'file': str(f.relative_to(SRC / folder)), 'seconds': round(d, 2), 'w': w, 'h': h})
    tot = sum(r['seconds'] for r in rows)
    data = {'line': folder, 'source': str(SRC / folder), 'count': len(rows), 'total_seconds': round(tot, 1),
            'unreadable': [r['file'] for r in rows if not r['seconds']], 'files': rows}
    (OUT / f'{key}.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(folder, len(rows), round(tot, 1), 'unreadable', len(data['unreadable']))
