# Save First — 30-second stickman video

A 9:16 (720×1280, 30 fps) code-rendered animation with narration, captions, music and sound effects. No AI video generator is used.

- `index.html` — the animation (open it in a browser for a live preview)
- `audio.py` — synthesises the soundtrack
- `voice.py` — synthesises the narration with Piper (voice: en-us-libritts-high, LibriTTS, CC BY 4.0, speaker 3) and mixes it over the music
- `render.mjs` — renders the frames with headless Chromium and encodes with ffmpeg
- `save-first.mp4` — the finished video

Rebuild:

```sh
python3 audio.py audio.wav
node render.mjs silent.mp4
python3 voice.py path/to/en-us-libritts-high.onnx audio.wav mix.wav 3   # pip install piper-tts
ffmpeg -y -i silent.mp4 -i mix.wav -c:v copy -c:a aac -shortest -movflags +faststart save-first.mp4
```
