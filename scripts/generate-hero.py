from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import json
import math
import shutil

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    "/Users/nahuelgavilan/.codex/generated_images/"
    "019dee9b-f808-7641-989c-b25d4547d6d8/"
    "ig_0f1d9fd55aadc8970169f7747b61d88191ba82ab923e8be5e1.png"
)

FRAME_SIZE = 128
COLUMNS = 4
SCALE = 3
BOTTOM_Y = 122
MAX_SUBJECT = 116

PALETTE = {
    "K": ("ink", (0x17, 0x21, 0x1B, 255)),
    "D": ("shadow", (0x4A, 0x57, 0x44, 255)),
    "M": ("cloth", (0x8F, 0x9A, 0x78, 255)),
    "L": ("light", (0xEF, 0xF1, 0xCF, 255)),
}


@dataclass(frozen=True)
class SourcePose:
    name: str
    crop: tuple[int, int, int, int]
    duration_ms: int


@dataclass(frozen=True)
class Frame:
    name: str
    image: Image.Image
    duration_ms: int


# The right-side pose grid in the imagegen concept.
# Coords intentionally crop inside the printed grid so the extractor never sees
# the border lines as part of the sprite.
SOURCE_POSES = [
    SourcePose("idle_down", (616, 132, 906, 510), 180),
    SourcePose("idle_up", (926, 132, 1188, 510), 180),
    SourcePose("idle_right", (1210, 132, 1492, 510), 180),
    SourcePose("concept_left", (616, 530, 906, 884), 140),
    SourcePose("walk_down_1", (926, 530, 1188, 884), 140),
    SourcePose("walk_right_1", (1210, 530, 1492, 884), 140),
]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing concept source: {SOURCE}")

    source = Image.open(SOURCE).convert("RGB")
    frames: list[Frame] = []
    extracted: dict[str, Image.Image] = {}

    for pose in SOURCE_POSES:
        sprite = extract_sprite(source.crop(pose.crop))
        extracted[pose.name] = sprite
        if pose.name != "concept_left":
            frames.append(Frame(pose.name, sprite, pose.duration_ms))

    frames.extend(
        [
            Frame("idle_left", mirror(extracted["idle_right"]), 180),
            Frame("walk_down_2", extracted["idle_down"].copy(), 140),
            Frame("walk_right_2", extracted["idle_right"].copy(), 140),
            Frame("walk_left_1", extracted["concept_left"], 140),
            Frame("walk_left_2", mirror(extracted["walk_right_1"]), 140),
            Frame("attack_right", extracted["idle_right"].copy(), 95),
            Frame("attack_left", mirror(extracted["idle_right"]), 95),
            Frame("hurt_down", make_hurt(extracted["idle_down"]), 120),
        ]
    )

    # Keep the sheet compact and predictable: 16 frames, 4x4.
    frames = order_frames(frames)

    out_dir = ROOT / "assets" / "hero"
    ref_dir = ROOT / "assets" / "reference"
    out_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    spritesheet = make_spritesheet(frames)
    preview = make_preview(frames)

    spritesheet_path = out_dir / "hero-spritesheet.png"
    preview_path = out_dir / "hero-preview.png"
    json_path = out_dir / "hero.json"
    reference_path = ref_dir / "hero-concept.png"

    spritesheet.save(spritesheet_path)
    preview.save(preview_path)
    shutil.copyfile(SOURCE, reference_path)
    write_metadata(json_path, frames)

    colors = visible_colors(spritesheet)
    expected = {rgba[:3] for _, rgba in PALETTE.values()}
    if colors != expected:
        raise SystemExit(f"Palette mismatch: got {sorted(colors)}, expected {sorted(expected)}")

    print(f"Generated {len(frames)} frames at {FRAME_SIZE}x{FRAME_SIZE}")
    print(f"Spritesheet: {spritesheet_path}")
    print(f"Preview: {preview_path}")
    print(f"Metadata: {json_path}")
    print(f"Reference: {reference_path}")
    print("Visible palette: " + ", ".join(rgb_to_hex(c) for c in sorted(colors)))


def order_frames(frames: list[Frame]) -> list[Frame]:
    by_name = {frame.name: frame for frame in frames}
    names = [
        "idle_down",
        "walk_down_1",
        "walk_down_2",
        "idle_up",
        "idle_right",
        "walk_right_1",
        "walk_right_2",
        "idle_left",
        "walk_left_1",
        "walk_left_2",
        "attack_right",
        "attack_left",
        "hurt_down",
        "idle_down",
        "idle_up",
        "idle_right",
    ]
    ordered: list[Frame] = []
    used: dict[str, int] = {}
    for name in names:
        frame = by_name[name]
        count = used.get(name, 0)
        used[name] = count + 1
        if count == 0:
            ordered.append(frame)
        else:
            ordered.append(Frame(f"{name}_alt{count}", frame.image.copy(), frame.duration_ms))
    return ordered


