"""MiniMax H3 official API runner: persisted submissions, native AV, no auto retry.

Only submit performs a billable POST. prepare is local; connection/query/resume are GET.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://api.minimax.io"
SCENES = ("home", "studio01", "studio02", "studio03", "studio04")
FFMPEG_DIRECTORY = Path(os.environ.get("FFMPEG_DIR", "C:/ProgramData/chocolatey/lib/ffmpeg/tools/ffmpeg/bin"))


class SubmissionUnknown(RuntimeError):
    """Request may have been accepted; blindly retrying could bill twice."""


class APIError(RuntimeError):
    def __init__(self, status, detail):
        self.http_status = int(status)
        self.detail = detail
        super().__init__(f"MiniMax API HTTP {self.http_status}: {json.dumps(detail, ensure_ascii=False)}")


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def redact(value, secret=None):
    if isinstance(value, dict):
        return {
            name: "[REDACTED]" if name.lower() in {"authorization", "api_key", "apikey", "access_token", "token"}
            else redact(item, secret)
            for name, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item, secret) for item in value]
    if isinstance(value, str):
        result = value.replace(secret, "[REDACTED]") if secret else value
        # Signed CDN URLs are capabilities: their query strings must not reach receipts/logs.
        result = re.sub(r"https?://[^\s\"<>]+", lambda match: match.group(0).split("?", 1)[0].split("#", 1)[0], result)
        result = re.sub(r"data:(image|audio|video)/[^;]+;base64,[A-Za-z0-9+/=]+", "[MEDIA DATA URI]", result)
        return result
    return value


def key_from_file(path):
    path = Path(path)
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\s*(?:export\s+)?MINIMAX_API_KEY\s*=\s*(.*?)\s*$", line)
        if not match:
            continue
        result = match.group(1)
        if len(result) >= 2 and result[0] == result[-1] and result[0] in "\"'":
            result = result[1:-1]
        else:
            result = result.split(" #", 1)[0].strip()
        if result and result.lower() not in {"your_api_key", "your-minimax-api-key", "replace_me"}:
            return result
    return None


def credential(path):
    value = os.environ.get("MINIMAX_API_KEY", "").strip()
    return value or key_from_file(path)


class NoAPIAuthRedirect(urllib.request.HTTPRedirectHandler):
    """Do not forward API Authorization across an unexpected redirect."""
    def redirect_request(self, request, response, code, message, headers, newurl):
        raise urllib.error.HTTPError(request.full_url, code, "API redirect refused", headers, response)


def request_json(method, url, payload=None, key=None):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "api.minimax.io":
        raise ValueError("Authorization is restricted to https://api.minimax.io")
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json", "User-Agent": "Banila-POC-MiniMax-Official/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if key:
        headers["Authorization"] = "Bearer " + key
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    opener = urllib.request.build_opener(NoAPIAuthRedirect())
    try:
        with opener.open(request, timeout=180 if method == "POST" else 60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except ValueError:
            detail = {"message": raw[:1500]}
        raise APIError(error.code, redact(detail, key)) from None


def download_video(url, destination):
    """Separate unauthenticated CDN request; never forwards the MiniMax API key."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("Provider output must be an HTTPS URL without embedded credentials")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "Banila-POC-Media-Download/1.0"})
    # A fresh request has no Authorization and no API cookie jar.
    with urllib.request.urlopen(request, timeout=180) as response, partial.open("wb") as output:
        shutil.copyfileobj(response, output, length=1024 * 1024)
    if not partial.stat().st_size:
        raise ValueError("The provider returned an empty video")
    os.replace(partial, destination)
    return destination


def executable(name):
    env = os.environ.get(name.upper() + "_PATH")  # ailive_config 가 FFMPEG_PATH·FFPROBE_PATH 를 채움
    if env and Path(env).is_file():
        return env
    candidate = FFMPEG_DIRECTORY / (name + ".exe")
    if candidate.is_file():
        return str(candidate)
    value = shutil.which(name)
    if not value:
        raise FileNotFoundError(f"{name} is required for native AV verification")
    return value


