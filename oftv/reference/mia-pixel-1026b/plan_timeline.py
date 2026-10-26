"""mia-pixel-1026b (@miapixel): Halloween makeup with Saw-style cheek swirls and lipstick 'blood' —
Downloads/монтаж пнд/mia/видео макияж hallowin (the autumn-habits video from the same folder is mia-pixel-1026).
Russian voice kept, English subtitles = hand translation per clean take. IMG_4282 = on-camera hello (two parts with a
pause -> jump cut), voice note 'Новая запись 2' = the steps (last clean take of each line; retakes, swearing and
'ещё раз' dropped) over the silent makeup footage, IMG_4272 / 4274 / 4277 = final look, tip and goodbye."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
TR = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
VO = next(k for k in TR if not k.startswith("IMG") and k.endswith("2"))   # 'Новая запись 2' (NFD on disk)

CFG = {
    "tag": "@miapixel",
    "music": [str(LOFI / "HoliznaCC0 - Never Sleeping(Lofi, Dark, Sad).mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Fractured.mp3").replace("\\", "/")],
    "intro": [("IMG_4282", 1.74, 10.99,
               "Hi everyone, I'm Mia, I'm an OnlyFans model and I have a vlog on OnlyFans TV. Halloween is almost "
               "here, so today I decided to do a slightly unusual makeup look."),
              ("IMG_4282", 15.34, 26.65,
               "I want to add a few creepy details to my usual pretty makeup: swirls on the cheeks and a little "
               "blood on the lips. So let's see how I create this Halloween look from scratch.")],
    "scenes": [
        ("Skin Prep", VO, [(4.56, 11.21), (12.58, 17.27), (18.86, 24.17)],
         ["I'll start with skin prep. Before makeup, I like to moisturize my face well, so the base looks neat "
          "and natural.", "Now I'm evening out my skin tone and adding a little concealer where it's needed.",
          "I don't want the makeup too heavy, because we'll have plenty of bright details later."],
         [("IMG_4248", 10.0, 22.0), ("IMG_6103", 5.0, 17.0), ("IMG_4249", 40.0, 52.0), ("IMG_6104", 10.0, 20.0)], 1),
        ("Brows & Eyes", VO, [(28.6, 35.05), (40.92, 45.61), (55.0, 60.37)],
         ["Today I want to keep the brows and eyes fairly classic, just beautifully defined, the way I usually "
          "do them.", "I'll add a little eyeshadow, define the lashes and make the eyes more expressive.",
          "I like it when even Halloween makeup stays pretty instead of turning into full-on costume makeup."],
         [("IMG_4250", 10.0, 25.0), ("IMG_4251", 5.0, 20.0), ("IMG_4252", 30.0, 45.0), ("IMG_4252", 60.0, 75.0)], 1),
        ("Red Lips", VO, [(62.0, 67.01), (72.5, 78.83)],
         ["And now one of the most important parts of the look: red lips.",
          "I want them bright and rich, because together with the blood they'll be the main accent."],
         [("IMG_4254", 80.0, 100.0), ("IMG_4254", 190.0, 210.0), ("IMG_4254", 240.0, 255.0)], 2),
        ("Dripping Blood", VO, [(80.18, 83.11), (88.22, 94.89), (96.76, 100.47)],
         ["Now I'm adding blood drips with eyeshadow.",
          "I'm not making the lines perfectly even on purpose. I want it to look like the lipstick just started "
          "to run.", "And now the look instantly becomes much more Halloween."],
         [("IMG_4257", 100.0, 115.0), ("IMG_4257", 300.0, 315.0), ("IMG_4257", 500.0, 515.0),
          ("IMG_4257", 525.0, 540.0)], 2),
        ("Saw Swirls", VO, [(102.84, 106.37), (123.1, 127.19), (136.96, 144.07), (144.98, 149.93)],
         ["But the main detail of my look is these swirls on the cheeks.",
          "I want them to look like the iconic pattern from Saw.",
          "First I try to make the basic shape, and then I add details, so both sides look as neat as possible.",
          "And the best part: just a few lines, and the face already looks completely different."],
         [("IMG_4261", 50.0, 62.0), ("IMG_4261", 420.0, 435.0), ("IMG_6106", 3.0, 15.0), ("IMG_4262", 85.0, 97.0),
          ("IMG_6107", 20.0, 32.0), ("IMG_4263", 0.0, 13.0), ("IMG_4264", 0.0, 21.0)], 2),
        ("Final Details", VO, [(159.72, 162.59), (162.86, 166.65), (171.66, 179.35)],
         ["Now I just have to check all the little things.",
          "I'll fix the lines a bit, add a couple more details, and that's it.",
          "I love that the base stays fairly simple and pretty, while a few details completely change the mood "
          "of the makeup."],
         [("IMG_4265", 0.0, 23.8)], 3),
    ],
    "outro": [("IMG_4272", 15.26, 17.83, "So, my Halloween makeup is ready."),
              ("IMG_4272", 20.7, 28.93,
               "Saw-style swirls, bright red lips and a little blood. I think it turned out scary enough, "
               "but still pretty."),
              ("IMG_4274", 3.66, 22.25,
               "I think the most fun thing about Halloween is the chance to try a look you'd never do in everyday "
               "life. And even if you don't want to recreate this exact makeup, you can take just one detail, like "
               "red lipstick, an unusual drawing or a little fake blood, and you'll get a completely different mood."),
              ("IMG_4277", 4.96, 18.9,   # keeps the moment after "Happy Halloween!"
               "Thank you for celebrating Halloween with me. I'm Mia, this was my vlog on OnlyFans TV. And if you "
               "want to see more of me and my content, subscribe to my OnlyFans. See you in the next video. "
               "Happy Halloween!")],
    "onlyfans_at": 13.88,
}

if __name__ == "__main__":
    build(PROJ, CFG)
