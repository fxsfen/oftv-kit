"""Build assets/analysis/subs_en.json (cue format of the renderer) from
transcripts.json written by plan_timeline.py: synthetic VO words for the kept
takes + large-v3 words of the English on-camera lines."""
import json
import re
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
MAX_CHARS = 32
FIXES = {"Misa,": "Misa,", "OnlyFans.": "OnlyFans."}


WEAK = {"a", "an", "the", "to", "of", "and", "or", "i", "i'm", "my", "with", "for", "in", "on", "is", "are",
        "be", "if", "so", "but", "that", "this", "your", "you", "can", "we", "it's", "some", "what"}


def text_of(ws):
    return " ".join(x["word"].strip() for x in ws)


def balanced(words):
    """Split one sentence into the fewest one-line cues of similar length,
    preferring breaks after commas and never after a weak word."""
    n = max(1, -(-len(text_of(words)) // MAX_CHARS))
    while True:
        target = len(text_of(words)) / n
        parts, cur = [], []
        for i, w in enumerate(words):
            cur.append(w)
            left = len(words) - i - 1
            if len(parts) < n - 1 and left and len(text_of(cur)) >= target * 0.85:
                t = w["word"].strip()
                nxt_len = len(text_of(cur + [words[i + 1]]))
                good = t.lower().strip(",.!?") not in WEAK
                if good and (t.endswith(",") or nxt_len > target * 1.15 or len(text_of(cur)) >= target):
                    parts.append(cur)
                    cur = []
        parts.append(cur)
        if all(len(text_of(p)) <= MAX_CHARS + 4 for p in parts) or n > 6:
            return [p for p in parts if p]
        n += 1


def cues(words, use_gaps=True):
    out, sent = [], []
    for i, w in enumerate(words):
        sent.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if (nxt and use_gaps) else (9 if not nxt else 0)
        if re.search(r"[.!?]$", w["word"].strip()) or gap > 0.6 or not nxt:
            for p in balanced(sent):
                out.append([round(p[0]["start"], 3), round(p[-1]["end"], 3), text_of(p)])
            sent = []
    return out


def cues_old(words, use_gaps=True):
    """One-line cues (<= MAX_CHARS): break at sentence ends, commas or pauses,
    and never leave a short function word dangling at the end of a line."""
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and len(text_of(cur + [w])) > MAX_CHARS:
            carry = []
            while len(cur) > 1 and cur[-1]["word"].strip().lower().strip(",.!?") in WEAK:
                carry.insert(0, cur.pop())
            out.append([round(cur[0]["start"], 3), round(cur[-1]["end"], 3), text_of(cur)])
            cur = carry
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        # VO lines are spliced from several takes: source-time gaps there are
        # splice points, not pauses, so only on-camera speech breaks on gaps.
        gap = (nxt["start"] - w["end"]) if (nxt and use_gaps) else (9 if not nxt else 0)
        t = w["word"].strip()
        if re.search(r"[.!?]$", t) or gap > 0.6 or (t.endswith(",") and len(text_of(cur)) >= 14):
            out.append([round(cur[0]["start"], 3), round(cur[-1]["end"], 3), text_of(cur)])
            cur = []
    if cur:
        out.append([round(cur[0]["start"], 3), round(cur[-1]["end"], 3), text_of(cur)])
    return out


def main():
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    tl = json.load(open(PROJ / "artifacts/timeline.json", encoding="utf-8"))
    db = {}
    for k, v in tr.items():
        if k == "vo_main":
            db[k] = cues(v, use_gaps=False)
            continue
        # on-camera: only words inside the ranges actually used, one cue run per range
        db[k] = []
        for it in tl["video"]:
            if it["src"] == k and it.get("speech"):
                ws = [w for w in v if w["start"] >= it["in"] - 0.05 and w["end"] <= it["out"] + 0.15]
                db[k] += cues(ws)
    # tidy the on-camera lines (Whisper casing / small slips)
    for k in db:
        for c in db[k]:
            c[2] = c[2].replace("bye everyone", "bye, everyone!").replace("in the my next", "in my next")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(db, indent=1, ensure_ascii=False), encoding="utf-8")
    for k, v in db.items():
        print(k, len(v), v[:2])


if __name__ == "__main__":
    main()

