"""Timeline for 'Five flowers I would never buy for myself' (@shelly_moss).

26 single-take talking clips (one line each, same 4K setup); IMG_1524 is a repeat take of IMG_1523 (dropped).
Intro -> five flowers -> final thoughts; whips only intro->main and main->outro.
Jump cuts between consecutive clips alternate a 1.08 punch-in so every cut reads as a cut.
Subtitles = the spoken words with Whisper slips fixed ("resin timers" -> "chrysanthemums",
"overheads" -> "orchids", "flower regiment" -> "flower arrangement"), one line <= 32 chars.
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import re
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "шелли 1"][0]
TALK_IN, TALK_OUT = 0.3, 0.35
MAX_CHARS = 32
ZOOM = 1.08

# (clip, group, section title or None, in override, out override, clean text)
CLIPS = [
    ("IMG_1508", "intro", None, None, None,
     "Hi everyone, I'm Shelly, I'm a model and an OnlyFans creator, and I'm also a florist. Welcome to my vlog."),
    ("IMG_1509", "intro", None, None, None,
     "Today I want to talk about flowers. I'm going to tell you about five flowers I would never buy for myself."),
    ("IMG_1512", "intro", None, None, None,
     "This doesn't mean they are bad flowers. They are just my personal choice."),
    ("IMG_1513", "main", "The Lily", None, None,
     "The first flower is the lily. I think lilies are very beautiful. They look elegant and special."),
    ("IMG_1514", "main", None, None, None,
     "But I don't really like their strong smell. When I work with lilies, I can smell them all day."),
    ("IMG_1515", "main", None, None, None, "So I like looking at them, but I wouldn't buy them for my home."),
    ("IMG_1517", "main", "The Sunflower", None, None,
     "The second flower is the sunflower. I know many people love sunflowers. They are bright and happy. "
     "I also think they look beautiful in a field."),
    ("IMG_1518", "main", None, None, None,
     "But they're just not my style. When I buy flowers for myself, I usually choose something smaller and more soft."),
    ("IMG_1519", "main", None, None, None, "So I wouldn't choose sunflowers for my own bouquet."),
    ("IMG_1520", "main", "The Carnation", None, None,
     "The third flower is a carnation. Carnations are actually very useful for florists."),
    ("IMG_1521", "main", None, None, None,
     "They can last for a long time and they come in many colors. I use them in flower arrangements, "
     "and I know they're a good flower."),
    ("IMG_1522", "main", None, None, None,
     "But I don't really want them for myself. If I buy flowers for my home, I usually choose something else."),
    # IMG_1524 is a second take of the same line — 1523 is used
    ("IMG_1523", "main", "The Chrysanthemum", None, None,
     "The fourth flower is the chrysanthemum. There are so many kinds of chrysanthemums. "
     "They come in many colors and shapes."),
    ("IMG_1525", "main", None, None, None,
     "They are also very useful when you make a big flower arrangement, but for myself I usually want "
     "something more simple and romantic."),
    ("IMG_1526", "main", None, None, None, "So chrysanthemums are not my first choice."),
    ("IMG_1527", "main", "The Orchid", None, None,
     "And the last flower is the orchid. I think orchids are very beautiful. They look elegant, "
     "and they can make your room look very nice."),
    ("IMG_1528", "main", None, None, None,
     "But for me, they feel a little too formal. I like flowers that feel more natural and relaxed."),
    ("IMG_1529", "main", None, None, None, "So I can enjoy orchids, but I would probably not buy one for myself."),
    ("IMG_1530", "outro", "Final Thoughts", None, None,
     "Of course, I don't think these flowers are bad. As a florist, I know that every flower can be beautiful."),
    ("IMG_1532", "outro", None, None, None,
     "It is just about personal taste. A flower I don't like for myself can be someone else's favorite flower."),
    ("IMG_1533", "outro", None, None, None, "And I think that is what makes flowers so interesting."),
    ("IMG_1534", "outro", None, None, None,
     "So these are the five flowers I would never buy for myself, but I still think they are beautiful, "
     "and I love working with them as a florist."),
    ("IMG_1537", "outro", None, None, None, "I think flowers are very personal. Everyone has their own favorite."),
    ("IMG_1539", "outro", None, None, None,
     "I'm Shelly, thank you for spending these few minutes with me. And if you want to see more of me "
     "and my content, you can find me on OnlyFans."),
    # runs on through the bye + blown kiss to the end of the take
    ("IMG_1540", "outro", None, None, 7.55, "I will see you in my next video, bye!"),
]
ONLYFANS = ("IMG_1539", 9.42)

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
        "music": [str(SRC / "YuraSoop - Lo-Fi Spring Mood .mp3.mp3").replace("\\", "/"),
                  str(SRC / "Yeah Smoove Smoove - Karneef.mp3").replace("\\", "/")],
        "sources": {v["src"]: str(SRC / f"{v['src']}.MOV").replace("\\", "/") for v in video},
        "video": video,
        "vo": [],
        "sections": sections,
        "word_edits": {"resin timers": "chrysanthemums", "overheads": "orchids", "regiment": "arrangement", "show sunflowers from": "choose sunflowers for", "normal personal": "my personal", "first flower is the chrysanthemum": "fourth flower"},
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
