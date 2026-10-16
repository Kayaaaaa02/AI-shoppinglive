"""R3 확정 후: 캐릭터 시트(각도·표정·손) + H3 첫 프레임(마스터 프레임). gpt-image images.edit, R3 정면을 레퍼런스로.
키는 저장소 루트 .env(ailive_config)에서 읽고 출력하지 않는다.
python -X utf8 gen_r3_character.py [sheet|master|all]
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import base64, datetime, json, sys, pathlib
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = ROOT / '4_테스트' / 'character' / 'CS-00R_real' / 'CS-00R_3.png'
OUT = ROOT / '5_에셋' / 'character_sheet' / 'R3'
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / 'generation_log.json'
MODEL = 'gpt-image-1.5'

client = cfg.openai_client()

SAME = ("EXACTLY the same woman as in the input image: identical face shape, eyes, eyelids, nose, lips, skin tone, "
        "freckles, hair color, hair length, bangs and slight wave, identical cream-white knit sweater. Fictional person. ")
REAL = ("Unretouched photograph, full-frame camera, natural soft window light. Real skin texture with visible fine pores, "
        "light freckles, faint peach fuzz, natural sheen; no airbrushing, no beauty filter, no plastic or CGI look. "
        "No earrings, necklace, rings, watch or hair clips. No text, labels, captions, logos or products. "
        "Hands with exactly five natural fingers, short bare nude nails. ")

JOBS = {
    'sheet_turnaround': ('1536x1024', SAME + REAL +
        "Character turnaround sheet, landscape, four evenly spaced head-and-shoulders panels on a plain light-pink background "
        "(#F6D9E4), same lighting in each: front view, three-quarter left, three-quarter right, left profile. Neutral friendly expression."),
    'sheet_expressions': ('1536x1024', SAME + REAL +
        "Expression sheet, landscape, 2 rows x 3 evenly spaced waist-up panels on a plain light-pink background (#F6D9E4): "
        "gentle closed-mouth smile; talking mid-sentence with mouth naturally open; bright excited smile showing a little teeth; "
        "light surprise; thoughtful nod; pointing down-right toward the bottom of the frame with the index finger at chest height."),
    'sheet_hands': ('1536x1024', SAME + REAL +
        "Hand-gesture sheet, landscape, 4 evenly spaced waist-up panels on a plain light-pink background (#F6D9E4): "
        "both hands loosely together at chest; one open palm presenting to her side; small wave hello with one hand; "
        "holding up one index finger. Every hand clearly anatomically correct."),
    'MF-01_master': ('1024x1536', SAME + REAL +
        "Live-shopping studio master frame for a vertical 9:16 broadcast. Medium waist-up shot, eye-level, locked camera, "
        "she sits centered behind a clean white tabletop, looking at the camera with a gentle closed-mouth smile, both hands "
        "relaxed together resting on the table. Her eyes are at about 46% of the image height from the top and the top of her "
        "head at about 30%, leaving calm empty background above her. The tabletop edge is at about 76% of the height and the "
        "table surface is completely empty. Background: soft pastel-pink studio wall with a gentle out-of-focus warm glow, "
        "no furniture, no shelves, no props. Soft key light from the front-left, gentle fill, natural shadows."),
}


def usage(resp):
    u = getattr(resp, 'usage', None)
    return u.model_dump() if u is not None and hasattr(u, 'model_dump') else None


def run(name):
    size, prompt = JOBS[name]
    out = OUT / f'R3_{name}.png'
    if out.exists():
        return None
    with open(REF, 'rb') as fh:
        resp = client.images.edit(model=MODEL, image=fh, prompt=prompt, size=size, quality='high', n=1,
                                  input_fidelity='high')
    out.write_bytes(base64.b64decode(resp.data[0].b64_json))
    print('ok', out.name, flush=True)
    return dict(step='R3 ' + name, model=MODEL, size=size, quality='high', input_fidelity='high', reference=str(REF),
                prompt=prompt, file=str(out), ts=datetime.datetime.now().isoformat(timespec='seconds'), usage=usage(resp))


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    names = [n for n in JOBS if which == 'all' or n.startswith(which) or n == which or (which == 'master' and 'master' in n)]
    with ThreadPoolExecutor(4) as ex:
        entries = [e for e in ex.map(run, names) if e]
    log = json.loads(LOG.read_text(encoding='utf-8')) if LOG.exists() else []
    LOG.write_text(json.dumps(log + entries, ensure_ascii=False, indent=1), encoding='utf-8')
