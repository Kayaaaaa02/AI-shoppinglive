"""최종 편집: 대본(shotlist) 순서대로 줄마다 화면을 합성해 V1·V2·V3 완성본(1080x1920, 30fps)을 만든다.
python -X utf8 build_final_edit.py [V1,V2,V3]
  → 1_최종영상/<V>_*.mp4 · 세그먼트 4_테스트/edit_seg/<V>/ · 편집 기록 4_테스트/edit_seg/<V>/edit_log.json

화면 유형 (shotlist type, VO는 계획서 3장 표의 유형):
  H    호스트 + 헤드라인(로고) + AI 고지 + 자막
  H+G  H + 측면 카드 (5_에셋/edit_gfx/card_*)
  S    H + 시연 창 (공식 상세페이지 영상, 원본 소리 제거)
  G    전체 화면 카드 + V/O            G+H  전체 화면 카드 + 호스트 음성
  D    공식 시연 영상 전체 화면 + V/O
호스트 클립: 편집본(*_cut.mp4, 대본 뒤 군말 제거)이 있으면 편집본. 번쩍임 프레임은 직전 프레임으로 교체(deflash).
호스트 레이어는 계획서 4장대로 아래로 내려 얼굴을 화면 약 44% 높이에 둔다. 위 빈 곳은 마스터 프레임 벽으로 채운다.
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import json, math, pathlib, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
H3 = ROOT / '3_소스클립' / 'H3'
QA = ROOT / '4_테스트' / 'h3_qa'
VO = ROOT / '2_나레이션' / 'vo'
GFX = ROOT / '5_에셋' / 'edit_gfx'
SRC = ROOT / '5_에셋' / '이미지생성_소스'
SEG = ROOT / '4_테스트' / 'edit_seg'
FINAL = ROOT / '1_최종영상'
MASTER = ROOT / '5_에셋' / 'character_sheet' / 'R3' / 'R3_MF-01_9x16.png'
FF, FP = cfg.FFMPEG, cfg.FFPROBE
FONT = str(ROOT / '5_에셋' / 'banner' / 'fonts' / 'Pretendard-Bold.otf')
W, HH, FPS, SHIFT = 1080, 1920, 30, 340
ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS),
       '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-b:a', '160k', '-movflags', '+faststart']

PRIME = SRC / '2.프라임 라인'
LC = SRC / '3.로맨틱 립앤치크' / '발색컷' / '4_gif'
CIZ = SRC / '1.클렌징밤'
# (파일, 시작초, 가로 크롭 중심 0~1)
DEMO = {
    'V1_P3-2': [(PRIME / '프라임 프라이머 선 베이스/상세페이지/선베이스 바르는 영상.mp4', 0, .5)],
    'V1_P3-3': [(PRIME / '프라임 프라이머 선 베이스/상세페이지/선베이스 볼 광채.mp4', 0, .5)],
    'V1_P4-2_1': [(PRIME / '프라임 프라이머 클래식/상세페이지/1_클래식 영상.mp4', 0, .5)],
    'V1_P4-2_2': [(PRIME / '프라임 프라이머 클래식/상세페이지/1_클래식 영상.mp4', 9, .5)],
    'V1_P5-2_1': [(PRIME / '프라임 프라이머 피니쉬 파우더 12g/상세페이지/피니쉬 파우더 영상.mp4', 0, .5)],
    'V1_P5-2_2': [(PRIME / '프라임 프라이머 피니쉬 파우더 12g/상세페이지/GIF/영상/프라임 프라이머 파우더  뜯어내기.mp4', 0, .55)],
    'V1_P6-2_1': [(PRIME / '프라임 프라이머 세팅 픽서 100ml/상세페이지/GIF/영상/프라임 프라이머 세팅픽서.mp4', 0, .66)],
    'V1_P6-2_2': [(PRIME / '프라임 프라이머 세팅 픽서 100ml/상세페이지/GIF/영상/프라임 프라이머 세팅픽서.mp4', 1.5, .66)],
    'V2_L3_1': [(LC / '8호 손바닥 그리기.gif', 0, .5), (LC / '8호 손바닥 퍼뜨리기.gif', 0, .5)],
    'V2_L3_2': [(LC / '8호 손바닥 퍼뜨리기.gif', 0, .5)],
    'V2_L2': [(LC / '8호 손바닥 그리기.gif', 0, .5), (LC / '8호 손바닥 퍼뜨리기.gif', 0, .5), (LC / '13호 치크 발색.gif', 0, .5)],
    'V2_L4': [(LC / '13호 립 발색.gif', 0, .5)],
    'V3_C2-1': [(CIZ / '클린 잇 제로 오리지널/3.제형/클린잇 제로 오리지널 밤 제형 스패출라.mp4', 0, .5)],
    'V3_C2-2': [(CIZ / '클린 잇 제로 오리지널/3.제형/클린잇 제로 오리지널 밤 제형 손등클렌징.mp4', 0, .5),
                (CIZ / '클린 잇 제로 오리지널/3.제형/클린잇 제로 오리지널 밤 제형.mp4', 0, .5)],
    'V3_C4-2': [(CIZ / '2. 클린 잇 제로 포어 클래리파잉/상세페이지컷/원본영상/손등.MP4', 0, .5)],
}
SPLIT = {'V1_P5-3': [(PRIME / '프라임 프라이머 피니쉬 파우더 12g/상세페이지/GIF/영상/프라임 프라이머 파우더 비포.mp4', 0, .42, 'BEFORE'),
                     (PRIME / '프라임 프라이머 피니쉬 파우더 12g/상세페이지/GIF/영상/프라임 프라이머 파우더 애프터.mp4', 0, .42, 'AFTER')]}
VO_MODE = {'V1_P2': 'g_V1_P2', 'V1_P4-4': 'g_V1_P4-4', 'V1_P6-4': 'g_V1_P6-4', 'V3_C5-2': 'g_V3_C5-2', 'V3_C7': 'g_V3_C7', 'V3_C8': 'g_V3_C8'}
D_OVERLAY = {}  # overlay_V3_C4-2(성분 칩) 2026-10-15 사용자 요청으로 삭제
CARD = {'COMMON_EC-1': 'card_EC-1', 'COMMON_EC-2': 'card_EC-2', 'COMMON_EC-3': 'card_EC-3',
        'V1_O-P': 'card_V1_O-P', 'V1_P3-1': 'card_V1_P3-1', 'V1_P4-1': 'card_V1_P4-1', 'V1_P5-1': 'card_V1_P5-1', 'V1_P6-1': 'card_V1_P6-1', 'V1_P7': 'card_V1_P7',
        'V2_O-L': 'card_V2_O-L', 'V2_L1': 'card_V2_L1', 'V2_L4-2': 'card_V2_L4-2', 'V2_L7': 'card_V2_L7',
        'V3_O-B': 'card_V3_O-B', 'V3_C3-1': 'card_V3_C3-1', 'V3_C3-2': 'card_V3_C3-2', 'V3_C4-1': 'card_V3_C4-1', 'V3_C5-1': 'card_V3_C5-1'}
GH = {'V1_P8': 'g_V1_P8', 'V2_L0': 'g_V2_L0', 'V2_L6': 'g_V2_L6', 'V2_L8': 'g_V2_L8', 'V3_C6': 'g_V3_C6', 'V3_C9': 'g_V3_C9'}
# 2026-10-15 사용자: 말이 느림 → 완성본 전체 1.25배속(음높이 유지 atempo). 세그먼트는 원속, 마지막 이어붙이기에서만 적용.
SPEED = 1.25
FINAL_NAME = {'V1': 'V1_PrimePrimer_AI라이브_v2.mp4', 'V2': 'V2_RomanticBlushLipCheek_AI라이브_v2.mp4', 'V3': 'V3_CleanItZero_AI라이브_v2.mp4'}
# 자막 표기: 발음 표기 → 숫자
CAP_SUB = [(r'\boh-two\b', '02'), (r'\boh-four\b', '04'), (r'\boh-five\b', '05'), (r'\boh-seven\b', '07'), (r'\boh-eight\b', '08'), (r'\boh-nine\b', '09'),
           (r'\btwelve\b', '12'), (r'\bthirteen\b', '13'), (r'\bfourteen\b', '14'), (r'\bseventeen\b', '17'), (r'\beighteen\b', '18'),
           (r'(?<=Shade )twenty\b', '20'), (r'\bfifty percent\b', '50%'), (r'\btwenty centimeters\b', '20 cm')]


def base_id(sid):
    return re.sub(r'_\d+$', '', sid) if re.search(r'_(\d)$', sid) else sid


def run(args):
    p = subprocess.run([FF, '-nostdin', '-v', 'error', '-y', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode:
        raise RuntimeError(p.stderr[-2000:])


def dur(p):
    return float(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout.strip())


def caption_text(s):
    for a, b in CAP_SUB:
        s = re.sub(a, b, s)
    return s


def chunks(text, n=40):
    """문장(. ! ? … —) 단위로 먼저 나누고, n자를 넘는 문장만 단어 경계에서 고르게 나눈다. 짧은 문장끼리는 n자 안에서 합친다."""
    sents = [x.strip() for x in re.split(r'(?<=[.!?…—])\s+', text) if x.strip()]
    out = []
    for snt in sents:
        if len(snt) <= n:
            if out and len(out[-1]) + 1 + len(snt) <= n and len(snt) < 16:
                out[-1] += ' ' + snt
            else:
                out.append(snt)
            continue
        words = snt.split(); k = math.ceil(len(snt) / n)
        target = len(snt) / k; cur = ''
        for w in words:
            if cur and len(cur) + 1 + len(w) > target + 6 and len(out) < 99:
                out.append(cur); cur = w
            else:
                cur = (cur + ' ' + w).strip()
        out.append(cur)
    return out


# 2026-10-15 사용자: 자막 시안 B(외곽선·상자 없음, 숏폼형) 채택 + 글자 크기는 기존 42px의 15% 축소 → 36px(42×0.85=35.7)
CAP_FONT = str(ROOT / '5_에셋' / 'banner' / 'fonts' / 'Pretendard-ExtraBold.otf')
CAP_SIZE, CAP_LH, CAP_STROKE, CAP_INK = 36, 47, 3, (43, 31, 37)  # 줄 간격·테두리 = 시안 B(48/62px, 3px) 비율 유지, 테두리색 #2B1F25


def caption_png(text, path):
    f = ImageFont.truetype(CAP_FONT, CAP_SIZE)
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if f.getlength(t) > 960 and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    lh = CAP_LH; y0 = 1458 - lh * len(lines) - 14
    # 그림자: 진한 색 40%, 아래 5px, 흐림 (시안 B의 0 5px 14px rgba(0,0,0,.4))
    sh = Image.new('RGBA', (W, HH)); ds = ImageDraw.Draw(sh)
    for i, l in enumerate(lines):
        ds.text((W / 2, y0 + i * lh + lh / 2 + 5), l, font=f, fill=(0, 0, 0, 102), anchor='mm', stroke_width=CAP_STROKE, stroke_fill=(0, 0, 0, 102))
    im = sh.filter(ImageFilter.GaussianBlur(7)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + i * lh + lh / 2), l, font=f, fill='white', anchor='mm', stroke_width=CAP_STROKE, stroke_fill=CAP_INK)
    im.save(path)


def speech_span(audio, total):
    p = subprocess.run([FF, '-nostdin', '-i', str(audio), '-af', 'silencedetect=n=-38dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', p)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', p)]
    a, b = 0.0, total
    if en and st and st[0] < 0.05: a = en[0]
    if st and (not en or st[-1] > en[-1]): b = st[-1]
    return a, max(b, a + 0.5)


def flashes(clip):
    """프레임 밝기(YAVG)가 앞뒤 9프레임 중앙값보다 2.0 넘게 튀는 구간 → [(first,last)]"""
    o = subprocess.run([FF, '-nostdin', '-i', str(clip), '-vf', 'scale=180:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG', '-an', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    y = [float(v) for v in re.findall(r'YAVG=([\d.]+)', o)]
    bad = [i for i in range(len(y)) if y[i] - sorted(y[max(0, i - 4):i + 5])[len(y[max(0, i - 4):i + 5]) // 2] > 2.0 and i > 0]
    groups = []
    for i in bad:
        if groups and i <= groups[-1][1] + 1: groups[-1][1] = i
        else: groups.append([i, i])
    return [(a, b, round(max(y[a:b + 1]) - y[a - 1], 1)) for a, b in groups if b - a < 8]


def assets():
    plate = SEG / '_plate.png'; mask = SEG / '_hostmask.png'
    if not plate.exists():
        SEG.mkdir(parents=True, exist_ok=True)
        m = Image.open(MASTER).convert('RGB').resize((W, HH))
        band = m.crop((0, 0, W, 170)).resize((W, SHIFT + 200)).filter(ImageFilter.GaussianBlur(18))
        pl = m.copy(); pl.paste(band, (0, 0)); pl.save(plate)
        mk = Image.new('L', (W, HH), 255); d = ImageDraw.Draw(mk)
        for y in range(160): d.line(((0, y), (W, y)), fill=int(255 * y / 160))
        mk.save(mask)
    return plate, mask


def d_plate():
    p = SEG / '_dplate.png'
    if not p.exists():
        im = Image.new('RGB', (W, HH)); d = ImageDraw.Draw(im)
        for y in range(HH):
            k = min(1, y / (HH * .45)); d.line(((0, y), (W, y)), fill=tuple(int(a + (b - a) * k) for a, b in ((0xFB, 0xF8), (0xE3, 0xED), (0xEC, 0xF1))))
        logo = Image.open(ROOT / '5_에셋' / 'logo' / 'BANILACO_logo_white.png'); logo = logo.resize((round(logo.width * 24 / logo.height), 24))
        pw = logo.width + 68; x0 = (W - pw) // 2  # G 화면과 같은 위치·크기의 로고 알약
        d.rounded_rectangle((x0, 300, x0 + pw, 356), 28, fill=(0xE9, 0x57, 0x9A)); im.paste(logo, (x0 + 34, 316), logo)
        im.save(p)
    return p


def rounded_mask(w, h, r, path):
    if not path.exists():
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); m.save(path)
    return path


def demo_inputs(items, total):
    """시연 소스를 이어 붙여 total 초를 채울 때까지 반복 → ffmpeg 입력 인자 목록과 (index, in, len, cx)"""
    seq, t, k = [], 0.0, 0
    while t < total + 0.1:
        f, ss, cx = items[k % len(items)][:3]
        L = max(0.5, dur(f) - ss)
        seq.append((f, ss, min(L, total - t + 0.2), cx)); t += seq[-1][2]; k += 1
        if k > 40: break
    return seq


def seg_filter_demo(seq, base_idx, w, h, cover=True):
    """seq 각 소스를 w×h로 맞춰 concat → [demo]"""
    parts = []
    for j, (f, ss, L, cx) in enumerate(seq):
        i = base_idx + j
        if cover:
            sc = f"scale='if(gt(a,{w}/{h}),-2,{w})':'if(gt(a,{w}/{h}),{h},-2)',crop={w}:{h}:'(iw-{w})*{cx}':'(ih-{h})/2'"
        else:
            sc = f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black@0'
        parts.append(f'[{i}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,fps={FPS},{sc},setsar=1,format=yuva420p[d{j}]')
    parts.append(''.join(f'[d{j}]' for j in range(len(seq))) + f'concat=n={len(seq)}:v=1:a=0[demo]')
    return ';'.join(parts)


def build_segment(v, idx, s, out_dir, log):
    sid, kind, typ = s['id'], s['kind'], s.get('type')
    b = base_id(sid)
    plate, hmask = assets()
    tmp = out_dir / '_tmp'; tmp.mkdir(exist_ok=True)
    out = out_dir / f'{idx:02d}_{sid}.mp4'
    inputs, filt, info = [], [], {'id': sid, 'kind': kind}
    if kind == 'h3':
        cut = next((QA / sid).glob('*_cut.mp4'), None) if (QA / sid).exists() else None
        src = cut or (H3 / sid / 'native.mp4')
        T = dur(src); audio_src = src
        fl = flashes(src)
        info.update(source=str(src.relative_to(ROOT)), edited_cut=bool(cut), flashes_replaced=fl)
        mode = 'G+H' if b in GH else ('S' if (sid in DEMO or sid in SPLIT) else ('H+G' if b in CARD or sid in CARD else 'H'))
    else:
        audio_src = VO / f'{sid}.wav'; T = dur(audio_src) + 0.35
        mode = 'D' if sid in DEMO else 'G'
        info.update(source=str(audio_src.relative_to(ROOT)))
    info['mode'] = mode; info['seconds'] = round(T, 2)
    # 입력 0: 바탕
    if mode in ('G', 'G+H'):
        g = VO_MODE.get(sid) or GH.get(b) or f'g_V2_L5_{sid[-2:]}'
        inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(GFX / f'{g}.png')]
        filt.append(f'[0:v]fps={FPS},scale={W}:{HH},format=yuv420p[bg]'); info['graphic'] = g
        last = 'bg'
    elif mode == 'D':
        seq = demo_inputs(DEMO[sid], T)
        for f, ss, L, cx in seq: inputs += ['-ss', f'{ss:.2f}', '-t', f'{L + 0.2:.3f}', '-i', str(f)]
        # 바탕: G 화면과 같은 핑크 판 / 전경: 34~70% 안에 원본 비율 그대로(크롭 없음)
        inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(d_plate())]
        filt.append(seg_filter_demo(seq, 0, 1040, 680, cover=False))
        filt.append(f'[{len(seq)}:v]fps={FPS},format=yuva420p[dp];[dp][demo]overlay=20:655,format=yuv420p[bg]')
        info['demo'] = [(str(f.relative_to(ROOT)), ss, round(L, 2)) for f, ss, L, cx in seq]
        last = 'bg'
    else:
        # 호스트 화면
        inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(plate), '-i', str(src), '-loop', '1', '-t', f'{T:.3f}', '-i', str(hmask)]
        if fl:  # freezeframes 는 교체 프레임을 두 번째 입력에서 가져온다 → 원본을 분기해 같은 클립을 넣음
            filt.append(f'[1:v]split={len(fl) + 1}' + ''.join(f'[r{j}]' for j in range(len(fl) + 1)))
            cur = 'r0'
            for j, (a, bb, _) in enumerate(fl):
                filt.append(f'[{cur}][r{j + 1}]freezeframes=first={a}:last={bb}:replace={a - 1}[f{j}]'); cur = f'f{j}'
        else:
            cur = '1:v'
        filt.append(f'[{cur}]fps={FPS},scale={W}:{HH},format=yuva420p[h0]')
        filt.append(f'[2:v]fps={FPS},scale={W}:{HH},format=gray[hm]')
        filt.append('[h0][hm]alphamerge[h1]')
        filt.append(f'[0:v]fps={FPS},scale={W}:{HH},format=yuva420p[pl]')
        filt.append(f'[pl][h1]overlay=0:{SHIFT}:shortest=1,format=yuv420p[bg]')
        last = 'bg'
        if mode == 'S':
            n0 = 3
            if sid in SPLIT:
                a, bsrc = SPLIT[sid]
                inputs += ['-ss', '0', '-i', str(a[0]), '-ss', '0', '-i', str(bsrc[0])]
                mk = rounded_mask(360, 408, 24, SEG / '_win360x408.png')
                inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(mk)]
                for j, it in enumerate((a, bsrc)):
                    filt.append(f"[{n0 + j}:v]fps={FPS},loop=-1:size=32767,trim=0:{T:.3f},setpts=PTS-STARTPTS,scale=-2:206,crop=360:200:'(iw-360)*{it[2]}':3,setsar=1[s{j}]")
                filt.append(f'[s0]pad=360:408:0:0:white[s0p];[s0p][s1]overlay=0:208[sw]')
                filt.append(f'[{n0 + 2}:v]fps={FPS},format=gray[wm];[sw]format=yuva420p[swa];[swa][wm]alphamerge[win]')
                filt.append(f'[{last}]drawbox=x=14:y=874:w=372:h=420:color=white@0.95:t=fill[bgx];[bgx][win]overlay=20:880:shortest=1[bgw]'); last = 'bgw'
                lab = tmp / f'{sid}_lab.png'
                im = Image.new('RGBA', (W, HH)); d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, 24)
                for y, tx in ((892, 'BEFORE'), (892 + 208, 'AFTER')):
                    d.rounded_rectangle((32, y, 32 + f.getlength(tx) + 24, y + 36), 12, fill=(233, 87, 154, 235)); d.text((44, y + 18), tx, font=f, fill='white', anchor='lm')
                im.save(lab); inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(lab)]
                filt.append(f'[{n0 + 3}:v]fps={FPS},format=rgba[lab];[{last}][lab]overlay=0:0[bgl]'); last = 'bgl'
                info['demo'] = [str(a[0].relative_to(ROOT)), str(bsrc[0].relative_to(ROOT))]
            else:
                seq = demo_inputs(DEMO[sid], T)
                for f, ss, L, cx in seq: inputs += ['-ss', f'{ss:.2f}', '-t', f'{L + 0.2:.3f}', '-i', str(f)]
                mk = rounded_mask(360, 360, 24, SEG / '_win360.png')
                inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(mk)]
                filt.append(seg_filter_demo(seq, n0, 360, 360, cover=True))
                filt.append(f'[{n0 + len(seq)}:v]fps={FPS},format=gray[wm];[demo][wm]alphamerge[win]')
                filt.append(f'[{last}]drawbox=x=14:y=874:w=372:h=372:color=white@0.95:t=fill[bgx];[bgx][win]overlay=20:880:shortest=1[bgw]'); last = 'bgw'
                info['demo'] = [(str(f.relative_to(ROOT)), ss, round(L, 2)) for f, ss, L, cx in seq]
    # 오버레이 (투명 PNG)
    ovs = []
    if mode in ('H', 'H+G', 'S'):
        ovs.append(GFX / f'overlay_headline_{v}.png')
    if mode == 'H+G':
        c = CARD.get(sid) or CARD.get(b); ovs.append(GFX / f'{c}.png'); info['card'] = c
    if mode == 'D' and sid in D_OVERLAY:
        ovs.append(GFX / f'{D_OVERLAY[sid]}.png')
    ovs.append(GFX / 'overlay_disclosure.png')
    # 자막
    a0, a1 = speech_span(audio_src, T if kind == 'h3' else T - 0.35)
    parts = chunks(caption_text(s['text']))
    tot = sum(len(p) for p in parts); t0 = a0; caps = []
    for k, ptxt in enumerate(parts):
        t1 = a0 + (a1 - a0) * sum(len(p) for p in parts[:k + 1]) / tot
        cp = tmp / f'{sid}_cap{k}.png'; caption_png(ptxt, cp)
        caps.append((cp, t0, t1 if k < len(parts) - 1 else max(t1, a1) + 0.3, ptxt)); t0 = t1
    info['captions'] = [(round(x, 2), round(y, 2), tx) for _, x, y, tx in caps]
    base_n = sum(1 for a in inputs if a == '-i')
    for j, p in enumerate(ovs):
        inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(p)]
        filt.append(f'[{base_n + j}:v]fps={FPS},format=rgba[o{j}];[{last}][o{j}]overlay=0:0[l{j}]'); last = f'l{j}'
    base_n += len(ovs)
    for j, (p, x, y, _) in enumerate(caps):
        inputs += ['-loop', '1', '-t', f'{T:.3f}', '-i', str(p)]
        filt.append(f"[{base_n + j}:v]fps={FPS},format=rgba[c{j}];[{last}][c{j}]overlay=0:0:enable='between(t,{x:.2f},{y:.2f})'[k{j}]"); last = f'k{j}'
    base_n += len(caps)
    # 오디오
    inputs += ['-i', str(audio_src)]
    filt.append(f'[{base_n}:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={T:.3f},atrim=0:{T:.3f},'
                f'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={max(0, T - 0.06):.3f}:d=0.06[aout]')
    filt.append(f'[{last}]trim=0:{T:.3f},setpts=PTS-STARTPTS,format=yuv420p[vout]')
    run([*inputs, '-filter_complex', ';'.join(filt), '-map', '[vout]', '-map', '[aout]', '-t', f'{T:.3f}', *ENC, str(out)])
    info['out'] = str(out.relative_to(ROOT)); info['out_seconds'] = round(dur(out), 2)
    log.append(info)
    return out


def ready(s):
    if s['kind'] != 'h3':
        return True
    r = H3 / s['id'] / 'run.json'
    return r.exists() and json.loads(r.read_text(encoding='utf-8')).get('generation_completed') and (H3 / s['id'] / 'native.mp4').exists()


def build_video(v, redo=()):
    """세그먼트 캐시: 같은 세그먼트 파일이 있고 그 기록(edit_log)의 소스가 지금 소스와 같으면 다시 만들지 않는다.
    아직 생성이 끝나지 않은 클립이 있으면 그 줄만 건너뛰고 최종 이어붙이기는 하지 않는다."""
    shots = json.loads((ROOT / '5_에셋/production/shotlist_v3.json').read_text(encoding='utf-8'))
    order = [s for s in shots if s['id'].startswith('COMMON_OC')] + [s for s in shots if s['video'] == v] + [s for s in shots if s['id'].startswith('COMMON_EC')]
    out_dir = SEG / v; out_dir.mkdir(parents=True, exist_ok=True)
    lp = out_dir / 'edit_log.json'
    prev = {x['id']: x for x in json.loads(lp.read_text(encoding='utf-8'))} if lp.exists() else {}
    log, segs, missing = [], [], []
    for i, s in enumerate(order):
        if not ready(s):
            missing.append(s['id']); print(v, i, s['id'], 'WAIT (생성 미완료)', flush=True); continue
        out = out_dir / f'{i:02d}_{s["id"]}.mp4'
        old = prev.get(s['id'])
        if old and out.exists() and s['id'] not in redo and 'all' not in redo and old.get('source') == current_source(s):
            log.append(old); segs.append(out); continue
        segs.append(build_segment(v, i, s, out_dir, log)); print(v, i, s['id'], log[-1]['mode'], log[-1]['out_seconds'], flush=True)
    lp.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding='utf-8')
    for p in (out_dir / '_tmp').iterdir(): p.unlink()
    if missing:
        print(v, 'NOT CONCATENATED — 생성 미완료', missing); return None
    lst = out_dir / 'concat.txt'
    lst.write_text(''.join(f"file '{p.as_posix()}'\n" for p in segs), encoding='utf-8')
    FINAL.mkdir(exist_ok=True)
    final = FINAL / FINAL_NAME[v]
    # 배속은 세그먼트마다 따로: 영상 setpts, 오디오 atempo 후 그 세그먼트 영상 길이에 맞춰 apad/trim.
    # (전체에 atempo 한 번 → 오디오가 약 0.85초 짧아짐 실측. 세그먼트 단위면 어긋남이 다음 세그먼트로 넘어가지 않음)
    fast_dir = out_dir / '_fast'; fast_dir.mkdir(exist_ok=True)
    fast = []
    for p in segs:
        T = dur(p) / SPEED; q = fast_dir / p.name
        run(['-i', str(p), '-filter_complex', f'[0:v]setpts=PTS/{SPEED},fps={FPS}[v];[0:a]atempo={SPEED},apad,atrim=0:{T:.3f}[a]',
             '-map', '[v]', '-map', '[a]', '-t', f'{T:.3f}', *ENC, str(q)])
        fast.append(q)
    ins = [a for q in fast for a in ('-i', str(q))]
    fc = ''.join(f'[{k}:v][{k}:a]' for k in range(len(fast))) + f'concat=n={len(fast)}:v=1:a=1[v][a]'
    run([*ins, '-filter_complex', fc, '-map', '[v]', '-map', '[a]', *ENC, str(final)])
    (SEG / 'final_meta.json').write_text(json.dumps({'speed': SPEED, 'files': FINAL_NAME}, ensure_ascii=False, indent=1), encoding='utf-8')
    print('FINAL', final, round(dur(final), 1), 's')
    return final


def current_source(s):
    if s['kind'] != 'h3':
        return str((VO / f"{s['id']}.wav").relative_to(ROOT))
    cut = next((QA / s['id']).glob('*_cut.mp4'), None) if (QA / s['id']).exists() else None
    return str((cut or (H3 / s['id'] / 'native.mp4')).relative_to(ROOT))


if __name__ == '__main__':
    redo = sys.argv[sys.argv.index('--redo') + 1].split(',') if '--redo' in sys.argv else ()
    for v in (sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'V1,V2,V3').split(','):
        build_video(v, redo)
