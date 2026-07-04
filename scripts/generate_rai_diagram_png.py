"""
Generate AWS-style Responsible AI Toolkit diagram as PNG.
Run: python scripts/generate_rai_diagram_png.py
Output: assets/rai-toolkit-architecture.png
Requires: pip install Pillow
"""
import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(ROOT, "assets", "rai-toolkit-architecture.png")

W, H = 1000, 900
BG = (26, 29, 41)
TITLE = (232, 232, 232)
SUB = (156, 163, 175)
ACCENT = (124, 58, 237)
BOX_APP = (37, 99, 235)
BOX_USAGE = (5, 150, 105)
BOX_TOOLKIT = (124, 58, 237)
BOX_OUTCOME = (13, 148, 136)
BORDER = (139, 92, 246)
PAD = 24
TOP = 40

SECTIONS = [
    ("APPLICATION LAYER (POTATO SHIELD)", [
        ("FastAPI", "api/main.py"),
        ("RAI Middleware", "rai_middleware.py"),
        ("RAI Client", "rai_client.py"),
    ], BOX_APP),
    ("HOW WE USE IT – INPUT", [
        ("validate_user_input()", "Before any agent"),
        ("Local guard", "PII · Blocked phrases"),
        ("check_input_moderation()", "ModerationLayer API"),
    ], BOX_USAGE),
    ("INFOSYS RAI TOOLKIT", [
        ("ModerationLayer", "Injection · JailBreak · Toxicity"),
        ("Privacy", "PII detect · Anonymize"),
        ("Hallucination", "Factual consistency"),
        ("Safety · Fairness · Explainability", ""),
    ], BOX_TOOLKIT),
    ("HOW WE USE IT – OUTPUT", [
        ("validate_ai_output()", "After response"),
        ("detect_hallucination()", "vs ground truth"),
        ("generate_explanation()", "CoT for high-risk"),
    ], BOX_USAGE),
    ("OUTCOMES", [
        ("Input blocked", "Unsafe → 403"),
        ("PII anonymized", "[REDACTED]"),
        ("Output validated", "Safe response"),
        ("Audit logged", "Redacted"),
    ], BOX_OUTCOME),
]


def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", size)
        except Exception:
            return ImageFont.load_default()


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    f_title = get_font(20)
    f_region = get_font(14)
    f_label = get_font(12)
    f_detail = get_font(10)

    y = TOP
    draw.text((W // 2 - 220, y), "Responsible AI Toolkit – How Potato Shield Uses It", fill=TITLE, font=f_title)
    y += 32
    draw.text((W // 2 - 180, y), "Infosys RAI Toolkit · api/main.py · rai_middleware · rai_client", fill=SUB, font=f_detail)
    y += 36

    for region_title, items, box_color in SECTIONS:
        cols = 3
        box_w, box_h = 218, 40
        n_rows = (len(items) + cols - 1) // cols
        r_h = 34 + n_rows * (box_h + 8) + 16
        # Region box
        draw.rounded_rectangle([PAD, y, W - PAD, y + r_h], radius=10, outline=BORDER, width=2,
                               fill=(box_color[0] // 6, box_color[1] // 6, min(255, box_color[2] // 4 + 40)))
        draw.text((PAD + 14, y + 8), region_title, fill=(167, 139, 250), font=f_region)
        y += 34

        # Item boxes (3 per row)
        for i, (label, detail) in enumerate(items):
            row, col = i // cols, i % cols
            x = PAD + 14 + col * (box_w + 10)
            yy = y + row * (box_h + 8)
            draw.rounded_rectangle([x, yy, x + box_w, yy + box_h], radius=6, outline=(200, 200, 220), width=1, fill=box_color)
            draw.text((x + 8, yy + 4), label[:30], fill=(255, 255, 255), font=f_label)
            if detail:
                draw.text((x + 8, yy + 22), detail[:36], fill=(220, 220, 240), font=f_detail)
        y += n_rows * (box_h + 8) + 24

        if y > H - 80:
            break

    draw.text((PAD, H - 28), "Potato Shield · UK–India AIxcelerate · Infosys RAI Toolkit", fill=SUB, font=f_detail)
    img.save(OUTPUT_PATH, "PNG")
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
