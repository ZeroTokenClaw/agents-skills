# Vision composed applications index

Read on demand. Commands and flags come from each `applications/<app>/README.md`.

| App dir | Capability | Typical pipeline / multi-model deps | Model cache hints |
| --- | --- | --- | --- |
| `face_recognition` | Face analyze / register / recognize / camera | det_10g → 5-point align → w600k_r50 embedding → genderage; optional 106 landmarks | `~/.cache/models/vision/buffalo_l/`; face DB default `~/.cache/face_db` |
| `emotion_detection` | Static emotion / camera temporal emotion | image: YOLOv5-Face + ResNet50; camera: Face + ResNet features + LSTM window | `emotion` etc.; see app `download_models.sh` (usually 4 models) |
| `fall_detection` | Fall detection | Pose + STGCN; business class index in app yaml | pose / `stgcn` etc.; see app README |
| `fire_detection` | Fire detection | YOLOv8 fire config | See `yolov8_fire` / app download script |
| `intrusion_detection` | Zone intrusion | ByteTrack + ROI/counting policy | Tracker depends on detector; see app README |

General notes:

- Entry config is usually `applications/<app>/config/<app>.yaml`; sub-models reference other yaml files in the same directory.
- Before running, confirm **all** required ONNX files are cached; missing any one fails the app.
- Confirm with the user before camera use or writing result images; on headless setups, save images or disable preview.
- Download: `applications/<app>/scripts/download_models.sh` when present.
