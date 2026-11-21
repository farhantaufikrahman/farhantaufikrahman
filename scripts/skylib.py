"""Shared helpers for the pixel night-sky SVGs in this profile.

Standard library only, so the GitHub Actions workflow can import it without
installing anything. Every SVG is self-contained (font and sprites inlined),
because GitHub serves README images through its camo proxy, which blocks
external requests made from inside an SVG.
"""

from __future__ import annotations

import base64
import json
import random
import re
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Palette shared with the portfolio (src/app/globals.css in main-portofolio).
SKY = "#050817"
SKY_LOW = "#0b1236"
DEEP = "#070b22"
PANEL = "#0e1538"
LINE = "#26326e"
LINE_STRONG = "#3d4c9a"
INK = "#ecf1ff"
INK_SOFT = "#c9d2f0"
MUTED = "#97a3cc"
ROUTE = "#5b7cff"
ROUTE_TEXT = "#8ea6ff"
AMBER = "#ffb524"
AMBER_TEXT = "#ffc552"
SIGNAL = "#3be38b"
MINT = "#4fe3c1"
STAR_BLUE = "#a9c3ff"
STAR_GOLD = "#ffd27a"
VIOLET = "#7c4dff"

FONT_FAMILY = "J"

_metrics = json.loads((HERE / "fonts" / "jersey10-metrics.json").read_text())


def text_width(text: str, size: float) -> float:
    """Rendered width of `text` in Jersey 10 at `size` px."""
    adv = _metrics["adv"]
    units = sum(adv.get(ch, adv["?"]) for ch in text)
    return units * size / _metrics["upm"]


