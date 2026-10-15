# AdCraft AI — Marketing Video Generator

A Flask web app that turns product images and product details into a short promotional MP4. It creates a simple marketing script, generates text-to-speech narration, adds text overlays to product images, and renders a video for social media.

## Features

- Product name, description, benefits, and call-to-action inputs
- Multiple product image uploads
- Vertical 9:16, square 1:1, and landscape 16:9 exports
- Text overlays and a gentle image-motion effect
- Text-to-speech narration through gTTS
- MP4 download and generated script preview
- Responsive HTML/CSS interface

## Tech stack

Python, Flask, MoviePy, Pillow, gTTS, HTML, CSS.

## Requirements

- Python 3.10 or 3.11 recommended
- Internet connection for gTTS narration
- FFmpeg (MoviePy's `imageio-ffmpeg` package normally supplies a compatible binary)

## Run locally

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Example input

- Product name: Eco Bottle
- Description: A reusable bottle designed for everyday hydration.
- Benefits: reusable, lightweight, easy to carry
- CTA: Discover yours today
- Format: 9:16
- Images: one or more product photos

## Project structure

```text
ai_marketing_video_generator/
├── app.py
├── video_generator.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── uploads/
│   └── .gitkeep
└── outputs/
    └── .gitkeep
```

## Important notes

- gTTS uses Google's online text-to-speech service; narration requires network access. If narration fails, the app attempts to render the video without audio.
- This is a portfolio prototype, not a production deployment. Before deploying publicly, add authentication, per-user storage, stronger upload validation, file cleanup, rate limiting, CSRF protection, and a production WSGI server.
- The script builder is rule-based, not a large language model. You can extend `build_script()` with an LLM API to generate more varied scripts.
- Review generated marketing copy for factual accuracy and applicable advertising rules before publishing.
- Only upload product images you have permission to use.
