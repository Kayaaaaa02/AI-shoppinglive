# -*- coding: utf-8 -*-
"""계획서 HTML용 미리보기 영상.

1) COMMON_OC.mp4 / COMMON_EC.mp4 — 세 편 공통 오프닝(OC-1~3) / 엔딩(EC-1~3). V1 편집 세그먼트를 이어 붙임(헤드라인은 V1용).
2) h3_groups/<V>_<장면>.mp4 — 같은 장면(예: V1 P3 선베이스)의 H3 클립을 대본 순서로 이어 붙인 것.
   편집본(_cut)이 있으면 편집본, 없으면 원본. 전부 1.25배속(음높이 유지). 합성 전 원소스(호스트만), 빛 반짝임 프레임 교체 전.
출력: 4_테스트/html_preview/ (+ index.json)
python -X utf8 5_에셋/scripts/build_html_previews.py
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FF = cfg.FFMPEG
FP = cfg.FFPROBE
OUT = ROOT / '4_테스트/html_preview'
SPEED = 1.25  # 2026-10-15 사용자: 완성본과 같이 1.25배속
(OUT / 'h3_groups').mkdir(parents=True, exist_ok=True)


def dur(p):
    r = subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return float(r.stdout.strip())


def concat(srcs, dst, w=720, h=1280):
    args = [FF, '-nostdin', '-v', 'error', '-y']
    for s in srcs:
        args += ['-i', str(s)]
    f = ''.join(f'[{i}:v]scale={w}:{h},fps=30,format=yuv420p,setsar=1[v{i}];'
                f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];' for i in range(len(srcs)))
    f += ''.join(f'[v{i}][a{i}]' for i in range(len(srcs))) + f'concat=n={len(srcs)}:v=1:a=1[vc][ac];[vc]setpts=PTS/{SPEED},fps=30[v];[ac]atempo={SPEED}[a]'
    args += ['-filter_complex', f, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '23', '-preset', 'veryfast',
             '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(dst)]
    subprocess.run(args, check=True)


cfg = json.loads((ROOT / '3_소스클립/H3/config.json').read_text(encoding='utf-8'))
shots = {s['id']: s for s in json.loads((ROOT / '5_에셋/production/shotlist_v3.json').read_text(encoding='utf-8'))}
index = {'common': None, 'groups': [], 'speed': SPEED}

# 1) 공통 오프닝 / 엔딩 (따로)
seg = ROOT / '4_테스트/edit_seg/V1'
index['common'] = {}
for part, keys in (('OC', ('OC-1', 'OC-2', 'OC-3')), ('EC', ('EC-1', 'EC-2', 'EC-3'))):
    srcs = [next(seg.glob(f'*_COMMON_{k}.mp4')) for k in keys]
    dst = OUT / f'COMMON_{part}.mp4'
    concat(srcs, dst, 1080, 1920)
    t, chap = 0.0, []
    for k, s_ in zip(keys, srcs):
        chap.append({'id': f'COMMON_{k}', 'start': round(t / SPEED, 2)}); t += dur(s_)
    index['common'][part] = {'file': dst.relative_to(ROOT).as_posix(), 'seconds': round(dur(dst), 2), 'clips': chap}
old_ = OUT / 'COMMON_OC_EC.mp4'
if old_.exists():
    old_.rename(OUT / '_old_COMMON_OC_EC.mp4')

# 2) 장면별 H3 묶음
groups = {}
for sid in cfg['jobs']:
    s = shots[sid]
    key = s['scene'][:2] if s['scene'].startswith(('OC', 'EC')) else s['scene'].split('-')[0] if not s['scene'].startswith('O-') else s['scene']
    groups.setdefault((s['video'], key), []).append(sid)
for (vid, key), ids in groups.items():
    srcs, clips, t = [], [], 0.0
    for sid in ids:
        gdir = ROOT / '4_테스트/h3_qa' / sid
        cut = next(gdir.glob('*_cut.mp4'), None) if gdir.exists() else None
        src = cut or (ROOT / '3_소스클립/H3' / sid / 'native.mp4')
        d = dur(src)
        srcs.append(src)
        clips.append({'id': sid, 'start': round(t / SPEED, 2), 'seconds': round(d / SPEED, 2),
                      'src': src.relative_to(ROOT).as_posix(), 'edited': bool(cut)})
        t += d
    dst = OUT / 'h3_groups' / f'{vid}_{key}.mp4'
    concat(srcs, dst)
    index['groups'].append({'video': vid, 'scene': key, 'file': dst.relative_to(ROOT).as_posix(),
                            'seconds': round(dur(dst), 2), 'clips': clips})
    print(vid, key, len(ids), round(t, 1))

(OUT / 'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
print('groups', len(index['groups']), 'common', index['common'])
