#!/usr/bin/env python3
"""Turn a true-scale plan SVG into a tiled, print-at-100% PDF (1 grid square = 1 inch).

Usage:
  python3 tools/woodworking/print_tiles.py static/static/woodworking/swoop-hanger-templates.svg --ppi 34
  python3 tools/woodworking/print_tiles.py FILE.svg --ppi 12 --grid --crop 0,60,1080,600 -o out.pdf

--ppi   pixels per inch in the SVG: the `s`/`S`/`K`/`P` constant in the matching
        tools/woodworking/*_drawings.py (swoop templates 34, most elevations 12,
        jeweler's chest 24, nightstand 16 / arched rails 24, picture frame 26).
--grid  overlay a 1-inch grid (for drawings that don't already carry one).
--crop  x,y,w,h in SVG px: only tile this region (skip titles/notes you don't need).
--letter / --a4 / --tabloid  paper (default letter).

Each sheet is a letter page with a 0.25 in margin, a 0.5 in overlap with its
neighbours (tape/trim on the dashed lines), a sheet label, and a 1 in + 2 in scale bar.
Print at 100% / "Actual size" — then check the scale bar with a ruler.
Needs `rsvg-convert` (brew install librsvg).
"""
import argparse, math, os, re, shutil, subprocess, sys, tempfile

PAPER = {"letter": (8.5, 11.0), "a4": (8.268, 11.693), "tabloid": (11.0, 17.0)}
MARGIN, OVERLAP = 0.25, 0.5


def read_svg(path):
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"^\s*<\?xml[^>]*\?>", "", txt)
    m = re.search(r"<svg\b[^>]*>", txt)
    root = m.group(0)
    vb = re.search(r'viewBox="([^"]+)"', root)
    if vb:
        x, y, w, h = map(float, vb.group(1).replace(",", " ").split())
    else:
        w = float(re.search(r'width="([\d.]+)', root).group(1))
        h = float(re.search(r'height="([\d.]+)', root).group(1))
        x = y = 0.0
    body = txt[m.end():txt.rindex("</svg>")]
    return body, (x, y, w, h)


