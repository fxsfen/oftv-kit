"""Timeline for 'How I entertain myself when I'm bored' (@miapixel).

Russian speech is kept as is; subtitles are English (one line, <= 32 chars).
The voice-over is one recording full of retakes and swearing: LINES lists the
clean take(s) of every line (from the phrase-by-phrase large-v3 pass, retakes
found by fine-splitting long phrases) plus its English text. B-roll ranges avoid
camera speech (Silero VAD + face-crop sheets). Writes artifacts/timeline.json
and assets/analysis/subs_en.json.
"""
import json
import re
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/Новая папка (14)"
GAP = 0.4            # between VO lines
PIECE_GAP = 0.12     # between pieces of one line (retake splices)
TOPIC_TAIL = 0.6
TALK_IN, TALK_OUT = 0.3, 0.45
MAX_CHARS = 32

LINES = [  # (topic, [(a, b), ...] in the VO file, English text)
    ("music", [(2.98, 5.46)], "The first and easiest option: put on some music."),
    ("music", [(5.88, 12.66)], "Sometimes I don't need anything special. "
                               "I just put on my favorite playlist and my mood instantly gets better."),
    ("music", [(13.16, 18.76)], "Although there's a risk of turning five minutes of music into a full-on concert at home."),
    ("kitchen", [(19.68, 22.64)], "If music doesn't help, you can head to the kitchen."),
    ("kitchen", [(23.02, 27.62)], "Although it usually looks like this: you open the fridge, look..."),
    ("kitchen", [(27.98, 30.52)], "close it, and open it again five minutes later."),
    ("kitchen", [(31.26, 36.52)], "But when I actually decide to cook something, it gets way more interesting."),
    ("kitchen", [(38.34, 42.74)], "Plus, in the end I get a tasty reward for at least doing something."),
    # 50.6-56.4 is a stumbled take of the list ("...everything that... once more") — use the retake
    ("spa", [(45.20, 50.26), (56.64, 64.02)], "Another favorite way to have fun is a little spa night at home. "
                                              "Face mask, skincare, cream, hair, everything I never have time for on a normal day."),
    ("spa", [(65.92, 72.14)], "And the best part: afterwards you're not just less bored, you also feel so much better."),
    ("cleaning", [(80.78, 85.56)], "If there's nothing else to do, you can do what you'd normally put off."),
    ("cleaning", [(86.06, 87.36)], "Yes, I'm talking about cleaning."),
    # 88-114 = eight broken takes with swearing; the clean one starts after "Да ёб твою мать." (115.65)
    ("cleaning", [(115.65, 122.35)], "The funny thing is, I start cleaning out of boredom "
                                     "and end up finding things I lost a month ago."),
    ("new", [(125.18, 128.88)], "And sometimes boredom is a great excuse to try something new."),
    ("new", [(129.46, 138.58)], "You can watch an interesting movie, try a new recipe, read about something unusual, "
                                "or finally do what you've been putting off."),
    ("new", [(158.66, 166.50)], "I always have ideas I want to try, but then everyday stuff pushes them aside."),
    ("new", [(167.26, 172.82)], "So sometimes I just pick one random idea and tell myself: why not?"),
    ("book", [(174.08, 178.42)], "And if I want something really calm, I just grab a book."),
    ("book", [(185.58, 190.32)], "Sometimes I don't need more entertainment, but a little bit of quiet instead."),
    ("book", [(190.92, 194.36)], "And that's also a great way to spend your free time."),
]

