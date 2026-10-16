"""ASR 대본 가드 — 생성 클립이 대본에 없는 말을 했는지 검사하고, 있으면 잘라낼 구간을 낸다.

배경: POC studio04(2026-10-13)에서 MiniMax H3가 대사 중간(6.9–9.7초)에 대본에 없는
발화("BAAC… pylacety")를 넣었다. 립싱크 단계 없이 영상 모델이 음성까지 만드는 경로라
생성 직후 이 가드를 통과해야 편집 단계로 넘긴다.

사용:
  python -X utf8 asr_script_guard.py CLIP.mp4 --script "대사 원문" --out OUT_DIR [--apply]
  python -X utf8 asr_script_guard.py CLIP.mp4 --script-file line.txt --out OUT_DIR

출력 (OUT_DIR):
  guard.json        판정·이탈 구간·대본 커버리지·keep 구간(편집용 컷 리스트)
  transcript.<model>.json   모델별 단어 타임스탬프
  <clip>_cut.mp4    --apply 시, 이탈 구간을 뺀 편집본 (원본은 건드리지 않음)

판정 규칙 (임계값은 아래 상수, guard.json에도 기록):
  - 두 ASR 모델(base·small)을 모두 돌려 대본과 단어 정렬. 대본에 없는 단어 묶음 = 이탈 후보.
  - 오인식 허용: 대본 단어와 같은 자리의 1:1 치환이고 글자 유사도 >= SUB_SIM 이면 이탈로 보지 않음
    (예: small "balm" / base "bomb").
  - 확정 이탈(confirmed): 두 모델의 이탈 후보 구간이 겹치고, 그 구간 평균 음량이 SPEECH_DB 이상.
    한 모델만 잡은 구간은 suspect(사람 청취 필요)로만 표시.
  - 판정:
      pass        확정 이탈 0 + 대본 커버리지 >= COVERAGE_PASS
      cut-needed  확정 이탈 합계 <= 클립 길이 x MAX_CUT_RATIO + 커버리지 >= COVERAGE_PASS
                  (이탈만 잘라내면 대본이 온전히 남음 → keep 구간으로 편집)
      trim-tail   확정 이탈이 모두 대본 마지막 단어 이후(꼬리) + 커버리지 >= COVERAGE_PASS
                  → 길이와 무관하게 첫 꼬리 이탈 직전까지만 남김 (2026-10-14 추가: H3가 짧은 대사 뒤 빈 시간을 말로 채움)
      regenerate  커버리지 < COVERAGE_PASS (대본 단어가 빠짐) 또는 중간 이탈 합계 > 클립 길이 x MAX_CUT_RATIO
  - 겹치거나 MIN_KEEP 초 미만 간격으로 붙은 확정 이탈은 하나의 컷으로 합친다.
  - 커버리지 = 두 모델 중 높은 쪽의 '대본 단어 중 정렬된 비율'.
한계: ASR이 이탈을 대본 단어로 잘못 들으면 못 잡는다. suspect 구간과 최종본은 사람이 한 번 듣는다.
"""
import sys as _sys, pathlib as _pl  # 저장소 루트의 ailive_config(.env·도구 경로)를 찾는다
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / 'ailive_config.py').exists())))
import ailive_config as cfg  # noqa: E402
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile

FFMPEG = cfg.FFMPEG  # PATH의 ffmpeg는 동작하지 않는 스텁
MODELS = ("base", "small")
SUB_SIM = 0.5          # 1:1 치환을 오인식으로 볼 최소 글자 유사도 (0~1)
MERGE_GAP = 0.6        # 이탈 단어 사이 간격이 이 초 이하면 한 구간으로 묶음
PAD = 0.08             # 컷 앞뒤 여유 (초)
SPEECH_DB = -35.0      # 이 dB 이상이면 발화로 간주 (구간 평균 음량)
COVERAGE_PASS = 0.9    # 대본 단어 커버리지 하한
MAX_CUT_RATIO = 0.4    # 잘라내는 길이가 클립의 40%를 넘으면 재생성 (남는 화면이 너무 짧음)
MIN_KEEP = 1.0         # 두 이탈 사이 남는 조각이 이 초 미만이면 함께 잘라냄 (튀는 짧은 조각 방지)


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower().replace("’", "'"))


NUMS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
        "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90"}


