# Interactive Hand Portal 🌀

A rebuilt, GitHub-ready **webcam desktop prototype** inspired by a futuristic Jarvis HUD. It tracks one hand and activates one of ten visual effects **only inside the central portal ROI** when your index fingertip enters the portal.

> Reconstructed from the project description, not a recovery of original source. This version uses an OpenCV desktop UI, **not** the earlier browser/Cloudflare deployment.

## Quick start (Windows)

Install **Python 3.11**, connect a webcam and double-click `START.bat`. On macOS/Linux: `python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py`.

## Controls

- Move index finger inside the portal to activate the effect. Pinch for green visual feedback.
- `1`–`9`, `0`: select ten effects (Neon, Pixel, Edge, Mirror, Thermal, Glitch, Invert, Trail, Scan, Orbit).
- `S`: save a snapshot in `captures/`; `Q` or `Esc`: quit.
- Alternative camera: `python main.py --camera 1`.

## Stack
Python, OpenCV, MediaPipe, NumPy. Webcam footage stays local; no network API or credentials required.

## Limitations / testing
Requires a working webcam and a compatible MediaPipe installation. No real camera was available during packaging, so hand detection and frame rate must be checked on your PC. This is a standalone MVP rather than a byte-for-byte copy of the previous multi-effect web application.

## GitHub
Create a repository named `interactive-hand-portal` and upload the **contents** of this folder. Do not commit `.venv/` or `captures/`.

MIT license.
