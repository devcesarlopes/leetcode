from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1100, 420
BG = (18, 18, 20)
FG = (235, 235, 235)
MUTED = (130, 130, 140)
ACCENT = (90, 170, 255)
RED = (230, 45, 20)
PURPLE = (124, 102, 147)
GOOD = (110, 220, 140)

RADIUS = 36
FONT = ImageFont.load_default()
OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "gifs"


def canvas(title: str, subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.text((28, 18), title, fill=ACCENT, font=FONT)
    if subtitle:
        draw.text((28, 40), subtitle, fill=MUTED, font=FONT)
    return img, draw


def draw_arrow(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, color=FG, width: int = 3) -> None:
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    head = 8
    if x2 >= x1:
        draw.polygon([(x2, y2), (x2 - head, y2 - 5), (x2 - head, y2 + 5)], fill=color)
    else:
        draw.polygon([(x2, y2), (x2 + head, y2 - 5), (x2 + head, y2 + 5)], fill=color)


def draw_node(draw: ImageDraw.ImageDraw, x: int, y: int, value: int, color: tuple[int, int, int]) -> None:
    draw.ellipse((x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS), fill=color, outline=(0, 0, 0), width=2)
    draw.text((x - 8, y - 7), str(value), fill=FG, font=FONT)


def draw_linked_list(
    draw: ImageDraw.ImageDraw,
    values: list[int],
    y: int,
    node_color: tuple[int, int, int],
    start_x: int = 110,
    gap: int = 150,
) -> list[tuple[int, int]]:
    centers: list[tuple[int, int]] = []
    for i, v in enumerate(values):
        x = start_x + i * gap
        centers.append((x, y))
        draw_node(draw, x, y, v, node_color)
        if i > 0:
            px, py = centers[i - 1]
            draw_arrow(draw, px + RADIUS, py, x - RADIUS, y, color=FG, width=2)
    return centers


def save_gif(name: str, frames: list[Image.Image], duration: int = 550) -> None:
    path = OUT_DIR / name
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True,
    )
    print(f"Generated: {path}")


def make_traversal_gif() -> None:
    values = [1, 2, 4, 7, 9]
    frames: list[Image.Image] = []

    for i in range(len(values) + 1):
        img, draw = canvas(
            "Linked List Traversal",
            "start at head and move current = current.next until current is None",
        )
        centers = draw_linked_list(draw, values, y=200, node_color=PURPLE)
        hx, hy = centers[0]
        draw.text((hx - 12, 130), "head", fill=GOOD, font=FONT)
        draw.text((hx + 8, 144), "v", fill=GOOD, font=FONT)

        if i < len(values):
            cx, cy = centers[i]
            draw.text((cx - 18, 90), "current", fill=ACCENT, font=FONT)
            draw.text((cx + 16, 106), "v", fill=ACCENT, font=FONT)
            draw.text((28, 332), f"Step {i + 1}: visit {values[i]}, then move to next node", fill=FG, font=FONT)
        else:
            tx = centers[-1][0] + 130
            draw.text((tx - 14, 90), "current", fill=ACCENT, font=FONT)
            draw.text((tx + 20, 106), "v", fill=ACCENT, font=FONT)
            draw.text((tx + 2, 198), "None", fill=MUTED, font=FONT)
            draw.text((28, 332), "Step end: current is None, traversal finished", fill=FG, font=FONT)

        frames.append(img)

    save_gif("linked-list-traversal.gif", frames, duration=520)


def make_relink_gif() -> None:
    list1 = [1, 2, 4]
    list2 = [1, 3, 4]
    merged_prefix = [1, 1, 2, 3, 4, 4]
    picks = ["list2", "list1", "list1", "list2", "list1", "list2"]

    frames: list[Image.Image] = []
    for i in range(len(merged_prefix) + 1):
        img, draw = canvas(
            "Relinking During Merge",
            "tail.next points to the smaller node, then tail moves forward",
        )

        top1 = draw_linked_list(draw, list1, y=115, node_color=RED)
        top2 = draw_linked_list(draw, list2, y=215, node_color=PURPLE)
        draw.text((28, 108), "list1", fill=RED, font=FONT)
        draw.text((28, 208), "list2", fill=PURPLE, font=FONT)

        draw.line((40, 270, W - 40, 270), fill=MUTED, width=2)

        if i > 0:
            merged_centers = draw_linked_list(draw, merged_prefix[:i], y=340, node_color=(64, 96, 145), start_x=110, gap=130)
            draw.text((28, 332), "merged", fill=GOOD, font=FONT)

            if i == 1:
                tx, ty = merged_centers[0]
            else:
                tx, ty = merged_centers[-1]
            draw.text((tx - 12, ty - 62), "tail", fill=ACCENT, font=FONT)
            draw.text((tx + 10, ty - 46), "v", fill=ACCENT, font=FONT)

            pick = picks[i - 1]
            src = "list1" if pick == "list1" else "list2"
            draw.text((760, 334), f"step {i}: picked from {src}", fill=FG, font=FONT)
        else:
            draw.text((28, 332), "merged", fill=GOOD, font=FONT)
            draw.text((110, 340), "dummy -> None", fill=MUTED, font=FONT)
            draw.text((760, 334), "start: tail = dummy", fill=FG, font=FONT)

        for x, y in top1:
            draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=RED)
        for x, y in top2:
            draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=PURPLE)

        frames.append(img)

    save_gif("linked-list-relink.gif", frames, duration=680)


