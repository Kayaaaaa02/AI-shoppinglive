# -*- coding: utf-8 -*-
"""개발자용 제작설계 v4 HTML → claude.ai 아티팩트 묶음.
2026-10-16 사용자: "제작설계 html은 아티팩트로 해봐".
아티팩트 제약: 파일당 15MB(바이너리) · 한 버전 256MB · 한 번 올릴 때 255파일·64MB.
원본 영상은 합계 약 714MB(완성본 1편 최대 76.6MB)라 그대로는 못 올린다. 그래서
- 화면에 직접 나오는 이미지·영상·음성만 담는다(링크로만 걸린 json·py 등은 링크를 풀고 글자만 남김).
- 영상은 540×960, 파일당 14MB 이하가 되도록 비트레이트를 길이에 맞춰 다시 인코딩. 음성 wav는 mp3 96k.
- 파일 이름은 영문 해시로 평평하게(media/), 같은 원본은 한 파일로.
입력: 0_기획/개발자용/Shopee_AI쇼호스트_제작설계_v4.html (build_v4.py 출력)
출력: 0_기획/artifact_bundle/ (index.html + media/) — 이전 묶음은 4_테스트/_old_artifact_* 로 이동
python -X utf8 5_에셋/scripts/build_artifact.py
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import hashlib
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '0_기획/개발자용/Shopee_AI쇼호스트_제작설계_v4.html'
OUT = ROOT / '0_기획/artifact_bundle'
FF = cfg.FFMPEG
FP = cfg.FFPROBE
MAX_MB = 14.0          # 파일당 상한(아티팩트 15MB 아래 여유)
V_MAX_K = 900          # 짧은 클립도 이 이상 비트레이트는 쓰지 않음
A_K = 64

import sys
HTML_ONLY = '--html-only' in sys.argv  # media/ 는 그대로 두고 index.html 만 다시 (파일 이름은 원본 경로 해시라 같음)
if not HTML_ONLY:
    if OUT.exists():
        shutil.move(str(OUT), str(ROOT / '4_테스트' / f'_old_artifact_{int(OUT.stat().st_mtime)}'))
    (OUT / 'media').mkdir(parents=True)

b = BeautifulSoup(SRC.read_text(encoding='utf-8'), 'html.parser')
EMBED = {'img', 'video', 'audio', 'source'}


def local(v):
    if not v or v.startswith(('#', 'http:', 'https:', 'mailto:', 'data:')):
        return None
    p = (SRC.parent / unquote(v.split('#')[0])).resolve()
    return p if p.is_file() else None


# 1) 화면에 직접 나오는 파일 모으기
jobs = {}  # 원본 경로 → 새 상대경로
for t in b.find_all(list(EMBED)):
    for at in ('src', 'poster'):
        p = local(t.get(at))
        if p and p not in jobs:
            ext = {'.wav': '.mp3'}.get(p.suffix.lower(), p.suffix.lower())
            jobs[p] = 'media/' + hashlib.sha1(str(p).encode('utf-8')).hexdigest()[:12] + ext


def dur(p):
    r = subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return float(r.stdout.strip() or 0)


def convert(item):
    p, rel = item
    dst = OUT / rel
    if HTML_ONLY:
        assert dst.exists(), rel
        return rel, dst.stat().st_size
    e = p.suffix.lower()
    if e == '.mp4':
        d = max(dur(p), 1.0)
        vk = int(min(V_MAX_K, MAX_MB * 8000 / d - A_K - 16))
        cmd = [FF, '-nostdin', '-v', 'error', '-y', '-i', str(p),
               '-vf', 'scale=540:960:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2',
               '-c:v', 'libx264', '-preset', 'medium', '-b:v', f'{vk}k', '-maxrate', f'{int(vk * 1.3)}k',
               '-bufsize', f'{vk * 2}k', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
               '-c:a', 'aac', '-b:a', f'{A_K}k', '-ac', '2', str(dst)]
    elif e == '.wav':
        cmd = [FF, '-nostdin', '-v', 'error', '-y', '-i', str(p), '-c:a', 'libmp3lame', '-b:a', '96k', str(dst)]
    else:
        shutil.copy2(p, dst)
        return rel, dst.stat().st_size
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)
    return rel, dst.stat().st_size


t0 = time.time()
with ThreadPoolExecutor(4) as ex:
    sizes = dict(ex.map(convert, jobs.items()))

# 2) 경로 바꾸기 — 링크(a)는 같은 파일이 묶음에 있으면 그쪽으로, 없으면 링크를 풀고 글자만
for t in b.find_all(list(EMBED)):
    for at in ('src', 'poster'):
        p = local(t.get(at))
        if p:
            t[at] = jobs[p]
# 목차 이동 후 이미지·영상이 늦게 불러와지며 자리가 밀리지 않도록 실제 크기를 적어 둔다(아티팩트에서 16장 링크가 10장에 멈춤 실측)
from PIL import Image


def wh(rel):
    q = OUT / rel
    if q.suffix in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
        with Image.open(q) as im:
            return im.size
    if q.suffix == '.mp4':
        r = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(q)],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        w, h = r.stdout.strip().split(',')[:2]
        return int(w), int(h)
    return None


dims = {rel: wh(rel) for rel in jobs.values()}
for t in b.find_all(['img', 'video']):
    rel = t.get('src') or (t.find('source') or {}).get('src')
    if rel in dims and dims[rel] and not t.get('width'):
        t['width'], t['height'] = dims[rel]
b.head.append(BeautifulSoup('<style>img,video{height:auto;max-width:100%}</style>', 'html.parser'))
unwrapped = 0
for a in b.find_all('a'):
    v = a.get('href')
    if not v or v.startswith(('#', 'http:', 'https:', 'mailto:')):
        continue
    p = local(v)
    if p in jobs:
        a['href'] = jobs[p]
    else:
        a.unwrap(); unwrapped += 1

# 3) 안내 문구: 개발자용 표시 옆에 아티팩트판 설명
note = b.find('div', class_='dev-only')
if note:
    note.append(BeautifulSoup('<br><b>아티팩트판</b> — 용량 제한(파일당 15MB)으로 영상은 540×960으로 줄였고, 로컬 파일로만 걸려 있던 링크(json·스크립트 등)는 글자만 남겼습니다. '
                              '원본 화질은 로컬 <code>1_최종영상/</code>에서 보세요.', 'html.parser'))

# 4) 아티팩트 형식: doctype/html/head/body 없이 title·style·본문·script 순서
head = b.head
parts = [str(head.title)] + [str(s) for s in head.find_all('style')] + [str(s) for s in head.find_all('script')]
body = ''.join(str(c) for c in b.body.contents)
(OUT / 'index.html').write_text('\n'.join(parts) + '\n' + body, encoding='utf-8')

tot = sum(sizes.values())
big = max(sizes.values())
print(f'files {len(sizes)} + index · total {tot / 1e6:.1f}MB · largest {big / 1e6:.1f}MB · unwrapped links {unwrapped} · {time.time() - t0:.0f}s')
