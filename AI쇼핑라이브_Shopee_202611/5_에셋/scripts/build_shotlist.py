"""v3 대본(build_v3_text.py의 v1·v2·v3 + 공통 OC/EC)을 생성 단위로 변환.
- kind=h3 : 호스트가 화면에서 직접 말함 (유형에 H 또는 S, 'V/O:' 아님). 15초 클립 1개 = 약 30단어 이하 청크
- kind=vo : T2A 음성만 (유형 D·G, 또는 'V/O:' 표기)
대본 원문에서 바꾼 곳은 changes 에 기록한다(RA 보수화 2건, L5 번호만).
python -X utf8 build_shotlist.py
"""
import html, json, re, sys, pathlib, importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / '5_에셋' / 'production' / 'shotlist_v3.json'
OUT.parent.mkdir(parents=True, exist_ok=True)

# build_v3_text.py 의 v1/v2/v3 리스트만 꺼낸다 (모듈 실행 없이 AST로)
import ast
src = (ROOT / '0_기획' / 'build_v3_text.py').read_text(encoding='utf-8')
tree = ast.parse(src)
rows = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], 'id', None) in ('v1', 'v2', 'v3'):
        items = []
        for elt in node.value.elts:
            vals = []
            for e in elt.elts[:5]:
                vals.append(e.value if isinstance(e, ast.Constant) else None)
            items.append(vals)
        rows[node.targets[0].id] = items

COMMON = [
    ('OC-1', 'H', '호스트 손 흔들며 인사', "Hi everyone, welcome to Banila Co Live! I'm your AI host today."),
    ('OC-2', 'H', '호스트, 기대감 표정', "Today's promotion is a really great chance — so I hope you grab your favorites this time!"),
    ('OC-3', 'H', '호스트, 화면 아래 가리킴', "Stay with me. I'll show you everything, step by step — and the deal is waiting below."),
    ('EC-1', 'H+G', '호스트 + 장바구니 안내 카드', "That's it for today! Remember, this deal is a great chance — I really hope you take it home this time."),
    ('EC-2', 'H+G', '장바구니 카드 강조', "Just tap the product card below to add it to your cart."),
    ('EC-3', 'H+G', '문의 카드', "Got a question? Leave it in the chat, and we'll get back to you. Thanks for watching — see you next live!"),
]

CHANGES = {
    # 대본 표 비고에 적힌 보수안을 그대로 적용
    'EC-3': ("Got a question? Leave it in the chat. Thanks for watching — see you next live!",
             "R8 응대 주체 미확인 → 'we'll get back to you' 제외 (3-0 비고)"),
    'P4-1': ("Next, the classic of the line — Prime Primer Classic. This is a cream primer, and it is the step right before your foundation.",
             "'bestseller' 판매 근거 미확인 → 'the classic of the line' (P4-1 비고 대체안)"),
}
SHADES = ['02', '04', '05', '07', '08', '09', '12', '13', '14', '17', '18', '20']
SPOKEN = {'02': 'oh-two', '04': 'oh-four', '05': 'oh-five', '07': 'oh-seven', '08': 'oh-eight', '09': 'oh-nine',
          '12': 'twelve', '13': 'thirteen', '14': 'fourteen', '17': 'seventeen', '18': 'eighteen', '20': 'twenty'}


def spoken(n):
    return SPOKEN[n]



def gesture(screen):
    s = screen or ''
    if '흔들' in s: return 'She gives a small friendly wave hello with one hand at chest height near the start, then lowers it.'
    if '가리' in s or '장바구니' in s or '카드' in s: return 'Near the end she points gently down toward the bottom of the frame with one index finger at chest height.'
    if '손가락 하나' in s: return 'She holds up one index finger at chest height while saying the key point.'
    if '퍼프' in s: return 'She makes a small light pressing motion with her fingertips at chest height, with nothing in her hand.'
    if '공감' in s: return 'She tilts her head slightly with an understanding expression at the start.'
    return 'She uses one or two small open-palm gestures below chest height.'


def chunks(text, limit=22):
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    out, cur = [], ''
    for s in sents:
        cand = (cur + ' ' + s).strip()
        if cur and len(cand.split()) > limit:
            out.append(cur); cur = s
        else:
            cur = cand
    if cur: out.append(cur)
    return out


shots, changes = [], []


def add(video, key, typ, screen, text):
    text = html.unescape(text)
    if key in CHANGES:
        new, why = CHANGES[key]; changes.append(dict(id=key, before=text, after=new, why=why)); text = new
    is_vo = text.startswith('V/O') or not ('H' in typ or 'S' in typ)
    text = re.sub(r'^V/O[^:]*:\s*', '', text)
    if key == 'L5':
        changes.append(dict(id='L5', before=text, after='12색 번호만 (Shade oh-two … twenty)',
                            why='영문 컬러명 미확정(R6) → 번호만 말함 (L5 비고)'))
        for n in SHADES:
            shots.append(dict(id=f'{video}_L5_{n}', video=video, scene='L5', kind='vo', emotion='happy',
                              text=f"Shade {spoken(n)}."))
        return
    if is_vo:
        emotion = 'calm' if typ.startswith('D') or '시연' in (screen or '') else 'happy'
        shots.append(dict(id=f'{video}_{key}', video=video, scene=key, kind='vo', emotion=emotion, text=text))
        return
    spoken_text = re.sub(r'(?<![\d.])(02|04|05|07|08|09|12|13|14|17|18|20)(?!\d)', lambda m: SPOKEN[m.group(1)], text)
    if spoken_text != text:
        changes.append(dict(id=key, before=text, after=spoken_text, why='호수 숫자를 발음 표기로 고정 (H3 읽기 오류 방지)'))
        text = spoken_text
    parts = chunks(text)
    for i, part in enumerate(parts, 1):
        sid = f'{video}_{key}' + (f'_{i}' if len(parts) > 1 else '')
        shots.append(dict(id=sid, video=video, scene=key, kind='h3', type=typ, screen=html.unescape(re.sub('<[^>]+>', '', screen or '')),
                          gesture=gesture(screen), text=part, words=len(part.split())))


for key, typ, screen, text in COMMON:
    add('COMMON', key, typ, screen, text)
for vid, name in (('v1', 'V1'), ('v2', 'V2'), ('v3', 'V3')):
    for key, t, typ, screen, text in rows[vid]:
        if text:
            add(name, key, typ, screen, text)

OUT.write_text(json.dumps(shots, ensure_ascii=False, indent=1), encoding='utf-8')
(OUT.parent / 'shotlist_v3_changes.json').write_text(json.dumps(changes, ensure_ascii=False, indent=1), encoding='utf-8')
h3 = [s for s in shots if s['kind'] == 'h3']; vo = [s for s in shots if s['kind'] == 'vo']
print('h3', len(h3), 'vo', len(vo), 'max words', max(s['words'] for s in h3))
for v in ('COMMON', 'V1', 'V2', 'V3'):
    print(v, 'h3', sum(1 for s in h3 if s['video'] == v), 'vo', sum(1 for s in vo if s['video'] == v))
