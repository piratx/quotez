#!/usr/bin/env python3
"""
Picks a random quote from quotes/*.md and renders it as a transparent-
background PNG (quote.png) for embedding in an email signature via
<img src="https://raw.githubusercontent.com/USER/REPO/main/quote.png">.

Run on a schedule by .github/workflows/rotate.yml.
"""
import glob
import os
import random
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

QUOTES_DIR = os.path.join(os.path.dirname(__file__), "quotes")
OUT_PATH = os.path.join(os.path.dirname(__file__), "quote.png")

# Fonts (installed via the workflow's `apt-get install fonts-dejavu-core`,
# also commonly present on Ubuntu runners by default).
FONT_CANDIDATES_ITALIC = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
]
FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

MAX_WIDTH = 480          # px, roughly matches a typical signature column
QUOTE_FONT_SIZE = 15
ATTR_FONT_SIZE = 13
LINE_SPACING = 6
PADDING = 4
# Neutral gray: readable on both light and dark email backgrounds.
TEXT_COLOR = (136, 136, 136, 255)


def load_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def parse_quote_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    i = 0
    # Skip YAML frontmatter.
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1  # skip closing ---
    # Skip blank lines and the "# heading" line.
    # Skip any number of blank lines and "# heading" lines, in any order
    # (some notes have a stray duplicate heading left in them).
    while i < len(lines) and (lines[i].strip() == "" or lines[i].startswith("#")):
        i += 1

    body_lines = [l for l in lines[i:] if l.strip() != ""]
    if not body_lines:
        return None, None

    zero_width = re.compile("[​‌‍﻿]")

    def clean(s):
        return zero_width.sub("", s).strip()

    attribution = clean(body_lines[-1])
    quote_text = " ".join(clean(l) for l in body_lines[:-1])
    return quote_text, attribution


def wrap_to_width(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main():
    files = glob.glob(os.path.join(QUOTES_DIR, "*.md"))
    if not files:
        raise SystemExit(f"No quote files found in {QUOTES_DIR}")

    quote_text = attribution = None
    random.shuffle(files)
    for path in files:
        quote_text, attribution = parse_quote_file(path)
        if quote_text and attribution:
            break
    if not quote_text:
        raise SystemExit("Could not parse a quote from any file")

    quote_text = f"“{quote_text}”"
    attribution = f"— {attribution}"

    quote_font = load_font(FONT_CANDIDATES_ITALIC, QUOTE_FONT_SIZE)
    attr_font = load_font(FONT_CANDIDATES_REGULAR, ATTR_FONT_SIZE)

    # Measure using a scratch image first.
    scratch = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(scratch)

    quote_lines = wrap_to_width(draw, quote_text, quote_font, MAX_WIDTH)
    attr_lines = wrap_to_width(draw, attribution, attr_font, MAX_WIDTH)

    def line_height(font):
        bbox = font.getbbox("Ag")
        return bbox[3] - bbox[1]

    qh = line_height(quote_font)
    ah = line_height(attr_font)

    total_height = (
        PADDING * 2
        + qh * len(quote_lines)
        + LINE_SPACING * (len(quote_lines) - 1)
        + LINE_SPACING * 2
        + ah * len(attr_lines)
        + LINE_SPACING * (len(attr_lines) - 1)
    )
    total_width = MAX_WIDTH + PADDING * 2

    img = Image.new("RGBA", (total_width, int(total_height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = PADDING
    for line in quote_lines:
        draw.text((PADDING, y), line, font=quote_font, fill=TEXT_COLOR)
        y += qh + LINE_SPACING
    y += LINE_SPACING
    for line in attr_lines:
        draw.text((PADDING, y), line, font=attr_font, fill=TEXT_COLOR)
        y += ah + LINE_SPACING

    img.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}: {quote_text} {attribution}")


if __name__ == "__main__":
    main()
