# -*- coding: utf-8 -*-
"""5단계: 배너 (1080×1920) — POC 배너 템플릿(promo·info)을 그대로 쓰고 내용만 brief/banners.json에서 받는다.
제품은 그리지 않는다: 2단계에서 받은 공식 누끼(작업용 사본)만 비율 유지로 배치.
문구는 claim 등급과 함께 copy_audit.csv로 남긴다 (cosmetic / RA = RA·법무 사전검토).

brief/banners.json 예:
[{"file": "BNR_V1_promo", "type": "promo", "eyebrow": "Prime Primer line", "big": "50<small>%</small> OFF",
  "plus": "+ Free Gift", "products": [["primer_classic", 330]], "line": "Prep · Finish · Set", "gift": true},
 {"file": "BNR_V1_info", "type": "info", "eyebrow": "...", "title": "...", "note": "Individual results may vary.",
  "cards": [["primer_classic", "#FFFFFF", "Primer · Prep", [["Pea-size amount is enough", "cosmetic"]]], ...]}]   # info 카드는 3장 또는 4장

python -X utf8 pipeline/build_banners.py --project <프로젝트 폴더>
"""
import argparse
import csv
import importlib.util
import json
import shutil
from pathlib import Path

HUB = Path(__file__).resolve().parents[1]
TPL = HUB / 'AI쇼핑라이브_Shopee_202611/5_에셋/banner/template/build_banners.py'
ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True)
a = ap.parse_args()
P = Path(a.project).resolve()
BN = P / '5_에셋/banner'

spec = importlib.util.spec_from_file_location('bb_tpl', TPL)
bb = importlib.util.module_from_spec(spec); spec.loader.exec_module(bb)
# 템플릿 모듈의 경로를 이 프로젝트로 돌린다 (POC 폴더에 쓰지 않도록)
bb.T = BN / 'template'; bb.T.mkdir(parents=True, exist_ok=True)
bb.CUT = BN / 'src_cutouts'; bb.CUT.mkdir(parents=True, exist_ok=True)
logo = P / '5_에셋/logo/BANILACO_logo_white.png'
if logo.exists():
    bb.LOGO = logo

# 누끼: assets_manifest.json의 cutout 중 제품 키마다 첫 번째(작업용 사본 우선)를 <key>.png 로
man = json.loads((P / '5_에셋/이미지생성_소스/assets_manifest.json').read_text(encoding='utf-8'))
picked = {}
for m in man.values():
    if m['role'] == 'cutout' and m['key'] not in picked:
        picked[m['key']] = P / (m.get('work') or m['local'])
for k, f in picked.items():
    shutil.copy2(f, bb.CUT / f'{k}.png')

pages = {}
for b in json.loads((P / '0_기획/brief/banners.json').read_text(encoding='utf-8')):
    missing = [k for k, *_ in (b.get('products') or b.get('cards') or []) if k not in picked]
    if missing:
        raise SystemExit(f"{b['file']}: 누끼 없음 {missing} — 2단계에서 먼저 받기")
    if b['type'] == 'promo':
        # 아래 한 줄(line)이 두 줄로 넘어가면 각주와 겹친다 (2026-10-16 테스트 실측: 51자에서 겹침, POC 최장 48자는 한 줄)
        if len(b['line']) > 48:
            raise SystemExit(f"{b['file']}: line {len(b['line'])}자 — 48자 이내로 줄이기 (두 줄이면 각주와 겹침)")
        pages[b['file']] = bb.promo(b['file'], eyebrow=b['eyebrow'], big=b['big'], plus=b['plus'],
                                    products=[tuple(x) for x in b['products']], line=b['line'],
                                    accent=b.get('accent', '#E9579A'), tint=b.get('tint', '#FFFFFF'),
                                    gift=b.get('gift', True), note=b.get('note', 'While stocks last.'))
    elif b['type'] == 'info':
        assert len(b['cards']) in (3, 4), f"{b['file']}: info 카드는 3장 또는 4장"
        pages[b['file']] = bb.info(b['file'], eyebrow=b['eyebrow'], title=b['title'], accent=b.get('accent', '#E9579A'),
                                   cards=[(k, bg, tag, [tuple(p) for p in pts]) for k, bg, tag, pts in b['cards']],
                                   note=b.get('note', ''))
out = BN / 'common'
rep = bb.render(pages, out, brand=True)
with open(out / 'copy_audit.csv', 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh); w.writerow(['banner', 'element', 'text', 'claim_level (cosmetic / RA=RA·법무 사전검토)'])
    w.writerows(bb.COPY)
(BN / 'template' / 'render_check.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
for k, v in rep.items():
    print(k, 'overflow=', v['overflow'][:4], 'broken=', v['broken'])