TOPICS = [  # (topic, section title, b-roll ranges (clip, in, out))
    ("music", "Music On", [("IMG_2976", 2.5, 20.0), ("IMG_2983", 0.8, 5.0), ("IMG_2989", 2.5, 9.5)]),
    ("kitchen", "Kitchen Time", [("IMG_2978", 0.5, 15.0), ("IMG_3029", 2.0, 6.0), ("IMG_3027", 1.0, 4.0),
                                 ("IMG_3024", 2.0, 5.0), ("IMG_2980", 0.0, 4.0)]),
    ("spa", "Home Spa", [("IMG_2981", 10.0, 22.0), ("IMG_2981", 28.0, 40.0), ("IMG_2981", 58.0, 72.0)]),
    ("cleaning", "Cleaning Mode", [("IMG_2984", 0.0, 9.0), ("IMG_2986", 1.0, 12.0), ("IMG_2987", 3.0, 12.0),
                                   ("IMG_2991", 0.0, 10.0)]),
    ("new", "Something New", [("IMG_2990", 0.0, 10.0), ("IMG_2990", 14.0, 45.0), ("IMG_2975", 7.0, 18.0)]),
    ("book", "Book Time", [("IMG_2992", 2.0, 28.0), ("IMG_2993", 2.0, 14.0), ("IMG_2993", 19.0, 33.0)]),
]

# On-camera Russian speech: (clip, in, out, [(start, end, English sentence), ...]) in clip time
INTRO = ("IMG_2974", 26.56, 42.86, [  # second take; the first (9.4-21.1) breaks off mid-sentence
    (26.56, 28.44, "Hi everyone, I'm Mia."),
    (28.48, 31.20, "I'm an OnlyFans model with a blog on OnlyFans TV."),
    (31.28, 33.62, "And today I have a very serious problem."),
    (33.84, 34.90, "I'm bored."),
    (35.00, 42.86, "So instead of lying around all day staring at the ceiling, "
                   "I'll show you how I keep myself busy when I have nothing to do."),
])
OUTRO = [
    ("IMG_2998", 7.02, 17.84, [
        (7.02, 8.36, "You know what's funny?"),
        (8.36, 12.86, "Sometimes after all of this, I still get bored again."),
        (12.86, 17.84, "And then I just accept that today is a boring day."),
    ]),
    ("IMG_3001", 3.78, 20.10, [  # drops the aside after 22 s
        (3.78, 7.28, "Honestly, I think being bored is totally normal sometimes."),
        (7.28, 12.12, "Not every day has to be super productive and packed with events."),
        (12.12, 18.54, "Sometimes you can just dance, cook something tasty, watch a movie, read a book"),
        (18.54, 20.10, "or just do nothing at all."),
    ]),
    ("IMG_3003", 3.10, 31.88, [
        (3.10, 7.82, "Remember, free time doesn't have to be spent perfectly."),
        (7.94, 14.94, "Sometimes that's exactly when we find new hobbies, a new idea, "
                      "or just enjoy some time with ourselves."),
        (16.12, 20.22, "Thanks for being bored and having fun with me today."),
        (21.24, 23.64, "I'm Mia, this was my blog on OnlyFans TV,"),
        (23.82, 29.24, "and if you want to see more of me and my content, subscribe to my OnlyFans."),
        (29.24, 30.92, "See you in the next video."),
        (31.32, 31.88, "Bye!"),
    ]),
]
ONLYFANS_AT = 28.74  # 'OnlyFans' in IMG_3003

WEAK = {"a", "an", "the", "to", "of", "and", "or", "i", "i'm", "my", "with", "for", "in", "on", "is", "are", "be",
        "if", "so", "but", "that", "this", "your", "you", "can", "we", "it's", "some", "what", "at", "about", "just",
        "it", "me", "into", "from", "when", "do", "of", "has", "have", "i'll", "how", "every", "more", "than"}


def split_cues(text):
    """Fewest one-line cues (<= MAX_CHARS) of similar length; breaks prefer punctuation
    and never leave a short function word dangling at the end of a cue."""
    words = text.split()
    n = len(words)
    n_parts = max(1, -(-len(text) // MAX_CHARS))
    ideal = len(text) / n_parts

    def cost(i, j):  # words[i:j] as one cue
        s = " ".join(words[i:j])
        if len(s) > MAX_CHARS:
            return None
        c = (len(s) - ideal) ** 2 + 150  # every extra cue costs
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


def timed_cues(text, spans):
    """Spread cues over the spoken spans proportionally to their length; a cue
    never straddles two spans (retake splices)."""
    cues = split_cues(text)
    total = sum(e - s for s, e in spans)
    weights = [len(c) for c in cues]
    out, acc = [], 0.0
    for c, wgt in zip(cues, weights):
        d = total * wgt / sum(weights)
        a, b = acc, acc + d
        # map virtual time -> source time inside the span holding the cue's midpoint
        mid, t = (a + b) / 2, 0.0
        for s, e in spans:
            if mid <= t + (e - s) + 1e-6:
                st = s + max(0.0, a - t)
                en = s + min(e - s, b - t)
                out.append([round(st, 3), round(en, 3), c])
                break
            t += e - s
        acc = b
    return out


def energy():
    w = wave.open(str(PROJ / "assets/audio/vo_main_q.wav"))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr * 0.02)
    n = len(x) // hop
    r = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    return r


R = energy()


def quietest(t, lo, hi):
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(R) - 1, int((t + hi) / 0.02))
    return (i0 + int(np.argmin(R[i0:i1 + 1]))) * 0.02


