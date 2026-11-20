"""Ghana at 70 UK logo, built to the Brand Book Version 1 (November 2026) proportions.
Symbol: the approved Akoko Nan vector (never redrawn). Wordmark: Bodoni Moda 500, outlined.
Tagline: Jost 500 capitals, justified to the wordmark width. Units: wordmark cap height = 100."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
HERE = os.path.dirname(os.path.abspath(__file__))
G = "M -360 0 C -285 -15, -212 -24, -152 -28 C -180 -100, -188 -220, -140 -284 C -104 -332, -8 -338, 38 -296 C 58 -278, 70 -256, 70 -230 C 46 -258, 8 -272, -28 -266 C -80 -257, -96 -170, -68 -112 C -36 -48, 40 -32, 100 -54 C 168 -79, 198 -170, 198 -264 C 198 -372, 128 -466, 18 -546 C 232 -494, 328 -352, 324 -200 C 320 -100, 270 -42, 230 0 C 270 42, 320 100, 324 200 C 328 352, 232 494, 18 546 C 128 466, 198 372, 198 264 C 198 170, 168 79, 100 54 C 40 32, -36 48, -68 112 C -96 170, -80 257, -28 266 C 8 272, 46 258, 70 230 C 70 256, 58 278, 38 296 C -8 338, -104 332, -140 284 C -188 220, -180 100, -152 28 C -212 24, -285 15, -360 0 Z"
GX0, GX1, GH = -360.0, 324.0, 1092.0
def _font(n): return TTFont(os.path.join(HERE, "fonts", n))
_cache = {}
def _line(fontname, text, cap, track_em):
    key = (fontname, text, cap, round(track_em, 5))
    if key in _cache: return _cache[key]
    f = _font(fontname); cmap = f.getBestCmap(); gs = f.getGlyphSet(); upm = f["head"].unitsPerEm
    capu = f["OS/2"].sCapHeight or 0.7 * upm
    size = cap * upm / capu; sc = size / upm
    x = 0; parts = []; xs = []
    for i, ch in enumerate(text):
        gname = cmap[ord(ch)]
        if ch != " ":
            sp = SVGPathPen(gs); gs[gname].draw(TransformPen(sp, (sc, 0, 0, -sc, x, 0))); parts.append(sp.getCommands())
            bp = BoundsPen(gs); gs[gname].draw(TransformPen(bp, (sc, 0, 0, -sc, x, 0)))
            if bp.bounds: xs += [bp.bounds[0], bp.bounds[2]]
        x += gs[gname].width * sc + (track_em * size if i < len(text) - 1 else 0)
    r = (" ".join(parts), min(xs), max(xs), size); _cache[key] = r; return r
def _fit(fontname, text, cap, width):
    d, a, b, size = _line(fontname, text, cap, 0)
    n = len(text) - 1; tr = (width - (b - a)) / n / size
    return _line(fontname, text, cap, tr)
WM_W = 1850.0     # wordmark width = 18.5 x cap height
def _words(fg, rule, tag):
    d, a, b, _ = _fit("bodoni-moda-latin-500-normal.woff2", "GHANA AT 70 UK", 100, WM_W)
    t, ta, tb, _ = _fit("jost-latin-500-normal.woff2", "THE PLATINUM JUBILEE CELEBRATIONS", 29, WM_W)
    return (f'<path fill="{fg}" transform="translate({-a:.2f},0)" d="{d}"/>'
            f'<rect x="0" y="44" width="{WM_W}" height="4" fill="{rule}"/>'
            f'<path fill="{tag}" transform="translate({-ta:.2f},121)" d="{t}"/>')
COLOURS = {  # wordmark, rule, tagline, symbol (None = metallic gradient)
    "gold-on-light": ("#0D0D0F", "#B58B3F", "#8C6B2F", None),
    "gold-on-green": ("#FFFFFF", "#B58B3F", "#E9CB8A", None),
    "gold-on-dark":  ("#FFFFFF", "#B58B3F", "#E9CB8A", None),
    "flat-gold":     ("#B58B3F", "#B58B3F", "#B58B3F", "#B58B3F"),
    "white":         ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"),
}
def _grad(gid): return (f'<linearGradient id="{gid}" x1="-370" y1="-560" x2="370" y2="560" gradientUnits="userSpaceOnUse">'
                        '<stop offset="0" stop-color="#E9CB8A"/><stop offset=".55" stop-color="#B58B3F"/><stop offset="1" stop-color="#8C6B2F"/></linearGradient>')
def horizontal(colour="gold-on-green", gid="ga70g", cls="", label="Ghana at 70 UK, The Platinum Jubilee Celebrations"):
    fg, rule, tag, sym = COLOURS[colour]
    s = 350 / GH                         # symbol 3.5 x cap height
    sw = (GX1 - GX0) * s; gap = 125
    # text block: cap top -100 to tagline baseline 121, centre 10.5; symbol centred on it
    cy = 10.5
    body = (f'<g transform="translate({-GX0*s:.2f},{cy:.2f}) scale({s:.5f})"><path d="{G}" fill="{sym or "url(#"+gid+")"}"/></g>'
            f'<g transform="translate({sw+gap:.2f},0)">{_words(fg, rule, tag)}</g>')
    W = sw + gap + WM_W; top = cy - 175; H = 350
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} xmlns="http://www.w3.org/2000/svg" viewBox="0 {top:.1f} {W:.1f} {H}" role="img" aria-label="{label}">'
            f'<defs>{_grad(gid)}</defs>{body}</svg>')
def stacked(colour="gold-on-green", gid="ga70s", cls="", label="Ghana at 70 UK, The Platinum Jubilee Celebrations"):
    fg, rule, tag, sym = COLOURS[colour]
    s = 520 / GH; sw = (GX1 - GX0) * s
    cx = WM_W / 2; gy = -100 - 120 - 260   # symbol centre above the wordmark
    lines = (f'<g fill="{rule}"><rect x="40" y="{gy-2:.1f}" width="{cx-sw/2-90:.1f}" height="4"/><rect x="{cx+sw/2+50:.1f}" y="{gy-2:.1f}" width="{cx-sw/2-90:.1f}" height="4"/>'
             f'<circle cx="40" cy="{gy:.1f}" r="7"/><circle cx="{WM_W-40:.1f}" cy="{gy:.1f}" r="7"/></g>')
    body = (lines + f'<g transform="translate({cx-(GX0+GX1)/2*s:.2f},{gy:.2f}) scale({s:.5f})"><path d="{G}" fill="{sym or "url(#"+gid+")"}"/></g>'
            + _words(fg, rule, tag))
    top = gy - 260; H = 121 - top + 10
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} xmlns="http://www.w3.org/2000/svg" viewBox="-24 {top:.1f} {WM_W+48:.1f} {H:.1f}" role="img" aria-label="{label}">'
            f'<defs>{_grad(gid)}</defs>{body}</svg>')
def symbol_tile(px=None, gid="ga70f"):
    pad = 170; S = GH + 2 * pad; cx = (GX0 + GX1) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx-S/2:.1f} {-S/2:.1f} {S:.1f} {S:.1f}">'
            f'<defs>{_grad(gid)}</defs><rect x="{cx-S/2:.1f}" y="{-S/2:.1f}" width="{S:.1f}" height="{S:.1f}" rx="{S*0.18:.1f}" fill="#0E3B2C"/>'
            f'<path d="{G}" fill="#C9A04B"/></svg>')
if __name__ == "__main__":
    open("/tmp/lh.svg", "w").write(horizontal("gold-on-light"))
    open("/tmp/lhg.svg", "w").write(horizontal("gold-on-green"))
    open("/tmp/ls.svg", "w").write(stacked("gold-on-green"))
    open("/tmp/lt.svg", "w").write(symbol_tile())
def symbol(gid="ga70y", cls="", colour=None):
    pad = 20; cx0 = GX0 - pad; W = GX1 - GX0 + 2 * pad; H = GH + 2 * pad
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} xmlns="http://www.w3.org/2000/svg" viewBox="{cx0:.1f} {-H/2:.1f} {W:.1f} {H:.1f}" aria-hidden="true">'
            f'<defs>{_grad(gid)}</defs><path d="{G}" fill="{colour or "url(#"+gid+")"}"/></svg>')
