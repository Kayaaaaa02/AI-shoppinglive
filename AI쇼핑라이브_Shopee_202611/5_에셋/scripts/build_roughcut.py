"""검토용 러프컷: 오프닝 → V1 → 엔딩을 대본(shotlist) 순서로 이어 붙인다. 합성 전이라 화면은 호스트만.
- H3 완료 클립: 편집본(*_cut.mp4)이 있으면 편집본, 없으면 원본
- V/O 줄: 마스터 프레임 정지화면 + V/O 음성 + "V/O · 시연 소스 자리" 라벨
- 아직 없는 H3 클립: 2초 회색 카드 + "미생성" 라벨
python -X utf8 build_roughcut.py   → 4_테스트/h3_preview/V1_roughcut.mp4 (+ _roughcut_index.json)
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import json, pathlib, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
H3 = ROOT / '3_소스클립' / 'H3'
QA = ROOT / '4_테스트' / 'h3_qa'
OUT = ROOT / '4_테스트' / 'h3_preview'
TMP = OUT / '_seg'
MASTER = ROOT / '5_에셋' / 'character_sheet' / 'R3' / 'R3_MF-01_9x16.png'
FFMPEG = cfg.FFMPEG
FFPROBE = cfg.FFPROBE
FONT = cfg.KO_FONT_BOLD
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24', '-pix_fmt', 'yuv420p', '-r', '24',
       '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '128k']
SCALE = 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1'


def card(path, title, body, base=None):
    im = (Image.open(base).convert('RGB').resize((1080, 1920)) if base else Image.new('RGB', (1080, 1920), (60, 60, 64)))
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 1380, 1080, 1920), fill=(0, 0, 0, 170))
    d.text((60, 1420), title, font=ImageFont.truetype(FONT, 54), fill='white')
    y = 1510
    for line in textwrap.wrap(body, 38)[:7]:
        d.text((60, y), line, font=ImageFont.truetype(FONT, 38), fill=(235, 235, 235)); y += 54
    im.save(path)


def dur(p):
    return float(subprocess.run([FFPROBE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True).stdout.strip())


def run(args):
    subprocess.run([FFMPEG, '-v', 'error', '-y', *args], check=True)


def main():
    shots = json.loads((ROOT / '5_에셋/production/shotlist_v3.json').read_text(encoding='utf-8'))
    order = [s for s in shots if s['id'].startswith('COMMON_OC')] + [s for s in shots if s['video'] == 'V1'] + \
            [s for s in shots if s['id'].startswith('COMMON_EC')]
    TMP.mkdir(parents=True, exist_ok=True)
    index, segs, t = [], [], 0.0
    for i, s in enumerate(order):
        seg = TMP / f'{i:02d}.mp4'
        sid = s['id']
        if s['kind'] == 'vo':
            png = TMP / f'{i:02d}.png'
            card(png, f'V/O · 시연 소스 자리 ({sid})', s['text'], MASTER)
            run(['-loop', '1', '-i', str(png), '-i', str(ROOT / '2_나레이션/vo' / f'{sid}.wav'),
                 '-af', 'apad=pad_dur=0.4', '-shortest', '-vf', SCALE, *ENC, str(seg)])
            kind = 'V/O (T2A)'
        else:
            run_json = H3 / sid / 'run.json'
            done = run_json.exists() and json.loads(run_json.read_text(encoding='utf-8')).get('generation_completed')
            cut = next((QA / sid).glob('*_cut.mp4'), None) if (QA / sid).exists() else None
            src = cut or (H3 / sid / 'native.mp4')
            if done and src.exists():
                run(['-i', str(src), '-vf', SCALE, *ENC, str(seg)])
                kind = 'H3 편집본' if cut else 'H3 원본'
            else:
                png = TMP / f'{i:02d}.png'
                card(png, f'미생성 · {sid}', s['text'])
                run(['-loop', '1', '-i', str(png), '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', '2',
                     '-vf', SCALE, *ENC, str(seg)])
                kind = '미생성(자리표시 2초)'
        d = dur(seg)
        index.append({'id': sid, 'kind': kind, 'start_s': round(t, 2), 'seconds': round(d, 2), 'text': s['text']})
        segs.append(seg); t += d
    lst = TMP / 'list.txt'
    lst.write_text(''.join(f"file '{p.as_posix()}'\n" for p in segs), encoding='utf-8')
    out = OUT / 'V1_roughcut.mp4'
    run(['-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', '-movflags', '+faststart', str(out)])
    (OUT / '_roughcut_index.json').write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
    for p in TMP.iterdir(): p.unlink()
    TMP.rmdir()
    print('ok', out, round(t, 1), 's', len(index), 'segments')


if __name__ == '__main__':
    main()
