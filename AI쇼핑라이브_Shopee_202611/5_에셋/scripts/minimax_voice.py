"""MiniMax 보이스: Voice Design(A-1) 1회 → T2A로 H3 reference 샘플·V/O 합성.
키는 저장소 루트 .env(ailive_config)에서 읽고 출력·로그하지 않는다.
python -X utf8 minimax_voice.py design            # voice_id 생성 (유료, 1회만 — 이미 있으면 거부)
python -X utf8 minimax_voice.py ref               # H3 reference_audio WAV (32k mono)
python -X utf8 minimax_voice.py vo <shotlist.json> # V/O 줄 전부 합성 (이미 있는 파일은 건너뜀)
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import os
import json, re, sys, pathlib, urllib.request, urllib.error, datetime, wave, io, subprocess

ROOT = pathlib.Path(os.environ.get('AILIVE_ROOT') or pathlib.Path(__file__).resolve().parents[2])  # 2026-10-16: 다른 프로젝트는 AILIVE_ROOT로 지정 (pipeline/)
VOICE = ROOT / '2_나레이션' / 'voice'
VO = ROOT / '2_나레이션' / 'vo'
VOICE.mkdir(parents=True, exist_ok=True); VO.mkdir(parents=True, exist_ok=True)
STATE = VOICE / 'voice_state.json'
KEYFILE = cfg.ENV_FILE  # 저장소 루트 .env 의 MINIMAX_API_KEY= 줄
FFMPEG = cfg.FFMPEG

PROMPT_A1 = ("Bright, youthful female voice in her early twenties, like a friendly K-pop idol hosting a live beauty show in English. "
             "Clear, neutral international English with crisp consonants, easy for non-native listeners. Warm, upbeat and confident, "
             "medium-high pitch, smooth and clean, not breathy, not childish, not exaggerated.")
PREVIEW = ("Hi everyone, welcome to BANILA CO Live! Today's deals are really good, so don't miss this chance. "
           "Scoop a little balm, massage it in, and watch it melt into oil.")
# H3 reference: 대본에 없는 중립 문장 (H3가 이 문장을 따라 말하지 않도록)
REF_TEXT = ("I always love these little moments with you. <#0.3#> Let's take it slow, <#0.2#> look closely, "
            "and have some fun together, okay? <#0.3#> I think you're going to like this one.")


def key():
    for line in KEYFILE.read_text(encoding='utf-8-sig').splitlines():
        m = re.match(r'^\s*(?:export\s+)?MINIMAX_API_KEY\s*=\s*(.*?)\s*$', line)
        if m:
            return m.group(1).strip('"\'')
    raise SystemExit('MINIMAX_API_KEY missing')


def post(path, body):
    req = urllib.request.Request('https://api.minimax.io' + path, data=json.dumps(body).encode('utf-8'), method='POST',
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key()})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code}: {e.read().decode("utf-8", "replace")[:500]}')
    br = data.get('base_resp', {})
    if br.get('status_code') != 0:
        raise SystemExit(f'API error {br}')
    return data


def state():
    return json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {}


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding='utf-8')


def design():
    s = state()
    if s.get('voice_id'):
        raise SystemExit('voice_id already exists: ' + s['voice_id'])
    d = post('/v1/voice_design', {'prompt': PROMPT_A1, 'preview_text': PREVIEW})
    raw = bytes.fromhex(d['trial_audio'])
    (VOICE / 'A1_design_preview.mp3').write_bytes(raw)
    s.update(candidate='A (A-1)', voice_id=d['voice_id'], prompt=PROMPT_A1, preview_text=PREVIEW,
             designed_at=datetime.datetime.now().isoformat(timespec='seconds'),
             retention_note='FAQ: voice_id kept permanently once used in T2A within 7 days (Voice Design applicability unconfirmed)')
    save_state(s)
    print('voice_id ok', len(raw), 'bytes preview')


def t2a(text, emotion='happy', speed=1.25, fmt='wav'):  # 2026-10-15 사용자: 0.95 → 1.25
    s = state()
    d = post('/v1/t2a_v2', {
        'model': 'speech-2.8-hd', 'text': text, 'stream': False, 'language_boost': 'English', 'output_format': 'hex',
        'voice_setting': {'voice_id': s['voice_id'], 'speed': speed, 'vol': 1, 'pitch': 0, 'emotion': emotion},
        'audio_setting': {'sample_rate': 32000, 'format': fmt, 'channel': 1}})
    return bytes.fromhex(d['data']['audio']), d.get('extra_info', {})


def to_wav32k(raw, out):
    # API wav 헤더가 비표준일 수 있어 ffmpeg로 정규화 (32k mono s16)
    p = subprocess.run([FFMPEG, '-v', 'error', '-y', '-i', 'pipe:0', '-ac', '1', '-ar', '32000', '-c:a', 'pcm_s16le', str(out)],
                       input=raw, capture_output=True)
    if p.returncode:
        raise SystemExit(p.stderr.decode()[-400:])
    with wave.open(str(out)) as w:
        return w.getnframes() / w.getframerate()


def ref():
    out = VOICE / 'host_reference.wav'
    if out.exists():
        print('exists', out); return
    raw, info = t2a(REF_TEXT)
    dur = to_wav32k(raw, out)
    s = state(); s.update(reference_wav=str(out), reference_text=REF_TEXT, reference_seconds=dur,
                          reference_made_at=datetime.datetime.now().isoformat(timespec='seconds'), reference_info=info)
    save_state(s)
    print('ref ok', round(dur, 2), 's')


def vo(shotlist):
    shots = json.loads(pathlib.Path(shotlist).read_text(encoding='utf-8'))
    log_path = VO / 'vo_log.json'
    log = json.loads(log_path.read_text(encoding='utf-8')) if log_path.exists() else {}
    for sh in shots:
        if sh['kind'] != 'vo':
            continue
        out = VO / f"{sh['id']}.wav"
        if out.exists():
            continue
        raw, info = t2a(sh['text'], emotion=sh.get('emotion', 'happy'))
        dur = to_wav32k(raw, out)
        log[sh['id']] = dict(text=sh['text'], seconds=round(dur, 2), emotion=sh.get('emotion', 'happy'),
                             usage_characters=info.get('usage_characters'))
        log_path.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding='utf-8')
        print('vo', sh['id'], round(dur, 2), flush=True)


if __name__ == '__main__':
    cmd = sys.argv[1]
    {'design': design, 'ref': ref}.get(cmd, lambda: vo(sys.argv[2]))()