def make_remove_node_gif() -> None:
    before = [1, 2, 3, 4]
    after = [1, 3, 4]
    frames: list[Image.Image] = []

    img1, draw1 = canvas(
        "Remove Node by Relinking",
        "remove the node after head with: head.next = head.next.next",
    )
    centers_before = draw_linked_list(draw1, before, y=170, node_color=PURPLE, start_x=130, gap=170)
    hx, hy = centers_before[0]
    draw1.text((hx - 10, 96), "head", fill=GOOD, font=FONT)
    draw1.text((hx + 8, 112), "v", fill=GOOD, font=FONT)

    nx, ny = centers_before[1]
    draw1.text((nx - 18, 232), "remove", fill=RED, font=FONT)
    draw1.text((28, 322), "Before: 1 -> 2 -> 3 -> 4", fill=FG, font=FONT)
    frames.append(img1)

    img2, draw2 = canvas(
        "Remove Node by Relinking",
        "step: set head.next to the node after it",
    )
    centers2 = draw_linked_list(draw2, before, y=170, node_color=PURPLE, start_x=130, gap=170)
    hx2, hy2 = centers2[0]
    draw2.text((hx2 - 10, 96), "head", fill=GOOD, font=FONT)
    draw2.text((hx2 + 8, 112), "v", fill=GOOD, font=FONT)

    n1x, n1y = centers2[1]
    n2x, n2y = centers2[2]
    draw_arrow(draw2, hx2 + RADIUS, hy2 - 14, n2x - RADIUS, n2y - 14, color=ACCENT, width=3)
    draw2.text((480, 126), "new link", fill=ACCENT, font=FONT)
    draw2.text((28, 322), "Operation: head.next = head.next.next", fill=FG, font=FONT)
    frames.append(img2)

    img3, draw3 = canvas(
        "Remove Node by Relinking",
        "result after skipping one node",
    )
    centers_after = draw_linked_list(draw3, after, y=170, node_color=(64, 96, 145), start_x=130, gap=170)
    hx3, hy3 = centers_after[0]
    draw3.text((hx3 - 10, 96), "head", fill=GOOD, font=FONT)
    draw3.text((hx3 + 8, 112), "v", fill=GOOD, font=FONT)
    draw3.text((28, 322), "After: 1 -> 3 -> 4", fill=FG, font=FONT)
    frames.append(img3)

    save_gif("linked-list-remove-node.gif", frames, duration=820)


def make_cycle_detection_gif() -> None:
    values = [3, 2, 0, -4]
    centers: list[tuple[int, int]] = []
    start_x = 180
    gap = 180
    y = 190
    cycle_to_index = 1

    for i in range(len(values)):
        centers.append((start_x + i * gap, y))

    frames: list[Image.Image] = []
    slow_steps = [0, 1, 2, 3, 1, 2]
    fast_steps = [0, 2, 1, 3, 2, 1]

    for step, (slow_i, fast_i) in enumerate(zip(slow_steps, fast_steps), start=1):
        img, draw = canvas(
            "Fast and Slow Pointers (Cycle Detection)",
            "slow moves 1 step, fast moves 2 steps; if they meet, cycle exists",
        )

        for i, v in enumerate(values):
            x, node_y = centers[i]
            draw_node(draw, x, node_y, v, PURPLE)
            if i > 0:
                px, py = centers[i - 1]
                draw_arrow(draw, px + RADIUS, py, x - RADIUS, node_y, color=FG, width=2)

        last_x, last_y = centers[-1]
        cycle_x, cycle_y = centers[cycle_to_index]
        draw.line((last_x + RADIUS - 4, last_y, last_x + 95, last_y, last_x + 95, cycle_y - 70, cycle_x, cycle_y - 70, cycle_x, cycle_y - RADIUS - 2), fill=FG, width=2)
        draw.polygon([(cycle_x, cycle_y - RADIUS - 2), (cycle_x - 6, cycle_y - RADIUS - 12), (cycle_x + 6, cycle_y - RADIUS - 12)], fill=FG)
        draw.text((cycle_x - 26, cycle_y - 96), "cycle", fill=MUTED, font=FONT)

        sx, sy = centers[slow_i]
        fx, fy = centers[fast_i]
        draw.text((sx - 14, sy + 52), "slow", fill=GOOD, font=FONT)
        draw.text((sx + 10, sy + 68), "^", fill=GOOD, font=FONT)

        draw.text((fx - 14, fy - 88), "fast", fill=ACCENT, font=FONT)
        draw.text((fx + 10, fy - 72), "v", fill=ACCENT, font=FONT)

        met = slow_i == fast_i
        if met:
            draw.text((28, 334), f"Step {step}: slow and fast meet at node {values[slow_i]} -> cycle detected", fill=GOOD, font=FONT)
        else:
            draw.text((28, 334), f"Step {step}: slow at {values[slow_i]}, fast at {values[fast_i]}", fill=FG, font=FONT)

        frames.append(img)

    save_gif("linked-list-fast-slow-cycle.gif", frames, duration=720)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_traversal_gif()
    make_relink_gif()
    make_remove_node_gif()
    make_cycle_detection_gif()
    print("Done. Linked list GIFs generated.")


if __name__ == "__main__":
    main()
