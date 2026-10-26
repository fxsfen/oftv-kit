import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
res = {}
for f in sys.argv[2:]:
    segs, info = m.transcribe(f, language="en", vad_filter=False, word_timestamps=True, condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in s.words: words.append([round(w.start, 2), round(w.end, 2), w.word])
        print("%7.2f %7.2f %s" % (s.start, s.end, s.text))
    res[f] = words
json.dump(res, open(sys.argv[1], "w"), indent=0)
