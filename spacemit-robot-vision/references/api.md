# Vision API quick reference

There is **no standalone `API.md`** in this repo. Use this file as the API entry, then read `include/vision_service.h` and `README.md` §3 for the full contract. Per-model CLI/config details stay in `examples/<model>/README.md`.

## Public surfaces

| Surface | Entry | Notes |
| --- | --- | --- |
| C++ | `#include "vision_service.h"` → `VisionService` | Only public header; link `vision` + OpenCV + `onnxruntime` + `spacemit_ep` + `yaml-cpp` |
| Python | `from spacemit_vision import VisionServiceNative` | Wheel wraps the same C++ service |

Instances are **not thread-safe**. Prefer one `VisionService` / `VisionServiceNative` per thread.

## C++ (`VisionService`)

Create:

```cpp
auto service = VisionService::Create(config_path, model_path_override, /*lazy_load=*/false);
if (!service) { /* VisionService::LastCreateError() */ }
```

Common calls:

| Method | Use |
| --- | --- |
| `Infer(image, &response)` / `Infer(request, &response)` | Image or unified request (sequence / prompts / thresholds) |
| `Draw(image, response, &vis)` | Overlay results onto `cv::Mat` |
| `LastError()` | Last failure message |
| Timing APIs (see header) | Optional preprocess / infer / postprocess timing |

Result types live in `namespace vision` as a `std::variant`: `Detection`, `Classification`, `Pose`, `Segmentation`, `Embedding`, `Tracking`, `Action`, `Text`. Helpers: `vision::get_bbox`, `get_score`, `get_label`, `get_track_id`; or `std::get_if<T>(&r)`.

Minimal image + draw pattern: see `README.md` §3.2 C++ sample.

## Python (`VisionServiceNative`)

```python
from spacemit_vision import VisionServiceNative, VisionServiceStatus

svc = VisionServiceNative.create("examples/yolov8/config/yolov8.yaml")
status, results = svc.infer_image(img)   # conf/iou optional; <=0 → yaml defaults
st, vis = svc.draw(img)                  # reuses last inference when supported
```

| Method | Use |
| --- | --- |
| `create(config_yaml, ...)` | Build service from yaml |
| `infer_image(img, ...)` | Detection / class / pose / seg / track / OCR-style image tasks |
| `infer_embedding(img)` | Image tower embedding (face / CLIP-style) |
| `encode_text(text)` | Text tower embedding (SigLIP2 / MobileCLIP2) |
| `embedding_similarity(a, b)` | Cosine similarity helper |
| `infer_sequence(...)` | Sequence models (e.g. STGCN / emotion LSTM inputs) |
| `draw(img)` / `supports_draw()` | Visualization |
| `last_error()` | Failure string |

Result objects expose task fields as needed (`label`, `score`, `x1/y1/x2/y2`, `keypoints`, `mask`, `class_scores`, …). Exact fields depend on the model; see example READMEs.

## Image-text embedding (SigLIP2 / MobileCLIP2)

1. Create from the dual-tower yaml (`examples/siglip2/config/siglip2.yaml` or `mobileclip2`).
2. `infer_embedding(image)` for the vision vector.
3. `encode_text("a photo of a dog")` for the text vector.
4. `VisionServiceNative.embedding_similarity(image_emb, text_emb)` (or equivalent C++ path in the example).

SigLIP2 also needs `tokenizer.bin` under the model cache; see `examples/siglip2/README.md`.

## Integration checklist

- Include/link only the public header + `vision` and deps listed in `README.md` §3.1.
- Prefer yaml configs from `examples/` or `applications/` as the model profile source.
- Do not invent API methods; if unsure, open `vision_service.h` or the matching example.
