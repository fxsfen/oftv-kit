"""Guion 30 (@bela_cruz): 5-minute gentle yoga. See plan_common.py.
All takes are silent (VAD); face close-ups e2t3 / e6t3 left out, e4t4 cut before she looks into the lens."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
MUS = "C:/Users/fosfe/Downloads/ана2/OFTV 27-20261019T165215Z-1-001/OFTV 27/Sound Of Freedom - "

CFG = {
    "tag": "@bela_cruz",
    "music": [MUS + "Lo-Fi R&B Vibe.mp3.mp3", MUS + "Jazzy Rhodes Deep House.mp3.mp3"],
    "intro": ("e1", 2.0, 20.45,
              "Hi everyone, I'm Bela, I'm an OnlyFans model and I have my own blog on OFTV. "
              "Today I invite you to do a short, five-minute gentle yoga session together. "
              "No complicated exercises, just calm movements, breathing and a few minutes for ourselves. "
              "Let's begin!"),
    "scenes": [
        ("Breathing", "vo2", [(0.74, 21.67), (22.98, 31.97)],
         "Let's start with breathing. Sit comfortably and relax your shoulders. "
         "Take a slow breath in through your nose, and then a calm, long breath out. There's no need to rush. "
         "Throughout the practice, try to move gently and avoid any position that feels uncomfortable. "
         "Now we'll add some gentle torso rotations. The movement is small. "
         "Our goal is simply to wake the body up a little.",
         [("e2t1", 0, 9.92), ("e2t2", 0, 16.02), ("e2t4", 0, 10.55)]),
        ("Neck & Shoulders", "vo3", [(1.06, 26.45)],
         "Now let's pay a little attention to the neck and shoulders. Slowly lower your chin, "
         "and then bring your head back to a neutral position. Lift your shoulders up and then relax them. "
         "Repeat a few times and feel the tension slowly fade away. Stretch your arms up, breathe in, "
         "and as you breathe out, lower them gently.",
         [("e3t1", 0, 12.79), ("e3t2", 0, 8.85), ("e3t3", 0, 10.22), ("e3t4", 0, 13.21)]),
        ("On All Fours", "vo4", [(1.48, 25.31)],
         "Now let's move onto all fours. Place your palms under your shoulders and your knees under your hips. "
         "As you breathe in, gently open your chest and arch your back a little. "
         "As you breathe out, round your back and relax your neck. "
         "Repeat the movement a few times at a comfortable pace. "
         "What matters here isn't depth, but smoothness.",
         [("e4t1", 0, 6.29), ("e4t2", 0, 16.21), ("e4t3", 0, 12.14), ("e4t4", 0, 2.5)]),
        ("Leg Stretch", "vo5", [(0.50, 20.11)],
         "Now let's stretch the back of the legs a little. Extend one leg and gently lean forward. "
         "You don't need to try to touch your foot with your hands. Stop where you feel a comfortable stretch. "
         "Take a few calm breaths, and then switch sides.",
         [("e5t1", 0, 5.63), ("e5t2", 0, 9.09), ("e5t3", 0, 10.74), ("e5t4", 0, 9.44)]),
        ("Time to Relax", "vo6", [(1.18, 19.03)],
         "And finally, simply stop. Lie down comfortably and relax your shoulders and arms. "
         "Take one last deep breath in and a slow breath out. "
         "Give yourself a few seconds to do nothing and simply feel your body relax.",
         [("e6t1", 0, 7.3), ("e6t2", 0, 14.86)]),
    ],
    "outro": ("e7", 2.7, 27.9,
              "And that's it, just about five minutes of gentle movement, breathing and calm stretching. "
              "I hope this little practice helped you slow down a bit and take a few moments for yourselves. "
              "Thank you for spending these five minutes with me. I'm Bela, this was my blog on OFTV. "
              "If you want to see more of me and my content, you can subscribe to my OnlyFans. "
              "Take good care of yourselves and see you in the next video."),
    "onlyfans_at": 23.94,
}

if __name__ == "__main__":
    build(PROJ, CFG)
