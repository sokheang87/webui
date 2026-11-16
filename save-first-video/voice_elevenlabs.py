# Generates the narration with ElevenLabs and mixes it over the music.
# Usage: ELEVENLABS_API_KEY=... python3 voice_elevenlabs.py <voice_id> audio.wav mix.wav
import sys, os, json, wave, subprocess, urllib.request, numpy as np
LINES=[(0.3,"You're not bad at saving money."),(2.7,"You're just saving last."),(4.7,"Most people pay everyone else first,"),(7.5,"then try to save whatever's left."),
 (10.2,"But leftovers disappear."),(12.3,"A coffee here,"),(14.3,"a subscription there,"),(16.0,"and the month is gone."),(17.35,"Willpower isn't the problem."),(19.0,"The order is."),
 (20.45,"So flip it."),(21.6,"Move a little to savings the day you get paid,"),(24.5,"then spend the rest guilt-free."),(27.6,"What would you save for first?")]
VOICE=sys.argv[1]; SR=44100; os.makedirs('vo',exist_ok=True)
def say(i,text):
    mp3=f'vo/{i:02d}.mp3'
    if not os.path.exists(mp3):
        body={"text":text,"model_id":"eleven_multilingual_v2",
              "voice_settings":{"stability":.5,"similarity_boost":.75,"style":.05,"use_speaker_boost":True,"speed":.95},
              "previous_text":" ".join(t for _,t in LINES[:i])[-300:],"next_text":" ".join(t for _,t in LINES[i+1:])[:300]}
        req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",json.dumps(body).encode(),
            {"xi-api-key":os.environ.get("ELEVENLABS_API_KEY","proxy-injected"),"Content-Type":"application/json"})
        open(mp3,'wb').write(urllib.request.urlopen(req,timeout=120).read())
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',mp3,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout
    y=np.frombuffer(raw,'<i2').astype(float)/32768; nz=np.where(np.abs(y)>.01)[0]
    return y[max(0,nz[0]-400):nz[-1]+4000]
m=wave.open(sys.argv[2]); mus=np.frombuffer(m.readframes(m.getnframes()),'<i2').astype(float).reshape(-1,2)[:,0]/32768
vo=np.zeros(len(mus))
for i,(t,text) in enumerate(LINES):
    y=say(i,text); y=y/np.max(np.abs(y))*.8; k=int(t*SR); y=y[:len(vo)-k]; vo[k:k+len(y)]+=y
    nxt=LINES[i+1][0] if i+1<len(LINES) else 30
    print(f"{t:5.1f} {len(y)/SR:4.2f}s gap {nxt-t-len(y)/SR:+.2f}  {text}")
env=np.convolve(np.abs(vo),np.ones(8000)/8000,'same'); duck=1-.55*np.clip(env*12,0,1)   # lower music under speech
mix=np.tanh(vo*1.1+mus*duck*.55); mix=mix/np.max(np.abs(mix))*.92
o=wave.open(sys.argv[3],'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((np.stack([mix,mix],1)*32767).astype('<i2').tobytes()); o.close()
