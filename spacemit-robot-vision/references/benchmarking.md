# Vision benchmarking

Read only when the user explicitly asks for latency, FPS, throughput, or before/after comparisons. Do not treat README §8 tables as results from this session unless you just ran the commands.

Two reproduction tracks:

| Track | Tool | What it measures |
| --- | --- | --- |
| **With** pre/post-process | `vision_infer_benchmark` | Full `VisionService` path (preprocess + ORT infer + postprocess), optional stage timing |
| **Without** pre/post-process | `onnxruntime_perf_test` | Raw ONNX Runtime (+ SpaceMIT EP) model inference only |

Authoritative numbers and platform notes: component `README.md` §8.

## With pre/post-process: `vision_infer_benchmark`

Prerequisites:

- C++ build with `BUILD_TESTS=ON` (default).
- Model + test image available (see `references/setup.md`).
- Binary: `build/tests/benchmarks/vision_infer_benchmark` (standalone layout).

From the **vision component root** (paths relative to CWD):

```bash
./build/tests/benchmarks/vision_infer_benchmark \
  --config examples/yolov8/config/yolov8.yaml \
  --image ~/.cache/assets/image/006_test.jpg
```

Useful flags (see binary `--help` / `tests/benchmarks/infer_benchmark.cpp`):

| Flag | Meaning |
| --- | --- |
| `--config` | Required yaml |
| `--image` | Input image; if omitted, falls back to yaml `test_image` when valid |
| `--model-path` | Override ONNX path (e.g. yolov8s instead of default n) |
| `--runs` / `--warmup` | Iteration counts |
| `--verbose-timing` | Print stage averages (preprocess / model_infer / postprocess) |

Inside the full SDK tree, point `--config` at `components/model_zoo/vision/examples/...` as needed. Run on the board in `remote` / `hybrid` modes.

## Without pre/post-process: `onnxruntime_perf_test`

Prerequisites: C++ ORT/SpaceMIT deps installed; model file downloaded. This path does **not** go through `VisionService` letterbox/NMS/draw.

Example (yolov8n; confirm before long runs):

```bash
onnxruntime_perf_test ~/.cache/models/vision/yolov8/yolov8n_no_dfl.q.onnx \
  -e spacemit -r 20 -x 1 -S 1 -s -I -c 1 \
  -i "SPACEMIT_EP_INTRA_THREAD_NUM|4"
```

Flag meanings and EP options: SpacemiT community doc [AI compute stack · ONNX Runtime](https://www.spacemit.com/community/document/info?lang=zh&nodepath=ai/compute_stack/ai_compute_stack/onnxruntime.md) (`onnxruntime_perf_test` section). Adjust thread count / model path for the comparison the user asked for.

## Reporting rules

- State which track was used (with vs without pre/post).
- Record model path, config, image (if any), thread/EP settings, run/warmup counts, and board/core context when known.
- Return real command output; do not copy README FPS tables as if freshly measured.
- Confirm before long stress runs or downloads needed only for benchmarking.
