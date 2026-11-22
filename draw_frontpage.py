#!/usr/bin/env python3
"""Draw the v6 front page: 50 stories, 9 regions, one image, 1024x1024.

Deterministic: same stories.json + same layout -> byte-identical PNG.
No network, no timestamps in the output. Pure PIL.

Layouts:
  A broadsheet  - masthead, numbers band, spine band, 3-col story grid
  B spine       - masthead, centre spine column, 2-col story grid
  C lead        - masthead, giant lead stat panel, 3-col story grid
Usage: python3 draw_frontpage.py <stories.json> <A|B|C> <out.png>
Prints: size, bytes, sha256, overflow count, font sizes used.
"""
import hashlib
import json
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 234)
INK = (20, 20, 20)
MUTED = (90, 86, 78)
RED = (179, 32, 44)
BLUE = (27, 58, 107)
TEAL = (14, 107, 92)
AMBER = (169, 110, 12)
RULE = (200, 192, 175)
DARK = (24, 24, 22)

BEAT_COLOR = {
    "MARKETS": BLUE, "WAR": RED, "GULF": TEAL, "POWER": (74, 60, 120),
    "CULTURE": AMBER, "LAUNCH": AMBER, "SPORT": (40, 90, 40), "LIFE": (120, 60, 90),
}

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy wrap; returns list of lines, never wider than width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def story_cell_height(draw, story, col_w, hf, nf, tf):
    tag = f"{story['id']:02d} · {story['region']} · {story['beat']} · HL {story['hl']}"
    if story.get("mark"):
        tag += " †"
    hl_lines = wrap(draw, story["headline"], hf, col_w)
    nx_lines = wrap(draw, "→ " + story["next"], nf, col_w)
    return len(hl_lines) * (hf.size + 1) + len(nx_lines) * (nf.size + 1) + tf.size + 7


def draw_cell(draw, story, x, y, col_w, hf, nf, tf):
    """Draw one story cell; returns bottom y."""
    beat_c = BEAT_COLOR.get(story["beat"], INK)
    draw.rectangle([x, y + 2, x + 4, y + 30], fill=beat_c)
    tag = f"{story['id']:02d} · {story['region']} · {story['beat']} · HL {story['hl']}"
    if story.get("mark"):
        tag += " †"
    draw.text((x + 10, y), tag, font=tf, fill=MUTED)
    yy = y + tf.size + 2
    for line in wrap(draw, story["headline"], hf, col_w - 10):
        draw.text((x + 10, yy), line, font=hf, fill=INK)
        yy += hf.size + 1
    for line in wrap(draw, "→ " + story["next"], nf, col_w - 10):
        draw.text((x + 10, yy), line, font=nf, fill=MUTED)
        yy += nf.size + 1
    yy += 3
    draw.line([(x, yy), (x + col_w, yy)], fill=RULE, width=1)
    return yy + 4


def masthead(draw, data, y, title_size=40):
    d = draw
    f_kick = font(SANS_B, 12)
    f_title = font(SERIF_B, title_size)
    f_hook = font(SANS_B, 17)
    d.text((28, y), "THE DAY IN ONE PAGE", font=f_kick, fill=RED)
    y += 18
    d.text((28, y), data["date"].upper(), font=f_title, fill=INK)
    y += title_size + 6
    d.text((28, y), data["hook"], font=f_hook, fill=INK)
    y += 26
    d.line([(28, y), (W - 28, y)], fill=INK, width=3)
    y += 4
    d.line([(28, y), (W - 28, y)], fill=INK, width=1)
    return y + 8


def numbers_band(draw, data, y, h=56):
    d = draw
    nums = data["lead_numbers"]
    col_w = (W - 56) // 4
    f_n = font(SERIF_B, 26)
    f_l = font(SANS_B, 10)
    for i, item in enumerate(nums):
        x = 28 + i * col_w
        d.text((x, y), item["n"], font=f_n, fill=RED if i in (0, 1) else INK)
        for j, line in enumerate(wrap(d, item["label"].upper(), f_l, col_w - 12)):
            d.text((x, y + 32 + j * 12), line, font=f_l, fill=MUTED)
        if i:
            d.line([(x - 8, y), (x - 8, y + h - 6)], fill=RULE, width=1)
    return y + h


