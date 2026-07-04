"""
Generate an animated GIF of the Potato Shield system architecture.
Run: python scripts/generate_architecture_gif.py
Output: assets/potato-shield-architecture.gif
Requires: pip install Pillow
"""
import os
from PIL import Image, ImageDraw, ImageFont

# Output path (from repo root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(ROOT, "assets", "potato-shield-architecture.gif")

# Frame size and colors
W, H = 900, 700
BG = (26, 29, 41)           # #1a1d29
TITLE_COLOR = (232, 232, 232)
SUB_COLOR = (156, 163, 175)
BOX_BG = (55, 65, 81)
BOX_HIGHLIGHT = (59, 130, 246)
BOX_BORDER = (75, 85, 99)
REGION_COLORS = [
    (55, 65, 81),   # user
    (37, 99, 235), # api
    (124, 58, 237),# rai
    (5, 150, 105), # agent
    (190, 24, 93), # model
    (13, 148, 136),# memory
    (30, 64, 175), # external
]

STEPS = [
    ("1. User & presentation", ["User (Farmer)", "Next.js", "Chat", "Dashboard"]),
    ("2. API & RAI", ["FastAPI", "RAI middleware", "Local guard"]),
    ("3. Infosys RAI Toolkit", ["Moderation", "Privacy", "Hallucination", "Safety"]),
    ("4. Agent orchestration", ["Router", "Predictive", "Diagnostic", "General chat"]),
    ("5. Models & algorithms", ["Disease classifier", "Rule engine", "Sliding window", "LLMs"]),
    ("6. Memory & storage", ["Short-term", "Long-term", "DynamoDB", "SQLite"]),
    ("7. External services", ["Open-Meteo", "Tavily", "OpenAI", "AWS SES"]),
]

FRAME_MS = 1800  # ms per frame
FONT_SIZE_TITLE = 22
FONT_SIZE_STEP = 18
FONT_SIZE_BOX = 14
BOX_W, BOX_H = 140, 44
PAD = 20
TOP = 50


def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def draw_frame(draw, font_title, font_step, font_box, step_index):
    draw.rectangle([0, 0, W, H], fill=BG)
    y = TOP

    # Title
    draw.text((W // 2 - 180, y), "Potato Shield – System Architecture", fill=TITLE_COLOR, font=font_title)
    y += 36
    draw.text((W // 2 - 160, y), "UK–India AIxcelerate · RAI · Agents · Models", fill=SUB_COLOR, font=font_step)
    y += 44

    # Draw all steps; highlight current (step_index in 0..len(STEPS)-1)
    for i, (step_title, items) in enumerate(STEPS):
        is_highlight = 0 <= step_index < len(STEPS) and i == step_index
        color = BOX_HIGHLIGHT if is_highlight else REGION_COLORS[i % len(REGION_COLORS)]
        border = (100, 150, 255) if is_highlight else BOX_BORDER

        # Region bar
        draw.rounded_rectangle([PAD, y, W - PAD, y + 28], radius=6, outline=border, width=2,
                               fill=(color[0] // 3, color[1] // 3, color[2] // 3) if not is_highlight else (color[0] // 4, color[1] // 4, min(255, color[2] // 2 + 60)))
        draw.text((PAD + 12, y + 6), step_title, fill=TITLE_COLOR, font=font_step)
        y += 36

        # Boxes
        x = PAD
        for label in items:
            draw.rounded_rectangle([x, y, x + BOX_W, y + BOX_H], radius=6, outline=border, width=1, fill=color)
            txt = label[:14] + ".." if len(label) > 14 else label
            draw.text((x + 8, y + 12), txt, fill=(255, 255, 255), font=font_box)
            x += BOX_W + 12
        y += BOX_H + 16

        if y > H - 60:
            break

    # Step indicator at top
    if 0 <= step_index < len(STEPS):
        draw.text((PAD, 12), STEPS[step_index][0], fill=BOX_HIGHLIGHT, font=font_step)
    else:
        draw.text((PAD, 12), "Potato Shield – full system", fill=SUB_COLOR, font=font_step)


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    font_title = get_font(FONT_SIZE_TITLE)
    font_step = get_font(FONT_SIZE_STEP)
    font_box = get_font(FONT_SIZE_BOX)

    frames = []
    for step_index in range(len(STEPS)):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        draw_frame(draw, font_title, font_step, font_box, step_index)
        frames.append(img)

    # Append a "full view" frame with no highlight (optional)
    img_all = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img_all)
    draw_frame(draw, font_title, font_step, font_box, -1)  # no highlight
    frames.append(img_all)

    # Save as animated GIF (loop forever, 1800 ms per frame)
    durations = [FRAME_MS] * len(STEPS) + [FRAME_MS]
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
