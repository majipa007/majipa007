#!/usr/bin/env python3
"""
GitHub ASCII Profile Generator
==============================
Turns YOUR photo into an ASCII-art "neofetch style" GitHub profile README,
just like Andrew6rant's profile.

Usage:
    python github_ascii_profile.py your_photo.jpg

Then copy the generated README.md into a repo named exactly
the same as your GitHub username (e.g. github.com/YOURNAME/YOURNAME).

Requires:  pip install pillow
"""

import sys
from datetime import date, timedelta
from PIL import Image, ImageOps, ImageEnhance

# ============================================================
#  1. EDIT YOUR PERSONAL INFO HERE
# ============================================================
USERNAME = "majipa007"         # shows as  majipa007@github
BIRTHDATE = date(2002, 12, 22)  # Uptime auto-computes from this


def uptime_string() -> str:
    today = date.today()
    y = today.year - BIRTHDATE.year
    m = today.month - BIRTHDATE.month
    d = today.day - BIRTHDATE.day
    if d < 0:
        m -= 1
        prev_month_end = date(today.year, today.month, 1) - timedelta(days=1)
        d += prev_month_end.day
    if m < 0:
        y -= 1
        m += 12
    return f"{y} years, {m} months, {d} days"


INFO = [
    ("header", f"{USERNAME}@github"),
    ("OS",                    "Linux (Ubuntu, Mint, Omarchy), Windows 11, Android"),
    ("Uptime",                uptime_string()),
    ("Host",                  "Ascentium"),
    ("Kernel",                "AI/ML Engineer"),
    ("Location",              "Coimbatore, India"),
    ("IDE",                   "VSCode, Neovim"),
    ("blank", ""),
    ("Languages.Programming", "Python, Go, JavaScript, TypeScript"),
    ("Languages.Computer",    "HTML, CSS, JSON, YAML, Bash"),
    ("Languages.Real",        "English, Nepali, Hindi"),
    ("blank", ""),
    ("Hobbies.Software",      "ML/AI Experiments, Open Source"),
    ("blank", ""),
    ("header", "Contact"),
    ("Email.Personal",        "sulavstha007@gmail.com"),
    ("LinkedIn",              "sulav-shrestha-16b1091bb"),
    ("Medium",                "@sulavstha007"),
    ("Discord",               "majipa007"),
    ("blank", ""),
    ("header", "GitHub Stats"),
    ("Repos",                 "27 | Stars: 34"),
    ("Commits",               "281 | Followers: 25"),
]

# ============================================================
#  2. TUNE THE ART LOOK (optional)
# ============================================================
MODE        = "braille"  # "braille" = high detail (2x4 dots/char), "ascii" = classic
COLORIZE    = True   # ANSI colors — GitHub renders them inside ```ansi blocks
ART_WIDTH   = 50     # characters wide (braille: 40-60, ascii: 40-55 looks best)
INFO_WIDTH  = 66     # width of the right info panel
CONTRAST    = 1.6    # 1.0 = normal, higher = punchier
BRIGHTNESS  = 1.05
INVERT      = True   # True = dark background (GitHub dark mode style)
DITHER      = True   # braille only: smooth shading via Floyd-Steinberg dithering
# Character ramp: dark -> light (ascii mode only)
RAMP = "@%#WM8B$kbdpqmwZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

CHAR_ASPECT = 0.5    # a terminal character is ~2x taller than wide

# Colors, per role. GitHub can't render ANSI in READMEs, so the colored
# version is written as profile.svg and embedded in the README as an image.
# ansi = terminal preview, svg = hex fill + weight for the SVG.
STYLES = {
    "art":    {"ansi": "",     "svg": ("#c9d1d9", "normal")},  # b&w portrait
    "header": {"ansi": "1;36", "svg": ("#39c5cf", "bold")},    # cyan
    "key":    {"ansi": "1;94", "svg": ("#79c0ff", "bold")},    # bright blue
    "dots":   {"ansi": "90",   "svg": ("#484f58", "normal")},  # faint gray
    "value":  {"ansi": "",     "svg": ("#e6edf3", "normal")},  # near-white
}
SVG_BG     = "#0d1117"   # GitHub dark-mode background
SVG_BORDER = "#30363d"
FONT_SIZE  = 14
CHAR_W     = 8.4         # monospace advance at 14px (0.6em)
LINE_H     = 16.8        # 2x char width keeps the braille art square


