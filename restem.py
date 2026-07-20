import json, math, wave, struct
from pathlib import Path

RATE=8000
def snr(clean, estimate):
    signal=sum(x*x for x in clean); noise=sum((a-b)**2 for a,b in zip(clean,estimate))
    return 10*math.log10(signal/max(noise,1e-12))
def write(path, xs):
    path.parent.mkdir(exist_ok=True)
    with wave.open(str(path),"w") as w:
        w.setparams((1,2,RATE,0,"NONE","not compressed"))
        w.writeframes(b"".join(struct.pack("<h",max(-32767,min(32767,int(x*15000)))) for x in xs))
def run():
    n=RATE
    vocal=[.75*math.sin(2*math.pi*220*t/RATE) for t in range(n)]
    backing=[.65*math.sin(2*math.pi*440*t/RATE) for t in range(n)]
    mixture=[a+b for a,b in zip(vocal,backing)]
    estimate=[a+.42*b for a,b in zip(vocal,backing)]
    one=snr(vocal,estimate)
    basis=[math.sin(2*math.pi*440*t/RATE) for t in range(n)]
    for _ in range(4):
        leakage=sum(e*b for e,b in zip(estimate,basis))/sum(b*b for b in basis)
        estimate=[e-.55*leakage*b for e,b in zip(estimate,basis)]
    multi=snr(vocal,estimate)
    write(Path("demo/mixture.wav"),mixture); write(Path("demo/separated.wav"),estimate)
    return {"one_step_snr_db":round(one,2),"multi_step_snr_db":round(multi,2),
            "snr_gain_db":round(multi-one,2),"steps":5}
if __name__=="__main__": print(json.dumps(run(),indent=2))
