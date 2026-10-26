"""mia-pixel-1026 (@miapixel): 'How I avoid getting sick in the cold autumn' — Downloads/монтаж пнд/mia/1.
(The Halloween makeup in the same folder is a separate video: projects/mia-pixel-1026b.)
Russian voice kept, English subtitles = hand translation (timed from the Russian words by plan_common).
IMG_4198 = on-camera hello, voice note 'Новая запись 3' = the seven habits (clean takes picked from the
phrase pass; retakes and swearing dropped) over silent b-roll, IMG_4231 / 4232 / 4235 = on-camera closing tip,
summary and goodbye (last clean take of each). Crew chatter on the b-roll is muted with all camera audio."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
TR = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
VO = next(k for k in TR if not k.startswith("IMG") and k.endswith("3"))   # 'Новая запись 3' (NFD on disk)

CFG = {
    "tag": "@miapixel",
    "music": [str(LOFI / "HoliznaCC0 - One Good Day.mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Waiting Around(LoFi, Calm).mp3").replace("\\", "/")],
    "intro": ("IMG_4198", 8.72, 30.81,
              "Hi everyone, I'm Mia, I'm an OnlyFans model and I have a vlog on OnlyFans TV. Now that the cold autumn "
              "is here, I especially want to spend more time at home, wrap up in a blanket and drink something warm. "
              "But along with the cold season comes cold and flu season. So today I want to tell you about a few "
              "simple habits that help me take care of myself and stay in shape."),
    "scenes": [
        ("Drink Water", VO, [(2.64, 9.97), (10.48, 14.91), (16.18, 21.29)],
         ["Number one: water. When it gets colder, for some reason it's much easier to forget about water, because "
          "you just don't feel as thirsty.", "So I try to keep a glass or a bottle of water next to me during the day.",
          "And if you want something warm, you can make some tea or just a warm drink."],
         [("IMG_4199", 0.5, 13.0), ("IMG_4201", 0.3, 8.0), ("IMG_4202", 0.3, 12.2)], 1),
        ("Dress for the Weather", VO, [(22.08, 28.15), (29.0, 35.47), (37.54, 41.35)],
         ["The second habit seems obvious, but sometimes we forget about it: dressing for the weather.",
          "If it's cold outside, I prefer a few comfy layers instead of freezing all day.",
          "The main thing is to feel warm and comfortable, not just look pretty."],
         [("IMG_4204", 3.0, 14.0), ("IMG_4204", 31.5, 39.5), ("IMG_4205", 1.0, 8.5)], 2),  # 4204 14-31: arms up / top changing (keep it SFW)
        ("Fresh Air", VO, [(42.58, 47.01), (65.06, 70.59)],
         ["Even when it's cold outside, I try to air out the room now and then.",
          "Fresh air at home matters too, so I don't like spending the whole day in a completely closed room."],
         [("IMG_4208", 0.5, 35.0)], 3),
        ("Eat Well", VO, [(80.94, 83.51), (83.88, 88.33), (88.5, 92.47), (93.32, 100.59)],
         ["Another important thing is eating properly.", "In autumn you really want to switch to endless sweets and treats,",
          "but I try to keep ordinary, varied food in my diet.",
          "Fruit, vegetables, a proper source of protein and simply enough food. "
          "For me, that matters much more than any complicated rules."],
         [("IMG_4213", 0.0, 6.5), ("IMG_4217", 20.0, 32.0), ("IMG_4217", 100.0, 112.0), ("IMG_4221", 1.0, 13.3)], 2),
        ("Good Sleep", VO, [(105.1, 107.21), (108.5, 112.83), (125.94, 131.85)],
         ["And probably the most important one: sleep.",
          "When I don't sleep enough for a few days in a row, I instantly feel much worse.",
          "So I try not to treat sleep as something I can sacrifice for a couple more hours of work or my phone."],
         [("IMG_4222", 0.5, 43.5), ("IMG_4223", 6.0, 15.5)], 2),
        ("Keep Moving", VO, [(133.24, 137.77), (138.34, 143.49), (144.62, 150.27)],
         ["And even when I spend most of the day at home, I try to move a little.",
          "It can be a quick stretch, a few exercises, or just walking around the apartment.",
          "You don't need a full workout, sometimes the main thing is just not to stay still all day."],
         [("IMG_4226", 0.5, 47.0)], 2),
        ("Clean Hands", VO, [(152.06, 159.37), (159.72, 163.35)],
         ["And of course, basic hygiene: washing your hands after being outside, before eating and after touching "
          "different surfaces.", "A really simple habit that's easy to keep every day."],
         [("IMG_4228", 0.5, 44.5)], 2),
    ],
    "outro": [("IMG_4231", 31.68, 46.21,
               "I also try not to ignore how I feel. If I realize I'm starting to get sick, I don't pretend that "
               "nothing is happening. Usually I give myself more time to rest, drink enough fluids and keep an eye "
               "on how I'm feeling."),
              ("IMG_4232", 46.82, 65.71,
               "If you put it all together, my main rules for the cold season are very simple: get enough sleep, "
               "drink water, eat properly, dress for the weather, air out the room, keep up hygiene and don't forget "
               "to rest. Of course, no habit gives a 100% guarantee that you won't get sick, but taking care of "
               "yourself every day is definitely worth it."),
              ("IMG_4235", 2.38, 24.3,   # keeps "Пока!" and the moment after it
               "So take care of yourselves this autumn, listen to your body and don't forget to give yourself time "
               "to rest. Thank you for spending this cozy autumn evening with me. I'm Mia, this was my vlog on "
               "OnlyFans TV. And if you want to see more of me and my content, subscribe to my OnlyFans. Take care, "
               "stay healthy, and see you in the next video. Bye!")],
    "onlyfans_at": 17.96,
}

if __name__ == "__main__":
    build(PROJ, CFG)
