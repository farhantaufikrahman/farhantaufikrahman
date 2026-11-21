"""Re-skins the Platane/snk contribution snake as a comet crossing a pixel night sky.

    python3 scripts/skin_snake.py <snk-output.svg> <out.svg>

Everything is done by appending CSS and a background layer, never by rewriting
snk's animation, so a future snk release that changes its markup degrades to
"plain snake on a night background" instead of breaking. If the input does not
look like an snk SVG at all, the input is copied through unchanged.
"""

from __future__ import annotations

import re
import shutil
import sys

from skylib import AMBER, DEEP, LINE, VIOLET, pixel_frame, starfield

# empty cell, then 4 activity levels: dim sky -> blue stars -> a gold star at the top
DOTS = ["#22307a66", "#24347a", "#3d55c8", "#7d96ff", "#ffd27a"]
# the snake is a comet: white-hot head, amber body, tail fading out
HEAD, BODY = "#fff3c4", AMBER


def skin(svg: str) -> str:
    m = re.search(r"<svg\b[^>]*>", svg)
    vb = re.search(r'viewBox="([-\d.\s]+)"', m.group(0)) if m else None
    if not m or not vb or "<style>" not in svg:
        raise ValueError("not an snk svg")
    vx, vy, vw, vh = (float(v) for v in vb.group(1).split())

    segments = sorted({int(n) for n in re.findall(r"\.s\.s(\d+)\b", svg)})
    tail = []
    for i in segments:
        k = i / max(1, len(segments) - 1)
        fill = HEAD if i == 0 else BODY
        tail.append(f".s.s{i}{{fill:{fill};opacity:{1 - .62 * k:.2f}}}")

    palette = (
        f"--cb:#ffffff0a;--cs:{BODY};--ce:{DOTS[0]};"
        + "".join(f"--c{i}:{c};" for i, c in enumerate(DOTS))
    )
    css = (
        f":root{{{palette}}}@media (prefers-color-scheme:dark){{:root{{{palette}}}}}"
        f"@media (prefers-color-scheme:light){{:root{{{palette}}}}}"
        ".c,.u{shape-rendering:crispEdges;stroke:var(--cb)}"
        f".s{{shape-rendering:crispEdges;filter:drop-shadow(0 0 3px {AMBER})}}"
        + "".join(tail)
        + ".tw{animation:tw 3.4s steps(4) infinite}@keyframes tw{50%{opacity:.2}}"
        "@media (prefers-reduced-motion:reduce){.tw{animation:none}}"
    )
    svg = svg.replace("</style>", css + "</style>", 1)

    # square pixels: drop the rounded corners on cells and snake segments
    svg = re.sub(r'\s(rx|ry)="[\d.]+"', "", svg)

    pad = 6
    x, y, w, h = vx - pad, vy - pad, vw + 2 * pad, vh + 2 * pad
    stars = starfield(7, int(w), int(h), 90, sparkle_every=0, opacity=.7)
    stars = stars.replace('class="t', 'class="tw t')  # snk has no twinkle classes; use ours
    frame = pixel_frame(w, h, 6)
    background = (
        f'<defs><radialGradient id="sky-nb" cx=".85" cy="0" r=".8">'
        f'<stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient></defs>'
        f'<g transform="translate({x} {y})"><path d="{frame}" fill="{DEEP}"/>'
        f'<path d="{frame}" fill="url(#sky-nb)"/>{stars}'
        f'<path d="{frame}" fill="none" stroke="{LINE}" stroke-width="1.5"/></g>'
    )
    svg = svg.replace("</style>", "</style>" + background, 1)

    # widen the viewBox a little so the frame is not clipped
    new_vb = f'viewBox="{x} {y} {w} {h}"'
    svg = svg.replace(vb.group(0), new_vb, 1)
    svg = re.sub(r'(<svg\b[^>]*?)\swidth="[\d.]+"', rf'\1 width="{w:g}"', svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\sheight="[\d.]+"', rf'\1 height="{h:g}"', svg, count=1)
    return svg


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    try:
        with open(src) as f:
            out = skin(f.read())
        with open(dst, "w") as f:
            f.write(out)
        print(f"skin_snake: wrote {dst}")
    except Exception as exc:
        print(f"skin_snake: copying the plain snake through ({exc})", file=sys.stderr)
        shutil.copyfile(src, dst)


if __name__ == "__main__":
    main()
