# -*- coding: utf-8 -*-
"""0단계: 새 AI 쇼핑라이브 프로젝트 폴더를 만든다 (5분류 + brief/intake.json).
기본 호스트(R3)의 마스터 프레임·시트·목소리 참조를 복사해 두면 캐릭터·목소리 단계를 무료로 건너뛸 수 있다.
폰트(Pretendard)·로고도 POC에서 복사한다(배너·카드 조판용).

python -X utf8 pipeline/new_project.py --name AI쇼핑라이브_Lazada_202612 --products "제품A,제품B" \
    --channel Lazada --countries SG,MY --promo "Buy 1 Get 1" [--host R3|none]
"""
import argparse
import json
import shutil
from datetime import date
from pathlib import Path

HUB = Path(__file__).resolve().parents[1]                 # fnco_ai-shoppinghost/
BASE = HUB / 'AI쇼핑라이브_Shopee_202611'                  # 재사용 자산이 있는 POC 프로젝트
FOLDERS = ['0_기획/brief', '1_최종영상', '2_나레이션/voice', '2_나레이션/vo', '3_소스클립/H3', '4_테스트',
           '5_에셋/이미지생성_소스', '5_에셋/production', '5_에셋/banner/common', '5_에셋/character_sheet', '5_에셋/logo']

ap = argparse.ArgumentParser()
ap.add_argument('--name', required=True)
ap.add_argument('--products', required=True, help='쉼표로 구분한 제품명 (한글 정식명 권장)')
ap.add_argument('--brand', default='BANILA CO')
ap.add_argument('--channel', default='Shopee')
ap.add_argument('--countries', default='')
ap.add_argument('--language', default='English')
ap.add_argument('--promo', default='', help='실무진이 준 프로모션 문구 그대로. 없으면 비움')
ap.add_argument('--host', default='R3', help='R3 = POC 호스트 재사용(무료) / none = 새 호스트 생성 예정')
a = ap.parse_args()

P = HUB / a.name
if P.exists():
    raise SystemExit(f'이미 있음: {P}')
for f in FOLDERS:
    (P / f).mkdir(parents=True, exist_ok=True)

shutil.copytree(BASE / '5_에셋/banner/fonts', P / '5_에셋/banner/fonts', ignore=shutil.ignore_patterns('Poppins*', 'Playfair*'))
for f in (BASE / '5_에셋/logo').glob('BANILACO_logo_*.png'):
    shutil.copy2(f, P / '5_에셋/logo' / f.name)

host = None
if a.host == 'R3':
    src = BASE / '5_에셋/character_sheet/R3'
    dst = P / '5_에셋/character_sheet/R3'
    dst.mkdir(parents=True)
    for f in src.glob('R3_*.png'):
        if not f.name.startswith('_op_'):
            shutil.copy2(f, dst / f.name)
    v = BASE / '2_나레이션/voice'
    for n in ('host_reference.wav', 'voice_state.json'):
        if (v / n).exists():
            shutil.copy2(v / n, P / '2_나레이션/voice' / n)
    host = {'id': 'R3', 'anchor': '5_에셋/character_sheet/R3/R3_MF-01_9x16.png',
            'note': 'POC 호스트 재사용. voice_id 보존 기한은 voice_state.json의 retention_note 확인'}

intake = {
    'created': date.today().isoformat(),
    'brand': a.brand, 'channel': a.channel, 'language': a.language,
    'countries': [c for c in a.countries.split(',') if c],
    'products': [{'name': n.strip()} for n in a.products.split(',') if n.strip()],
    'promo': {'text': a.promo or None, 'price': None, 'gift': None, 'period': None,
              '_comment': '실무진 회신값만 채움. 비어 있으면 대본·배너에서 숫자 없이'},
    'host': host,
}
(P / '0_기획/brief/intake.json').write_text(json.dumps(intake, ensure_ascii=False, indent=1), encoding='utf-8')
print('created', P)
print('next: Claude가 Product Spec·NAS MCP로 1·2단계 진행 (pipeline/SKILL.md)')
