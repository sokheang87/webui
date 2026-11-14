# Save First — 30-second stickman video

A 9:16 (720×1280, 30 fps) code-rendered animation with captions, music and sound effects. No AI video generator is used.

- `index.html` — the animation (open it in a browser for a live preview)
- `audio.py` — synthesises the soundtrack
- `render.mjs` — renders the frames with headless Chromium and encodes with ffmpeg
- `save-first.mp4` — the finished video

Rebuild:

```sh
python3 audio.py audio.wav
node render.mjs silent.mp4
ffmpeg -y -i silent.mp4 -i audio.wav -c:v copy -c:a aac -shortest -movflags +faststart save-first.mp4
```