def tokens_of(text):
    """단어 → 정규화 토큰. 하이픈 분리, 숫자 단어 → 숫자, 'oh/o/zero + 한 자리' → '0d', 'o5' → '05'.
    (대본 'oh-five' / ASR '05'·'O5'·'oh five' 를 같은 토큰으로 맞춤)"""
    raw = [norm(x) for x in re.split(r"[\s\-–—]+", text) if norm(x)]
    raw = [NUMS.get(t, t) for t in raw if t not in ("percent", "per", "cent")]  # "fifty percent" = ASR "50%"
    raw = ["0" + t[1] if re.fullmatch(r"o\d", t) else t for t in raw]
    out = []
    for t in raw:
        if out and out[-1] in ("oh", "o", "0") and re.fullmatch(r"\d", t):
            out[-1] = "0" + t
        else:
            out.append(t)
    return out


def extract_wav(clip, wav):
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)


def duration(clip):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", clip], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def mean_db(wav, s, e):
    r = subprocess.run([FFMPEG, "-hide_banner", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", wav, "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else None


def mean_db_cache(clip, s, e):
    return mean_db(clip, s, e)


def transcribe(wav, model_name):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(wav, language="en", word_timestamps=True, beam_size=5, initial_prompt=None,
                               condition_on_previous_text=False, vad_filter=False)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"word": w.word.strip(), "start": round(float(w.start), 2), "end": round(float(w.end), 2)})
    return words


def align(words, script_tokens):
    # 단어 하나가 여러 토큰이 될 수 있어(하이픈) 토큰 → 원래 단어 index 를 함께 둔다
    hs, keep = [], []
    for i, w in enumerate(words):
        for t in tokens_of(w["word"]):
            if keep and keep[-1] != i and hs and hs[-1] in ("oh", "o") and re.fullmatch(r"\d", t):
                hs[-1] = "0" + t; continue
            hs.append(t); keep.append(i)
    sm = difflib.SequenceMatcher(a=hs, b=script_tokens, autojunk=False)
    off, matched, last_end = [], 0, 0.0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            matched += i2 - i1
            last_end = max(last_end, words[keep[i2 - 1]]["end"])
        elif tag == "replace" and (i2 - i1) == (j2 - j1) and all(
                difflib.SequenceMatcher(a=hs[i1 + k], b=script_tokens[j1 + k]).ratio() >= SUB_SIM for k in range(i2 - i1)):
            matched += i2 - i1  # 오인식으로 간주
        elif tag in ("replace", "delete"):  # a=들은 단어: delete = 대본에 없는 말을 들음
            off.extend(keep[k] for k in range(i1, i2))
    spans = []
    for idx in sorted(set(off)):
        w = words[idx]
        if spans and w["start"] - spans[-1]["end"] <= MERGE_GAP:
            spans[-1]["end"] = w["end"]
            spans[-1]["heard"] += " " + w["word"]
        else:
            spans.append({"start": w["start"], "end": w["end"], "heard": w["word"]})
    coverage = matched / max(1, len(script_tokens))
    return spans, round(coverage, 3), last_end


