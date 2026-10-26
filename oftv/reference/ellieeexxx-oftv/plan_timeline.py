"""ellieeexxx (@ellieeexxx), 'монтаж пт': Alice in Wonderland Halloween costume. Spanish speech kept, English subs
(hand translation timed from the Spanish words). Intro IMG_1070 + goodbye IMG_1084 on camera, four voice notes over
the silent try-on footage. B-roll trimmed off where she leans/reaches into the lens (1074 0-3 and 15+, 1075 38+,
1081 3-6, 1083 10-14 and 21+). VO 'Eh...' and the doubled 'les mando un beso enorme y gracias...' in the goodbye
are cut (the last take with the blown kiss is kept)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import plan_common  # noqa: E402

plan_common.MIN_SPEED = 0.72
PROJ = Path(__file__).resolve().parents[1]
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
V1, V2, V3, V4 = ("audio_2026-10-23_13-21-35", "audio_2026-10-23_13-21-45", "audio_2026-10-23_13-21-50",
                  "audio_2026-10-23_13-21-55")

CFG = {
    "tag": "@ellieeexxx",
    "music": [str(LOFI / "HoliznaCC0 - Dreamy Reverie(Lofi, Nostalgic, Chill).mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Wave Maker(Lofi, Dreamy, Retro).mp3").replace("\\", "/")],
    "intro": ("IMG_1070", 0.4, 27.75,
              "Hi, how are you? I'm Ellie, an OnlyFans model. Welcome back to a new video of mine on OFTV. "
              "Since Halloween is coming up, today I want to show you what my Halloween costume is going to be. "
              "This time it's going to be Alice in Wonderland, and I'll show you in detail what the costume looks like."),
    "scenes": [
        ("Skirt & Top", V1, [(1.52, 19.89), (21.62, 30.31)],
         "Let's start with the main part of the look: the blue skirt and the matching top. "
         "I chose this shade of blue because it instantly reminds me of Alice's classic look. "
         "I love how the skirt gives the outfit a very feminine and playful touch. "
         "The truth is, even though blue is the main color, the little details are what really make it look like "
         "a Halloween costume.",
         [("IMG_1074", 3.0, 14.5), ("IMG_1075", 0.0, 20.0)]),
        ("Arm Details", V2, [(0.52, 16.85)],
         "Now let's talk about the details I'm wearing on my arms. These accessories make the look much more "
         "interesting and help give it that touch of fantasy. I really like how they complement the blue of the "
         "outfit without stealing the spotlight.",
         [("IMG_1075", 20.0, 38.0), ("IMG_1083", 14.0, 21.0)]),
        ("The Headband", V3, [(1.12, 20.59)],
         "And of course, we can't forget the hair accessory. I think this is one of the most important details, "
         "because it makes the character instantly recognizable. Without this accessory the look would be pretty, "
         "but with it, it really feels like Alice in Wonderland.",
         [("IMG_1080", 0.0, 32.6)]),
        ("The Full Look", V4, [(1.26, 24.97)],
         "And now let's see the full look. I love how all the elements work together. It's feminine, playful, "
         "and it has that little touch of fantasy that's perfect for Halloween. I think Alice in Wonderland is a "
         "really cute option if you want to dress up as something classic that still looks special.",
         [("IMG_1081", 6.0, 15.1), ("IMG_1083", 0.0, 9.5)]),
    ],
    "outro": [
        ("IMG_1084", 0.9, 40.52,
         "Well, this has been my Alice in Wonderland look for this Halloween. I think I'm ready to literally step "
         "into Wonderland. I hope you liked all the details of the costume and the whole design. And if you want to "
         "see more of my exclusive content, you can visit my OnlyFans, follow me and subscribe, and if you like my "
         "OFTV content, you can subscribe and keep watching my videos.", True),
        ("IMG_1084", 48.54, 53.7, "I'm sending you a big kiss, and thank you for everything!", True),
    ],
    "onlyfans_piece": 0,
    "onlyfans_at": 31.4,   # into IMG_1084 (first outro piece): '...pueden entrar a mi OnlyFans'
}

if __name__ == "__main__":
    plan_common.build(PROJ, CFG)