def sheet(body, ppi, crop, col, row, ncol, nrow, paper, grid, name):
    pw, ph = paper
    cw, ch = pw - 2 * MARGIN, ph - 2 * MARGIN - 0.55    # content area; footer for scale bar
    step_x, step_y = cw - OVERLAP, ch - OVERLAP
    cx, cy, _, _ = crop
    vx, vy = cx + col * step_x * ppi, cy + row * step_y * ppi   # SVG px at top-left of tile
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw}in" height="{ph}in" viewBox="0 0 {pw} {ph}">')
    o.append(f'<rect width="{pw}" height="{ph}" fill="#fff"/>')
    o.append(f'<svg x="{MARGIN}" y="{MARGIN}" width="{cw}" height="{ch}" viewBox="{vx} {vy} {cw*ppi} {ch*ppi}" '
             f'preserveAspectRatio="xMinYMin slice" overflow="hidden">')
    o.append(body)
    if grid:   # 1 in lines anchored to the SVG origin, so they continue across sheets
        g = []
        i0, i1 = math.floor(vx / ppi), math.ceil((vx + cw * ppi) / ppi)
        j0, j1 = math.floor(vy / ppi), math.ceil((vy + ch * ppi) / ppi)
        for i in range(i0, i1 + 1):
            g.append(f'<line x1="{i*ppi}" y1="{vy}" x2="{i*ppi}" y2="{vy+ch*ppi}"/>')
        for j in range(j0, j1 + 1):
            g.append(f'<line x1="{vx}" y1="{j*ppi}" x2="{vx+cw*ppi}" y2="{j*ppi}"/>')
        o.append(f'<g stroke="#6a8fc4" stroke-width="{0.012*ppi:.3f}" opacity=".55">{"".join(g)}</g>')
    o.append("</svg>")
    # overlap guides (in page inches): dashed lines where the neighbour sheet overlaps
    guide = 'stroke="#c0392b" stroke-width="0.012" stroke-dasharray="0.08 0.06" fill="none"'
    if col < ncol - 1:
        o.append(f'<line x1="{MARGIN+cw-OVERLAP}" y1="{MARGIN}" x2="{MARGIN+cw-OVERLAP}" y2="{MARGIN+ch}" {guide}/>')
    if col > 0:
        o.append(f'<line x1="{MARGIN+OVERLAP}" y1="{MARGIN}" x2="{MARGIN+OVERLAP}" y2="{MARGIN+ch}" {guide}/>')
    if row < nrow - 1:
        o.append(f'<line x1="{MARGIN}" y1="{MARGIN+ch-OVERLAP}" x2="{MARGIN+cw}" y2="{MARGIN+ch-OVERLAP}" {guide}/>')
    if row > 0:
        o.append(f'<line x1="{MARGIN}" y1="{MARGIN+OVERLAP}" x2="{MARGIN+cw}" y2="{MARGIN+OVERLAP}" {guide}/>')
    o.append(f'<rect x="{MARGIN}" y="{MARGIN}" width="{cw}" height="{ch}" fill="none" stroke="#999" stroke-width="0.01"/>')
    # footer: sheet label + scale bars
    fy = MARGIN + ch + 0.12
    font = 'font-family="Helvetica,Arial,sans-serif"'
    o.append(f'<text x="{MARGIN}" y="{fy+0.14}" {font} font-size="0.14" fill="#222">'
             f'{name} — sheet {row*ncol+col+1} of {ncol*nrow} (column {col+1}, row {row+1})</text>')
    o.append(f'<text x="{MARGIN}" y="{fy+0.32}" {font} font-size="0.11" fill="#555">'
             f'Print at 100% / Actual size. Red dashes = overlap: align to the neighbour sheet, then tape. '
             f'Check the bar: it must measure exactly 1 in and 2 in.</text>')
    bx, by = pw - MARGIN - 2.2, fy + 0.02
    o.append(f'<g stroke="#000" stroke-width="0.02" fill="none">'
             f'<line x1="{bx}" y1="{by+0.1}" x2="{bx+2}" y2="{by+0.1}"/>'
             f'<line x1="{bx}" y1="{by}" x2="{bx}" y2="{by+0.2}"/>'
             f'<line x1="{bx+1}" y1="{by+0.03}" x2="{bx+1}" y2="{by+0.17}"/>'
             f'<line x1="{bx+2}" y1="{by}" x2="{bx+2}" y2="{by+0.2}"/></g>')
    o.append(f'<text x="{bx}" y="{by-0.03}" {font} font-size="0.1" fill="#000">0</text>'
             f'<text x="{bx+1}" y="{by-0.03}" {font} font-size="0.1" fill="#000" text-anchor="middle">1 in</text>'
             f'<text x="{bx+2}" y="{by-0.03}" {font} font-size="0.1" fill="#000" text-anchor="end">2 in</text>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--ppi", type=float, required=True)
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--crop")
    ap.add_argument("-o", "--out")
    for p in PAPER:
        ap.add_argument(f"--{p}", dest="paper", action="store_const", const=p)
    a = ap.parse_args()
    if not shutil.which("rsvg-convert"):
        sys.exit("rsvg-convert not found (brew install librsvg)")
    body, view = read_svg(a.svg)
    crop = tuple(map(float, a.crop.split(","))) if a.crop else view
    paper = PAPER[a.paper or "letter"]
    cw, ch = paper[0] - 2 * MARGIN, paper[1] - 2 * MARGIN - 0.55
    win_w, win_h = crop[2] / a.ppi, crop[3] / a.ppi      # drawing size in inches
    ncol = max(1, math.ceil((win_w - OVERLAP) / (cw - OVERLAP)))
    nrow = max(1, math.ceil((win_h - OVERLAP) / (ch - OVERLAP)))
    name = os.path.splitext(os.path.basename(a.svg))[0]
    out = a.out or os.path.splitext(a.svg)[0] + "-print.pdf"
    with tempfile.TemporaryDirectory() as td:
        files = []
        for r in range(nrow):
            for c in range(ncol):
                f = os.path.join(td, f"{r*ncol+c:03d}.svg")
                open(f, "w", encoding="utf-8").write(sheet(body, a.ppi, crop, c, r, ncol, nrow, paper, a.grid, name))
                files.append(f)
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", out, *files], check=True)
    print(f"{out}: drawing {win_w:.1f} × {win_h:.1f} in → {ncol} × {nrow} = {ncol*nrow} sheet(s)")


if __name__ == "__main__":
    main()