def overlap(a, b):
    return max(0.0, min(a["end"], b["end"]) - max(a["start"], b["start"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--script")
    g.add_argument("--script-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--apply", action="store_true", help="이탈 구간을 뺀 편집본 mp4 작성")
    a = ap.parse_args()
    script = a.script if a.script else open(a.script_file, encoding="utf-8").read()
    tokens = tokens_of(script)
    os.makedirs(a.out, exist_ok=True)
    dur = duration(a.clip)

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        extract_wav(a.clip, wav)
        per = {}
        for m in MODELS:
            words = transcribe(wav, m)
            json.dump({"model": f"faster-whisper-{m}", "initial_prompt": None, "words": words},
                      open(os.path.join(a.out, f"transcript.{m}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            spans, cov, last_end = align(words, tokens)
            per[m] = {"text": " ".join(w["word"] for w in words), "coverage": cov, "off_script": spans, "script_end_s": last_end}

        confirmed, suspect = [], []
        base_sp, small_sp = per["base"]["off_script"], per["small"]["off_script"]
        for s in small_sp:
            hits = [b for b in base_sp if overlap(s, b) > 0]
            if hits:
                span = {"start": min([s["start"]] + [b["start"] for b in hits]), "end": max([s["end"]] + [b["end"] for b in hits]),
                        "heard_small": s["heard"], "heard_base": " / ".join(b["heard"] for b in hits)}
                span["mean_db"] = mean_db(wav, span["start"], span["end"])
                (confirmed if span["mean_db"] is not None and span["mean_db"] >= SPEECH_DB else suspect).append(span)
            else:
                suspect.append({"start": s["start"], "end": s["end"], "heard_small": s["heard"], "only": "small"})
        for b in base_sp:
            if not any(overlap(b, s) > 0 for s in small_sp):
                suspect.append({"start": b["start"], "end": b["end"], "heard_base": b["heard"], "only": "base"})

    merged = []
    for s in sorted(confirmed, key=lambda x: x["start"]):
        if merged and s["start"] - merged[-1]["end"] < MIN_KEEP:
            m = merged[-1]
            m["end"] = max(m["end"], s["end"])
            for k in ("heard_small", "heard_base"):
                if s.get(k) and s[k] not in m.get(k, ""):
                    m[k] = (m.get(k, "") + " | " + s[k]).strip(" |")
        else:
            merged.append(dict(s))
    for m in merged:
        m["start"], m["end"] = float(m["start"]), float(m["end"])
        m["mean_db"] = mean_db_cache(a.clip, m["start"], m["end"])
    confirmed = merged
    suspect = [{**x, "start": float(x["start"]), "end": float(x["end"])} for x in suspect]

    coverage = max(per[m]["coverage"] for m in MODELS)
    cut_total = round(sum(min(dur, s["end"] + PAD) - max(0.0, s["start"] - PAD) for s in confirmed), 2)
    # 대본을 다 말한 뒤(두 모델 중 늦은 쪽 마지막 대본 단어 이후)에만 이탈이 있으면 꼬리만 자르면 된다
    script_end = max(per[m]["script_end_s"] for m in MODELS)
    tail_only = bool(confirmed) and all(s["start"] >= script_end - 0.05 for s in confirmed)
    if coverage < COVERAGE_PASS:
        verdict = "regenerate"
    elif tail_only:
        verdict = "trim-tail"
        confirmed = [{**confirmed[0], "end": dur, "tail": True}]  # 첫 꼬리 이탈부터 끝까지 제거
        cut_total = round(dur - max(0.0, confirmed[0]["start"] - PAD), 2)
    elif cut_total > dur * MAX_CUT_RATIO:
        verdict = "regenerate"
    elif confirmed:
        verdict = "cut-needed"
    else:
        verdict = "pass"

    keep, t = [], 0.0
    for s in sorted(confirmed, key=lambda x: x["start"]):
        cs, ce = max(0.0, s["start"] - PAD), min(dur, s["end"] + PAD)
        if cs > t:
            keep.append([round(t, 2), round(cs, 2)])
        t = max(t, ce)
    if t < dur:
        keep.append([round(t, 2), round(dur, 2)])

    result = {
        "clip": os.path.abspath(a.clip), "duration_s": round(dur, 2), "script": script, "verdict": verdict,
        "script_coverage": coverage, "confirmed_off_script": confirmed, "suspect_needs_listening": suspect,
        "cut_total_s": cut_total, "keep_segments_s": keep, "script_end_s": script_end, "per_model": per,
        "thresholds": {"SUB_SIM": SUB_SIM, "MERGE_GAP": MERGE_GAP, "PAD": PAD, "SPEECH_DB": SPEECH_DB,
                       "COVERAGE_PASS": COVERAGE_PASS, "MAX_CUT_RATIO": MAX_CUT_RATIO, "MIN_KEEP": MIN_KEEP},
        "note": "ASR 기반 자동 판정. suspect 구간과 최종본은 사람이 청취 확인.",
    }

    if a.apply and verdict in ("cut-needed", "trim-tail"):
        out_mp4 = os.path.join(a.out, os.path.splitext(os.path.basename(a.clip))[0] + "_cut.mp4")
        parts, labels = [], []
        for i, (s, e) in enumerate(keep):
            parts.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[a{i}]")
            labels.append(f"[v{i}][a{i}]")
        fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", a.clip, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", out_mp4], check=True)
        result["cut_output"] = os.path.abspath(out_mp4)
        result["cut_output_duration_s"] = round(duration(out_mp4), 2)

    json.dump(result, open(os.path.join(a.out, "guard.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: result[k] for k in ("verdict", "script_coverage", "confirmed_off_script", "cut_total_s", "keep_segments_s")},
                     ensure_ascii=False))
    print("suspect:", [(s["start"], s["end"], s.get("only", "both")) for s in suspect])
    return 0


if __name__ == "__main__":
    sys.exit(main())