def spine_band(draw, data, y, h=50):
    d = draw
    d.rectangle([28, y, W - 28, y + h], fill=DARK)
    f_s = font(SANS_B, 11)
    f_t = font(SANS, 13)
    d.text((40, y + 7), "THE SPINE", font=f_s, fill=(232, 200, 90))
    spine = data["spine"]
    for j, line in enumerate(wrap(d, spine, f_t, W - 56 - 24)):
        d.text((40, y + 23 + j * 16), line, font=f_t, fill=(247, 243, 234))
    return y + h + 10


def footer(draw, data, y):
    d = draw
    counts = {}
    for s in data["stories"]:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    legend = "  ·  ".join(
        f"{r['code']} {counts.get(r['code'], 0)}" for r in data["regions"]
    )
    f_f = font(SANS, 11)
    f_fb = font(SANS_B, 11)
    d.line([(28, y), (W - 28, y)], fill=INK, width=2)
    y += 7
    d.text((28, y), "DATE CHECK — " + data["date_check"], font=f_fb, fill=INK)
    y += 15
    d.text((28, y), legend, font=f_f, fill=MUTED)
    y += 15
    d.text((28, y), "Drawn after the day ended · Saturday 21 November 2026 · 50 stories, 9 regions",
           font=f_f, fill=MUTED)
    return y + 15


