from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 340
BG = (18, 18, 20)
FG = (235, 235, 235)
ACCENT = (90, 170, 255)
MUTED = (120, 120, 130)
GOOD = (110, 220, 140)
WARN = (255, 170, 90)
FONT = ImageFont.load_default()

OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "gifs"


def canvas(title: str, subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.text((28, 18), title, fill=ACCENT, font=FONT)
    if subtitle:
        draw.text((28, 40), subtitle, fill=MUTED, font=FONT)
    return img, draw


def draw_array(draw: ImageDraw.ImageDraw, arr: list[int], y: int = 105) -> tuple[int, int, int]:
    x0 = 40
    cell_w = 120
    cell_h = 44
    for idx, value in enumerate(arr):
        x = x0 + idx * cell_w
        draw.rectangle((x, y, x + cell_w - 10, y + cell_h), outline=MUTED, width=2)
        draw.text((x + 42, y + 14), str(value), fill=FG, font=FONT)
        draw.text((x + 48, y + cell_h + 6), str(idx), fill=MUTED, font=FONT)
    return x0, cell_w, cell_h


def save_gif(name: str, frames: list[Image.Image], duration: int = 320) -> None:
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


def make_simple_iteration() -> None:
    arr = [0, 1, 2, 3, 4, 5, 6]
    frames: list[Image.Image] = []
    for i in range(len(arr)):
        img, draw = canvas("Simple Iteration", "single pointer i from 0..n-1")
        x0, cell_w, _ = draw_array(draw, arr)
        x = x0 + i * cell_w + 50
        draw.text((x - 7, 80), "i", fill=GOOD, font=FONT)
        draw.text((x, 92), "v", fill=GOOD, font=FONT)
        draw.text((40, 220), f"i = {i}, process element {arr[i]}", fill=FG, font=FONT)
        frames.append(img)
    save_gif("array-simple.gif", frames)


def make_two_pointers() -> None:
    arr = [0, 1, 2, 3, 4, 5, 6]
    frames: list[Image.Image] = []
    for p1 in range(0, len(arr)):
        for p2 in range(p1 + 1, len(arr)):
            img, draw = canvas("Two Pointers (nested scan)", "p1 from 0..n-1, p2 from p1+1..n-1")
            x0, cell_w, _ = draw_array(draw, arr)
            x1 = x0 + p1 * cell_w + 50
            x2 = x0 + p2 * cell_w + 50
            draw.text((x1 - 12, 80), "p1", fill=GOOD, font=FONT)
            draw.text((x1, 92), "v", fill=GOOD, font=FONT)
            draw.text((x2 - 12, 80), "p2", fill=WARN, font=FONT)
            draw.text((x2, 92), "v", fill=WARN, font=FONT)
            draw.text((40, 220), f"Current pair: ({p1}, {p2})", fill=FG, font=FONT)
            frames.append(img)
    save_gif("array-two-pointers.gif", frames)


def make_lazy_pointer() -> None:
    arr = [0, 1, 2, 3, 4, 5, 6]
    keep_idxs = {1, 3, 4, 6}
    write = 1
    frames: list[Image.Image] = []
    for read in range(1, len(arr)):
        img, draw = canvas("Lazy Pointer", "read scans, write advances only when condition is true")
        x0, cell_w, _ = draw_array(draw, arr)
        xr = x0 + read * cell_w + 50
        xw = x0 + write * cell_w + 50
        draw.text((xr - 12, 80), "read", fill=GOOD, font=FONT)
        draw.text((xr, 92), "v", fill=GOOD, font=FONT)
        draw.text((xw - 14, 245), "write", fill=WARN, font=FONT)
        draw.text((xw, 232), "^", fill=WARN, font=FONT)
        keep = read in keep_idxs
        draw.text((40, 220), f"read={read} -> keep={keep}", fill=FG, font=FONT)
        if keep:
            draw.text((40, 238), "condition is true -> write += 1", fill=GOOD, font=FONT)
            write += 1
        else:
            draw.text((40, 238), "skip", fill=MUTED, font=FONT)
        frames.append(img)
    save_gif("array-lazy-pointer.gif", frames)


def draw_grid(draw: ImageDraw.ImageDraw, rows: int, cols: int, x0: int, y0: int, size: int) -> None:
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * size
            y = y0 + r * size
            draw.rectangle((x, y, x + size - 4, y + size - 4), outline=MUTED, width=2)
            draw.text((x + 12, y + 10), f"{r},{c}", fill=MUTED, font=FONT)


def make_matrix_traversal() -> None:
    rows, cols = 3, 4
    size = 65
    x0, y0 = 40, 80
    frames: list[Image.Image] = []
    for i in range(rows):
        for j in range(cols):
            img, draw = canvas("Matrix Traversal", "first pointer scans rows, second pointer scans columns")
            draw_grid(draw, rows, cols, x0, y0, size)
            cx = x0 + j * size
            cy = y0 + i * size
            draw.rectangle((cx, cy, cx + size - 4, cy + size - 4), outline=GOOD, width=3)
            draw.text((40, 300), f"current cell = ({i}, {j})", fill=FG, font=FONT)
            frames.append(img)
    save_gif("array-matrix-traversal.gif", frames, duration=420)


def make_matrix_neighbors() -> None:
    rows, cols = 3, 4
    size = 65
    x0, y0 = 40, 80
    frames: list[Image.Image] = []
    for i in range(rows):
        for j in range(cols):
            img, draw = canvas("Matrix + Surrounding Neighbors", "scan (i,j), then check neighbors")
            draw_grid(draw, rows, cols, x0, y0, size)
            cx = x0 + j * size
            cy = y0 + i * size
            draw.rectangle((cx, cy, cx + size - 4, cy + size - 4), outline=GOOD, width=3)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and not (di == 0 and dj == 0):
                        nx = x0 + nj * size
                        ny = y0 + ni * size
                        draw.rectangle((nx + 5, ny + 5, nx + size - 9, ny + size - 9), outline=WARN, width=2)
            draw.text((40, 300), f"cell=({i},{j})", fill=FG, font=FONT)
            frames.append(img)
    save_gif("array-matrix-neighbors.gif", frames, duration=420)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_simple_iteration()
    make_two_pointers()
    make_lazy_pointer()
    make_matrix_traversal()
    make_matrix_neighbors()

    print("Done. Generated per-pattern iteration GIFs.")


if __name__ == "__main__":
    main()