def extract_sprite(crop: Image.Image) -> Image.Image:
    base_mask = subject_seed_mask(crop)
    filled_mask = fill_enclosed_light_pixels(base_mask)
    component_mask = keep_main_subject(filled_mask)
    bbox = mask_bbox(component_mask)
    if bbox is None:
        raise ValueError("Could not find subject in crop")

    bbox = expand_bbox(bbox, crop.size, 4)
    cutout = crop.crop(bbox).convert("RGBA")
    cutout_mask = component_mask.crop(bbox)
    cutout.putalpha(cutout_mask)
    cutout = quantize_to_gameboy(cutout)
    return fit_to_frame(cutout)


def subject_seed_mask(img: Image.Image) -> Image.Image:
    px = img.load()
    mask = Image.new("L", img.size, 0)
    out = mask.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = px[x, y]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            greenish = g >= r - 18 and g >= b - 12
            dark_subject = lum < 178
            mid_subject = lum < 205 and greenish and abs(r - b) < 55
            if dark_subject or mid_subject:
                out[x, y] = 255

    return remove_border_noise(mask)


def remove_border_noise(mask: Image.Image) -> Image.Image:
    # Thin crop-edge marks and panel leftovers are never part of the actor.
    out = mask.copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    draw.rectangle((0, 0, w - 1, 7), fill=0)
    draw.rectangle((0, h - 8, w - 1, h - 1), fill=0)
    draw.rectangle((0, 0, 7, h - 1), fill=0)
    draw.rectangle((w - 8, 0, w - 1, h - 1), fill=0)
    return out


def fill_enclosed_light_pixels(mask: Image.Image) -> Image.Image:
    w, h = mask.size
    seed = mask.load()
    outside = Image.new("1", mask.size, 0)
    outside_px = outside.load()
    q: deque[tuple[int, int]] = deque()

    def push(x: int, y: int) -> None:
        if x < 0 or y < 0 or x >= w or y >= h:
            return
        if outside_px[x, y] or seed[x, y] > 0:
            return
        outside_px[x, y] = 1
        q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        x, y = q.popleft()
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    filled = Image.new("L", mask.size, 0)
    out = filled.load()
    for y in range(h):
        for x in range(w):
            if seed[x, y] > 0 or not outside_px[x, y]:
                out[x, y] = 255
    return filled


def keep_main_subject(mask: Image.Image) -> Image.Image:
    w, h = mask.size
    src = mask.load()
    seen = [[False] * w for _ in range(h)]
    components: list[list[tuple[int, int]]] = []

    for y in range(h):
        for x in range(w):
            if seen[y][x] or src[x, y] == 0:
                continue
            q = deque([(x, y)])
            seen[y][x] = True
            comp: list[tuple[int, int]] = []
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and src[nx, ny] > 0:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            components.append(comp)

    if not components:
        return mask

    largest = max(components, key=len)
    lx0, ly0, lx1, ly1 = points_bbox(largest)
    kept = Image.new("L", mask.size, 0)
    out = kept.load()

    for comp in components:
        x0, y0, x1, y1 = points_bbox(comp)
        area = len(comp)
        close_to_actor = not (x1 < lx0 - 24 or x0 > lx1 + 24 or y1 < ly0 - 24 or y0 > ly1 + 24)
        meaningful = area > len(largest) * 0.035
        if comp is largest or (close_to_actor and meaningful):
            for x, y in comp:
                out[x, y] = 255

    return kept