def paint(text: str, role: str) -> str:
    """ANSI-colorize for the terminal preview."""
    code = STYLES[role]["ansi"]
    if not COLORIZE or not code or not text:
        return text
    return f"\033[{code}m{text}\033[0m"


def load_photo(path: str) -> Image.Image:
    """Load, square-crop and tone-adjust the photo."""
    img = Image.open(path).convert("L")
    img = ImageOps.exif_transpose(img)

    # crop to square around the center (like a profile avatar)
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2,
                    (w + side) // 2, (h + side) // 2))

    img = ImageEnhance.Contrast(img).enhance(CONTRAST)
    img = ImageEnhance.Brightness(img).enhance(BRIGHTNESS)
    return img


# Braille dot bit positions within a 2x4 cell:
#   (x=0,y=0)=0x01  (x=1,y=0)=0x08
#   (x=0,y=1)=0x02  (x=1,y=1)=0x10
#   (x=0,y=2)=0x04  (x=1,y=2)=0x20
#   (x=0,y=3)=0x40  (x=1,y=3)=0x80
_BRAILLE_BITS = {(0, 0): 0x01, (0, 1): 0x02, (0, 2): 0x04, (0, 3): 0x40,
                 (1, 0): 0x08, (1, 1): 0x10, (1, 2): 0x20, (1, 3): 0x80}


