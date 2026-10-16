# -*- coding: utf-8 -*-
"""6단계(새 호스트가 필요할 때만, 유료): host_spec → 후보 → (사람이 1장 선택) → 캐릭터 시트 + 9:16 마스터 프레임.
기본은 POC 호스트 R3 재사용(new_project.py --host R3, 무료)이라 이 스크립트를 안 돌린다.
프롬프트 골격은 POC 5_에셋/scripts/gen_r3_character.py · outpaint_master.py에서 그대로 가져왔다.
키는 저장소 루트 .env(ailive_config)에서 읽고 출력·기록하지 않는다. --confirm 없으면 요청 내용만 보여 주고 끝난다.

0_기획/brief/host_spec.json 예:
{"id": "H2", "identity": "fictional early-20s Korean woman, light freckles, soft-brown long hair with see-through bangs",
 "wardrobe": "cream-white knit sweater", "set": "soft pastel-pink studio wall, clean white tabletop", "bg_hex": "#F6D9E4"}

python -X utf8 pipeline/gen_character.py --project <P> candidates [--n 4] [--confirm]
python -X utf8 pipeline/gen_character.py --project <P> sheets --ref <선택한 후보 png> [--confirm]
python -X utf8 pipeline/gen_character.py --project <P> master916 [--confirm]   # 마스터 프레임 → 1080x1920 (빈 곳만 아웃페인트)
모델: gpt-image-2.5-flare (2026-10-16 사용자 결정, 1.5 대신). 다른 모델을 시험할 때만 --model
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import argparse
import base64
import datetime
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True)
ap.add_argument('step', choices=['candidates', 'sheets', 'master916'])
ap.add_argument('--ref')
ap.add_argument('--n', type=int, default=4)
ap.add_argument('--confirm', action='store_true', help='유료 호출 실행 (사용자 승인 후에만)')
ap.add_argument('--model', default='gpt-image-2.5-flare')
a = ap.parse_args()
P = Path(a.project).resolve()
hs = json.loads((P / '0_기획/brief/host_spec.json').read_text(encoding='utf-8'))
OUT = P / '5_에셋/character_sheet' / hs['id']
TEST = P / '4_테스트/character' / hs['id']
MODEL = a.model

REAL = ("Unretouched photograph, full-frame camera, natural soft window light. Real skin texture with visible fine pores, "
        "natural sheen; no airbrushing, no beauty filter, no plastic or CGI look. "
        "No earrings, necklace, rings, watch or hair clips. No text, labels, captions, logos or products. "
        "Hands with exactly five natural fingers, short bare nude nails. ")
SAME = (f"EXACTLY the same woman as in the input image: identical face shape, eyes, eyelids, nose, lips, skin tone, "
        f"hair color, hair length and bangs, identical {hs['wardrobe']}. Fictional person. ")
BG = f"on a plain light background ({hs.get('bg_hex', '#F6D9E4')}), same lighting in each"
JOBS = {
    'sheet_turnaround': ('1536x1024', SAME + REAL + f"Character turnaround sheet, landscape, four evenly spaced head-and-shoulders panels {BG}: "
                         "front view, three-quarter left, three-quarter right, left profile. Neutral friendly expression."),
    'sheet_expressions': ('1536x1024', SAME + REAL + f"Expression sheet, landscape, 2 rows x 3 evenly spaced waist-up panels {BG}: "
                          "gentle closed-mouth smile; talking mid-sentence with mouth naturally open; bright excited smile showing a little teeth; "
                          "light surprise; thoughtful nod; pointing down-right toward the bottom of the frame with the index finger at chest height."),
    'sheet_hands': ('1536x1024', SAME + REAL + f"Hand-gesture sheet, landscape, 4 evenly spaced waist-up panels {BG}: "
                    "both hands loosely together at chest; one open palm presenting to her side; small wave hello with one hand; "
                    "holding up one index finger. Every hand clearly anatomically correct."),
    'MF-01_master': ('1024x1536', SAME + REAL + "Live-shopping studio master frame for a vertical 9:16 broadcast. Medium waist-up shot, eye-level, locked camera, "
                     "she sits centered behind a clean white tabletop, looking at the camera with a gentle closed-mouth smile, both hands "
                     "relaxed together resting on the table. Her eyes are at about 46% of the image height from the top and the top of her "
                     "head at about 30%, leaving calm empty background above her. The tabletop edge is at about 76% of the height and the "
                     f"table surface is completely empty. Background: {hs['set']}, no furniture, no shelves, no props. "
                     "Soft key light from the front-left, gentle fill, natural shadows."),
}
CAND = (f"Photorealistic waist-up portrait of a {hs['identity']}, wearing a {hs['wardrobe']}, {hs['set']}. "
        "Friendly, natural expression, looking at the camera. " + REAL)


def client():
    return cfg.openai_client()


def log(entry):
    f = OUT / 'generation_log.json'
    f.parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(f.read_text(encoding='utf-8')) if f.exists() else []
    f.write_text(json.dumps(old + [entry], ensure_ascii=False, indent=1), encoding='utf-8')


OUTPAINT = ("Extend the scene naturally into the transparent areas only: continue the same background and lighting above and beside her, "
            "and continue the clean white tabletop to the left and right edges. "
            "Do not change the woman, her face, hair, clothes, hands or pose. No objects, props, text or logos.")  # POC outpaint_master.py 문장에서 세트 묘사만 일반화


def edit(c, model, ref, prompt, size, mask=None):
    kw = dict(model=model, prompt=prompt, size=size, quality='high', n=1, input_fidelity='high')
    with open(ref, 'rb') as fh:
        if mask:
            with open(mask, 'rb') as mk:
                return c.images.edit(image=fh, mask=mk, **kw)
        return c.images.edit(image=fh, **kw)


if a.step == 'master916':
    from PIL import Image
    import io
    src = OUT / f"{hs['id']}_MF-01_master.png"
    print(f'[요청] {MODEL} edit+mask 1024x1536 (인물 0.72배 축소, 눈 높이 46%) ← {src.name}\n{OUTPAINT}')
    if not a.confirm:
        raise SystemExit('--confirm 없음: 유료 호출 안 함')
    im = Image.open(src).convert('RGBA'); s_ = 0.72; eye = 400   # POC outpaint_master.py 값 (원본 눈 높이 400px 가정 — 새 호스트는 확인 필요)
    sm = im.resize((round(im.width * s_), round(im.height * s_)), Image.LANCZOS)
    ox, oy = (1024 - sm.width) // 2, round(1536 * 0.46 - eye * s_)
    canvas = Image.new('RGBA', (1024, 1536), (0, 0, 0, 0)); canvas.paste(sm, (ox, oy))
    mask = Image.new('RGBA', (1024, 1536), (0, 0, 0, 0)); mask.paste(Image.new('RGBA', sm.size, (0, 0, 0, 255)), (ox, oy))
    cp, mp = TEST / '_op_canvas.png', TEST / '_op_mask.png'
    TEST.mkdir(parents=True, exist_ok=True); canvas.save(cp); mask.save(mp)
    r = edit(client(), MODEL, cp, OUTPAINT, '1024x1536', mask=mp)
    full = Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json))).convert('RGB')
    full.crop((80, 0, 944, 1536)).resize((1080, 1920), Image.LANCZOS).save(OUT / f"{hs['id']}_MF-01_9x16.png")
    log({'step': 'MF-01 9x16 outpaint', 'model': MODEL, 'prompt': OUTPAINT, 'ts': datetime.datetime.now().isoformat(timespec='seconds')})
    print('ok', OUT / f"{hs['id']}_MF-01_9x16.png", '→ intake.json host.anchor 로 지정')
    raise SystemExit(0)
if a.step == 'candidates':
    print(f'[요청] {MODEL} generate × {a.n}장 (1024x1536, high)\n{CAND}')
    if not a.confirm:
        raise SystemExit('--confirm 없음: 유료 호출 안 함')
    TEST.mkdir(parents=True, exist_ok=True)
    r = client().images.generate(model=MODEL, prompt=CAND, size='1024x1536', quality='high', n=a.n)
    for i, d in enumerate(r.data, 1):
        (TEST / f'cand_{i}.png').write_bytes(base64.b64decode(d.b64_json))
    log({'step': 'candidates', 'model': MODEL, 'n': a.n, 'prompt': CAND, 'ts': datetime.datetime.now().isoformat(timespec='seconds')})
    print('후보 저장', TEST, '→ 사람이 1장 고른 뒤 sheets --ref')
else:
    assert a.ref, '--ref 필요 (사람이 고른 후보)'
    for k, (size, prompt) in JOBS.items():
        print(f'[요청] {MODEL} edit {k} {size}')
    if not a.confirm:
        raise SystemExit('--confirm 없음: 유료 호출 안 함')
    OUT.mkdir(parents=True, exist_ok=True)
    c = client()
    for k, (size, prompt) in JOBS.items():
        out = OUT / f"{hs['id']}_{k}.png"
        if out.exists():
            continue
        r = edit(c, MODEL, a.ref, prompt, size)
        out.write_bytes(base64.b64decode(r.data[0].b64_json))
        log({'step': k, 'model': MODEL, 'size': size, 'reference': str(a.ref), 'prompt': prompt, 'file': str(out),
             'ts': datetime.datetime.now().isoformat(timespec='seconds')})
        print('ok', out.name)
    print('다음: master916 단계로 9:16(1080x1920) 마스터 프레임 → intake.json host.anchor')
