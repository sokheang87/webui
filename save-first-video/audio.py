# Synthesises the soundtrack (plucked-guitar music + sound effects) for the Save First video.
import numpy as np, wave, sys
SR=44100; DUR=30.0; N=int(SR*DUR); out=np.zeros(N+SR*3)
rng=np.random.default_rng(7)
def add(sig,t,g=1.0):
    i=int(t*SR); out[i:i+len(sig)]+=sig*g
def pluck(f,dur=1.6,bright=.5):
    n=int(SR/f); buf=rng.uniform(-1,1,n); m=int(dur*SR); y=np.empty(m)
    for i in range(m):
        y[i]=buf[i%n]; buf[i%n]=(.996)*((1-bright*.5)*buf[i%n]+bright*.5*buf[(i+1)%n])
    return y*np.exp(-np.arange(m)/SR*1.8)
def tone(f,dur,decay=8,harm=()):
    t=np.arange(int(dur*SR))/SR; y=np.sin(2*np.pi*f*t)
    for k,a in harm: y+=a*np.sin(2*np.pi*f*k*t)
    return y*np.exp(-t*decay)*np.minimum(1,t*400)
def clink(g=1.0,f=None):
    f=f or rng.uniform(2500,3100); return tone(f,.22,22,((1.51,.6),(2.3,.3)))*g
def whoosh(dur=.5):
    n=int(dur*SR); x=rng.normal(0,1,n); k=np.ones(60)/60; x=np.convolve(x,k,'same'); return x*np.hanning(n)*3
def pop(f0=420,f1=900,dur=.09):
    t=np.arange(int(dur*SR))/SR; f=np.linspace(f0,f1,len(t)); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.hanning(len(t))
NOTE={'C':261.63,'D':293.66,'E':329.63,'F':349.23,'G':392.0,'A':440.0,'B':493.88}
def n(name,o=0): return NOTE[name]*2**o
CH={'C':['C','E','G'],'G':['G','B','D'],'Am':['A','C','E'],'F':['F','A','C'],'Dm':['D','F','A'],'E':['E','B','E']}
prog=['C','G','Am','F','Am','F','Dm','E','C','G','F','C']
beat=.625; cache={}
def P(f,b=.5):
    k=(round(f,2),b)
    if k not in cache: cache[k]=pluck(f,1.6,b)
    return cache[k]
for bi,ch in enumerate(prog):
    t0=bi*2.5; r,th,fi=CH[ch]
    low={'C':-1,'G':-2,'Am':-2,'F':-2,'Dm':-1,'E':-2}[ch]
    pat=[(r,low),(fi,low if ch in('C','Dm') else low+1),(r,low+1),(th,low+1),(fi,low+1 if ch in('C','Dm') else low+1),(r,low+1),(th,low+1),(fi,low if ch in('C','Dm') else low+1)]
    mid=4<=bi<8
    for i,(nm,o) in enumerate(pat):
        if bi==11 and i>3: break
        add(P(n(nm,o),.35 if mid else .55),t0+i*beat/2,.20 if i else .28)
    add(tone(n(r,low-1 if low>-2 else low),2.4,1.2,((2,.3),))*.5,t0,.16)          # soft bass
    for nm in (r,th,fi): add(tone(n(nm,0),2.5,1.0)*np.hanning(int(2.5*SR)),t0,.018 if not mid else .026)  # pad
for i,(nm,o) in enumerate([('C',-1),('G',-1),('C',0),('E',0),('G',0),('C',1)]): add(pluck(n(nm,o),2.6,.6),28.75+i*.035,.22)  # final strum
for i,f in enumerate([1046.5,1318.5,1568,2093]): add(tone(f,.9,4),28.95+i*.09,.07)                                     # sparkle
# ---- sound effects (times match index.html) ----
for i in range(10): add(clink(),1.9+i*.09+.45,.10)
for t in (3.1,4.0,4.9): add(whoosh(.45),t,.20); add(clink(),t+.45,.12); add(clink(),t+.5,.09); add(whoosh(.4),t+.6,.14)
add(pop(300,700,.14),6.9,.25); add(tone(140,.18,25),7.58,.5)
add(tone(1750,.6,7,((2.76,.4),)),8.24,.22)                      # lonely "tink" in the jar
add(clink(),11.85,.11); add(pop(),12.38,.22); add(tone(180,.12,30),13.45,.35)
for t in (3.7,4.8,5.9): add(pop(500,1100,.08),10+t,.2); add(clink(f=3300),10+t+.5,.09)
for t in (14.2,15.3,16.4,17.3): add(whoosh(.6),t,.07)
add(whoosh(.8),19.05,.3)
add(whoosh(.7),20.1,.16)
for i in range(8): add(clink(f=2400+i*90),21.8+i*.18,.13)
for i in range(3): add(whoosh(.5),23.1+i*.7,.08); add(clink(),23.1+i*.7+.8,.07)
add(clink(),26.55,.11); add(pop(600,1200,.1),26.95,.2)
# gentle ambience: street hum (scene 2), birds (scene 3)
t=np.arange(N)/SR
hum=np.convolve(rng.normal(0,1,N),np.ones(400)/400,'same')*8
out[:N]+=hum*np.clip(np.minimum(t-10,20-t),0,1)*.05
for bt in (20.9,22.6,24.3,25.9,27.6,29.2):
    for k in range(3):
        d=.09; tt=np.arange(int(d*SR))/SR; f=3200+900*np.sin(tt*60)+k*250
        add(np.sin(2*np.pi*np.cumsum(f)/SR)*np.hanning(len(tt)),bt+k*.13,.035)
y=out[:N]; y[-int(.6*SR):]*=np.linspace(1,0,int(.6*SR)); y[:int(.05*SR)]*=np.linspace(0,1,int(.05*SR))
y=np.tanh(y*1.6)/np.max(np.abs(np.tanh(y*1.6)))*.85
st=np.stack([y,y],1); w=wave.open(sys.argv[1] if len(sys.argv)>1 else 'audio.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st*32767).astype('<i2').tobytes()); w.close()
