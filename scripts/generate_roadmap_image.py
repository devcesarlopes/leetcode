from math import hypot
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1800, 1550
BACKGROUND = (20, 24, 34)
NODE_FILL = (74, 88, 230)
NODE_TEXT = (240, 245, 255)
ARROW_COLOR = (235, 238, 245)

NODE_W = 230
NODE_H = 76

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "assets" / "roadmap.png"


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT = load_font(26)


NODES = {
    "arrays_hashing": (900, 80, "Arrays & Hashing"),
    "two_pointers": (620, 260, "Two Pointers"),
    "stack": (900, 260, "Stack"),
    "binary_search": (420, 440, "Binary Search"),
    "sliding_window": (700, 440, "Sliding Window"),
    "linked_list": (980, 440, "Linked List"),
    "trees": (550, 620, "Trees"),
    "tries": (250, 820, "Tries"),
    "backtracking": (1260, 820, "Backtracking"),
    "heap": (550, 1030, "Heap / Priority Queue"),
    "graphs": (1060, 1030, "Graphs"),
    "dp1": (1450, 1030, "1-D DP"),
    "intervals": (230, 1230, "Intervals"),
    "greedy": (550, 1230, "Greedy"),
    "adv_graphs": (860, 1230, "Advanced Graphs"),
    "dp2": (1260, 1230, "2-D DP"),
    "bit": (1580, 1230, "Bit Manipulation"),
    "math": (1260, 1430, "Math & Geometry"),
}


EDGES = [
    ("arrays_hashing", "two_pointers"),
    ("arrays_hashing", "stack"),
    ("two_pointers", "binary_search"),
    ("two_pointers", "sliding_window"),
    ("two_pointers", "linked_list"),
    ("binary_search", "trees"),
    ("linked_list", "trees"),
    ("trees", "tries"),
    ("trees", "backtracking"),
    ("trees", "heap"),
    ("backtracking", "graphs"),
    ("backtracking", "dp1"),
    ("heap", "intervals"),
    ("heap", "greedy"),
    ("heap", "adv_graphs"),
    ("graphs", "adv_graphs"),
    ("graphs", "dp2"),
    ("dp1", "dp2"),
    ("dp1", "bit"),
    ("dp2", "math"),
    ("bit", "math"),
]


def node_box(node_id: str) -> tuple[int, int, int, int]:
    x, y, _ = NODES[node_id]
    return x - NODE_W // 2, y - NODE_H // 2, x + NODE_W // 2, y + NODE_H // 2


def anchor_points(src: str, dst: str) -> tuple[tuple[int, int], tuple[int, int]]:
    sx, sy, _ = NODES[src]
    dx, dy, _ = NODES[dst]

    if dy > sy:
        start = (sx, sy + NODE_H // 2)
        end = (dx, dy - NODE_H // 2)
    elif dy < sy:
        start = (sx, sy - NODE_H // 2)
        end = (dx, dy + NODE_H // 2)
    elif dx > sx:
        start = (sx + NODE_W // 2, sy)
        end = (dx - NODE_W // 2, dy)
    else:
        start = (sx - NODE_W // 2, sy)
        end = (dx + NODE_W // 2, dy)

    return start, end


def _cubic_bezier_points(
    start: tuple[int, int], control1: tuple[int, int], control2: tuple[int, int], end: tuple[int, int], steps: int = 42
) -> list[tuple[int, int]]:
    sx, sy = start
    c1x, c1y = control1
    c2x, c2y = control2
    ex, ey = end

    points: list[tuple[int, int]] = []
    for i in range(steps + 1):
        t = i / steps
        one_minus_t = 1 - t
        x = (
            one_minus_t**3 * sx
            + 3 * one_minus_t * one_minus_t * t * c1x
            + 3 * one_minus_t * t * t * c2x
            + t**3 * ex
        )
        y = (
            one_minus_t**3 * sy
            + 3 * one_minus_t * one_minus_t * t * c1y
            + 3 * one_minus_t * t * t * c2y
            + t**3 * ey
        )
        points.append((int(x), int(y)))
    return points


def _vertical_controls(start: tuple[int, int], end: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    sx, sy = start
    ex, ey = end
    dy = ey - sy

    if dy >= 0:
        pull = min(max(int(abs(dy) * 0.45), 36), 140)
        c1 = (sx, sy + pull)
        c2 = (ex, ey - pull)
    else:
        pull = min(max(int(abs(dy) * 0.45), 36), 140)
        c1 = (sx, sy - pull)
        c2 = (ex, ey + pull)

    return c1, c2


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], width: int = 5) -> None:
    control1, control2 = _vertical_controls(start, end)
    curve_points = _cubic_bezier_points(start, control1, control2, end)
    draw.line(curve_points, fill=ARROW_COLOR, width=width)

    ex, ey = curve_points[-1]
    tx, ty = curve_points[-3]

    dx = ex - tx
    dy = ey - ty
    length = max(hypot(dx, dy), 1)
    ux = dx / length
    uy = dy / length

    head_len = 16
    head_w = 9
    bx = ex - ux * head_len
    by = ey - uy * head_len

    px = -uy
    py = ux

    p1 = (ex, ey)
    p2 = (int(bx + px * head_w), int(by + py * head_w))
    p3 = (int(bx - px * head_w), int(by - py * head_w))
    draw.polygon([p1, p2, p3], fill=ARROW_COLOR)


def draw_node(draw: ImageDraw.ImageDraw, node_id: str) -> None:
    x0, y0, x1, y1 = node_box(node_id)
    _, _, label = NODES[node_id]

    draw.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=NODE_FILL)

    bbox = draw.textbbox((0, 0), label, font=FONT)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x0 + (NODE_W - tw) // 2
    ty = y0 + (NODE_H - th) // 2 - 2
    draw.text((tx, ty), label, fill=NODE_TEXT, font=FONT)

    draw.line((x0 + 18, y1 - 16, x1 - 18, y1 - 16), fill=(221, 228, 255), width=6)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(img)

    for src, dst in EDGES:
        start, end = anchor_points(src, dst)
        draw_arrow(draw, start, end)

    for node_id in NODES:
        draw_node(draw, node_id)

    img.save(OUT_PATH)
    print(f"Roadmap generated at: {OUT_PATH}")


if __name__ == "__main__":
    main()
