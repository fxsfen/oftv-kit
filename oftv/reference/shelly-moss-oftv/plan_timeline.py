"""Timeline for 'What makes a great detective story' (@shelly_moss).

21 single-take talking clips (one sentence each, same 4K setup). Order = shooting order.
Intro -> five parts -> final thoughts; whips only intro->main and main->outro.
Jump cuts between consecutive clips alternate a 1.08 punch-in so every cut reads as a cut.
Subtitles = the spoken words with Whisper slips fixed ("clothes" -> "clues"), one line <= 32 chars.
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import re
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "шелли2"][0]
TALK_IN, TALK_OUT = 0.3, 0.35
MAX_CHARS = 32
ZOOM = 1.08

# (clip, group, section title or None, in override, out override, clean text)
CLIPS = [
    ("IMG_1552", "intro", None, 0.0, None,
     "Hi everyone, I'm Shelly, I'm a model and an OnlyFans creator, and welcome to my blog."),
    ("IMG_1554", "intro", None, None, None, "Today I want to talk about something I really love: detective stories."),
    ("IMG_1556", "intro", None, None, None,
     "I've always loved stories that make me think and try to guess what will happen next. "
     "So today I want to talk about what makes a detective story really good."),
    ("IMG_1557", "main", "A Good Mystery", None, None,
     "For me, the first thing is a good mystery. At the start of the story I want to have questions."),
    ("IMG_1558", "main", None, None, None,
     "Who did it? Why did they do it? What really happened? I like when the story gives me some clues, "
     "but not all the answers."),
    ("IMG_1560", "main", None, None, None, "I want to think about the clues and try to solve the mystery myself."),
    ("IMG_1562", "main", "Smart Clues", None, None,
     "The second thing is good clues. I love when small details have meaning later in the story."),
    ("IMG_1563", "main", None, None, None, "Maybe someone says something strange, or we see something very small."),
    ("IMG_1564", "main", None, None, None,
     "At first it may not seem important, but later you'll understand why it was there. "
     "That is always very satisfying for me."),
    ("IMG_1566", "main", "A Good Twist", None, None,
     "The third thing is a good twist. I love when I think I know what happened, and then the story "
     "changes everything."),
    ("IMG_1567", "main", None, None, None, "The best twist makes sense when you think about the story again."),
    ("IMG_1570", "main", None, None, None,
     "I don't like twists that come from nowhere. I want to be surprised, but I also want the story to make sense."),
    ("IMG_1574", "main", "Real Characters", None, None,
     "Another important thing is the characters. I want the characters to feel real. I like when every person "
     "has their own story and their own secrets."),
    ("IMG_1578", "main", None, None, None,
     "Sometimes the person who looks innocent is not innocent at all. And sometimes the person who looks "
     "suspicious is actually innocent. That makes the story much more interesting."),
    ("IMG_1580", "main", "The Ending", None, None,
     "And of course, I need a good ending. I want to understand what happened and why. "
     "I don't need everything to be happy."),
    ("IMG_1583", "main", None, None, None,
     "But I want the ending to feel right. A good ending can make me love the whole story even more."),
    ("IMG_1584", "outro", "Final Thoughts", 2.5, None,
     "So, my perfect detective story needs a good mystery, smart clues, interesting characters "
     "and a surprising ending."),
    ("IMG_1585", "outro", None, None, None,
     "Most of all, I want a story that makes me think. If I keep thinking about the story after I finish it, "
     "then I know it was a good one."),
    ("IMG_1586", "outro", None, None, None,
     "So that's what makes a great detective story for me. I love stories that make me ask questions, "
     "look for clues and change my mind."),
    ("IMG_1588", "outro", None, None, 10.70,
     "I'm Shelly, and thank you for spending these few minutes with me. If you want to see more of me "
     "and my content, you can find me on OnlyFans."),
    # runs on through the bye + blown kiss to the end of the take
    ("IMG_1589", "outro", None, None, 7.15, "I will see you in my next video. Bye!"),
]
ONLYFANS = ("IMG_1588", 9.46)

WEAK = {"a", "an", "the", "to", "of", "and", "or", "i", "i'm", "my", "with", "for", "in", "on", "is", "are", "be",
        "if", "so", "but", "that", "this", "your", "you", "can", "we", "it's", "some", "what", "at", "about", "just",
        "it", "me", "into", "from", "when", "do", "has", "have", "i'll", "how", "every", "more", "than", "her",
        "she", "she's", "those", "such", "let", "us", "our"}


def split_cues(text):
    """Fewest balanced one-line cues (<= MAX_CHARS) via DP; breaks prefer punctuation and
    never leave a short function word dangling at the end of a cue."""
    words = text.split()
    n = len(words)
    ideal = len(text) / max(1, -(-len(text) // MAX_CHARS))

    def cost(i, j):
        s = " ".join(words[i:j])
        if len(s) > MAX_CHARS:
            return None
        c = (len(s) - ideal) ** 2 + 150
        if re.search(r"[.!?]\s", s):  # never glue the end of one sentence to the next
            c += 600
        last = words[j - 1]
        if j < n:
            if last.lower().strip(",.!?:") in WEAK:
                c += 400
            if re.search(r"[,.!?:]$", last):
                c -= 120
        return c

    best = [0.0] + [None] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j):
            c = cost(i, j)
            if c is None or best[i] is None:
                continue
            if best[j] is None or best[i] + c < best[j]:
                best[j], back[j] = best[i] + c, i
    parts, j = [], n
    while j > 0:
        parts.insert(0, " ".join(words[back[j]:j]))
        j = back[j]
    return parts


def timed_cues(text, spans, words=None):
    """Time cues from the real word timestamps when given (word count alignment),
    else spread proportionally; a cue never straddles two spans (splices)."""
    cues = split_cues(text)
    if words:
        ws = [w for w in words if any(s - 0.05 <= w["start"] < e for s, e in spans)]
        n_txt = sum(len(c.split()) for c in cues)
        out, k = [], 0
        for c in cues:
            cnt = len(c.split())
            a = round(k * len(ws) / n_txt)
            b = max(a + 1, round((k + cnt) * len(ws) / n_txt))
            seg = ws[a:min(b, len(ws))] or ws[-1:]
            out.append([round(seg[0]["start"], 3), round(seg[-1]["end"], 3), c])
            k += cnt
        return out
    total = sum(e - s for s, e in spans)
    out, acc = [], 0.0
    for c in cues:
        d = total * len(c) / sum(len(x) for x in cues)
        a, b = acc, acc + d
        mid, t = (a + b) / 2, 0.0
        for s, e in spans:
            if mid <= t + (e - s) + 1e-6:
                out.append([round(s + max(0.0, a - t), 3), round(s + min(e - s, b - t), 3), c])
                break
            t += e - s
        acc = b
    return out




def main():
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    bounds = json.load(open(PROJ / "assets/analysis/speech_bounds.json", encoding="utf-8"))
    video, sections, subs = [], [], {}
    prev_group, z = None, False
    for clip, group, title, a, b, text in CLIPS:
        bd, ws = bounds[clip], tr[clip]
        s_in = a if a is not None else max(0.0, bd["speech_in"] - TALK_IN)
        s_out = b if b is not None else min(bd["dur"], max(bd["speech_out"], ws[-1]["end"]) + TALK_OUT)
        # punch-in alternates inside a group; a whip or a new part resets to the wide shot
        z = False if (group != prev_group or title) else not z
        it = {"group": group, "src": clip, "in": round(s_in, 3), "out": round(s_out, 3), "speech": True}
        if z:
            it["zoom"] = ZOOM
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video),
                             "offset": 0.15})
        video.append(it)
        prev_group = group
        subs[clip] = timed_cues(text, [(0.0, bd["dur"])], ws)  # words at 0.0 sit before s_in
    # a whip needs >= 0.5 s of silence: freeze the last frame of each outgoing group
    for i in range(len(video) - 1):
        if video[i]["group"] != video[i + 1]["group"]:
            video[i]["pad_tail"] = 0.4
    video[-1]["pad_tail"] = 1.0  # let the music breathe after the kiss
    of_item = next(i for i, v in enumerate(video) if v["src"] == ONLYFANS[0])
    tl = {
        "tag": "@shelly_moss",
        "tag_at": 0.8,
        "tag_repeats": [{"item": of_item, "offset": round(ONLYFANS[1] - video[of_item]["in"], 3),
                         "note": "'you can find me on OnlyFans'"}],
        "music": [str(SRC / "Moonlit - Dyalla.mp3").replace("\\", "/"),
                  str(SRC / "Cooked - Dyalla (1) (1).mp3").replace("\\", "/")],
        "sources": {v["src"]: str(SRC / f"{v['src']}.MOV").replace("\\", "/") for v in video},
        "video": video,
        "vo": [],
        "sections": sections,
        "word_edits": {"clothes": "clues", "shelley": "Shelly", "we say something": "we see something"},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s "
          f"longest_cue={len(longest[2])} '{longest[2]}'")
    for k, v in subs.items():
        for c in v:
            print(k, c)


if __name__ == "__main__":
    main()