def points_bbox(points: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def mask_bbox(mask: Image.Image) -> tuple[int, int, int, int] | None:
    return mask.getbbox()


def expand_bbox(
    bbox: tuple[int, int, int, int], size: tuple[int, int], padding: int
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = bbox
    w, h = size
    return max(0, x0 - padding), max(0, y0 - padding), min(w, x1 + padding), min(h, y1 + padding)


def quantize_to_gameboy(img: Image.Image) -> Image.Image:
    src = img.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    in_px = src.load()
    out_px = out.load()
    colors = [rgba for _, rgba in PALETTE.values()]

    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = in_px[x, y]
            if a < 128:
                continue
            out_px[x, y] = nearest_color((r, g, b), colors)
    return out


def nearest_color(rgb: tuple[int, int, int], colors: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    r, g, b = rgb
    return min(
        colors,
        key=lambda c: (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2,
    )


def fit_to_frame(sprite: Image.Image) -> Image.Image:
    bbox = sprite.getbbox()
    if bbox is None:
        return Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))

    sprite = sprite.crop(bbox)
    scale = min(MAX_SUBJECT / sprite.width, MAX_SUBJECT / sprite.height)
    target = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    sprite = sprite.resize(target, Image.Resampling.NEAREST)

    frame = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
    x = (FRAME_SIZE - sprite.width) // 2
    y = BOTTOM_Y - sprite.height
    frame.alpha_composite(sprite, (x, y))
    return frame


def mirror(img: Image.Image) -> Image.Image:
    return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def make_hurt(img: Image.Image) -> Image.Image:
    shifted = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shifted.alpha_composite(img, (3, 0))
    return shifted


def make_spritesheet(frames: list[Frame]) -> Image.Image:
    rows = math.ceil(len(frames) / COLUMNS)
    sheet = Image.new("RGBA", (COLUMNS * FRAME_SIZE, rows * FRAME_SIZE), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        x = (index % COLUMNS) * FRAME_SIZE
        y = (index // COLUMNS) * FRAME_SIZE
        sheet.alpha_composite(frame.image, (x, y))
    return sheet


def make_preview(frames: list[Frame]) -> Image.Image:
    gap = 2
    rows = math.ceil(len(frames) / COLUMNS)
    cell = FRAME_SIZE * SCALE
    preview = Image.new(
        "RGBA",
        (COLUMNS * cell + (COLUMNS + 1) * gap, rows * cell + (rows + 1) * gap),
        (0, 0, 0, 0),
    )
    draw_checker(preview, 16 * SCALE)
    draw = ImageDraw.Draw(preview)
    grid = (0x72, 0x7A, 0x62, 255)
    for y in range(0, preview.height, cell + gap):
        draw.rectangle((0, y, preview.width, y + gap - 1), fill=grid)
    for x in range(0, preview.width, cell + gap):
        draw.rectangle((x, 0, x + gap - 1, preview.height), fill=grid)

    for index, frame in enumerate(frames):
        x = gap + (index % COLUMNS) * (cell + gap)
        y = gap + (index // COLUMNS) * (cell + gap)
        scaled = frame.image.resize((cell, cell), Image.Resampling.NEAREST)
        preview.alpha_composite(scaled, (x, y))
    return preview


def draw_checker(img: Image.Image, size: int) -> None:
    px = img.load()
    a = (0xC8, 0xCF, 0xA8, 255)
    b = (0xE3, 0xE7, 0xC7, 255)
    for y in range(img.height):
        for x in range(img.width):
            px[x, y] = a if (x // size + y // size) % 2 else b


def visible_colors(img: Image.Image) -> set[tuple[int, int, int]]:
    colors: set[tuple[int, int, int]] = set()
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                colors.add((r, g, b))
    return colors


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{c:02x}" for c in rgb)


def write_metadata(path: Path, frames: list[Frame]) -> None:
    frame_defs = [
        {
            "name": frame.name,
            "x": (index % COLUMNS) * FRAME_SIZE,
            "y": (index // COLUMNS) * FRAME_SIZE,
            "width": FRAME_SIZE,
            "height": FRAME_SIZE,
            "durationMs": frame.duration_ms,
        }
        for index, frame in enumerate(frames)
    ]

    metadata = {
        "image": "hero-spritesheet.png",
        "frameSize": {"width": FRAME_SIZE, "height": FRAME_SIZE},
        "columns": COLUMNS,
        "origin": {"x": 64, "y": BOTTOM_Y},
        "hitbox": {"x": 46, "y": 91, "width": 36, "height": 28},
        "recommendedGameScale": {
            "nativeHeroFrame": "128x128",
            "tileSize": 64,
            "viewport": "640x360 logical pixels or larger",
            "rendering": "nearest-neighbor / pixelated",
        },
        "palette": {
            key: {"name": name, "hex": rgb_to_hex(rgba[:3])}
            for key, (name, rgba) in PALETTE.items()
        },
        "frames": frame_defs,
        "animations": {
            "idle_down": [{"frame": "idle_down", "durationMs": 180}],
            "idle_up": [{"frame": "idle_up", "durationMs": 180}],
            "idle_right": [{"frame": "idle_right", "durationMs": 180}],
            "idle_left": [{"frame": "idle_left", "durationMs": 180}],
            "walk_down": [
                {"frame": "walk_down_1", "durationMs": 140},
                {"frame": "idle_down", "durationMs": 140},
                {"frame": "walk_down_2", "durationMs": 140},
                {"frame": "idle_down", "durationMs": 140},
            ],
            "walk_up": [
                {"frame": "idle_up", "durationMs": 150},
                {"frame": "idle_up_alt1", "durationMs": 150},
            ],
            "walk_right": [
                {"frame": "walk_right_1", "durationMs": 140},
                {"frame": "walk_right_2", "durationMs": 140},
            ],
            "walk_left": [
                {"frame": "walk_left_1", "durationMs": 140},
                {"frame": "walk_left_2", "durationMs": 140},
            ],
            "attack_right": [{"frame": "attack_right", "durationMs": 95}],
            "attack_left": [{"frame": "attack_left", "durationMs": 95}],
            "hurt_down": [{"frame": "hurt_down", "durationMs": 120}],
        },
        "source": {
            "concept": "../reference/hero-concept.png",
            "method": "Cropped from the imagegen concept, background-masked, reduced to 4 colors, and framed at 128x128.",
        },
        "notes": [
            "This version intentionally raises the game's sprite resolution to preserve the character from the concept.",
            "The pose set is a faithful extracted prototype, not a clean hand-authored animation sheet yet.",
            "For production, regenerate or redraw clean pose-specific frames at this same 128x128 target.",
        ],
    }
    path.write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
