import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "output"

INPUT_QUOTE = OUTPUT / "today_quote.json"
OUT_VIDEO = OUTPUT / "reel.mp4"

BG_IMAGE = ASSETS / "bg_krishna_arjuna.png"

W, H = 1080, 1920
DURATION = 12
FPS = 30


def load_quote():
    return json.loads(INPUT_QUOTE.read_text(encoding="utf-8"))


def font(path: Path, size: int):
    if not path.exists():
        raise FileNotFoundError(f"Font not found: {path}")
    return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)


def clamp(x, a=0, b=1):
    return max(a, min(b, x))


def ease_out(t):
    return 1 - (1 - t) * (1 - t)


def fade_alpha(t, start, duration=0.8):
    x = (t - start) / duration
    return ease_out(clamp(x))


def wrap_lines(draw, text, font_obj, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font_obj)
        if bbox[2] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ✅ UPDATED: Thin premium shadow + subtle glow
def draw_text_glow(draw, x, y, text, font_obj, alpha=255):
    """
    White text with very subtle glow + soft shadow (premium look).
    """

    # softer shadow (smaller offset, lighter alpha)
    shadow_alpha = int(alpha * 0.35)
    draw.text((x + 2, y + 3), text, font=font_obj, fill=(0, 0, 0, shadow_alpha))

    # subtle glow (fewer passes -> not thick)
    glow_alpha = int(alpha * 0.10)
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw.text((x + ox, y + oy), text, font=font_obj, fill=(255, 255, 255, glow_alpha))

    # main text
    draw.text((x, y), text, font=font_obj, fill=(255, 255, 255, alpha))


def draw_centered_block(draw, text, font_obj, center_y, alpha, max_width=940, line_spacing=18):
    lines = wrap_lines(draw, text, font_obj, max_width=max_width)

    heights, widths = [], []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])

    total_h = sum(heights) + line_spacing * (len(lines) - 1)
    y = int(center_y - total_h / 2)

    for i, line in enumerate(lines):
        x = (W - widths[i]) // 2
        draw_text_glow(draw, x, y, line, font_obj, alpha=int(255 * alpha))
        y += heights[i] + line_spacing


def load_background():
    if not BG_IMAGE.exists():
        raise FileNotFoundError(f"Background image not found: {BG_IMAGE}")

    img = Image.open(BG_IMAGE).convert("RGB")

    # Resize & center-crop to 1080x1920
    img_ratio = img.width / img.height
    target_ratio = W / H

    if img_ratio > target_ratio:
        new_h = H
        new_w = int(H * img_ratio)
    else:
        new_w = W
        new_h = int(W / img_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - W) // 2
    top = (new_h - H) // 2
    img = img.crop((left, top, left + W, top + H))

    return img


def main():
    quote = load_quote()

    # Fonts (bundled in repo)
    f_title = font(FONTS / "NotoSans-Regular.ttf", 62)
    f_sanskrit = font(FONTS / "NotoSansDevanagari-Regular.ttf", 82)
    f_eng = font(FONTS / "NotoSans-Regular.ttf", 48)
    f_hin = font(FONTS / "NotoSansDevanagari-Regular.ttf", 58)
    f_footer = font(FONTS / "NotoSans-Regular.ttf", 34)

    bg_base = load_background()

    def make_frame(t):
        zoom = 1.0 + 0.025 * (t / DURATION)

        bg = bg_base.copy().convert("RGBA")

        # slight overlay only (keep background visible)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 55))
        bg = Image.alpha_composite(bg, overlay)

        # zoom crop
        zw, zh = int(W / zoom), int(H / zoom)
        x1 = (W - zw) // 2
        y1 = (H - zh) // 2
        bg = bg.crop((x1, y1, x1 + zw, y1 + zh)).resize((W, H), Image.LANCZOS)

        draw = ImageDraw.Draw(bg, "RGBA")

        # Fade timings
        a_title = fade_alpha(t, 0.2, 0.8)
        a_san = fade_alpha(t, 1.2, 0.8)
        a_en = fade_alpha(t, 2.7, 0.8)
        a_hi = fade_alpha(t, 4.0, 0.8)
        a_footer = fade_alpha(t, 5.2, 0.8)

        # Premium Title (ॐ + Topic)
        draw_centered_block(draw, "ॐ", f_sanskrit, center_y=165, alpha=a_title, max_width=400, line_spacing=0)
        draw_centered_block(draw, quote["topic"], f_title, center_y=270, alpha=a_title, max_width=900, line_spacing=10)

        # Sanskrit
        draw_centered_block(draw, quote["sanskrit"], f_sanskrit, center_y=560, alpha=a_san)

        # English (no EN label)
        draw_centered_block(draw, quote["english"], f_eng, center_y=1040, alpha=a_en)

        # Hindi (no HI label)
        draw_centered_block(draw, quote["hindi"], f_hin, center_y=1240, alpha=a_hi)

        # Footer
        footer = f"Bhagavad Gita {quote['reference']}  •  {quote['date']}"
        draw_centered_block(draw, footer, f_footer, center_y=1760, alpha=a_footer, max_width=1000, line_spacing=10)

        return np.array(bg.convert("RGB"))

    clip = VideoClip(make_frame, duration=DURATION)
    OUTPUT.mkdir(exist_ok=True)

    clip.write_videofile(
        str(OUT_VIDEO),
        fps=FPS,
        codec="libx264",
        audio=False,
        bitrate="10M"
    )

    print("✅ Reel created (thin glow+shadow):", OUT_VIDEO)


if __name__ == "__main__":
    main()
