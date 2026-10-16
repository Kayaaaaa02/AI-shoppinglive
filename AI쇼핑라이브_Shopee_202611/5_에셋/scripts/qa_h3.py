"""완료된 H3 클립 검수: ASR 대사 가드(guard.json) + 0·25·50·75%·끝 프레임 컨택트시트 → 4_테스트/h3_qa/<ID>/
python -X utf8 qa_h3.py ID[,ID..|all]
결과 요약: 4_테스트/h3_qa/qa_summary.json
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import os
import json, sys, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(os.environ.get('AILIVE_ROOT') or pathlib.Path(__file__).resolve().parents[2])  # 2026-10-16: 다른 프로젝트는 AILIVE_ROOT로 지정 (pipeline/)
H3 = ROOT / '3_소스클립' / 'H3'
QA = ROOT / '4_테스트' / 'h3_qa'
GUARD = ROOT / '5_에셋' / 'scripts' / 'asr_script_guard.py'
FFMPEG = cfg.FFMPEG
FONT = ImageFont.truetype(cfg.KO_FONT, 26)


def frames(clip, out, dur):
    tiles = []
    for t in [0.2] + [round(dur * k / 4, 1) for k in (1, 2, 3)] + [round(dur - 0.4, 1)]:
        f = out / f'f_{t:04.1f}.jpg'
        subprocess.run([FFMPEG, '-v', 'error', '-y', '-ss', str(t), '-i', str(clip), '-frames:v', '1', '-vf', 'scale=360:-2', str(f)], check=True)
        tiles.append((t, Image.open(f).convert('RGB')))
    w, h = tiles[0][1].size
    sheet = Image.new('RGB', (w * len(tiles), h + 40), 'white'); d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(tiles):
        sheet.paste(im, (i * w, 40)); d.text((i * w + 8, 4), f'{t:.1f}s', fill='black', font=FONT)
        (out / f'f_{t:04.1f}.jpg').unlink()
    sheet.save(out / 'contact.jpg', quality=88)


def main(arg):
    cfg = json.loads((H3 / 'config.json').read_text(encoding='utf-8'))
    ids = list(cfg['jobs']) if arg == 'all' else arg.split(',')
    summ_path = QA / 'qa_summary.json'
    summ = json.loads(summ_path.read_text(encoding='utf-8')) if summ_path.exists() else {}
    for sid in ids:
        run = H3 / sid / 'run.json'
        if not run.exists():
            continue
        rec = json.loads(run.read_text(encoding='utf-8'))
        if not rec.get('generation_completed'):
            continue
        out = QA / sid; out.mkdir(parents=True, exist_ok=True)
        if (out / 'contact.jpg').exists() and sid in summ:
            continue
        clip = H3 / sid / 'native.mp4'
        p = subprocess.run([sys.executable, '-X', 'utf8', str(GUARD), str(clip), '--script', rec['inputs']['dialogue'], '--out', str(out), '--apply'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        g = json.loads((out / 'guard.json').read_text(encoding='utf-8')) if (out / 'guard.json').exists() else {'verdict': 'guard-error', 'stderr': p.stderr[-500:]}
        frames(clip, out, float(g.get('duration_s') or 15))
        summ[sid] = {k: g.get(k) for k in ('verdict', 'script_coverage', 'confirmed_off_script', 'suspect_needs_listening', 'cut_total_s', 'keep_segments_s', 'duration_s') if k in g}
        if 'stderr' in g: summ[sid]['stderr'] = g['stderr']
        summ_path.write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding='utf-8')
        print(sid, summ[sid].get('verdict'), 'coverage', summ[sid].get('script_coverage'), flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
