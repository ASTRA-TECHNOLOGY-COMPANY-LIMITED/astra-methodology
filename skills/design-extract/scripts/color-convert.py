#!/usr/bin/env python3
"""
color-convert.py — sRGB hex → OKLCH converter for /design-extract.

Reference math: Björn Ottosson, "A perceptual color space for image processing"
(https://bottosson.github.io/posts/oklab/).

Pipeline:
  sRGB hex → sRGB linear → linear-to-LMS matrix → cube-root LMS → OKLab
  → polar form OKLCH (L kept, a/b → C/h).

Usage:
  python3 color-convert.py "#3b82f6"
  python3 color-convert.py "#3b82f6" "#10b981" "#f59e0b"
  echo "#3b82f6" | python3 color-convert.py -        # stdin

Output: one OKLCH string per line in the same form used by DESIGN.md
Front Matter (e.g., "oklch(62.3% 0.214 259.8)").

This script intentionally has zero non-stdlib dependencies. If you need
batch conversion or palette expansion (50 → 950 shades), call this script
once per shade or extend it.
"""
from __future__ import annotations

import math
import sys


def _srgb_to_linear(c: float) -> float:
    """Inverse sRGB transfer function. Input/output in 0..1."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _hex_to_linear_rgb(hex_color: str) -> tuple[float, float, float]:
    """Parse #RRGGBB or #RGB into linear-light RGB triples in 0..1."""
    s = hex_color.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"invalid hex color: {hex_color!r}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)


def _linear_rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    """Apply Ottosson's M1 then cube-root then M2."""
    # M1: linear sRGB → LMS
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    # Non-linearity
    l_ = l ** (1.0 / 3.0) if l >= 0 else -((-l) ** (1.0 / 3.0))
    m_ = m ** (1.0 / 3.0) if m >= 0 else -((-m) ** (1.0 / 3.0))
    s_ = s ** (1.0 / 3.0) if s >= 0 else -((-s) ** (1.0 / 3.0))
    # M2: LMS' → Lab
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_ = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, a, b_


def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    """Convert #RRGGBB to (L%, C, h°). L is 0..100 percent for DESIGN.md style."""
    r, g, b = _hex_to_linear_rgb(hex_color)
    L, a, b_ = _linear_rgb_to_oklab(r, g, b)
    C = math.sqrt(a * a + b_ * b_)
    h = math.degrees(math.atan2(b_, a))
    if h < 0:
        h += 360.0
    return L * 100.0, C, h


def format_oklch(L_pct: float, C: float, h: float) -> str:
    """Render in the DESIGN.md Front Matter convention."""
    # Chroma can be 0 for true neutrals; suppress hue noise in that case.
    if C < 1e-4:
        return f"oklch({L_pct:.1f}% 0 0)"
    return f"oklch({L_pct:.1f}% {C:.3f} {h:.1f})"


def _iter_inputs(argv: list[str]):
    if argv and argv[0] == "-":
        for line in sys.stdin:
            line = line.strip()
            if line:
                yield line
        return
    yield from argv


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    rc = 0
    for token in _iter_inputs(argv):
        try:
            L, C, h = hex_to_oklch(token)
            print(format_oklch(L, C, h))
        except ValueError as exc:
            print(f"# error: {exc}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
