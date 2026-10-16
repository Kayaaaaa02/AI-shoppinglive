# -*- coding: utf-8 -*-
"""저장소 공통 설정 — API 키·도구 경로를 저장소 루트 .env 한 곳에서 읽는다.

처음 import 될 때 .env 가 없으면 .env.example 을 복사해 자동으로 만든다.
이때 이 PC에 예전 키 파일이 있으면(아래 LEGACY) 값만 옮겨 채운다. 값은 화면·로그에 출력하지 않는다.
키를 직접 넣으려면 생성된 .env 를 열어 '=' 뒤에 붙여 넣는다. .env 는 .gitignore 로 저장소에 올라가지 않는다.

    python -X utf8 ailive_config.py        # .env 만들고 어떤 키가 비어 있는지 확인 (값은 출력 안 함)
"""
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent
ENV_FILE = REPO / '.env'
EXAMPLE = REPO / '.env.example'
# 이 저장소를 만든 PC에서 쓰던 키 파일 위치. 다른 PC에는 없으므로 그냥 건너뛴다.
LEGACY = [Path(r'D:\fnco_orca\fnco_seeding\.env'), REPO.parent / '.env.minimax.local']
KEYS = ('OPENAI_API_KEY', 'MINIMAX_API_KEY')


def _parse(path):
    out = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.replace('export ', '').strip()
        v = v.split(' #', 1)[0].strip().strip('"\'')
        out[k] = v
    return out


def ensure_env(verbose=True):
    """.env 가 없으면 만든다. 만들었으면 True."""
    if ENV_FILE.exists():
        return False
    text = EXAMPLE.read_text(encoding='utf-8') if EXAMPLE.exists() else ''.join(f'{k}=\n' for k in KEYS)
    found = {}
    for f in LEGACY:
        for k, v in _parse(f).items():
            if v and k not in found:
                found[k] = v
    for k, v in os.environ.items():
        if k in KEYS and v and k not in found:
            found[k] = v
    lines, filled = [], []
    for line in text.splitlines():
        k = line.split('=', 1)[0].strip()
        if '=' in line and not line.lstrip().startswith('#') and not line.split('=', 1)[1].strip() and found.get(k):
            line = f'{k}={found[k]}'
            filled.append(k)
        lines.append(line)
    ENV_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if verbose:
        print(f'[ailive] .env 생성: {ENV_FILE}')
        print(f'[ailive] 이 PC의 기존 키 파일에서 채운 항목: {", ".join(filled) or "없음"} (값은 출력하지 않음)')
    return True


ensure_env()
_ENV = _parse(ENV_FILE)
for _k, _v in _ENV.items():          # 하위 모듈(MiniMax official_api 등)이 os.environ 에서도 읽게
    if _v and not os.environ.get(_k):
        os.environ[_k] = _v


def get(name, default=None):
    return os.environ.get(name) or _ENV.get(name) or default


def require(name):
    v = get(name)
    if not v:
        raise SystemExit(f'{name} 이(가) 비어 있습니다 — {ENV_FILE} 에 값을 넣으세요 (README "API 키" 참고)')
    return v


def _works(path, name):
    """실제로 실행되는지 확인 (PATH에 동작하지 않는 스텁 ffmpeg가 있는 PC가 있음)."""
    import subprocess
    try:
        r = subprocess.run([path, '-version'], capture_output=True, text=True, timeout=15, stdin=subprocess.DEVNULL)
        return r.returncode == 0 and f'{name} version' in (r.stdout or '')
    except Exception:
        return False


def _tool(name, env):
    cands = [get(env), f'C:/ProgramData/chocolatey/bin/{name}.exe', shutil.which(name)]
    for c in cands:
        if c and Path(c).exists() and _works(c, name):
            return str(c)
    return name  # 마지막 수단: PATH


FFMPEG = _tool('ffmpeg', 'FFMPEG_PATH')
FFPROBE = _tool('ffprobe', 'FFPROBE_PATH')
os.environ.setdefault('FFMPEG_PATH', FFMPEG)     # lib/minimax_official_api.py 가 읽음
os.environ.setdefault('FFPROBE_PATH', FFPROBE)
# 라벨용 한글 글꼴(컨택트시트·러프컷). 없으면 저장소 Pretendard
_KO = [get('KO_FONT_PATH'), 'C:/Windows/Fonts/malgun.ttf', '/System/Library/Fonts/AppleSDGothicNeo.ttc',
       str(REPO / 'AI쇼핑라이브_Shopee_202611/5_에셋/banner/fonts/Pretendard-Medium.otf')]
KO_FONT = next((c for c in _KO if c and Path(c).exists()), _KO[-1])
KO_FONT_BOLD = next((c for c in [get('KO_FONT_BOLD_PATH'), 'C:/Windows/Fonts/malgunbd.ttf',
                                 str(REPO / 'AI쇼핑라이브_Shopee_202611/5_에셋/banner/fonts/Pretendard-Bold.otf')] if c and Path(c).exists()), KO_FONT)


def openai_client():
    from openai import OpenAI
    return OpenAI(api_key=require('OPENAI_API_KEY'), base_url=get('OPENAI_BASE_URL') or None)


if __name__ == '__main__':
    print('[ailive] .env:', ENV_FILE, '(있음)' if ENV_FILE.exists() else '(없음)')
    for k in ('OPENAI_API_KEY', 'OPENAI_BASE_URL', 'MINIMAX_API_KEY', 'SECONDARY_CONTENT_DIR'):
        print(f'  {k:24s}', '설정됨' if get(k) else '비어 있음')
    print('  ffmpeg :', FFMPEG)
    print('  ffprobe:', FFPROBE)
