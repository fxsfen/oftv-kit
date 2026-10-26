"""One-line subtitle cue splitting/timing (from shelly-moss-oftv plan_timeline.py)."""
import re
MAX_CHARS = 32

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






def timed_cues_xl(text, words):
    """Translated cues timed from the source-language words by character fraction:
    an English cue covering chars [a, b) of the English text maps to the Spanish words at the
    same fraction of the Spanish text (more robust than word counts across languages)."""
    cues = split_cues(text)
    ws = [w for w in words if w["word"].strip()]
    lens = [len(w["word"].strip()) + 1 for w in ws]
    tot_src = sum(lens)
    cum, acc = [], 0
    for L in lens:
        cum.append((acc, acc + L))
        acc += L
    tot_en = sum(len(c) + 1 for c in cues)
    out, pos = [], 0
    for c in cues:
        a, b = pos / tot_en, (pos + len(c) + 1) / tot_en
        pos += len(c) + 1
        i = next(k for k, (s, e) in enumerate(cum) if e / tot_src > a + 1e-9)
        j = next((k for k, (s, e) in enumerate(cum) if e / tot_src >= b - 1e-9), len(ws) - 1)
        j = max(i, j if (cum[j][0] / tot_src) < b - 0.35 * lens[j] / tot_src else max(i, j - 1)) \
            if j < len(ws) - 1 else j
        out.append([round(ws[i]["start"], 3), round(ws[j]["end"], 3), c])
    for k in range(1, len(out)):  # no overlaps, keep order
        out[k][0] = max(out[k][0], out[k - 1][1])
        out[k][1] = max(out[k][1], out[k][0] + 0.3)
    return out
