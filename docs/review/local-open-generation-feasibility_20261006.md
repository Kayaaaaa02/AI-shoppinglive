# Higgsfield를 사용하지 않는 로컬 생성 경로 검토

검토일: 2026-10-06. 공식 저장소·모델 카드·배포 문서를 확인했다. 이 문서는 설치·추론 결과가 아니라 의존성 선택 근거다. 이 검토에서 모델 설치, 유료 생성, 자격 증명 변경은 실행하지 않았다.

권장 경로는 **Qwen3-TTS 1.7B-CustomVoice → MuseTalk 1.5**이다. 음성을 먼저 생성하고 GPU를 해제한 뒤, 이미 보유한 홈 영상의 입 주변을 새 음성에 맞춘다. 새로운 Higgsfield 요청 없이 실행할 수 있는 경로이며, 배경·몸동작을 처음부터 만드는 MiniMax H3와는 출력 범위가 다르다. MuseTalk은 입력 영상과 음성으로 얼굴 영역을 수정한다. [MuseTalk 공식 개요](https://github.com/TMElyralab/MuseTalk#overview)

## 이번 장치와 선택

리더가 확인한 장치: Windows 11, RTX 4080 16 GB(당시 약 13.5 GB 사용 가능), RAM 64 GB, D: 약 1.38 TB 여유. WSL Ubuntu-22.04는 `Wsl/Service/CreateInstance/CreateVm/HCS/0x80070569`로 시작하지 못했다. 이 장치 정보는 리더의 로컬 조사 결과이며 외부 문서로 검증한 값이 아니다.

| 후보 | 확인된 공식 조건 | 이번 선택 |
|---|---|---|
| MiniMax H3 Base | 소비자 GPU 사례 중 4090 24 GB + INT8/offload도 약 18 GB GPU peak. 768p 공개 Base, 2K 재생성은 비공개 | 실행하지 않음. 현재 메모리보다 큰 검증 사례이며 별도 라이선스 문제도 있음 |
| Qwen3-TTS 1.7B-CustomVoice | 4.52 GB 모델 저장소, SDPA 지원, English/Korean 지원 | 음성 기본 후보. 16 GB에서의 실제 peak와 속도는 실행 후 측정 필요 |
| MuseTalk 1.5 | 공식 Windows fp16 데모는 4 GB RTX 3050 Ti Laptop에서 8초 생성 약 5분을 기록 | 립싱크 기본 후보. 이번 장치 성능을 데모 수치로 단정하지 않음 |
| LatentSync 1.5 / 1.6 | 최소 VRAM 8 GB / 18 GB | 1.5는 대안. 1.6은 현재 장치 기준 우선 후보에서 제외 |

각 조건: [H3 로컬 배포](https://platform.minimax.io/docs/guides/local-deploy-h3), [H3 공개 범위](https://github.com/MiniMax-AI/MiniMax-H3#model-architecture), [Qwen 모델 파일](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice/tree/main), [Qwen SDPA 구현](https://raw.githubusercontent.com/QwenLM/Qwen3-TTS/main/qwen_tts/core/models/modeling_qwen3_tts.py), [MuseTalk Windows 실험](https://github.com/TMElyralab/MuseTalk#gradio-demo), [LatentSync 추론 조건](https://github.com/bytedance/LatentSync#-inference).

## MiniMax H3를 이 PC에 설치하지 않는 이유

공개 H3는 33B Omni Transformer와 Qwen3-VL-32B 인코더를 사용한다. 추론용 AdaLN 캐싱은 지원되지만, 공식 문서는 RTX 4080 16 GB·RAM 64 GB에서 검증한 경로를 제공하지 않는다. 단일 4090의 INT8/offload 공개 사례조차 GPU peak가 약 18 GB다. 디스크도 대형 체크포인트이고, 2 GPU vLLM offload 사례는 가용 시스템 RAM 200 GiB 이상을 요구한다. 이 수치는 그 사례의 조건이며 모든 구현의 수학적 최소값으로 해석하지 않는다. [구조](https://github.com/MiniMax-AI/MiniMax-H3#model-architecture), [하드웨어와 저장 공간](https://platform.minimax.io/docs/guides/local-deploy-h3)

**공개 H3 Community License I.5는 대한민국을 Excluded Territories로 명시한다.** 한국에서 공개 가중치를 배포·실행하려면 기본 공개 라이선스만으로 진행할 수 없으며, 문서 II에 별도 라이선스 문의 경로가 있다. IV.1에는 관련 상업 제품·서비스 연 매출 2천만 USD 초과에 대한 별도 서면 승인 조건도 있다. 이 공개 가중치 라이선스를 기존 Higgsfield 이용 계약과 동일하다고 단정하지 않는다. [라이선스 원문 I.5, II, IV.1, V.4](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)

Higgsfield 없이 MiniMax 공식 서비스를 직접 호출하는 경로는 존재한다. `POST https://api.minimax.io/v2/video_generation`은 Bearer API key와 Pay-as-you-go 계정을 요구하고 H3 768P/2K를 지원한다. 이는 로컬 오픈 가중치 추론과 다른 유료 경로다. 이번 검토에서는 요청하지 않았다. [MiniMax 직접 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)

## Windows 설치 조합

서로 다른 두 환경을 사용한다. Qwen은 transformers 4.57.3 / accelerate 1.12.0을 고정하고, MuseTalk은 transformers 4.39.2 / accelerate 0.28.0을 고정한다. 공유 환경은 이 조건을 동시에 충족하지 않는다. [Qwen pyproject](https://raw.githubusercontent.com/QwenLM/Qwen3-TTS/main/pyproject.toml), [MuseTalk requirements](https://raw.githubusercontent.com/TMElyralab/MuseTalk/main/requirements.txt)

Qwen 환경은 Python 3.11 + torch 2.6.0 / torchaudio 2.6.0 CUDA 12.4 wheel + `qwen-tts` 0.1.1을 제안한다. 공식 Python 최소는 3.9이며 README는 3.12의 새 환경을 예시로 든다. transformers 4.57.3은 torch >= 2.2를 요구한다. Torch 2.6.0 CUDA 12.4 Windows wheel은 공식 배포 조합이다. 이것은 호환성 근거이며 아직 이번 장치에서 실행 검증한 조합은 아니다. [Qwen 패키지 조건](https://raw.githubusercontent.com/QwenLM/Qwen3-TTS/main/pyproject.toml), [Transformers 조건](https://raw.githubusercontent.com/huggingface/transformers/v4.57.3/setup.py), [Torch Windows wheel](https://pytorch.org/get-started/previous-versions/#v260)

Qwen 로드 설정은 BF16, CUDA 0, `attn_implementation="sdpa"`를 우선 사용한다. FlashAttention 2는 README의 권장 옵션이지 필수 패키지 목록은 아니며, 모델 클래스는 SDPA 지원을 명시한다. 따라서 첫 Windows POC에서 FlashAttention 소스 빌드를 생략할 수 있다. [권장 환경](https://github.com/QwenLM/Qwen3-TTS#environment-setup), [SDPA 구현](https://raw.githubusercontent.com/QwenLM/Qwen3-TTS/main/qwen_tts/core/models/modeling_qwen3_tts.py)

MuseTalk의 공식 baseline은 Python 3.10, torch 2.0.1 / torchvision 0.15.2 / torchaudio 2.0.2 CUDA 11.8 wheel이다. MMLab은 mmcv 2.0.1, mmdet 3.1.0, mmpose 1.1.0 조합이다. 공식 OpenMMLab wheel index에 mmcv 2.0.1의 cp310 및 cp311 Windows AMD64 wheel이 존재하므로 해당 조합에서 소스 컴파일을 우선 요구하지 않는다. FFmpeg 경로도 명시한다. [MuseTalk 설치](https://github.com/TMElyralab/MuseTalk#installation), [공식 Windows mmcv wheel index](https://download.openmmlab.com/mmcv/dist/cu118/torch2.0/index.html)

## 생성과 발음 확인

Qwen 1.7B-CustomVoice의 `generate_custom_voice`에 같은 여자 화자 `Sohee`를 쓰고, 영어 문장 안의 브랜드를 한글 `바닐라코`로 입력해 `Auto`와 `English` 결과를 비교한다. Sohee의 원어는 한국어이고 모델의 언어 목록에는 영어·한국어가 있다. 혼합 언어에서 브랜드를 정확히 말하는지는 직접 생성·청취할 검증 항목이다. [공식 화자·언어](https://github.com/QwenLM/Qwen3-TTS#custom-voice-generate)

**0.6B-CustomVoice는 톤 지시 fallback이 아니다.** 공식 wrapper의 `generate_custom_voice`는 0.6B이면 `instruct`를 제거한다. 자연스러운 설명 톤 지시를 실제 적용하려면 1.7B를 우선 쓴다. 0.6B의 전체 모델 저장소는 2.5 GB이며 메모리 또는 다운로드 fallback 후보다. [실제 wrapper 코드](https://raw.githubusercontent.com/QwenLM/Qwen3-TTS/main/qwen_tts/inference/qwen3_tts_model.py), [0.6B 파일](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice/tree/main)

MuseTalk에는 원본 영상과 최종 WAV를 전달한다. 25 fps 입력이 공식 권장이고, 1.5 CLI는 `--use_float16`, `--batch_size`를 제공한다. 낮은 batch부터 짧은 발음 클립을 검증한 다음 전체 15초를 만든다. 모델은 256×256 얼굴 영역을 합성하므로 큰 얼굴·턱에서 부드러움이나 경계가 드러나는지는 결과로 확인해야 한다. [권장 입력](https://github.com/TMElyralab/MuseTalk#inference), [추론 flags와 합성 코드](https://raw.githubusercontent.com/TMElyralab/MuseTalk/main/scripts/inference.py)

## 필요한 가중치와 비용 범위

MuseTalk 1.5 본체만 선택하면 UNet 약 3.4 GB다. 보조 가중치는 VAE bin 335 MB, Whisper tiny bin 151 MB, DWPose pth 407 MB, 얼굴 파서·ResNet 등이 추가된다. 전체 저장소를 내려받으면 MuseTalk 1.0까지 중복 다운로드하므로 선택 다운로드가 맞다. 공식 다운로드 스크립트는 Hugging Face mirror endpoint를 설정하므로, 이번 목적의 공식 소스 다운로드에서는 각 공식 저장소를 직접 지정하고 불필요한 SyncNet 학습 가중치는 실제 사용 여부를 보고 선택한다. [MuseTalk 1.5](https://huggingface.co/TMElyralab/MuseTalk/tree/main/musetalkV15), [VAE](https://huggingface.co/stabilityai/sd-vae-ft-mse/tree/main), [Whisper](https://huggingface.co/openai/whisper-tiny/tree/main), [DWPose](https://huggingface.co/yzd-v/DWPose/tree/main), [공식 다운로드 항목](https://raw.githubusercontent.com/TMElyralab/MuseTalk/main/download_weights.sh)

로컬 추론에는 Higgsfield 크레딧·외부 생성 API 요금이 없다. GPU 전력, 설치/다운로드 시간, 기존 장비비는 별도로 기록해야 하며 총 운영 비용을 0원으로 표시하지 않는다. 전력 비용은 실제 측정값과 전기 단가 없이 만들지 않는다.

## 라이선스와 유지보수

Qwen 코드와 모델 카드는 Apache-2.0이다. MuseTalk은 코드 MIT, 자체 학습 모델 상업 이용 허용이라고 명시하며, 모델 저장소 LICENSE도 MIT 및 부속 라이선스 목록을 제공한다. 예시 testdata에는 비상업 연구 제한이 있으므로 사용자 소유 원본만 사용한다. Whisper/VAE/얼굴 파서는 MIT, DWPose는 Apache-2.0으로 표시되어 있다. S3FD 등 모든 부속 체크포인트의 권리 범위를 이 검토가 일괄 보증하지는 않는다. [Qwen](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice), [MuseTalk 상업 사용 설명](https://github.com/TMElyralab/MuseTalk#disclaimerlicense), [MuseTalk 모델 LICENSE](https://huggingface.co/TMElyralab/MuseTalk/blob/main/LICENSE.txt), [DWPose](https://huggingface.co/yzd-v/DWPose), [VAE](https://huggingface.co/stabilityai/sd-vae-ft-mse)

LatentSync 코드는 Apache-2.0이지만 Hugging Face 체크포인트 카드는 OpenRAIL++이다. 코드 라이선스만으로 가중치를 Apache라고 표시하지 않는다. MuseTalk의 얼굴 재합성 품질이 부족하면 8 GB 추론 조건의 LatentSync 1.5를 별도 비교할 수 있다. [코드와 VRAM](https://github.com/bytedance/LatentSync), [가중치 카드](https://huggingface.co/ByteDance/LatentSync/blob/main/README.md)

GitHub API에서 2026-10-06 확인한 최근 기본 브랜치 커밋: [MuseTalk 2025-09-26](https://github.com/TMElyralab/MuseTalk/commit/0a89dec45a0192b824e3cf4daf96c239440c5ed8), [Qwen3-TTS 2026-03-17](https://github.com/QwenLM/Qwen3-TTS/commit/022e286b98fbec7e1e916cb940cdf532cd9f488e), [LatentSync 2025-06-20](https://github.com/bytedance/LatentSync/commit/a229c3948406bc2cf6eaf4873e662e70c6a04746), [H3 2026-08-15](https://github.com/MiniMax-AI/MiniMax-H3/commit/d21241f0a4b3acbb34c97dae47fa417b7065e438). MuseTalk·LatentSync는 최근 커밋이 12개월을 넘었으므로 현재 조합을 고정하고 설치·출력 검증을 남기는 것이 맞다. 이번 검토는 취약점 전수 감사가 아니다.

완료 증거는 리더가 생성한 실제 WAV·MP4, 제출/완료 시간, CUDA 사용·최대 VRAM, 브랜드 음성 발췌, 영상 디코드와 시각 검토로 남겨야 한다. 이 문서만으로 생성 완료·정확한 발음·완전한 립싱크를 선언하지 않는다.
