# Synthesises the narration with Piper (offline neural TTS) and mixes it over the music.
# Usage: python3 voice.py <piper-model.onnx> audio.wav mix.wav [speaker_id]
# Voice used: Piper en-us-libritts-high (LibriTTS, CC BY 4.0), speaker 3.
import sys, wave, io, numpy as np
from piper import PiperVoice, SynthesisConfig
LINES=[(0.3,"You're not bad at saving money."),(2.7,"You're just saving last."),(4.7,"Most people pay everyone else first,"),(7.5,"then try to save whatever's left."),
 (10.2,"But leftovers disappear."),(12.3,"A coffee here,"),(14.3,"a subscription there,"),(16.1,"and the month is gone."),(17.5,"Willpower isn't the problem."),(19.0,"The order is."),
 (20.6,"So flip it."),(21.6,"Move a little to savings the day you get paid,"),(24.5,"then spend the rest guilt-free."),(27.6,"What would you save for first?")]
voice=PiperVoice.load(sys.argv[1]); SR=44100; SPK=int(sys.argv[4]) if len(sys.argv)>4 else 3
def say(text):
    buf=io.BytesIO(); w=wave.open(buf,'wb')
    voice.synthesize_wav(text,w,syn_config=SynthesisConfig(speaker_id=SPK))
    w.close(); buf.seek(0); r=wave.open(buf); sr=r.getframerate()
    y=np.frombuffer(r.readframes(r.getnframes()),'<i2').astype(float)/32768
    nz=np.where(np.abs(y)>.01)[0]; y=y[max(0,nz[0]-200):nz[-1]+2000]
    return np.interp(np.arange(0,len(y),sr/SR),np.arange(len(y)),y)
m=wave.open(sys.argv[2]); mus=np.frombuffer(m.readframes(m.getnframes()),'<i2').astype(float).reshape(-1,2)[:,0]/32768
vo=np.zeros(len(mus)); 
for t,text in LINES:
    y=say(text); i=int(t*SR); y=y[:len(vo)-i]; vo[i:i+len(y)]+=y; print(f"{t:5.1f} {len(y)/SR:4.2f}s  {text}")
vo*=.9/np.max(np.abs(vo))
env=np.convolve(np.abs(vo),np.ones(8000)/8000,'same'); duck=1-.55*np.clip(env*12,0,1)   # lower music under speech
mix=np.tanh(vo*1.1+mus*duck*.55); mix=mix/np.max(np.abs(mix))*.92
o=wave.open(sys.argv[3],'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((np.stack([mix,mix],1)*32767).astype('<i2').tobytes()); o.close()