def wrap(text: str, size: float, max_width: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and text_width(trial, size) > max_width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def font_face() -> str:
    data = base64.b64encode((HERE / "fonts" / "jersey10.woff").read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{FONT_FAMILY}';"
        f"src:url(data:font/woff;base64,{data}) format('woff')}}"
        f"text{{font-family:'{FONT_FAMILY}',monospace}}"
    )


BASE_CSS = """
.t1{animation:tw 2.6s steps(4) infinite}.t2{animation:tw 3.4s steps(4) infinite}
.t3{animation:tw 4.2s steps(5) infinite}.t4{animation:tw 5.1s steps(5) infinite}
@keyframes tw{0%,100%{opacity:1}50%{opacity:.2}}
.rise{animation:rise .9s cubic-bezier(.16,1,.3,1) both}
@keyframes rise{from{opacity:0;transform:translateY(12px)}}
.float{animation:float 7s ease-in-out infinite}
@keyframes float{50%{transform:translateY(7px)}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.sweep{animation:sweep 7s cubic-bezier(.45,0,.55,1) infinite}
@keyframes sweep{0%{transform:translateX(-500px)}55%,100%{transform:translateX(1700px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def esc(s: str) -> str:
    return escape(s, quote=True)


def pixel_frame(w: float, h: float, c: float = 8) -> str:
    """Rectangle with stepped (pixel) corners, as an SVG path `d`."""
    return f"M0 {c}H{c}V0H{w-c}V{c}H{w}V{h-c}H{w-c}V{h}H{c}V{h-c}H0Z"


def pixel_chip(x: float, y: float, w: float, h: float, c: float = 4) -> str:
    return (
        f"M{x} {y+c}H{x+c}V{y}H{x+w-c}V{y+c}H{x+w}V{y+h-c}H{x+w-c}V{y+h}"
        f"H{x+c}V{y+h-c}H{x}Z"
    )


def starfield(
    seed: int,
    w: int,
    h: int,
    n: int,
    *,
    sparkle_every: int = 9,
    colors=("#ffffff", "#ffffff", "#ffffff", STAR_BLUE, STAR_BLUE, STAR_GOLD),
    opacity: float = 1.0,
    avoid=None,
) -> str:
    """Scattered square stars with stepped twinkles; every Nth star gets a sparkle cross."""
    rnd = random.Random(seed)
    out = [f'<g shape-rendering="crispEdges" opacity="{opacity}">']
    for i in range(n):
        for _ in range(20):
            x, y = rnd.randrange(0, w), rnd.randrange(0, h)
            if not avoid or not avoid(x, y):
                break
        col = rnd.choice(colors)
        cls = f"t{rnd.randint(1, 4)}"
        delay = f"{-rnd.uniform(0, 4):.2f}s"
        if sparkle_every and i % sparkle_every == 0:
            out.append(
                f'<g class="{cls}" style="animation-delay:{delay}" fill="{col}">'
                f'<rect x="{x}" y="{y}" width="4" height="4"/>'
                f'<rect x="{x-4}" y="{y+1}" width="3" height="2" opacity=".55"/>'
                f'<rect x="{x+5}" y="{y+1}" width="3" height="2" opacity=".55"/>'
                f'<rect x="{x+1}" y="{y-4}" width="2" height="3" opacity=".55"/>'
                f'<rect x="{x+1}" y="{y+5}" width="2" height="3" opacity=".55"/></g>'
            )
        else:
            s = rnd.choice((2, 2, 2, 3))
            out.append(
                f'<rect class="{cls}" style="animation-delay:{delay}" x="{x}" y="{y}" '
                f'width="{s}" height="{s}" fill="{col}"/>'
            )
    out.append("</g>")
    return "".join(out)


def sprite(name: str, x: float, y: float, scale: float, extra: str = "") -> str:
    """Inline one of the portfolio's pixel sprites (rect-only SVGs) as a <g>."""
    raw = (HERE / "sprites" / f"{name}.svg").read_text()
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", raw, flags=re.S)
    return (
        f'<g transform="translate({x} {y}) scale({scale})" shape-rendering="crispEdges" {extra}>'
        f"{inner}</g>"
    )


def sprite_size(name: str) -> tuple[float, float]:
    raw = (HERE / "sprites" / f"{name}.svg").read_text()
    vb = re.search(r'viewBox="([\d.\s-]+)"', raw).group(1).split()
    return float(vb[2]), float(vb[3])


def comet(x: float, y: float, px: int, head: str, tail: str) -> str:
    """A pixel comet pointing to the upper right, built from squares."""
    cells = []
    # head (3x3 with a bright core)
    for dx, dy, col in [(0, 0, "#ffffff"), (1, 0, head), (0, 1, head), (1, 1, head),
                        (-1, 0, head), (0, -1, head), (2, 1, head), (1, 2, head)]:
        cells.append((dx, dy, col, 1))
    # tail toward the lower left, fading out
    for i in range(1, 14):
        op = max(0.08, 1 - i / 13)
        cells.append((-i, i, tail, op))
        if i < 10:
            cells.append((-i + 1, i, tail, op * 0.7))
            cells.append((-i, i - 1, tail, op * 0.7))
        if i < 6:
            cells.append((-i + 1, i + 1, tail, op * 0.45))
    out = [f'<g transform="translate({x} {y})" shape-rendering="crispEdges">']
    for dx, dy, col, op in cells:
        out.append(
            f'<rect x="{dx*px}" y="{dy*px}" width="{px}" height="{px}" fill="{col}" '
            f'opacity="{op:.2f}"/>'
        )
    out.append("</g>")
    return "".join(out)


def pixel_star(x: float, y: float, px: int, col: str, core: str = "#ffffff") -> str:
    """Big four-point pixel star."""
    pts = [(0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (-3, 0), (-2, 0), (-1, 0),
           (1, 0), (2, 0), (3, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    out = [f'<g transform="translate({x} {y})" shape-rendering="crispEdges">']
    for dx, dy in pts:
        out.append(f'<rect x="{dx*px}" y="{dy*px}" width="{px}" height="{px}" fill="{col}"/>')
    out.append(f'<rect x="0" y="0" width="{px}" height="{px}" fill="{core}"/>')
    out.append("</g>")
    return "".join(out)


def svg_doc(w: int, h: int, title: str, desc: str, css: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" role="img" aria-labelledby="t d">'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
        f"<style>{font_face()}{BASE_CSS}{css}</style>{body}</svg>"
    )