def fit_fonts(draw, stories, col_w, avail_h, ncols):
    """Pick the largest font set whose grid fits avail_h."""
    per_col = -(-len(stories) // ncols)
    for hs, ns, ts in [(12, 10, 9), (11, 10, 8), (10, 9, 8)]:
        hf, nf, tf = font(SANS_B, hs), font(SANS, ns), font(SANS_B, ts)
        total = 0
        for c in range(ncols):
            col = stories[c * per_col:(c + 1) * per_col]
            total = max(total, sum(
                story_cell_height(draw, s, col_w, hf, nf, tf) for s in col))
        if total <= avail_h:
            return hf, nf, tf, total, (hs, ns, ts)
    hf, nf, tf = font(SANS_B, 10), font(SANS, 9), font(SANS_B, 8)
    total = 0
    for c in range(ncols):
        col = stories[c * per_col:(c + 1) * per_col]
        total = max(total, sum(
            story_cell_height(draw, s, col_w, hf, nf, tf) for s in col))
    return hf, nf, tf, total, (10, 9, 8)


def layout_a(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = masthead(d, data, 12)
    y = numbers_band(d, data, y)
    y += 6
    y = spine_band(d, data, y)
    foot_h = 54
    avail = H - 12 - foot_h - y
    ncols, gap = 3, 16
    col_w = (W - 56 - (ncols - 1) * gap) // ncols
    hf, nf, tf, used, sizes = fit_fonts(d, data["stories"], col_w, avail, ncols)
    per_col = -(-len(data["stories"]) // ncols)
    for c in range(ncols):
        col = data["stories"][c * per_col:(c + 1) * per_col]
        x = 28 + c * (col_w + gap)
        yy = y
        for s in col:
            yy = draw_cell(d, s, x, yy, col_w, hf, nf, tf)
    footer(d, data, H - 12 - foot_h + 4)
    return img, sizes, used, avail


def layout_b(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = masthead(d, data, 12, title_size=36)
    spine_w = 150
    spine_x = (W - spine_w) // 2
    grid_top = y + 4
    grid_bot = H - 12
    d.rectangle([spine_x, grid_top, spine_x + spine_w, grid_bot], fill=DARK)
    f_sb = font(SANS_B, 12)
    f_st = font(SANS, 12)
    yy = grid_top + 12
    d.text((spine_x + 12, yy), "THE SPINE", font=f_sb, fill=(232, 200, 90))
    yy += 22
    for beat in data["spine_beats"]:
        d.text((spine_x + 12, yy), beat["beat"], font=f_sb, fill=(232, 200, 90))
        yy += 16
        for line in wrap(d, beat["text"], f_st, spine_w - 24):
            d.text((spine_x + 12, yy), line, font=f_st, fill=(247, 243, 234))
            yy += 15
        yy += 10
    yy += 6
    f_n = font(SERIF_B, 24)
    f_l = font(SANS_B, 9)
    for item in data["lead_numbers"]:
        d.text((spine_x + 12, yy), item["n"], font=f_n, fill=(232, 200, 90))
        yy += 28
        for line in wrap(d, item["label"].upper(), f_l, spine_w - 24):
            d.text((spine_x + 12, yy), line, font=f_l, fill=(200, 196, 186))
            yy += 12
        yy += 10
    side_w = spine_x - 28 - 12
    col_w = side_w
    avail = grid_bot - grid_top
    left = data["stories"][:25]
    right = data["stories"][25:]
    hf, nf, tf, used, sizes = fit_fonts(d, left, col_w, avail, 1)
    hf2, nf2, tf2, used2, _ = fit_fonts(d, right, col_w, avail, 1)
    if sizes > (hf2.size, nf2.size, tf2.size):
        hf, nf, tf = hf2, nf2, tf2
        used = max(used, used2)
    for col, x in ((left, 28), (right, spine_x + spine_w + 12)):
        yy = grid_top
        for s in col:
            yy = draw_cell(d, s, x, yy, col_w, hf, nf, tf)
    return img, sizes, used, avail


def layout_c(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = masthead(d, data, 12)
    panel_h = 150
    d.rectangle([28, y, W - 28, y + panel_h], fill=DARK)
    leads = [
        ("$3.79bn", "GTA VI — the biggest entertainment day ever"),
        ("-5.3%", "NASDAQ — worst week since 2020, $4tn wiped"),
        ("400+", "DRONES — Russia’s biggest attack of the year"),
    ]
    col_w = (W - 56) // 3
    f_n = font(SERIF_B, 44)
    f_l = font(SANS_B, 12)
    for i, (n, label) in enumerate(leads):
        x = 28 + i * col_w
        d.text((x + 16, y + 14), n, font=f_n, fill=(232, 200, 90))
        for j, line in enumerate(wrap(d, label, f_l, col_w - 32)):
            d.text((x + 16, y + 72 + j * 16), line, font=f_l,
                   fill=(247, 243, 234))
        if i:
            d.line([(x, y + 14), (x, y + panel_h - 14)], fill=(90, 86, 78), width=1)
    f_sp = font(SANS, 13)
    d.text((44, y + panel_h - 30), "THE SPINE — " + data["spine"],
           font=f_sp, fill=(200, 196, 186))
    y += panel_h + 12
    foot_h = 54
    avail = H - 12 - foot_h - y
    ncols, gap = 3, 16
    col_w = (W - 56 - (ncols - 1) * gap) // ncols
    hf, nf, tf, used, sizes = fit_fonts(d, data["stories"], col_w, avail, ncols)
    per_col = -(-len(data["stories"]) // ncols)
    for c in range(ncols):
        col = data["stories"][c * per_col:(c + 1) * per_col]
        x = 28 + c * (col_w + gap)
        yy = y
        for s in col:
            yy = draw_cell(d, s, x, yy, col_w, hf, nf, tf)
    footer(d, data, H - 12 - foot_h + 4)
    return img, sizes, used, avail


def main():
    stories_path, layout, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(stories_path) as fh:
        data = json.load(fh)
    fn = {"A": layout_a, "B": layout_b, "C": layout_c}[layout]
    img, sizes, used, avail = fn(data)
    img.save(out_path, format="PNG", optimize=True)
    raw = open(out_path, "rb").read()
    print(f"layout={layout} size={img.size} bytes={len(raw)} "
          f"sha256={hashlib.sha256(raw).hexdigest()} fonts={sizes} "
          f"grid_used={used} grid_avail={avail} overflow={max(0, used - avail)}")


if __name__ == "__main__":
    main()
