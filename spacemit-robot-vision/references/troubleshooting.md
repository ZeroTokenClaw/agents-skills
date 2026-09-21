# Vision troubleshooting index

Read on demand. Authoritative FAQ is component `README.md` §4; this file is a routing summary only.

| Symptom | Check first | Where to fix |
| --- | --- | --- |
| `No module named 'spacemit_vision'` | Wheel not installed / wrong interpreter | `README.md` §2.1: after build, `pip install src/python/dist/*.whl`, then verify `VisionServiceNative` with the same `python3` |
| Model file not found / bad model path | Cache dir or yaml `model_path` | Run matching `examples/.../download_models.sh` or `applications/.../download_models.sh`; confirm `~/.cache/models/vision/<type>/` |
| Default test image/video missing | Assets not downloaded | `scripts/download_assets.sh` → `~/.cache/assets/{image,video}/` |
| `imshow` / highgui / display failure | No desktop, pure SSH, no DISPLAY | Save with `imwrite`; environment limit, not model logic |
| Camera fails to open or black frames | Device index, permissions, occupancy | Try `--camera-id` / another index; confirm user accepts camera use |
| Composed app fails to start | One of several models missing | Cross-check `references/applications-index.md` and the app README cache files |
| SigLIP2 tokenizer failure | Missing `tokenizer.bin` | See `examples/siglip2/README.md` (archive download or `export_tokenizer_bin.py`) |
| Only one model fails; others OK | EP / runtime compatibility | Record model name, ORT/EP version, and logs; avoid changing unrelated examples first |
| Standalone build cannot find libs | `LD_LIBRARY_PATH` / missing system deps | `package.xml` and `README.md` §2.1; `sudo apt` deps (confirm before install) |
| Board run fails after SDK `mm` | Missing `source build/envsetup.sh` / staging path | Follow `README.md` §2.4.1; leave build details to `spacemit-robot-build` |

Safety confirmation gates (explain impact before acting):

- `sudo apt` system package installs
- Large model downloads / full `download_all_models.sh`
- Opening a camera or holding capture devices for a long time
- Overwriting existing result images or face-DB directories
