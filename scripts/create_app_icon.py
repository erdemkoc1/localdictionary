"""Create the LocalDictionary blue LD application icon.

The mark follows the supplied reference: a bright-blue rounded D/frame shape
with a dark center and white LD lettering. The PNG is used by the GUI/tray;
the multi-resolution ICO is used by the Windows executable build.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets"
PNG_PATH = ASSET_DIR / "localdictionary.png"
ICO_PATH = ASSET_DIR / "localdictionary.ico"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _gradient(size: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = image.load()
    assert pixels is not None
    for y in range(size):
        ratio = y / max(1, size - 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3)) + (255,)
        for x in range(size):
            pixels[x, y] = color
    return image


def create_icon() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    scale = 4
    size = 512
    canvas_size = size * scale
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    # The outer silhouette is a thick rounded D/frame, matching the reference.
    outer_box = (int(canvas_size * 0.045), int(canvas_size * 0.075),
                 int(canvas_size * 0.955), int(canvas_size * 0.925))
    outer_mask = Image.new("L", (canvas_size, canvas_size), 0)
    ImageDraw.Draw(outer_mask).rounded_rectangle(
        outer_box, radius=int(canvas_size * 0.19), fill=255
    )
    blue = _gradient(canvas_size, (12, 151, 255), (5, 91, 222))
    blue.putalpha(outer_mask)
    canvas.alpha_composite(blue)

    # Dark inset creates the recognizable center opening while keeping the
    # outside corners transparent for taskbar and Explorer rendering.
    inner_box = (int(canvas_size * 0.205), int(canvas_size * 0.225),
                 int(canvas_size * 0.795), int(canvas_size * 0.775))
    inner_mask = Image.new("L", (canvas_size, canvas_size), 0)
    ImageDraw.Draw(inner_mask).rounded_rectangle(
        inner_box, radius=int(canvas_size * 0.105), fill=255
    )
    center = _gradient(canvas_size, (10, 15, 24), (2, 5, 10))
    center.putalpha(inner_mask)
    canvas.alpha_composite(center)

    draw = ImageDraw.Draw(canvas)
    # Highlight edge and a subtle right-side accent give the small icon shape.
    highlight_width = max(2, int(canvas_size * 0.012))
    draw.rounded_rectangle(
        outer_box,
        radius=int(canvas_size * 0.19),
        outline=(111, 207, 255, 210),
        width=highlight_width,
    )
    draw.rounded_rectangle(
        inner_box,
        radius=int(canvas_size * 0.105),
        outline=(3, 116, 232, 230),
        width=max(2, int(canvas_size * 0.010)),
    )

    font = _font(int(canvas_size * 0.285))
    text = "LD"
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = (
        (canvas_size - text_width) // 2,
        (canvas_size - text_height) // 2 - int(canvas_size * 0.018),
    )
    draw.text(
        (position[0] + int(canvas_size * 0.010), position[1] + int(canvas_size * 0.014)),
        text,
        font=font,
        fill=(0, 0, 0, 190),
    )
    draw.text(position, text, font=font, fill=(255, 255, 255, 255))

    icon = canvas.resize((size, size), Image.Resampling.LANCZOS)
    icon.save(PNG_PATH, format="PNG", optimize=True)
    icon.save(
        ICO_PATH,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(PNG_PATH)
    print(ICO_PATH)


if __name__ == "__main__":
    create_icon()
