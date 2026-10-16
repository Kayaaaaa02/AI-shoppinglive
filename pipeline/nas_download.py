# -*- coding: utf-8 -*-
"""2단계: NAS MCP에서 고른 원본을 내려받고, 누끼는 실측(비율·색)해 product_lock.json을 만든다.

NAS 원본 링크는 5분이면 만료된다. 그래서 Claude가
  ① search_nas_assets / get_sku_assets 로 후보를 고르고(미리보기 링크 1시간)
  ② 내려받기 직전에 get_asset(file_id) 로 새 original.url 을 받아
  ③ 아래 형식의 JSON을 쓰고 바로 이 스크립트를 실행한다.

입력 (--sel): [{"key": "primer_classic", "role": "cutout|swatch|detail|demo_video|mood",
               "file_id": "5099beb3caf5", "filename": "...png", "url": "<original.url>", "nas_path": "...",
               "width": 7200, "height": 7200, "has_alpha": true}]
출력: 5_에셋/이미지생성_소스/<key>/<role>/<filename>
      5_에셋/이미지생성_소스/assets_manifest.json   (누적, file_id 기준 중복 없음)
      5_에셋/product_lock.json                     (누끼별 실측: 불투명 영역 bbox·가로세로 비율·대표색 hex)
      큰 누끼는 작업용 사본(긴 변 2000px) <name>__w2000.png 도 함께 만든다(원본은 그대로).

python -X utf8 pipeline/nas_download.py --project <프로젝트 폴더> --sel sel.json
"""
import argparse
import json
import urllib.request
from collections import Counter
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True)
ap.add_argument('--sel', required=True)
a = ap.parse_args()

P = Path(a.project).resolve()
SRC = P / '5_에셋/이미지생성_소스'
MAN = SRC / 'assets_manifest.json'
LOCK = P / '5_에셋/product_lock.json'
sel = json.loads(Path(a.sel).read_text(encoding='utf-8'))
man = json.loads(MAN.read_text(encoding='utf-8')) if MAN.exists() else {}
lock = json.loads(LOCK.read_text(encoding='utf-8')) if LOCK.exists() else {}


def safe(name):
    return ''.join('_' if c in '<>:"/\\|?*' else c for c in name).strip()


def measure(png):
    """누끼 실측: 알파>16인 영역의 bbox, 가로:세로 비율, 불투명 픽셀 상위 색 3개(hex, 16단계로 묶음)."""
    im = Image.open(png).convert('RGBA')
    im.thumbnail((1200, 1200))
    alpha = im.getchannel('A').point(lambda v: 255 if v > 16 else 0)
    box = alpha.getbbox()
    if not box:
        return None
    crop = im.crop(box)
    px = [p[:3] for p in crop.getdata() if p[3] > 200]
    q = Counter(tuple(c // 16 * 16 + 8 for c in p) for p in px)
    tot = sum(q.values()) or 1
    w, h = box[2] - box[0], box[3] - box[1]
    return {'bbox_ratio_w_h': round(w / h, 3), 'opaque_px_share': round(len(px) / (crop.width * crop.height), 3),
            'top_colors': [{'hex': '#%02X%02X%02X' % c, 'share': round(n / tot, 3)} for c, n in q.most_common(3)],
            'measured_on': f'{im.width}x{im.height} 축소본에서 알파 실측 (원본 비율 동일)'}


for s in sel:
    d = SRC / s['key'] / s['role']
    d.mkdir(parents=True, exist_ok=True)
    out = d / safe(s['filename'])
    if not out.exists():
        req = urllib.request.Request(s['url'], headers={'User-Agent': 'ailive-pipeline'})
        with urllib.request.urlopen(req, timeout=300) as r, open(out, 'wb') as fh:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                fh.write(b)
    ent = {k: s.get(k) for k in ('key', 'role', 'file_id', 'filename', 'nas_path', 'width', 'height', 'has_alpha')}
    ent['local'] = out.relative_to(P).as_posix()
    if out.suffix.lower() == '.png' and s.get('has_alpha'):
        im = Image.open(out)
        if max(im.size) > 2000:
            work = out.with_name(out.stem + '__w2000.png')
            if not work.exists():
                im.thumbnail((2000, 2000)); im.save(work)
            ent['work'] = work.relative_to(P).as_posix()
        m = measure(out)
        if m:
            lock.setdefault(s['key'], {})[out.name] = m
    man[s['file_id']] = ent
    print('ok', ent['local'])

MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=1), encoding='utf-8')
print('manifest', len(man), '| lock products', len(lock))
