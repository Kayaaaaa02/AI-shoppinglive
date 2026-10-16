# -*- coding: utf-8 -*-
"""[대체됨 2026-10-15 → build_share_page.py (공유용 한 장 구성)] v4 계획서 HTML → dcsai Quick Dashboard 업로드용 묶음.

QD는 html·css·js·이미지·폰트·json만 받음(mp4·wav·mp3 불가, 200파일·파일당 50MB).
그래서 영상·음성은 빼고, 주요 영상(완성본·공통 오프닝/엔딩·장면별 묶음)은 대표 프레임 이미지 + 원본 경로 안내로 바꾼다.
출력: 0_기획/공유용/dcsai_bundle/ (index.html + 같은 상대경로의 이미지)
python -X utf8 5_에셋/scripts/build_dcsai_bundle.py
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '0_기획/개발자용/Shopee_AI쇼호스트_제작설계_v4.html'
OUT = ROOT / '0_기획/공유용/dcsai_bundle'  # 2026-10-15 사용자: dcsai 판 = 공유용. 묶음 폴더 이름은 영문이어야 함(한글 이름 폴더로 올리면 이미지 깨짐 실측)
FF = cfg.FFMPEG
FP = cfg.FFPROBE
MEDIA = ('.mp4', '.wav', '.mp3')
if OUT.exists():
    shutil.move(str(OUT), str(ROOT / '4_테스트' / f'_old_dcsai_qd_{int(OUT.stat().st_mtime)}'))
OUT.mkdir(parents=True)

b = BeautifulSoup(SRC.read_text(encoding='utf-8'), 'html.parser')
for d in b.select('.dev-only'):  # 개발자용 전용 블록(테스트 비용 구분 등)은 공유판에서 뺀다
    d.decompose()


def rel(v):
    """'../X' (0_기획 기준) → 'X' (묶음 루트 기준)"""
    p = unquote(v.split('#')[0])
    while p.startswith('../'):
        p = p[3:]
    return p


_AMAP = {}
# 빌드마다 파일 이름을 새로 — 같은 이름으로 app update 하면 이미지가 사라짐(2026-10-15 실측: 재업로드 후 112장 중 1장만 열림)
import time as _time
BUILD = str(int(_time.time()))


def ascii_path(r):
    """QD 서버가 한글 경로 파일을 못 내줌(2026-10-15 실측: 한글 경로 이미지 112개 전부 깨짐),
    Windows에서 올린 하위 폴더 파일도 그 경로로 열리지 않음(NoSuchKey 실측) → 영문 이름으로 루트에 평평하게 둔다."""
    if r not in _AMAP:
        import hashlib, re as _re
        stem = _re.sub(r'[^A-Za-z0-9._-]+', '_', Path(r).stem).strip('_')[:60] or 'f'
        _AMAP[r] = f'{hashlib.md5((BUILD + r).encode()).hexdigest()[:6]}_{stem}{Path(r).suffix.lower()}'
    return _AMAP[r]


def dur(p):
    r = subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return float(r.stdout.strip() or 0)


n_poster = 0
for v in b.find_all('video'):
    src = rel(v['src'])
    main = v.find_parent(class_='fv') is not None or 'h3_groups/' in src or 'COMMON_' in src
    note = b.new_tag('div', attrs={'class': 'vph'})
    if main:
        poster = ascii_path('posters/' + src.rsplit('.', 1)[0] + '.jpg')
        t = min(2.0, dur(ROOT / src) / 2)
        subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(ROOT / src), '-frames:v', '1',
                        '-vf', 'scale=360:-2', '-q:v', '4', str(OUT / poster)], check=True)
        img = b.new_tag('img', attrs={'src': poster, 'alt': '영상 대표 프레임', 'loading': 'lazy'})
        note.append(img); n_poster += 1
    cap = b.new_tag('span', attrs={'class': 'small'})
    cap.append(BeautifulSoup(f'영상은 이 공유 페이지에서 재생되지 않습니다(사내 대시보드가 영상 파일을 받지 않음). 원본: <code>{src}</code> ({dur(ROOT / src):.0f}초)', 'html.parser'))
    note.append(cap)
    v.replace_with(note)
for a_ in b.find_all('audio'):
    c = b.new_tag('code'); c.string = rel(a_['src']) + ' (음성, 로컬 파일)'
    a_.replace_with(c)
for a_ in b.find_all('a', href=True):
    h = a_['href']
    if h.startswith(('http', '#', 'mailto')):
        continue
    if rel(h).lower().endswith(MEDIA):
        a_.name = 'span'; del a_['href']
    else:
        a_['href'] = rel(h)
for im in b.find_all('img', src=True):
    s = im['src']
    if s in _AMAP.values() or s.startswith(('http', 'data:')):
        continue
    r = rel(s); im['src'] = ascii_path(r)
    dst = OUT / im['src']; dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(ROOT / r, dst)
# 링크로만 걸린 이미지(크게 보기)도 복사
for a_ in b.find_all('a', href=True):
    r = a_['href']
    if r.startswith(('http', '#', 'mailto')):
        continue
    if (ROOT / r).is_file():
        if Path(r).suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.json'):
            a_['href'] = ascii_path(r)
            if not (OUT / a_['href']).exists():
                shutil.copy2(ROOT / r, OUT / a_['href'])
        else:
            a_.name = 'span'; del a_['href']
b.head.append(BeautifulSoup('<style>.vph{border:1px dashed rgba(128,128,128,.5);border-radius:10px;padding:8px;display:flex;flex-direction:column;gap:6px;'
                            'max-width:380px}.vph img{width:100%;max-width:360px;border-radius:6px}</style>', 'html.parser'))
top = b.find('main') or b.body
top.insert(0, BeautifulSoup('<div class="callout warn"><b>공유판 안내</b> — 사내 대시보드는 영상·음성 파일을 올릴 수 없어, 영상 자리는 대표 프레임과 원본 파일 경로로 바꿨습니다. '
                            '구간 버튼은 이 페이지에선 동작하지 않습니다. 영상은 담당자에게 원본(<code>1_최종영상/</code>)을 받아 보세요.</div>', 'html.parser'))
(OUT / 'index.html').write_text(str(b), encoding='utf-8')
files = [p for p in OUT.rglob('*') if p.is_file()]
big = [p for p in files if p.stat().st_size > 50e6]
print('files', len(files), 'posters', n_poster, 'MB', round(sum(p.stat().st_size for p in files) / 1e6, 1), 'over50MB', big)