def image_to_braille(path: str) -> list[str]:
    """Each braille char encodes 2x4 pixels -> 8x the detail of ascii."""
    img = load_photo(path)

    # 2 px per char horizontally, 4 px vertically; a char is ~2x taller
    # than wide, so a square pixel grid keeps the photo's proportions.
    px_w = ART_WIDTH * 2
    px_h = px_w
    img = img.resize((px_w, px_h))

    # lit dots should be the BRIGHT parts of the photo on a dark background
    if not INVERT:
        img = ImageOps.invert(img)

    if DITHER:
        img = img.convert("1")  # Floyd-Steinberg dithering
    else:
        img = img.point(lambda p: 255 if p > 127 else 0).convert("1")

    px = img.load()
    lines = []
    for cy in range(px_h // 4):
        row = []
        for cx in range(px_w // 2):
            code = 0x2800
            for (dx, dy), bit in _BRAILLE_BITS.items():
                if px[cx * 2 + dx, cy * 4 + dy]:
                    code |= bit
            row.append(chr(code))
        lines.append("".join(row))
    return lines


def image_to_ascii(path: str) -> list[str]:
    img = load_photo(path)

    new_h = int(ART_WIDTH * CHAR_ASPECT)
    img = img.resize((ART_WIDTH, new_h))

    if INVERT:
        img = ImageOps.invert(img)

    ramp = RAMP
    n = len(ramp) - 1
    lines = []
    px = img.load()
    for y in range(img.height):
        row = "".join(ramp[int(px[x, y] / 255 * n)] for x in range(img.width))
        lines.append(row.rstrip())
    return lines


Segment = tuple[str, str]  # (text, role)


def build_info_panel() -> list[list[Segment]]:
    """Each line is a list of (text, role) segments so any renderer can color it."""
    lines: list[list[Segment]] = []
    for key, val in INFO:
        if key == "blank":
            lines.append([(".", "dots")])
        elif key == "header":
            title = f"- {val} " if lines else f"{val} "
            line = title + "-" * max(0, INFO_WIDTH - len(title) - 1) + "-."
            lines.append([(line, "header")])
        else:
            label = f". {key}: "
            dots = "." * max(1, INFO_WIDTH - len(label) - len(val) - 1)
            lines.append([(label, "key"), (dots, "dots"), (" " + val, "value")])
    return lines


def combine_rows(art: list[str], info: list[list[Segment]]) -> list[list[Segment]]:
    """Merge art and info into full-width segment rows."""
    height = max(len(art), len(info))
    art = art + [""] * (height - len(art))
    info = info + [[]] * (height - len(info))
    rows = []
    for a, b in zip(art, info):
        rows.append([(f"{a:<{ART_WIDTH}}  ", "art")] + b)
    return rows


def render_ansi(rows: list[list[Segment]]) -> str:
    return "\n".join(
        "".join(paint(text, role) for text, role in row).rstrip() for row in rows
    )


def render_plain(rows: list[list[Segment]]) -> str:
    return "\n".join(
        "".join(text for text, _ in row).rstrip() for row in rows
    )


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(art: list[str], info: list[list[Segment]]) -> str:
    """Art and info are separate text elements, and every segment is pinned to
    an exact pixel grid with textLength — font metric differences (especially
    braille glyph widths) can't shift or clip the layout."""
    pad = 20
    info_x = pad + (ART_WIDTH + 2) * CHAR_W
    n_info = max((sum(len(t) for t, _ in row) for row in info), default=0)
    width = int(info_x + n_info * CHAR_W + pad)
    height = int(max(len(art), len(info)) * LINE_H + pad * 2)
    font = ('ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, '
            '"Liberation Mono", "DejaVu Sans Mono", monospace')
    art_fill = STYLES["art"]["svg"][0]

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" rx="8" fill="{SVG_BG}" '
        f'stroke="{SVG_BORDER}" stroke-width="1"/>',
        f'<g font-family=\'{font}\' font-size="{FONT_SIZE}" xml:space="preserve">',
    ]
    for i in range(max(len(art), len(info))):
        y = pad + FONT_SIZE + i * LINE_H
        if i < len(art) and art[i].strip("⠀ "):
            out.append(
                f'<text x="{pad}" y="{y:.1f}" fill="{art_fill}" '
                f'textLength="{ART_WIDTH * CHAR_W:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{art[i]:<{ART_WIDTH}}</text>')
        if i < len(info) and info[i]:
            spans, cx = [], info_x
            for text, role in info[i]:
                if not text:
                    continue
                fill, weight = STYLES[role]["svg"]
                bold = ' font-weight="bold"' if weight == "bold" else ""
                seg_w = len(text) * CHAR_W
                spans.append(
                    f'<tspan x="{cx:.1f}" textLength="{seg_w:.1f}" '
                    f'lengthAdjust="spacingAndGlyphs" fill="{fill}"{bold}>'
                    f'{_xml_escape(text)}</tspan>')
                cx += seg_w
            out.append(f'<text y="{y:.1f}">{"".join(spans)}</text>')
    out.append("</g></svg>")
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        print("Usage: python github_ascii_profile.py <photo.jpg>")
        sys.exit(1)

    if MODE == "braille":
        art = image_to_braille(sys.argv[1])
    else:
        art = image_to_ascii(sys.argv[1])
    info = build_info_panel()
    rows = combine_rows(art, info)

    if COLORIZE:
        # GitHub can't render ANSI colors in a README code block,
        # so colors ship as an SVG image embedded in the README.
        with open("profile.svg", "w", encoding="utf-8") as f:
            f.write(render_svg(art, info))
        readme = '<img src="./profile.svg" alt="terminal-style profile card">\n'
    else:
        readme = "```text\n" + render_plain(rows) + "\n```\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print(render_ansi(rows))
    print("\n✅ README.md" + (" + profile.svg" if COLORIZE else "")
          + " generated! Push to a repo named after your username.")


if __name__ == "__main__":
    main()
