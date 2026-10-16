# ComfyUI 없이 MiniMax H3를 생성하는 방법

확인일: **2026-10-06**. 공식 문서 조사이며 아래 대안의 설치·로컬 실행·생성·유료 API 요청은 하지 않았습니다.

**ComfyUI는 필수가 아닙니다.** 직접 Python 실행과 MiniMax 공식 API 모두 H3 영상과 음성을 함께 생성합니다.

| 경로 | 실제 생성 진입점 | 현재 PC 검증 상태 |
|---|---|---|
| Hugging Face Diffusers | `ModularPipeline`, `workflow="fl2va"` | 미실행; 메모리 구성 추가 검증 필요 |
| MiniMax 공식 hosted API | `POST https://api.minimax.io/v2/video_generation`, `model="MiniMax-H3"` | 미제출; API 키·계정 이용 권한·잔액 필요 |
| SGLang 자체 서버 | `sglang serve --model-variant fl2va`, `/v1/videos` | Windows RTX4080 경로 미검증 |
| vLLM-Omni 자체 서버 | `/v1/videos/sync` 또는 `/v1/videos` | 실험적 upstream 경로; 현재 PC 미검증 |

## 직접 Python 실행

[공식 Diffusers H3 문서](https://huggingface.co/docs/diffusers/main/en/api/pipelines/minimax_h3)는 `ModularPipeline`에서 텍스트·첫/마지막 프레임을 입력하고 `videos`, `audio`, `sampling_rate`를 반환하는 방식을 설명합니다. 음성은 영상과 같은 denoising에서 생성됩니다. 일반 `DiffusionPipeline`과 다른 진입점이며, 단일 workflow를 선택하면 다른 transformer 파티션을 불필요하게 받지 않습니다.

아래는 인터페이스 설명용 예시입니다. 메모리 최적화 구성과 의존성 준비를 생략했으며 실행한 코드는 아닙니다.

```python
pipe = ModularPipeline.from_pretrained("MiniMaxAI/MiniMax-H3", workflow="fl2va")
pipe.load_components(dtype=torch.bfloat16)
result = pipe(prompt=scene_and_dialogue, image=home_anchor, num_frames=124,
              output=["videos", "audio", "sampling_rate"])
encode_video(result["videos"][0], fps=24, output_path="h3.mp4",
             audio=result["audio"][0], audio_sample_rate=result["sampling_rate"])
```

현재 문서는 `main` 채널이며 source 설치를 안내합니다. 문서의 12–16GB GPU 예제는 INT8와 group offload, 작은 캔버스, VAE offload를 사용합니다. 예상 호스트 RAM 약75GB는 **그 구성의 수치**입니다. RTX4080 16GB·총 RAM63.7GiB에서 모든 H3 구현이 불가능하다는 근거가 아닙니다. 현재 가용 RAM과 추가 양자화·디스크 활용·단계별 언로드 구성은 별도 실행 검증이 필요합니다.

## ComfyUI와 Higgsfield를 거치지 않는 공식 API

[MiniMax 생성 문서](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)는 `model`, `content`, `resolution`, `duration`을 받습니다. 텍스트와 `image_url: {url: ...}, role: "first_frame"` 형태로 홈 앵커를 제출할 수 있습니다. H3는 768P·2K, 정수4–15초를 지원합니다. 반환된 `task_id`로 [조회 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)를 호출하고 성공 시 `task.content.url`의 MP4를 저장합니다. 공식 [H3 연구 설명](https://www.minimax.io/blog/minimax-h3)이 native 영상·스테레오 음성 공동 생성을 확인합니다. 호스팅 방식이므로 모델 로딩을 현재 PC의 GPU/RAM에 맡기지 않습니다.

## 자체 서버 대안

[MiniMax 자체 배포 문서](https://platform.minimax.io/docs/guides/local-deploy-h3)는 SGLang FL2VA 서비스와 영상·스테레오 음성이 포함된 MP4를 검증하는 절차를 제공합니다. Linux/Python3.12·8×B200은 문서의 고정 reference 구성이지 보편적 최소 사양이 아닙니다. vLLM-Omni도 동기/비동기 영상 서버를 제공하지만 문서는 experimental upstream recipe로 구분합니다. 둘 다 현재 Windows 머신에서 실행한 결과가 없습니다.

[vLLM-Omni 자체 H3 recipe](https://github.com/vllm-project/vllm-omni/blob/main/recipes/MiniMaxAI/MiniMax-H3.md)도 FL2VA 영상·음성 생성과 동기화 스테레오 오디오가 담긴 MP4 출력을 명시합니다. 진입점은 `vllm serve MiniMaxAI/MiniMax-H3 --omni --task-type fl2va`에 하드웨어별 옵션을 붙이는 형태입니다. 이 진입점의 존재는 현재 PC에서 해당 구성을 실행했다는 뜻이 아닙니다.

## HTML에 사용할 방법 설명

현재 작업이 리더가 설명한 HTTP/CLI 실행 경로라면 다음 내용을 사용할 수 있습니다. 실제 완료 결과는 리더가 확인해야 합니다.

> MiniMax Direct는 로컬 H3를 ComfyUI 엔진의 HTTP/CLI로 실행한 영상입니다. 브라우저의 노드를 직접 조작할 필요는 없습니다. ComfyUI 없이 실행하는 공식 Diffusers Python 경로와 MiniMax 공식 hosted API도 있으며, 두 대안은 이번 PC에서 실행한 비교 결과가 아닙니다.

ComfyUI는 생성 엔진과 서버 기능을 제공합니다. [공식 서버 API](https://docs.comfy.org/development/comfyui-server/comms_routes)의 `POST /prompt`, `GET /history/{prompt_id}`로 프로그램에서 실행할 수 있으며, [현재 소스](https://github.com/Comfy-Org/ComfyUI/blob/d49e888586dd8ae012c0667b33466b815fee07f7/main.py)도 브라우저 자동 실행을 별도 옵션으로 처리합니다. 따라서 화면을 통한 수작업 사용과 엔진 의존성은 구분해야 합니다.

Home type1·Showhost type2 비교표에는 실제 생성 영상만 완료로 표시하고, 이 문서의 미실행 대안을 생성 완료처럼 표시하지 않습니다. 발음·자연스러운 연기·립싱크 품질은 방법의 존재 여부와 별도로 실제 영상 검수가 필요합니다.
