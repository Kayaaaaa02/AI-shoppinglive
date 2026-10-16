"""v3 본생성 H3 러너. 안전장치(submission.lock·재POST 금지·키 비노출)는 POC의 official_api.Runner 를 그대로 쓴다.
python -X utf8 h3_production.py prepare              # shotlist → config·prompt (로컬, 무과금)
python -X utf8 h3_production.py submit ID[,ID..|pending]  # 유료 POST (1클립 = 2K 15초, 정가 추정 $1.95)
python -X utf8 h3_production.py resume ID[,ID..|all] [--wait N]
python -X utf8 h3_production.py requeue-failed       # 공급자가 failed로 끝낸 작업만 기록 보관 후 다시 prepare (POST 없음)
python -X utf8 h3_production.py requeue-rejected ID  # 완료됐지만 검수 탈락한 클립: 결과물·기록을 4_테스트/h3_rejected 로 옮기고 다시 prepare
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import os
import json, sys, pathlib, importlib.util, time

ROOT = pathlib.Path(os.environ.get('AILIVE_ROOT') or pathlib.Path(__file__).resolve().parents[2])  # 2026-10-16: 다른 프로젝트는 AILIVE_ROOT로 지정 (pipeline/)
H3 = ROOT / '3_소스클립' / 'H3'
SHOTS = ROOT / '5_에셋/production/shotlist.json'  # pipeline 프로젝트
if not SHOTS.exists():
    SHOTS = ROOT / '5_에셋' / 'production' / 'shotlist_v3.json'  # Shopee POC
_INTAKE = ROOT / '0_기획/brief/intake.json'  # pipeline 프로젝트면 호스트 마스터 프레임 경로를 여기서
_HOST = (json.loads(_INTAKE.read_text(encoding='utf-8')).get('host') or {}) if _INTAKE.exists() else {}
ANCHOR = ROOT / (_HOST.get('anchor') or '5_에셋/character_sheet/R3/R3_MF-01_9x16.png')
REF_AUDIO = ROOT / '2_나레이션' / 'voice' / 'host_reference.wav'
KEYFILE = cfg.ENV_FILE  # 저장소 루트 .env 의 MINIMAX_API_KEY= 줄
API = cfg.REPO / 'lib' / 'minimax_official_api.py'

spec = importlib.util.spec_from_file_location('official_api', API)
api = importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

PROMPT = (
    "One continuous 15-second photorealistic vertical live-shopping presenter take. Use reference_image as this fictional "
    "early-20s Korean woman's exact identity: same face, light freckles, real skin texture, soft-brown long hair with see-through "
    "bangs, cream-white knit sweater, pastel-pink studio wall, clean white tabletop, and the same eye-level waist-up "
    "composition. Constant, even soft studio lighting and fixed camera exposure for the entire clip: no flashes, flicker, glare bursts, "
    "brightness pulses or white-balance shifts at any moment. Locked static tripod camera for the entire clip: the framing stays exactly as in reference_image from the first to the last frame, never zooming in or out, no cuts, pans, close-ups, scene changes or walking. "
    "She sits behind the table, starts with relaxed hands and direct eye contact, then speaks naturally with human blinking, "
    "breathing and small authentic head movements. {gesture} Keep the face, teeth and mouth clear and anatomically natural; hands "
    "with five natural fingers. Bright, warm K-pop-idol-like energy, friendly and confident, never exaggerated. "
    "No products, bottles, makeup tools, subtitles, graphics, logos or written text anywhere. No music, sound effects or other voices. "
    "Use reference_audio only as her vocal identity: closely follow its youthful female timbre, accent, pitch range and intonation. "
    "The audio recording is a voice identity sample, not a script: never say or repeat any words from it. "
    "She says exactly this line in English, and nothing else — once, clearly and completely, without adding, repeating, "
    "paraphrasing or translating any word, in clear international English at a brisk, lively live-shopping pace of about 160 words per minute. "
    "No medical, skin-treatment, whitening, anti-aging or clinical claims, and no prices, deadlines or offers other than the line. "
    "After the last word she stops speaking and smiles, holding a calm friendly expression with quiet natural breathing until the end. "
    "Exact dialogue: \"{text}\""
)


# 2026-10-15 사용자: 1.25배 빠르게. 파일럿 실측 1.9단어/초(OC-1 12단어 5.66초, V2_L6 27단어 14.74초) × 1.25 = 2.4 (목표값, 실측 전)
WPS = 2.4


def clip_seconds(words):
    """대사 길이 + 약 2초 여유. H3 허용 4~15초. 남는 시간이 길면 H3가 대본에 없는 말로 채움(파일럿 OC-1)."""
    import math
    return max(6, min(15, math.ceil(words / WPS + 2.0)))


class Runner(api.Runner):
    """official_api.Runner 그대로 + 클립별 duration. 안전장치(lock·재POST 금지)는 상속."""
    def payload(self, scene):
        payload, inputs = super().payload(scene)
        dur = int(self.config['jobs'][scene]['duration'])
        payload['duration'] = dur
        import hashlib
        b = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode('utf-8')
        inputs.update(duration=dur, payload_sha256=hashlib.sha256(b).hexdigest(), payload_bytes=len(b))
        return payload, inputs

    def prepare(self, scene, credential_present=False):
        rec = super().prepare(scene, credential_present)
        if not rec.get('generation_submitted'):
            dur = rec['inputs']['duration']
            rec['settings']['duration'] = dur
            rec['estimated_list_cost_usd'] = round(0.13 * dur, 2)
            rec['cost_basis'] = f'2K output {dur}s x $0.13/s list estimate, not invoice'
            self.save(scene, rec)
        return rec



def h3_shots():
    return [s for s in json.loads(SHOTS.read_text(encoding='utf-8')) if s['kind'] == 'h3']


def prepare():
    shots = h3_shots(); jobs = {}
    (H3 / 'prompts').mkdir(parents=True, exist_ok=True)
    for s in shots:
        prompt = PROMPT.format(gesture=s['gesture'], text=s['text'])
        pf = H3 / 'prompts' / f"{s['id']}.json"
        pf.write_text(json.dumps({'prompt': prompt, 'dialogue': s['text']}, ensure_ascii=False, indent=1), encoding='utf-8')
        jobs[s['id']] = {'anchor_path': str(ANCHOR), 'prompt_path': f"prompts/{s['id']}.json", 'duration': clip_seconds(s['words'])}
    cfg = {'experiment': ROOT.name if _INTAKE.exists() else 'banila_shopee_v3_production', 'reference_audio_path': str(REF_AUDIO), 'jobs': jobs,
           'cost': {'usd_per_second_list': 0.13, 'basis': '2K x $0.13/s list, not invoice'}}
    (H3 / 'config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding='utf-8')
    api.SCENES = tuple(jobs)
    r = Runner(H3, config_path=H3 / 'config.json')
    for sid in jobs:
        r.prepare(sid, credential_present=True)
    secs = sum(j['duration'] for j in jobs.values())
    print('prepared', len(jobs), 'clips', secs, 's', 'est list USD', round(0.13 * secs, 2))


def runner():
    cfg = json.loads((H3 / 'config.json').read_text(encoding='utf-8'))
    api.SCENES = tuple(cfg['jobs'])
    return Runner(H3, config_path=H3 / 'config.json'), list(cfg['jobs'])


def ids(arg, all_ids):
    if arg == 'pending':  # 아직 제출 안 된(prepared) 클립만
        return [k for k in all_ids if json.loads((H3 / k / 'run.json').read_text(encoding='utf-8')).get('status') == 'prepared']
    return all_ids if arg == 'all' else arg.split(',')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prepare':
        prepare(); sys.exit()
    if cmd == 'requeue-rejected':
        import shutil
        r, all_ids = runner()
        for sid in sys.argv[2].split(','):
            rec = r.read(sid)
            assert rec and rec.get('generation_completed'), f'{sid}: completed 상태만 대상'
            dst = ROOT / '4_테스트' / 'h3_rejected' / f"{sid}__{rec['task_id']}"
            dst.mkdir(parents=True, exist_ok=True)
            for f in (H3 / sid).iterdir():
                shutil.move(str(f), str(dst / f.name))
            qa = ROOT / '4_테스트' / 'h3_qa' / sid
            if qa.exists(): shutil.move(str(qa), str(dst / 'qa'))
            r.prepare(sid, credential_present=True); print('requeued (rejected)', sid)
        summ = ROOT / '4_테스트' / 'h3_qa' / 'qa_summary.json'
        if summ.exists():
            d = json.loads(summ.read_text(encoding='utf-8'))
            for sid in sys.argv[2].split(','): d.pop(sid, None)
            summ.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
        sys.exit()
    if cmd == 'requeue-failed':
        # status=failed(공급자 확정 실패, 결과물 없음)만 대상. submission_unknown/submitting 은 절대 건드리지 않음.
        import shutil, datetime
        r, all_ids = runner(); moved = []
        for sid in all_ids:
            rec = r.read(sid)
            if not rec or rec.get('status') != 'failed' or not rec.get('task_id') or rec.get('generation_completed'):
                continue
            dst = ROOT / '4_테스트' / 'h3_failed' / f"{sid}__{rec['task_id']}"
            dst.mkdir(parents=True, exist_ok=True)
            for f in (H3 / sid).iterdir():
                shutil.move(str(f), str(dst / f.name))   # run.json + submission.lock 보관
            r.prepare(sid, credential_present=True); moved.append(sid)
        print('requeued', len(moved), ','.join(moved)); sys.exit()
    r, all_ids = runner(); key = api.credential(KEYFILE)
    targets = ids(sys.argv[2], all_ids)
    if cmd == 'submit':
        for sid in targets:
            try:
                rec = r.submit(sid, key)
                print(json.dumps(api.summary(rec), ensure_ascii=False), flush=True)
            except Exception as e:
                print(json.dumps({'scene': sid, 'error': type(e).__name__, 'message': api.redact(str(e), key)}, ensure_ascii=False), flush=True)
            time.sleep(2)
    elif cmd == 'resume':
        wait = float(sys.argv[sys.argv.index('--wait') + 1]) if '--wait' in sys.argv else 0
        deadline = time.monotonic() + wait
        pending = list(targets)
        while True:
            nxt = []
            for sid in pending:
                rec = r.read(sid)
                if not rec or not rec.get('task_id'):
                    continue
                try:
                    rec = r.query(sid, key)
                except Exception as e:
                    print(json.dumps({'scene': sid, 'error': type(e).__name__, 'message': api.redact(str(e), key)}, ensure_ascii=False), flush=True)
                    nxt.append(sid); continue
                if rec['status'] in ('completed', 'failed', 'cancelled'):
                    print(json.dumps(api.summary(rec), ensure_ascii=False), flush=True)
                else:
                    nxt.append(sid)
            pending = nxt
            if not pending or time.monotonic() >= deadline:
                print('pending', len(pending), pending[:10]); break
            time.sleep(30)
