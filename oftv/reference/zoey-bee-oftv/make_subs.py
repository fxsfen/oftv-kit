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


FIXES = [(r"\bZoe\b", "Zoey"), (r"\bZoya\b", "Zoey"), (r"\b(Lila|Leila|Lilo|Leela|Lilu)\b", "Leeloo"),
         (r"\b5th [Ee]lement", "Fifth Element"), (r"\bthird little\b", "weird little"),
         (r"\bI wore the girl\b", "I was the girl"), (r"\bOFTV\.", "OFTV.")]


def main():
    words = json.load(open(PROJ / "assets/analysis/words_phr.json", encoding="utf-8"))["zzz"]
    tl = json.load(open(PROJ / "artifacts/timeline.json", encoding="utf-8"))
    out = []
    for it in tl["video"]:
        ws = [w for w in words if w["start"] >= it["in"] - 0.05 and w["end"] <= it["out"] + 0.1]
        out += cues(ws)
    # the kept retake "And I was wearing this." was attributed to the dropped take by Whisper
    out.append([26.78, 28.28, "And I was wearing this."])
    out.sort(key=lambda c: c[0])
    for c in out:
        for pat, rep in FIXES:
            c[2] = re.sub(pat, rep, c[2])
        c[2] = {"somehow it felt": "And somehow it felt", "And I'll put it.": "And opened it.",
                "But honestly, I'm not.": "But honestly, I'm not", "Complain.": "complaining.",
                "I'm Zoy.": "I'm Zoey."}.get(c[2], c[2])
        c[2] = c[2].replace("lila costume", "little costume").replace("running a road", "running around")
    # glue dangling one-word tails ("party.", "video.") onto the previous line
    merged = []
    for c in out:
        if merged and len(c[2]) <= 8 and not c[2][:1].isupper() and len(merged[-1][2]) + len(c[2]) + 1 <= 42 \
                and c[0] - merged[-1][1] < 0.6:
            merged[-1] = [merged[-1][0], c[1], merged[-1][2] + " " + c[2]]
        else:
            merged.append(list(c))
    out = merged
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps({"zzz": out}, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    print(len(out), max(len(c[2]) for c in out))
    for c in out:
        print(f"{c[0]:7.2f} {c[2]}")


if __name__ == "__main__":
    main()

