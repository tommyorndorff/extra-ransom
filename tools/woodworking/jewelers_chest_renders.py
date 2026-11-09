#!/usr/bin/env python3
"""Three-quarter concept rendering of the jeweler's chest (cabinet-style oblique
projection, lid propped open). Illustrations from the plan dimensions, not photographs.

Usage: python3 tools/woodworking/jewelers_chest_renders.py
Writes static/static/woodworking/jewelers-chest-render.svg
"""
import math, os

K = 22
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
CX, CY = 0.5, 0.35   # oblique depth shift per inch of depth (right, up)


class R:
    def __init__(self, w, h, ox, oy, k=22):
        self.w, self.h, self.ox, self.oy, self.p, self.k = w, h, ox, oy, [], k

    def P(self, x, y, z):          # x right, y depth (back), z up, inches
        return (self.ox + (x + y * CX) * self.k, self.oy - (z + y * CY) * self.k)

    def poly(self, pts, fill, stroke="#4a3320", w=1.2):
        s = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.P(*q) for q in pts))
        self.p.append(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>')

    def box(self, x0, y0, z0, x1, y1, z1, front, top, side):
        self.poly([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], side)
        self.poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top)
        self.poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], front)

    def circle(self, x, y, z, r, fill):
        a, b = self.P(x, y, z)
        self.p.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{r*self.k:.1f}" fill="{fill}" stroke="#2b1a0f"/>')

    def text(self, px, py, s, size=12, anchor="start", fill="#444"):
        self.p.append(f'<text x="{px}" y="{py}" font="" font-family="Helvetica Neue,Arial,sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{s}</text>')

    def save(self, name, title):
        body = "\n".join(self.p)
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                    f'width="{self.w}" height="{self.h}" role="img" aria-label="{title}"><title>{title}</title>'
                    f'<rect width="{self.w}" height="{self.h}" fill="#fff"/>{body}</svg>\n')


FRONT, FACE, TOP, SIDE, DARK, INSIDE = "#e6c79c", "#f3dfbf", "#f0d7b0", "#cfa972", "#5a3b26", "#b88d5a"


def pekovich():
    r = R(780, 670, 90, 590, 18)
    W, D, H, LID = 22, 12, 13, 0.75
    # inside first, then tray, then the front wall and end so they hide what is behind
    r.poly([(0.5, 0.5, H), (W - 0.5, 0.5, H), (W - 0.5, D - 0.5, H), (0.5, D - 0.5, H)], INSIDE)
    r.poly([(0.5, D, 0), (W - 0.5, D, 0), (W - 0.5, D, H), (0.5, D, H)], INSIDE)          # inner back wall
    r.box(0.7, 1.0, 10.75, W - 0.7, D - 0.7, 12.5, FACE, TOP, SIDE)
    for x in (5.2, 11.0, 15.8):
        r.poly([(x, 1.3, 12.5), (x + 0.12, 1.3, 12.5), (x + 0.12, D - 1.0, 12.5), (x, D - 1.0, 12.5)], FRONT, w=0.6)
    r.poly([(0, 0, 0), (W, 0, 0), (W, 0, H), (0, 0, H)], FRONT)                          # front
    r.poly([(W, 0, 0), (W, D, 0), (W, D, H), (W, 0, H)], SIDE)                           # right end
    r.poly([(0, 0, H), (W, 0, H), (W, 0.5, H), (0, 0.5, H)], TOP)                        # front rim
    for lo in (0.8125, 4.5625):
        r.poly([(.56, 0, lo), (W - .56, 0, lo), (W - .56, 0, lo + 3.1875), (.56, 0, lo + 3.1875)], FACE)
        r.circle(W / 2, 0, lo + 1.6, 0.3, DARK)
    r.poly([(W, 4.5, 8.7), (W + 0.6, 4.5, 8.7), (W + 0.6, 7.5, 8.7), (W, 7.5, 8.7)], DARK, w=1)
    # lid propped open, hinged at the back, leaning back about 15 degrees past vertical
    a = math.radians(75)
    dy, dz = math.cos(a), math.sin(a)
    hy, hz = D, H
    o = lambda x, t, h: (x, hy + t * dy - h * dz, hz + t * dz + h * dy)
    L = D
    r.poly([o(0, 0, 0), o(W, 0, 0), o(W, L, 0), o(0, L, 0)], INSIDE)
    r.poly([o(0, 0, LID), o(W, 0, LID), o(W, L, LID), o(0, L, LID)], FRONT)
    r.poly([o(2, 2, LID), o(W - 2, 2, LID), o(W - 2, L - 2, LID), o(2, L - 2, LID)], FACE, w=0.7)
    r.text(20, 650, "Concept rendering, proposed: Pekovich-style traveling chest. Cherry case, lid propped open over the lift-out tray. Not a photograph.", 12)
    r.save("jewelers-chest-render.svg", "Concept rendering of the jeweler's traveling chest, lid open")


if __name__ == "__main__":
    pekovich(); print("ok")
