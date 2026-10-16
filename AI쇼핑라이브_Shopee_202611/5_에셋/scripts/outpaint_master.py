"""MF-01 9:16 재구성: 인물 0.72배 축소 → 눈 높이 46% 위치로 내림 → 빈 영역만 gpt-image 아웃페인트(mask) → 864x1536 크롭 → 1080x1920."""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import base64, io, json, datetime, pathlib
from PIL import Image
from openai import OpenAI
D = pathlib.Path(__file__).resolve().parents[1] / 'character_sheet' / 'R3'
client = cfg.openai_client()
src = Image.open(D / 'R3_MF-01_master.png').convert('RGBA')
s = 0.72; EYE_SRC = 400
sm = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
ox = (1024 - sm.width) // 2; oy = round(1536 * 0.46 - EYE_SRC * s)
canvas = Image.new('RGBA', (1024, 1536), (0, 0, 0, 0)); canvas.paste(sm, (ox, oy))
mask = Image.new('RGBA', (1024, 1536), (0, 0, 0, 0)); mask.paste(Image.new('RGBA', sm.size, (0, 0, 0, 255)), (ox, oy))
canvas.save(D / '_op_canvas.png'); mask.save(D / '_op_mask.png')
prompt = ("Extend the scene naturally into the transparent areas only: continue the same soft pastel-pink studio wall with the "
          "same gentle warm glow and lighting above and beside her, and continue the clean white tabletop to the left and right edges. "
          "Do not change the woman, her face, hair, sweater, hands or pose. No objects, props, text or logos.")
with open(D / '_op_canvas.png', 'rb') as im, open(D / '_op_mask.png', 'rb') as mk:
    r = client.images.edit(model='gpt-image-1.5', image=im, mask=mk, prompt=prompt, size='1024x1536', quality='high', input_fidelity='high')
full = Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json))).convert('RGB')
full.save(D / 'R3_MF-01_outpaint_1024x1536.png')
crop = full.crop((80, 0, 944, 1536)).resize((1080, 1920), Image.LANCZOS)
crop.save(D / 'R3_MF-01_9x16.png')
log = json.loads((D / 'generation_log.json').read_text(encoding='utf-8'))
u = getattr(r, 'usage', None)
log.append(dict(step='R3 MF-01 outpaint (mask)', model='gpt-image-1.5', scale=s, offset=[ox, oy], prompt=prompt,
                file=str(D / 'R3_MF-01_9x16.png'), ts=datetime.datetime.now().isoformat(timespec='seconds'),
                usage=u.model_dump() if u is not None and hasattr(u, 'model_dump') else None))
(D / 'generation_log.json').write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', ox, oy, crop.size)
