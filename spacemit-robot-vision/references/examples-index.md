# Vision single-model examples index

Read on demand. Details and CLI flags come from each `examples/<name>/README.md`. Models default to `~/.cache/models/vision/<cache_dir>/`.

| Example dir | Task type | Typical cache dir | Notes |
| --- | --- | --- | --- |
| `yolov8` | Detection | `yolov8` | Common smoke-test entry |
| `yolov11` | Detection | `yolov11` | |
| `yolo12` | Detection | See example README | |
| `yolo26` | Detection | See example README | |
| `yolov5` | Detection | `yolov5` | |
| `yolov5_gesture` | Gesture detection | See example README | |
| `yolov5-face` | Face detection | `yolov5-face` | |
| `yolov8_pose` | Pose | `yolov8_pose` | |
| `yolov8_seg` | Instance segmentation | `yolov8_seg` | |
| `bytetrack` | Multi-object tracking | Depends on detector; see README | |
| `ocsort` | Multi-object tracking | `ocsort` | |
| `resnet` | Classification | `resnet` | |
| `mobilenet` / `mobilenetv1` | Classification | See example README | |
| `efficientnet` / `efficientnet_v2s` | Classification | See example README | |
| `vit` | Classification | See example README | |
| `arcface` | Face embedding | `arcface` | |
| `adaface` | Face embedding | `adaface` | |
| `emotion` | Emotion (single-model example) | `emotion` | Composed app: `applications/emotion_detection` |
| `ppocr` | OCR | See example README | |
| `siglip2` | Image-text embedding | `siglip2` | Text side via `encode_text`; needs `tokenizer.bin` |
| `mobileclip2` | Image-text embedding | `mobileclip2` | Text side via `encode_text` |
| `yolo_world` / `yoloe` | Open-vocab detection | See example README | |

Download: prefer `examples/<name>/scripts/download_models.sh`; bulk download via component-root `scripts/download_all_models.sh` (some models may be omitted and need a per-example script).

Default test images/videos: `~/.cache/assets/image/`, `~/.cache/assets/video/` (`scripts/download_assets.sh`).