def verify_media(path):
    path = Path(path).resolve()
    probe = subprocess.run([executable("ffprobe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8", check=True)
    data = json.loads(probe.stdout)
    video = next((item for item in data.get("streams", []) if item.get("codec_type") == "video"), None)
    audio = next((item for item in data.get("streams", []) if item.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise ValueError("H3 output must contain both native video and audio streams")
    decoded = subprocess.run([executable("ffmpeg"), "-v", "error", "-i", str(path), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8")
    if decoded.returncode or decoded.stderr.strip():
        raise ValueError("Full native AV decode failed: " + decoded.stderr[-1500:])
    return {
        "native_video_audio_present": True,
        "full_decode_passed": True,
        "duration_seconds": float(data["format"]["duration"]),
        "video": video,
        "audio": audio,
        "sha256": sha256_file(path),
        "file_bytes": path.stat().st_size,
        "verified_at": now(),
    }


class Runner:
    def __init__(self, root, v2=None, config_path=None):
        self.root = Path(root).resolve()
        self.config_path = Path(config_path or (self.root / "config.json")).resolve()
        self.config = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if not isinstance(self.config.get("jobs"), dict):
            raise ValueError("config.jobs must map scene names (home/studio01-04) to their input settings")

    def path(self, scene):
        if scene not in SCENES or scene not in self.config["jobs"]:
            raise ValueError("Unknown scene: " + str(scene))
        return self.root / scene / "run.json"

    def read(self, scene):
        path = self.path(scene)
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

    def save(self, scene, record):
        atomic_json(self.path(scene), record)

    def source(self, value):
        path = Path(value)
        return path.resolve() if path.is_absolute() else (self.config_path.parent / path).resolve()

    def payload(self, scene):
        self.path(scene)
        job = self.config["jobs"][scene]
        job_input = dict(job)
        if job.get("prompt_path"):
            source = json.loads(self.source(job["prompt_path"]).read_text(encoding="utf-8-sig"))
            job_input = {**source, **job}
        prompt = job_input.get("prompt")
        dialogue = job_input.get("dialogue", job_input.get("script"))
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 7000:
            raise ValueError("The prompt must be nonempty and at most 7000 characters")
        if not isinstance(dialogue, str) or not dialogue.strip() or dialogue not in prompt:
            raise ValueError("The exact dialogue must be preserved inside the prompt")
        anchor = self.source(job_input["anchor_path"])
        audio_value = job_input.get("reference_audio_path", self.config.get("reference_audio_path"))
        if not audio_value:
            raise ValueError("This voice-consistency experiment requires reference_audio_path")
        audio = self.source(audio_value)
        if not anchor.is_file() or not audio.is_file():
            raise FileNotFoundError("The owned image and shared reference audio must exist before submission")
        image_mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(anchor.suffix.lower())
        if not image_mime:
            raise ValueError("Unsupported anchor format")
        if anchor.stat().st_size > 30 * 1024 * 1024:
            raise ValueError("Anchor exceeds the official 30MB image limit")
        if audio.suffix.lower() != ".wav":
            raise ValueError("Use the prepared shared WAV reference for this experiment")
        with wave.open(str(audio), "rb") as stream:
            audio_duration = stream.getnframes() / stream.getframerate()
        if not 2 <= audio_duration <= 15:
            raise ValueError("Reference audio must be 2–15 seconds")
        payload = {
            "model": "MiniMax-H3", "resolution": "2K", "duration": 15, "ratio": "9:16",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": "data:" + image_mime + ";base64," + base64.b64encode(anchor.read_bytes()).decode("ascii")}, "role": "reference_image"},
                {"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64," + base64.b64encode(audio.read_bytes()).decode("ascii")}, "role": "reference_audio"},
            ],
        }
        payload_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(payload_bytes) > 64 * 1024 * 1024:
            raise ValueError("Request exceeds the official 64MB limit")
        inputs = {
            "anchor_path": str(anchor), "anchor_sha256": sha256_file(anchor),
            "reference_audio_path": str(audio), "reference_audio_sha256": sha256_file(audio),
            "reference_audio_duration_seconds": audio_duration,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "dialogue": dialogue, "prompt": prompt,
            "payload_sha256": hashlib.sha256(payload_bytes).hexdigest(), "payload_bytes": len(payload_bytes),
        }
        return payload, inputs

    def prepare(self, scene, credential_present=False):
        payload, inputs = self.payload(scene)
        previous = self.read(scene)
        if previous and (previous.get("task_id") or previous.get("generation_submitted")):
            return previous
        record = {
            "scene": scene, "provider": "MiniMax Open Platform", "route": "official_api",
            "endpoint": BASE_URL + "/v2/video_generation", "prepared_at": now(),
            "status": "prepared" if credential_present else "blocked_missing_credentials",
            "generation_submitted": False, "generation_accepted": False, "generation_completed": False,
            "task_id": None, "actual_billed_usd": None, "estimated_list_cost_usd": 1.95,
            "cost_basis": "2K output 15s × $0.13/s; one image and reference audio; list estimate, not invoice",
            "pricing_source": "https://platform.minimax.io/docs/pricing/overview",
            "requested_delivery": {"width": 1080, "height": 1920, "api_1080_selection_supported": False, "method": "downscale native 2K after generation"},
            "settings": {"model": payload["model"], "resolution": payload["resolution"], "duration": payload["duration"], "ratio": payload["ratio"], "dialogue": inputs["dialogue"], "native_audio": True},
            "inputs": inputs,
        }
        self.save(scene, record)
        return record

    def submit(self, scene, key, http=request_json, retry_rejected=False):
        if not key:
            raise ValueError("MINIMAX_API_KEY is missing; no request was submitted")
        record = self.read(scene) or self.prepare(scene, credential_present=True)
        if record.get("task_id"):
            return record
        previous_status = record.get("status")
        if previous_status in {"submission_unknown", "submitting"}:
            raise SubmissionUnknown("The previous POST may have been accepted; locate its task_id before continuing")
        if record.get("generation_submitted") and not (retry_rejected and previous_status == "rejected"):
            raise ValueError("This scene was already submitted; use resume rather than submit")
        payload, inputs = self.payload(scene)
        if inputs != record.get("inputs"):
            raise ValueError("Prepared inputs changed; refusing the paid submission")
        lock = self.path(scene).parent / "submission.lock"
        if retry_rejected and previous_status == "rejected":
            # Only a definitive HTTP 4xx rejection can enter this explicit correction path.
            if not 400 <= int(record.get("provider_http_status", 0)) < 500:
                raise SubmissionUnknown("Only a definitive HTTP 4xx rejection is retryable")
            lock.unlink(missing_ok=True)
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SubmissionUnknown("Submission lock exists; refusing a concurrent or repeated paid POST") from None
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps({"scene": scene, "created_at": now(), "process": os.getpid()}))
        record.update({"status": "submitting", "generation_submitted": True, "submitted_at": now(), "post_attempts": int(record.get("post_attempts", 0)) + 1})
        self.save(scene, record)  # Persist before touching the billable HTTP boundary.
        try:
            response = http("POST", BASE_URL + "/v2/video_generation", payload, key)
        except APIError as error:
            definitive = 400 <= error.http_status < 500
            record.update({"status": "rejected" if definitive else "submission_unknown", "provider_http_status": error.http_status, "provider_error": redact(error.detail, key), "last_checked_at": now()})
            self.save(scene, record)
            if not definitive:
                raise SubmissionUnknown("Provider HTTP 5xx may follow an accepted POST; do not retry blindly") from None
            raise
        except Exception as error:
            record.update({"status": "submission_unknown", "transport_error": redact(str(error), key), "last_checked_at": now()})
            self.save(scene, record)
            raise SubmissionUnknown("The POST outcome is unknown; no automatic resubmission is allowed") from None
        task_id = response.get("task_id") if isinstance(response, dict) else None
        record["submit_response"] = redact(response, key)
        if not isinstance(task_id, (str, int)) or not str(task_id).strip():
            record["status"] = "submission_unknown"
            self.save(scene, record)
            raise SubmissionUnknown("Provider response had no task_id; refusing a second paid POST")
        record.update({"task_id": str(task_id), "status": "submitted", "generation_accepted": True, "submission_acknowledged_at": now()})
        self.save(scene, record)
        return record

    def connection(self, key, http=request_json):
        if not key:
            raise ValueError("MINIMAX_API_KEY is missing")
        endpoint = BASE_URL + "/v2/query/video_generation?page_num=1&page_size=1&filter.model=MiniMax-H3"
        response = http("GET", endpoint, key=key)
        if not isinstance(response, dict) or not isinstance(response.get("items"), list) or not isinstance(response.get("total"), int):
            raise ValueError("GET did not return the official authenticated task-list schema")
        record = {"authenticated": True, "billable_generation_request": False, "verified_at": now(), "endpoint": BASE_URL + "/v2/query/video_generation", "task_count_last_7_days": response["total"]}
        atomic_json(self.root / "connection.json", record)
        return record

    def query(self, scene, key, http=request_json, downloader=download_video, verifier=verify_media):
        record = self.read(scene)
        if not record or not record.get("task_id"):
            raise ValueError("No persisted task_id; resume never submits a new task")
        if record.get("generation_completed"):
            media = Path(record["native_video_path"])
            if not media.is_file() or sha256_file(media) != record.get("output_sha256"):
                raise ValueError("Completed native media was changed or removed")
            return record
        if not key:
            raise ValueError("MINIMAX_API_KEY is missing")
        task_id = record["task_id"]
        response = http("GET", BASE_URL + "/v2/query/video_generation/" + urllib.parse.quote(task_id, safe=""), key=key)
        task = response.get("task") if isinstance(response, dict) else None
        if not isinstance(task, dict) or str(task.get("id", "")) != task_id:
            raise ValueError("Task response does not match the submitted task_id")
        status = task.get("status")
        if status not in {"queued", "running", "pending", "succeeded", "failed", "cancelled"}:
            raise ValueError("Unrecognized provider status: " + str(status))
        record.update({"status": status, "provider_status": status, "last_checked_at": now(), "query_response": redact(response, key)})
        if task.get("usage") is not None:
            record["provider_usage"] = redact(task["usage"], key)
        if status in {"failed", "cancelled"}:
            record["provider_error"] = redact(task.get("error", {}), key)
            self.save(scene, record)
            return record
        self.save(scene, record)
        if status == "succeeded":
            url = task.get("content", {}).get("url")
            if not isinstance(url, str) or not url:
                raise ValueError("Succeeded task has no content.url")
            destination = self.path(scene).parent / "native.mp4"
            downloader(url, destination)
            proof = verifier(destination)
            expected = float(record.get("settings", {}).get("duration", 15))  # 기본 15초(POC), 본생성은 클립별 4~15초
            if not expected - 1 <= proof["duration_seconds"] <= expected + 1:
                raise ValueError(f"Provider media duration is outside the requested {expected:g}s tolerance")
            atomic_json(destination.with_name("native_probe.json"), proof)
            completed_at = now()
            elapsed = (datetime.fromisoformat(completed_at) - datetime.fromisoformat(record["submitted_at"])).total_seconds()
            record.update({"status": "completed", "generation_completed": True, "completed_at": completed_at, "submit_to_completion_seconds": elapsed, "native_video_path": str(destination), "output_sha256": proof["sha256"], "native_probe_path": str(destination.with_name("native_probe.json")), "native_video_audio_present": True, "full_decode_passed": True})
            self.save(scene, record)
        return record

    def resume(self, scene, key, wait_seconds=0, poll_seconds=15):
        deadline = time.monotonic() + max(0, wait_seconds)
        while True:
            record = self.query(scene, key)
            if record["status"] in {"completed", "failed", "cancelled"} or time.monotonic() >= deadline:
                return record
            time.sleep(min(max(1, poll_seconds), 30, max(0, deadline - time.monotonic())))


def summary(record):
    fields = ("scene", "status", "task_id", "generation_submitted", "generation_completed", "estimated_list_cost_usd", "actual_billed_usd", "native_video_path", "submit_to_completion_seconds", "authenticated", "task_count_last_7_days")
    return {name: record[name] for name in fields if name in record}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--key-file", type=Path, default=Path(__file__).resolve().parents[1] / ".env")  # 저장소 루트 .env
    parser.add_argument("command", choices=("connection", "prepare", "submit", "resume"))
    parser.add_argument("--scene", choices=(*SCENES, "all"), default="all")
    parser.add_argument("--wait-seconds", type=float, default=0)
    parser.add_argument("--poll-seconds", type=float, default=15)
    parser.add_argument("--retry-rejected", action="store_true", help="Explicit correction after a definitive HTTP 4xx; never after a timeout")
    args = parser.parse_args(argv)
    key = credential(args.key_file)
    try:
        runner = Runner(args.config.parent, config_path=args.config)
        if args.command == "connection":
            result = runner.connection(key)
            print(json.dumps(summary(result), ensure_ascii=False))
            return 0
        scenes = SCENES if args.scene == "all" else (args.scene,)
        for scene in scenes:
            if args.command == "prepare":
                result = runner.prepare(scene, credential_present=bool(key))
            elif args.command == "submit":
                result = runner.submit(scene, key, retry_rejected=args.retry_rejected)
            else:
                result = runner.resume(scene, key, wait_seconds=args.wait_seconds, poll_seconds=args.poll_seconds)
            print(json.dumps(summary(result), ensure_ascii=False), flush=True)
        return 0
    except Exception as error:
        # Do not show a traceback containing credentials, full payloads or signed URLs.
        print(json.dumps({"error": type(error).__name__, "message": redact(str(error), key)}, ensure_ascii=False), file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
