"""Find the offset of the karaoke backing track inside the camera recording (onset-envelope + chroma xcorr)."""
import sys, numpy as np, scipy.io.wavfile as wf, scipy.signal as ss
def load(p):
    sr, x = wf.read(p); x = x.astype(np.float32)
    if x.ndim > 1: x = x.mean(1)
    return sr, x / (np.abs(x).max() + 1e-9)
def feats(p, hop=441):
    sr, x = load(p)
    f, t, Z = ss.stft(x, sr, nperseg=2048, noverlap=2048 - hop)
    S = np.log1p(100 * np.abs(Z))
    flux = np.maximum(np.diff(S, axis=1), 0).sum(0)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    rms = np.sqrt((np.abs(Z) ** 2).mean(0))
    return flux, rms, sr / hop
a, arms, fr = feats(sys.argv[1]); b, brms, _ = feats(sys.argv[2])
print("cam stem rms db", 20*np.log10(arms.mean()+1e-9), " karaoke rms db", 20*np.log10(brms.mean()+1e-9))
c = ss.correlate(b, a, mode="full")  # lag where cam aligns inside karaoke
lags = np.arange(-len(a) + 1, len(b))
c /= len(a)
i = np.argmax(c); print("best lag (karaoke_t = cam_t + lag): %.3f s  score %.3f" % (lags[i] / fr, c[i]))
order = np.argsort(c)[::-1][:8]; print([(round(lags[j]/fr,2), round(float(c[j]),3)) for j in order])
# local check: windowed lags along the clip
W = int(20 * fr)
for s0 in range(0, len(a) - W, int(20 * fr)):
    seg = a[s0:s0 + W]; cc = ss.correlate(b, seg, mode="valid") / W
    j = np.argmax(cc); print("cam %6.1fs -> karaoke %6.2fs  lag %.3f score %.3f" % (s0 / fr, j / fr, (j - s0) / fr, cc[j]))
