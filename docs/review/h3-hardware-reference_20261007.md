# MiniMax H3 RAM·VRAM reference — 2026-10-07

VRAM은 GPU가 계산 중인 가중치·활성값을, RAM은 CPU offload 가중치를 담습니다. RAM 추가는 GPU VRAM과 같은 속도를 주지 않습니다. Offload와 정밀도를 줄이는 양자화는 별개입니다. [Diffusers 메모리 설명](https://huggingface.co/docs/diffusers/main/en/optimization/memory)

현재 **RTX4080 16GB /RAM63.7GiB에서320×576·15초 영상＋음성 생성 성공**은 부모가 전달한 실측입니다. 이 연구자가 재실행한 benchmark가 아니며 native768p 성공까지 입증하지 않습니다.

| 공식 Diffusers 예제 | 정밀도·배치 | RAM 해석 |
|---|---|---|
| 12–16GB GPU /960×544 | INT8＋CPU/VAE offload | 해당 recipe 약75GB; 보편적 최소 아님 |
| 24–32GB GPU | INT8＋CPU block/leaf stream | 로딩·OS 여유도 필요 |
| 1×80GB GPU | BF16＋CPU auto offload | 정확한 host 최소 미공개 |
| 2×48GB GPU | INT8, encoder와 나머지 분리 상주 | 정확한 host 최소 미공개 |
| 2×80GB GPU | BF16, encoder와 나머지 분리 상주 | 정확한 host 최소 미공개 |

원본 BF16 transformer61.7GB＋conditioner62.1GB와, 현재 Comfy의 pruned INT8 DiT＋NVFP4 encoder 등4파일 **37.3217GiB**는 다른 artifact입니다. 파일 크기는 peak RAM/VRAM이 아닙니다. 위 예제는 모든 해상도·길이·reference 조합의 실행 보장이 아닙니다. [Diffusers H3, main/source-install 문서](https://huggingface.co/docs/diffusers/main/en/api/pipelines/minimax_h3), [Comfy metadata](https://huggingface.co/api/models/Comfy-Org/MiniMax-H3?blobs=true)

공개 Base의 native canvas는768px short edge, 약1MP입니다. 공식2K는 hosted Context-IR와 아직 비공개인 Regenerate-2K를 포함합니다. GPU 증설이나 일반 upscale을 공식2K workflow와 동일시하지 않습니다. [MiniMax model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)

품질에는 native canvas, steps, Turbo LoRA와 attention도 영향을 줍니다. Comfy 공식 가이드는 base20steps를 사용하고8-step의 음성·음색이 약하다고 설명합니다. INT8 가중치와 Sage INT8 attention은 별개이며, int8_convrot에는 기본 attention을 권합니다. 길이가 늘면 attention 부담이 커집니다. 현재 canvas에서1344×768로 올리면 픽셀 수는5.6배이나 RAM·VRAM·시간을 같은 배수로 계산할 수 없습니다. [Comfy H3 가이드](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)

**설계 제안이며 미실측:** native canvas benchmark 후보는32GB VRAM＋128GB RAM＋NVMe2TB입니다. Preview16GB/96–128GB RAM은 추가 여유 제안이며 현재64GB 성공을 부정하는 필수요건이 아닙니다. 2×48GB INT8/128–256GB RAM,2×80GB BF16/256GB RAM의 host 값도 제안입니다. CPU8–16core는 일반 균형 제안이며 H3 성능 측정이 아닙니다.768p15초 성공·시간을 보장하지 않습니다.

서버별 구현도 구분해야 합니다. MiniMax 문서의 vLLM 두GPU offload는200GiB available RAM recipe이며 다른 표의128GB 제안을 그대로 적용할 수 없습니다. Comfy의 공식 최소 VRAM은 미공개입니다. [MiniMax 배포 문서, reviewed2026-08-26](https://platform.minimax.io/docs/guides/local-deploy-h3)

현재 연구에서는 다운로드, 설치, 생성 요청, benchmark를 수행하지 않았습니다. 모델 metadata만 조회했습니다. 상세 출처·파일 byte 크기·실측과 제안 구분은 동명JSON에 있습니다.