def pieces(ranges):
    return [(round(quietest(a, -0.15, 0.06), 3), round(quietest(b, -0.06, 0.2), 3)) for a, b in ranges]


def talk_item(group, clip, s_in, s_out, extra=0.0):
    return {"group": group, "src": clip, "in": round(max(0.0, s_in - TALK_IN), 3),
            "out": round(s_out + TALK_OUT + extra, 3), "speech": True}


def main():
    video, vo, sections, subs = [], [], [], {}
    clip, s_in, s_out, sents = INTRO
    video.append(talk_item("intro", clip, s_in, s_out))
    video[-1]["pad_tail"] = 0.4  # the whip starts after her last word
    subs[clip] = [c for a, b, t in sents for c in timed_cues(t, [(a, b)])]
    subs["vo_main"] = []
    for n, (topic, title, clips) in enumerate(TOPICS, 1):
        lines = [ln for ln in LINES if ln[0] == topic]
        plan = [pieces(r) for _, r, _ in lines]
        lead = 0.5
        need = lead + sum(sum(e - s for s, e in p) + PIECE_GAP * (len(p) - 1) for p in plan) \
            + GAP * (len(plan) - 1) + TOPIC_TAIL
        avail = sum(o - i for _, i, o in clips)
        k = need / avail
        assert k <= 1, (topic, need, avail)
        first = len(video)
        for src, i, o in clips:
            length = (o - i) * k
            mid = i + (o - i) / 2
            video.append({"group": "main", "src": src, "in": round(mid - length / 2, 3),
                          "out": round(mid + length / 2, 3)})
        t = lead
        for (_, _, text), p in zip(lines, plan):
            for s, e in p:
                vo.append({"src": "vo_main", "in": s, "out": e, "item": first, "offset": round(t, 3)})
                t += (e - s) + PIECE_GAP
            t += GAP - PIECE_GAP
            subs["vo_main"] += timed_cues(text, p)
        sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
    first = len(video)
    for clip, s_in, s_out, sents in OUTRO:
        video.append(talk_item("outro", clip, s_in, s_out, extra=0.8 if clip == OUTRO[-1][0] else 0.0))
        subs[clip] = [c for a, b, t in sents for c in timed_cues(t, [(a, b)])]
    sections.append({"index": len(TOPICS) + 1, "label": "Part", "title": "Final Thoughts", "item": first,
                     "offset": 0.6})
    last = len(video) - 1

    srcs = {v["src"] for v in video}
    tl = {
        "tag": "@miapixel",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": round(ONLYFANS_AT - video[last]["in"], 3),
                         "note": "'подписывайтесь на мой OnlyFans'"}],
        "music": [f"{SRC}/Lazy Walk - Cheel.mp3", f"{SRC}/On The Flip - The Grey Room _ Density & Time (2).mp3"],
        "sources": {**{c: f"{SRC}/{c}.MOV" for c in srcs}, "vo_main": f"{SRC}/Новая запись 3.m4a"},
        "transcript_keys": {**{c: c for c in srcs}, "vo_main": "vo_main"},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} vo_pieces={len(vo)} sections={[s['title'] for s in sections]} "
          f"~duration={tot:.1f}s longest_cue={len(longest[2])} '{longest[2]}'")


if __name__ == "__main__":
    main()
