"""Split each source into vocals / accompaniment with Demucs htdemucs_ft (CPU)."""
import sys
from pathlib import Path
import soundfile as sf, torch
from demucs.pretrained import get_model
from demucs.apply import apply_model

PROJ = Path(__file__).resolve().parents[1]
torch.set_num_threads(14)
model = get_model("htdemucs"); model.eval()
for key in sys.argv[1:]:
    x, sr = sf.read(PROJ / f"assets/audio/{key}_48k.wav", dtype="float32")
    import torchaudio.functional as AF
    wav = AF.resample(torch.from_numpy(x.T), sr, model.samplerate)
    ref = wav.mean(0); m, s = ref.mean(), ref.std()
    with torch.no_grad():
        out = apply_model(model, ((wav - m) / s)[None], shifts=2, overlap=0.25, split=True, progress=True)[0] * s + m
    vi = model.sources.index("vocals")
    voc = AF.resample(out[vi], model.samplerate, sr)
    acc = AF.resample(out.sum(0) - out[vi], model.samplerate, sr)
    sf.write(PROJ / f"assets/audio/{key}_vocals.wav", voc.T.numpy(), sr, subtype="FLOAT")
    sf.write(PROJ / f"assets/audio/{key}_music.wav", acc.T.numpy(), sr, subtype="FLOAT")
    print(key, "done", flush=True)
