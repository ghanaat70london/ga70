#!/usr/bin/env python3
"""Builds the Ghana at 70 UK static site into ../ghana-at-70, for Cloudflare Pages"""
import os, shutil, json, hashlib, re, sys
import html as _h
if sys.version_info < (3, 12):
    sys.exit("Python 3.12 or later is needed to build the site. You have " + sys.version.split()[0] + ".")
try:
    import PIL, fontTools  # noqa: F401
except ImportError:
    sys.exit("Two packages are missing. Run: python3 -m pip install -r src/requirements.txt")
import brandlogo
ASSET_V = hashlib.md5((open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.css"), "rb").read() + open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.js"), "rb").read())).hexdigest()[:8]

# The live address: canonical tags, share tags, sitemap, robots and llms.txt all use it. SITE_URL overrides it.
SITE_URL = (os.environ.get("SITE_URL") or "https://ghanaat70uk.com").rstrip("/")
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(SRC, "..", "ghana-at-70"))

GOLD_DEF = '<defs><linearGradient id="{id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8C6510"/><stop offset=".22" stop-color="#E3B53E"/><stop offset=".4" stop-color="#FFF1B8"/><stop offset=".58" stop-color="#D4A62A"/><stop offset=".78" stop-color="#946B12"/><stop offset="1" stop-color="#F3D271"/></linearGradient></defs>'

def star(fill="#14110D", stroke="#D4A62A", sw=3):
    return f'<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="50,4 61.2,37.6 96.6,37.6 68.1,58.6 78.9,92.4 50,71.6 21.1,92.4 31.9,58.6 3.4,37.6 38.8,37.6" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/></svg>'

def wax_seal(uid="a", cls="wax"):
    """Gold wax seal with the Black Star pressed into it. The star is always black."""
    import math as _m
    pts=[]
    for i in range(36):
        a=_m.tau*i/36
        r=54+3.2*_m.sin(i*2.7)+2.1*_m.cos(i*5.3)
        pts.append(f"{60+r*_m.cos(a):.1f},{60+r*_m.sin(a):.1f}")
    st=[]
    for i in range(10):
        a=-_m.pi/2+i*_m.pi/5; r=22 if i%2==0 else 9
        st.append(f"{60+r*_m.cos(a):.1f},{61+r*_m.sin(a):.1f}")
    return (f'<svg class="{cls}" viewBox="0 0 120 120" aria-hidden="true"><defs>'
      f'<radialGradient id="wx{uid}" cx="36%" cy="30%" r="80%"><stop offset="0" stop-color="#FFF1B8"/><stop offset=".35" stop-color="#E3B53E"/><stop offset=".75" stop-color="#A57D19"/><stop offset="1" stop-color="#6E4F0C"/></radialGradient>'
      f'<radialGradient id="wi{uid}" cx="62%" cy="70%" r="75%"><stop offset="0" stop-color="#F3D27A"/><stop offset=".6" stop-color="#C9A04B"/><stop offset="1" stop-color="#8C6510"/></radialGradient></defs>'
      f'<polygon points="{" ".join(pts)}" fill="url(#wx{uid})"/>'
      f'<circle cx="60" cy="60" r="39" fill="url(#wi{uid})" stroke="#7A5A12" stroke-opacity=".55" stroke-width="1.2"/>'
      f'<circle cx="60" cy="60" r="33" fill="none" stroke="#FFF3C2" stroke-opacity=".55" stroke-width=".9" stroke-dasharray="1.4 2.6"/>'
      f'<polygon points="{" ".join(st)}" fill="#16201B" stroke="#F6DB86" stroke-width=".9" stroke-linejoin="round"/>'
      f'<ellipse cx="44" cy="36" rx="14" ry="6" fill="#FFF8DC" opacity=".35" transform="rotate(-28 44 36)"/></svg>')

# Adinkra symbols, drawn as engraved gold
import math, itertools
import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from savedate import save_date, sd_ics
from kw import KW as SEO_KW
META_DOMAIN_VERIFY = ""  # Meta Business Manager domain verification code, content value only
_AID = itertools.count(1)

def _spiral(cx, cy, r, turns=2.2, flip=1, rot=0):
    pts = []
    n = 60
    for i in range(n + 1):
        a = i / n * turns * 2 * math.pi
        rr = r * (i / n)
        x = cx + flip * rr * math.cos(a + rot)
        y = cy + rr * math.sin(a + rot)
        pts.append(f"{x:.1f},{y:.1f}")
    return "M" + " L".join(pts)

def adinkra(name, color="#F6DB86", solid=False):
    gid = f"ag{next(_AID)}"
    c = color if solid else f"url(#{gid})"
    if name == "adinkrahene":
        body = f'<g fill="none" stroke="{c}" stroke-width="7"><circle cx="50" cy="50" r="43"/><circle cx="50" cy="50" r="29"/><circle cx="50" cy="50" r="15"/></g>'
    elif name == "akoma":
        body = f'<path d="M50 90 C18 66 5 50 5 31 C5 16 17 6 31 6 C41 6 47 12 50 20 C53 12 59 6 69 6 C83 6 95 16 95 31 C95 50 82 66 50 90 Z" fill="{c}"/><path class="shade" d="M50 76 C28 60 18 48 18 34 C18 25 25 18 33 18" fill="none" stroke="#0B3D2C" stroke-opacity=".35" stroke-width="3"/>'
    elif name == "hwemudua":
        body = f'<g fill="{c}"><rect x="44" y="12" width="12" height="76"/><rect x="12" y="44" width="76" height="12"/><rect x="30" y="6" width="40" height="10" rx="2"/><rect x="30" y="84" width="40" height="10" rx="2"/><rect x="6" y="30" width="10" height="40" rx="2"/><rect x="84" y="30" width="10" height="40" rx="2"/></g>'
    elif name == "tabono":
        body = f'<g fill="{c}"><ellipse cx="50" cy="23" rx="12" ry="19"/><ellipse cx="50" cy="77" rx="12" ry="19"/><ellipse cx="23" cy="50" rx="19" ry="12"/><ellipse cx="77" cy="50" rx="19" ry="12"/></g><circle cx="50" cy="50" r="9" fill="none" stroke="{c}" stroke-width="5"/>'
    elif name == "besesaka":
        body = "".join(f'<g transform="rotate({a} 50 50)"><ellipse cx="50" cy="22" rx="11" ry="17" fill="none" stroke="{c}" stroke-width="6"/><circle cx="50" cy="20" r="4" fill="{c}"/><path d="M50 39 V44" stroke="{c}" stroke-width="5"/></g>' for a in (45, 135, 225, 315)) + f'<circle cx="50" cy="50" r="8" fill="none" stroke="{c}" stroke-width="6"/>'
    elif name == "nyamenwu":
        body = f'<g fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round"><path d="M28 28L72 72M72 28L28 72"/><circle cx="19" cy="19" r="11"/><circle cx="81" cy="19" r="11"/><circle cx="19" cy="81" r="11"/><circle cx="81" cy="81" r="11"/></g>'
    elif name == "eban":
        body = f'<g fill="none" stroke="{c}" stroke-width="7" stroke-linejoin="round"><rect x="21" y="21" width="58" height="58" transform="rotate(45 50 50)"/></g><g fill="{c}">' + "".join(f'<rect x="{x-9}" y="{y-9}" width="18" height="18" rx="5" transform="rotate(45 {x} {y})"/>' for x, y in ((50, 33), (50, 67), (33, 50), (67, 50))) + '</g>'
    elif name == "dwennimmen":
        sp = "".join(f'<path d="{_spiral(cx, cy, 17, 2.1, f, r)}"/>' for cx, cy, f, r in ((29, 28, 1, 0), (71, 28, -1, 0), (29, 72, 1, math.pi), (71, 72, -1, math.pi)))
        body = f'<g fill="none" stroke="{c}" stroke-width="5.5" stroke-linecap="round">{sp}<path d="M6 50 H94"/></g><circle cx="50" cy="50" r="8" fill="{c}"/>'
    elif name == "owiakokroko":
        seg = "".join(f'<path d="M{50+40*math.cos(math.radians(a)):.1f},{50+40*math.sin(math.radians(a)):.1f} A40 40 0 0 1 {50+40*math.cos(math.radians(a+22)):.1f},{50+40*math.sin(math.radians(a+22)):.1f}"/>' for a in range(0, 360, 30))
        body = f'<g fill="none" stroke="{c}" stroke-width="12">{seg}</g><path d="{_spiral(50, 50, 24, 2.4)}" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/>'
    elif name == "fawohodie":
        body = f'<g fill="none" stroke="{c}" stroke-width="6" stroke-linejoin="round"><path d="M12 12 H88 V88 H12 Z"/><path d="M24 24 L50 46 L76 24"/><path d="M24 76 L50 54 L76 76"/><path d="M24 24 V76 M76 24 V76"/><path d="M38 24 H62 M38 76 H62"/></g>'
    elif name == "asaseyeduru":
        body = f'<g fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M50 4 C70 18 90 34 90 54 C90 74 70 88 50 96 C30 88 10 74 10 54 C10 34 30 18 50 4 Z"/><path d="{_spiral(38, 40, 11, 1.4, -1, 0)}"/><path d="{_spiral(62, 40, 11, 1.4, 1, math.pi)}"/><path d="{_spiral(38, 66, 11, 1.4, 1, math.pi)}"/><path d="{_spiral(62, 66, 11, 1.4, -1, 0)}"/><path d="M30 53 H70"/></g>'
    elif name == "nkonsonkonson":
        body = f'<g fill="none" stroke="{c}" stroke-width="7"><rect x="10" y="12" width="44" height="76" rx="22"/><rect x="46" y="12" width="44" height="76" rx="22"/></g><g fill="{c}"><rect x="28" y="40" width="8" height="20" rx="4"/><rect x="64" y="40" width="8" height="20" rx="4"/></g>'
    elif name == "sankofa":
        body = f'<g fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="{_spiral(32, 34, 16, 1.6, -1, math.pi)}"/><path d="{_spiral(68, 34, 16, 1.6, 1, 0)}"/><path d="M16 36 C16 60 40 74 50 92 C60 74 84 60 84 36"/><path d="M50 50 L58 60 L50 70 L42 60 Z"/></g>'
    elif name == "aya":
        leaves = "".join(f'<path d="M50 {y} L{50-w} {y-12} M50 {y} L{50+w} {y-12}"/>' for y, w in ((86, 34), (74, 31), (62, 27), (50, 22), (38, 16), (26, 10)))
        body = f'<g fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"><path d="M50 96 V8"/>{leaves}</g>'
    elif name == "ananse":
        rad = "".join(f'<path d="M50 50 L{50+46*math.cos(math.radians(a)):.1f} {50+46*math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 45))
        rings = ""
        for r in (14, 28, 42):
            pts = [(50 + r * math.cos(math.radians(a)), 50 + r * math.sin(math.radians(a))) for a in range(0, 360, 45)]
            d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(f" Q{50 + r*.72*math.cos(math.radians(a*45+22.5)):.1f} {50 + r*.72*math.sin(math.radians(a*45+22.5)):.1f} {pts[(a+1) % 8][0]:.1f} {pts[(a+1) % 8][1]:.1f}" for a in range(8))
            rings += f'<path d="{d}"/>'
        body = f'<g fill="none" stroke="{c}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round">{rad}{rings}</g>'
    elif name == "osram":
        body = (f'<path d="M50 8 A42 42 0 1 0 50 92 A48 48 0 0 1 50 8 Z" fill="{c}"/>'
                f'<polygon transform="translate(44 34) scale(.34)" points="50,4 61.2,37.6 96.6,37.6 68.1,58.6 78.9,92.4 50,71.6 21.1,92.4 31.9,58.6 3.4,37.6 38.8,37.6" fill="{c}"/>')
    elif name == "duafe":
        teeth = "".join(f'<rect x="{x}" y="58" width="6" height="36" rx="3"/>' for x in range(17, 84, 11))
        body = f'<g fill="{c}"><rect x="12" y="48" width="76" height="12" rx="4"/>{teeth}</g><path d="M30 48 V30 A20 20 0 0 1 70 30 V48" fill="none" stroke="{c}" stroke-width="7"/><circle cx="50" cy="28" r="6" fill="{c}"/>'
    elif name == "nkyinkyim":
        body = f'<path d="M30 6 L70 22 L30 38 L70 54 L30 70 L70 86 L50 96" fill="none" stroke="{c}" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>'
    else:  # nsoromma
        rays = "".join(f'<polygon points="50,2 56,22 44,22" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 45))
        body = f'<g fill="{c}">{rays}</g><circle cx="50" cy="50" r="21" fill="none" stroke="{c}" stroke-width="7"/><circle cx="50" cy="50" r="8" fill="{c}"/>'
    defs = "" if solid else f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A57D19"/><stop offset=".3" stop-color="#F6DB86"/><stop offset=".5" stop-color="#FFF3C2"/><stop offset=".7" stop-color="#D4A62A"/><stop offset="1" stop-color="#9A7214"/></linearGradient></defs>'
    return f'<svg class="adk" viewBox="0 0 100 100" aria-hidden="true">{defs}{body}</svg>'

def adl(name, cls=""):
    return adinkra(name, "currentColor", solid=True).replace('class="adk"', f'class="adk adk-line {cls}"', 1)

_RAYS = "".join(f'<polygon points="440,190 {440+232*math.cos(math.radians(a-1.2)):.1f},{190+232*math.sin(math.radians(a-1.2)):.1f} {440+232*math.cos(math.radians(a+1.2)):.1f},{190+232*math.sin(math.radians(a+1.2)):.1f}"/>' for a in range(0, 360, 15))
STARPTS = "440.0,128.0 454.7,169.8 499.0,170.8 463.8,197.7 476.4,240.2 440.0,215.0 403.6,240.2 416.2,197.7 381.0,170.8 425.3,169.8"
LOCKUP = ('<svg class="lockup rise d1" viewBox="0 0 640 380" role="img" aria-label="Seventy, with the Black Star inside a ring of gold" overflow="visible">'
          + GOLD_DEF.format(id="lg") +
          '<defs><radialGradient id="glow"><stop offset="0" stop-color="#F6DB86" stop-opacity=".55"/><stop offset="1" stop-color="#F6DB86" stop-opacity="0"/></radialGradient></defs>'
          '<g class="rays" fill="url(#lg)" opacity=".2">' + _RAYS + '</g>'
          '<circle class="glow" cx="440" cy="190" r="150" fill="url(#glow)"/>'
          '<text x="20" y="342" font-family="Bodoni Moda, Didot, Georgia, serif" font-weight="600" font-size="400" fill="url(#lg)">7</text>'
          '<g class="ring"><circle cx="440" cy="190" r="166" fill="none" stroke="url(#lg)" stroke-width="20"/></g>'
          '<g class="ring r2"><circle cx="440" cy="190" r="126" fill="none" stroke="url(#lg)" stroke-width="6" stroke-dasharray="2 14"/></g>'
          '<g class="ring-glint"><circle cx="440" cy="190" r="166" fill="none" stroke="#FFF8DC" stroke-width="9" stroke-linecap="round" data-pl="100" stroke-dasharray="5 95"/></g>'
          '<g class="sparkles" fill="#FFF6D2"><path class="spk s0" d="M523.6,16.8 L527.1,29.3 L539.6,32.8 L527.1,36.4 L523.6,48.8 L520.0,36.4 L507.6,32.8 L520.0,29.3 Z" style="transform-origin:523.6px 32.8px"/><path class="spk s1" d="M599.7,121.9 L601.9,129.7 L609.7,131.9 L601.9,134.1 L599.7,141.9 L597.5,134.1 L589.7,131.9 L597.5,129.7 Z" style="transform-origin:599.7px 131.9px"/><path class="spk s2" d="M600.7,261.4 L603.8,272.4 L614.7,275.4 L603.8,278.5 L600.7,289.4 L597.6,278.5 L586.7,275.4 L597.6,272.4 Z" style="transform-origin:600.7px 275.4px"/><path class="spk s3" d="M482.4,339.4 L484.4,346.4 L491.4,348.4 L484.4,350.4 L482.4,357.4 L480.5,350.4 L473.4,348.4 L480.5,346.4 Z" style="transform-origin:482.4px 348.4px"/><path class="spk s4" d="M357.4,330.4 L360.7,342.1 L372.4,345.4 L360.7,348.7 L357.4,360.4 L354.1,348.7 L342.4,345.4 L354.1,342.1 Z" style="transform-origin:357.4px 345.4px"/><path class="spk s5" d="M280.3,238.1 L282.5,245.9 L290.3,248.1 L282.5,250.3 L280.3,258.1 L278.1,250.3 L270.3,248.1 L278.1,245.9 Z" style="transform-origin:280.3px 248.1px"/><path class="spk s6" d="M276.9,101.9 L279.5,111.3 L288.9,113.9 L279.5,116.6 L276.9,125.9 L274.2,116.6 L264.9,113.9 L274.2,111.3 Z" style="transform-origin:276.9px 113.9px"/><path class="spk s7" d="M383.2,25.0 L385.2,32.0 L392.2,34.0 L385.2,36.0 L383.2,43.0 L381.2,36.0 L374.2,34.0 L381.2,32.0 Z" style="transform-origin:383.2px 34.0px"/><path class="spk s8" d="M527.0,26.3 L529.9,36.5 L540.0,39.3 L529.9,42.2 L527.0,52.3 L524.1,42.2 L514.0,39.3 L524.1,36.5 Z" style="transform-origin:527.0px 39.3px"/></g>'
          '<circle cx="440" cy="190" r="100" fill="#0B3D2C"/><circle cx="440" cy="190" r="96" fill="none" stroke="url(#lg)" stroke-width="10"/>'
          f'<polygon class="bstar" points="{STARPTS}" fill="#16201B" stroke="url(#lg)" stroke-width="3.5" stroke-linejoin="round" data-pl="100"/>'
          f'<polygon class="bstar-shine" points="{STARPTS}" fill="none" stroke="#FFF3C2" stroke-width="2" stroke-linejoin="round" data-pl="100"/>'
          '</svg>')


def _star(cx, cy, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * .4
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return " ".join(pts)

def skyline(cls="skyline", gid="skg", labels=False):
    shapes = [
        '<polygon points="30,190 60,190 53,82 37,82"/><rect x="34" y="64" width="22" height="18"/><polygon points="32,64 45,50 58,64"/>',
        '<rect x="70" y="150" width="40" height="40"/><rect x="115" y="128" width="36" height="62"/>',
        '<path fill-rule="evenodd" d="M162 112 H328 V190 H290 V152 A45 45 0 0 0 200 152 V190 H162 Z M174 128 H190 V170 H174 Z M300 128 H316 V170 H300 Z"/><rect x="150" y="100" width="190" height="12"/>' + f'<polygon points="{_star(245, 80, 20)}"/>',
        '<rect x="345" y="120" width="45" height="70"/><rect x="395" y="70" width="50" height="120"/><rect x="405" y="55" width="30" height="15"/>',
        '<rect x="455" y="40" width="45" height="150"/><polygon points="474,40 481,40 478,6"/><rect x="505" y="100" width="35" height="90"/>',
        '<polygon points="585,190 615,190 642,96 558,96"/><rect x="554" y="88" width="92" height="8"/>' + f'<polygon points="{_star(600, 74, 11)}"/>',
        '<rect x="655" y="110" width="40" height="80"/><rect x="700" y="84" width="55" height="106"/><rect x="760" y="126" width="30" height="64"/>',
        '<path d="M800 190 V152 Q828 106 858 140 Q888 98 918 136 Q944 112 962 150 V190 Z"/>',
        '<rect x="975" y="96" width="45" height="94"/><path d="M1025 190 V72 Q1045 50 1065 72 V190 Z"/><rect x="1070" y="116" width="50" height="74"/><rect x="1125" y="142" width="45" height="48"/>',
        '<rect x="0" y="186" width="1200" height="6"/>',
    ]
    lab = ""
    if labels:
        for x, y, a, n in ((24, 214, "start", "Jamestown Lighthouse"), (245, 232, "middle", "Independence Arch"), (600, 214, "middle", "Nkrumah Memorial"), (881, 232, "middle", "National Theatre"), (1176, 214, "end", "Accra")):
            lab += f'<text x="{x}" y="{y}" text-anchor="{a}">{n}</text>'
    return (f'<svg class="{cls}" viewBox="0 0 1200 {240 if labels else 192}" preserveAspectRatio="xMidYMax meet" role="img" aria-label="The Accra skyline: Jamestown Lighthouse, Independence Arch, Nkrumah Memorial and National Theatre">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9A7214"/><stop offset=".3" stop-color="#F6DB86"/><stop offset=".5" stop-color="#FFF3C2"/><stop offset=".7" stop-color="#D4A62A"/><stop offset="1" stop-color="#A57D19"/></linearGradient></defs>'
            f'<g fill="url(#{gid})">' + "".join(shapes) + f'</g>{lab}</svg>')




_DG = itertools.count(1)





STRIPS = {
    "royal-gala": [("18:30", "Royal arrival", "drum"), ("19:00", "The portrait", "camera"), ("19:45", "The drums begin", "door"), ("20:10", "The banquet", "plate"),
                   ("22:00", "Tribute to 1957", "star"), ("22:20", "Highlife live", "music"), ("23:15", "Last dances", "dance"), ("00:00", "Midnight toast", "glass"), ("00:15", "Carriages", "carriage")],
    "ghana-day": [("11:00", "Doors open", "door"), ("12:00", "The anniversary", "star"), ("12:30", "DJ and dancing", "dance"), ("13:30", "Oware", "game"),
                  ("14:30", "Networking", "people"), ("15:30", "Big Ghana Quiz", "quiz"), ("16:30", "The runway", "dress"), ("17:00", "Dance circle", "dance")],
    "women-of-the-motherland": [("12:00", "Market and portraits", "camera"), ("13:00", "Afternoon tea", "cup"), ("14:00", "Wall of Mothers", "heart"), ("16:00", "Networking hour", "people"), ("17:00", "Voices", "book"), ("17:45", "Honouring mothers", "music"), ("18:30", "Farewell", "carriage")],
}

def strip(day, title=None, note=""):
    items = "".join(f'<li style="--i:{i}"><span class="st-ic">{icon(ic)}</span><time>{tm}</time><span class="st-tick"></span><span class="st-l">{lab}</span></li>' for i, (tm, lab, ic) in enumerate(STRIPS[day]))
    head = f'<div class="st-head"><span class="eyebrow">At a glance</span><h3>{title}</h3>{f"<p class=muted>{note}</p>" if note else ""}</div>' if title else ""
    return f'<div class="strip">{head}<div class="st-scroll"><ol class="st-line">{items}</ol></div></div>'











CAT_GROUPS = [
    ("home", "Home and money in Ghana", "tabono", "The questions every diaspora family is asking: where to build, how to send money, how to protect it."),
    ("travel", "Travel and shipping", "nkonsonkonson", "Getting people and parcels between London and Ghana, simply and safely."),
    ("future", "Learning and careers", "ananse", "For the next generation, and for the next step in a career."),
    ("care", "Health and beauty", "duafe", "Looking after body, hair and skin, the Ghanaian way."),
    ("fashion", "Fashion and adornment", "adinkrahene", "Cloth, tailoring, gold and beads. Dressed for every occasion of the year."),
    ("taste", "Food and drink to take home", "besesaka", "The flavours of home, sealed and ready for your kitchen."),
    ("culture", "Culture, home and celebrations", "sankofa", "Art, books, interiors and everything for the next family celebration."),
]
CATEGORIES = [
    ("realestate", "Real estate in Ghana", "Developers and estate agents selling land, homes and apartments in Ghana to buyers in Britain.", 2, "home"),
    ("money", "Banking, money transfer and mobile money", "Remittance, accounts, mortgages and mobile money between Britain and Ghana.", 2, "home"),
    ("legal", "Legal services", "Solicitors for wills, probate, property in Ghana and family matters.", 2, "home"),
    ("planning", "Financial planning and insurance", "Pensions, savings, investments and protection for families with two homes.", 2, "home"),
    ("travel", "Travel to Ghana", "Airlines, tour operators and heritage journeys home.", 2, "travel"),
    ("shipping", "Shipping and cargo to Ghana", "Barrels, boxes, vehicles and containers, door to door.", 2, "travel"),
    ("education", "Education and tutoring", "Schools, universities, tutors and classes in the languages of Ghana.", 2, "future"),
    ("careers", "Careers and business support", "Recruiters, employers, support for new businesses and business advice.", 2, "future"),
    ("health", "Health and wellbeing", "Health checks, pharmacy, fitness and wellbeing services.", 2, "care"),
    ("hair", "Hair and wigs", "Braiding, wigs, natural hair care and salon products.", 2, "care"),
    ("skin", "Skin care and cosmetics", "Shea, black soap, skin care, cosmetics and fragrance.", 2, "care"),
    ("kente", "Kente and traditional cloth", "Kente, Adinkra cloth, batik and fabric by the yard.", 2, "fashion"),
    ("fashion", "Contemporary Ghanaian fashion", "Designers dressing modern Ghana for every day and every party.", 2, "fashion"),
    ("tailoring", "Tailoring and menswear", "Bespoke suits, kaftans, smocks and occasion wear.", 2, "fashion"),
    ("jewellery", "Jewellery, gold and beads", "Gold, Krobo beads and fine and costume jewellery.", 2, "fashion"),
    ("groceries", "Ghanaian groceries and spices", "Sealed and labelled foods, spices, sauces and staples.", 2, "taste"),
    ("cocoa", "Chocolate, cocoa and drinks", "Ghanaian chocolate, coffee, sobolo and drinks to take home.", 2, "taste"),
    ("art", "Art, photography and books", "Painters, photographers, authors and publishers.", 2, "culture"),
    ("interiors", "Home, interiors and gifts", "Baskets, textiles, ceramics, furniture and gifts.", 2, "culture"),
    ("weddings", "Weddings and celebrations", "Planners, decor, cakes and everything for engagements, weddings and outdoorings.", 2, "culture"),
]



def exhibitor_form():
    cats = "".join(f'<optgroup label="{gn}">' + "".join(f"<option>{c[1]}</option>" for c in CATEGORIES if c[4] == gk) + "</optgroup>" for gk, gn, _, _ in CAT_GROUPS)
    return f"""
<div class="form-card">
  <form data-register novalidate class="stack-lg" aria-labelledby="ex-title">
    <input type="hidden" name="type" value="exhibitor">
    <div class="stack"><span class="eyebrow">Exhibitor application</span><h3 id="ex-title">Apply for a stand</h3><p class="muted">Two minutes. We confirm within five working days. Nothing is payable until your stand is confirmed.</p></div>
    <div class="row2"><div class="field"><label for="ex-name">Your name</label><input id="ex-name" name="firstName" autocomplete="name" required></div><div class="field"><label for="ex-org">Business name</label><input id="ex-org" name="organisation" autocomplete="organization" required></div></div>
    <div class="row2"><div class="field"><label for="ex-email">Email</label><input id="ex-email" type="email" name="email" autocomplete="email" required></div><div class="field"><label for="ex-phone">Mobile</label><input id="ex-phone" type="tel" name="phone" autocomplete="tel"></div></div>
    <div class="row2"><div class="field"><label for="ex-cat">Category</label><select id="ex-cat" name="category" required><option value="">Please choose</option>{cats}</select></div>
</div>
    <div class="field"><label for="ex-web2">Website or Instagram</label><input id="ex-web2" name="organisationUrl" inputmode="url" placeholder="For example, instagram.com/yourbrand"></div>
    <fieldset class="ex-step"><legend><span class="ex-n">1</span>Which stand are you buying?</legend>
      <div class="ex-opts"><label class="ex-opt"><input type="radio" name="standType" value="Market stand, GBP 250 + VAT" required><span class="ex-opt-in"><b>Market stand</b><span class="ex-price">GBP 250 + VAT</span><span class="ex-work">GBP 250 + VAT at 20% (GBP 50) = GBP 300</span></span></label><label class="ex-opt"><input type="radio" name="standType" value="Feature stand, GBP 600 + VAT" required><span class="ex-opt-in"><b>Feature stand</b><span class="ex-price">GBP 600 + VAT</span><span class="ex-work">GBP 600 + VAT at 20% (GBP 120) = GBP 720</span></span></label><label class="ex-opt"><input type="radio" name="partySize" value="Sunday market stand, GBP 150 + VAT" required><span class="ex-opt-in"><b>Sunday market stand</b><span class="ex-price">GBP 150 + VAT</span><span class="ex-work">GBP 150 + VAT at 20% (GBP 30) = GBP 180</span></span></label><label class="ex-opt"><input type="radio" name="partySize" value="Both days, market stand Saturday and Sunday, GBP 400 + VAT" required><span class="ex-opt-in"><b>Both days</b><span class="ex-price">GBP 400 + VAT</span><span class="ex-work">GBP 250 + GBP 150 = GBP 400 + VAT at 20% (GBP 80) = GBP 480</span></span></label><label class="ex-opt"><input type="radio" name="partySize" value="Rising Stars complimentary stand" required><span class="ex-opt-in"><b>Rising Stars</b><span class="ex-price">Complimentary</span><span class="ex-work">For new Ghanaian businesses, two stands only</span></span></label><label class="ex-opt"><input type="radio" name="partySize" value="Not sure, advise me" required><span class="ex-opt-in"><b>Not sure yet</b><span class="ex-price">We advise you</span><span class="ex-work">We call you within five working days</span></span></label></div></fieldset>
    <fieldset class="ex-step ex-gala"><legend><span class="ex-n">2</span>Royal Jubilee Gala seats, Friday 5 March</legend>
      <label class="ex-yes"><input type="checkbox" name="galaWanted" value="yes"><span><b>Yes, I want to buy Royal Jubilee Gala seats at the exhibitor rate</b><span class="hint">Not included with any stand. The exhibitor rate is below the public price of GBP 275.</span></span></label>
      <div class="field ex-gala-n"><label for="ex-gala">How many seats?</label><select id="ex-gala" name="galaSeats"><option value="1">1 seat</option><option value="2" selected>2 seats</option><option value="3">3 seats</option><option value="4">4 seats</option><option value="5 or more">5 or more</option></select></div>
    </fieldset>
    <div class="field"><label for="ex-msg">What will you show and sell</label><textarea id="ex-msg" name="message" required></textarea></div>
    <div class="hp" aria-hidden="true"><label for="ex-hp">Leave blank</label><input id="ex-hp" name="website" tabindex="-1" autocomplete="off"></div>
    <label class="consent"><input type="checkbox" name="consent" value="yes" required><span>I agree to be contacted about exhibiting at Ghana at 70 UK. <a href="privacy.html">Privacy</a></span></label>
    <div class="form-status" role="status" aria-live="polite"></div>
    <button class="btn gold" type="submit">Send my application</button>
    <p class="reassure c">Never more than two of a kind · Reply within five working days · One clear price, plus VAT</p>
  </form>
  <div class="form-done" hidden><span class="eyebrow">Application received</span><h3>Medaase. Thank you.</h3><p class="muted">Your application is with our exhibitions team. You will hear from us within five working days, with the exhibitor pack and next steps.</p></div>
</div>"""

def hours_table(rows):
    body = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    return f'<div class="table-wrap"><table class="hours"><tbody>{body}</tbody></table></div>'

NAV_GROUPS = [
    ("days", "The three days", [("royal-gala", "The Royal Jubilee Gala", "Friday 5 March · GBP 275, early bird GBP 250"), ("ghana-day", "Ghana Day Festival", "Saturday 6 March · GBP 50"),
                                ("women-of-the-motherland", "Women of the Motherland", "Sunday 7 March · GBP 150"), ("programme", "The full programme", "All three days at a glance"),
                                ("sessions", "Talks and sessions", "Expert talks, clinics and masterclasses")]),
    ("visit", "Visit", [("visit", "Plan your visit", "Opening times and getting there"), ("dress-code", "What to wear", "Dress codes for each day"),
                        ("stay", "Travel and stay", "Hotels, Oyster cards, flights from Ghana"), ("accessibility", "Accessibility", "Access, seating and Comfort view"), ("faq", "Questions", "Tickets, timings, dress")]),
    ("exhibit", "Exhibit", [("exhibit", "Exhibit on Ghana Day", "Stands, categories and timeline"), ("exhibitors", "Who is exhibiting", "The exhibitor directory"),
                            ("exhibit#faq-exhibit", "Exhibitor questions", "Before you apply"), ("exhibit#rising", "Rising Stars", "Two stands for new makers")]),
    ("involved", "Get involved", [("partners", "Partners and sponsors", "Request the sponsorship pack"), ("get-involved#speak", "Speak or host", "Register to speak"),
                                  ("get-involved#compete", "Join in", "Dance, oware and the quiz"), ("get-involved#volunteer", "Volunteer", "Join the team on the day"), ("contact#press", "Press", "Media accreditation")]),
    ("about", "About", [("about", "About Ghana at 70 UK", "Why we gather, and who we are"), ("ghana", "The meaning", "Flag, symbols and the map of Ghana"),
                        ("news", "News", "Announcements and dates"), ("contact", "Contact", "Who to talk to")]),
]
NAV_GROUPS = [
    ("weekend", "The weekend", [("royal-gala", "The Royal Jubilee Gala", "Friday 5 March · GBP 275"), ("ghana-day", "Ghana Day Festival", "Saturday 6 March · GBP 50"),
                                ("women-of-the-motherland", "Women of the Motherland", "Sunday 7 March · GBP 150"), ("tickets", "Tickets and the Weekend Pass", "All three days · GBP 435")]),
    ("plan", "Plan your visit", [("dress-code", "What to wear", "Kente, Ankara print and Sunday best"), ("visit", "Times and getting there", "Doors, transport and access"),
                                 ("stay", "Travel and stay", "Hotels, Oyster cards, flights from Ghana"), ("faq", "Questions", "Tickets, timings and dress")]),
    ("involved", "Get involved", [("partners", "Partner with us", "Brands, sponsors and supporters"), ("exhibit", "Exhibit", "Forty stands on Independence Day"),
                                  ("press", "Tell our story", "Press, podcasters, creators and community media"), ("contact", "Contact", "Call or WhatsApp Asantewaa")]),
]
NAV_MAIN = [("gallery", "Gallery"), ("about", "Our story")]

VENUE_LD = {"@type": "Place", "name": "Banking Hall", "address": {"@type": "PostalAddress", "streetAddress": "14 Cornhill", "addressLocality": "London", "addressRegion": "City of London", "postalCode": "EC3V 3ND", "addressCountry": "GB"},
            "geo": {"@type": "GeoCoordinates", "latitude": 51.5133, "longitude": -0.0868}, "description": "A Grade II listed Art Deco banking hall on Cornhill, moments from the Bank of England. Bank station is two minutes on foot."}
ORG_NODE = {"@type": "Organization", "@id": SITE_URL + "/#org", "name": "Ghana at 70 UK", "alternateName": ["Ghana at 70 London", "Ghana at 70 UK, The Platinum Jubilee Celebrations"],
            "url": SITE_URL, "logo": SITE_URL + "/images/brand/icon-512.png", "email": "ghanaat70.uk@gmail.com", "telephone": "+447824555307",
            "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "telephone": "+447824555307", "email": "ghanaat70.uk@gmail.com", "areaServed": "GB", "availableLanguage": "en-GB"}}
ORG_LD = json.dumps({"@context": "https://schema.org", "@graph": [ORG_NODE, {"@type": "WebSite", "@id": SITE_URL + "/#site", "name": "Ghana at 70 UK", "url": SITE_URL, "inLanguage": "en-GB", "publisher": {"@id": SITE_URL + "/#org"}}]})

def _kw_tags(slug):
    t = ""
    if slug in SEO_KW: t += '<meta name="keywords" content="' + ", ".join(SEO_KW[slug]) + '">'
    if META_DOMAIN_VERIFY: t += '<meta name="facebook-domain-verification" content="' + META_DOMAIN_VERIFY + '">'
    return t

def head(title, desc, slug, extra=""):
    url = SITE_URL + ("/" if slug == "index" else "/" + slug)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#051C12">{_kw_tags(slug)}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ghana at 70 UK">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/images/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="icon" href="images/brand/icon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="images/brand/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500&family=Pinyon+Script&family=Spectral:ital,wght@0,300;0,400;0,500;1,400&display=swap">
<link rel="stylesheet" href="site.css?v={ASSET_V}">
<script>if("IntersectionObserver" in window)document.documentElement.classList.add("js");try{{if(sessionStorage.getItem("ga70-tri"))document.documentElement.classList.add("tri-seen");else sessionStorage.setItem("ga70-tri","1")}}catch(e){{document.documentElement.classList.add("tri-seen")}}try{{var c=localStorage.getItem("ga70-comfort");if(c==="1"||(c===null&&matchMedia("(prefers-contrast: more)").matches))document.documentElement.classList.add("comfort")}}catch(e){{}}</script>
<link rel="alternate" type="text/plain" href="llms.txt" title="Ghana at 70 UK summary for AI assistants">
<script type="application/ld+json">{ORG_LD}</script>
{extra}</head>'''

DAYS_LEFT = (__import__('datetime').date(2027, 3, 6) - __import__('datetime').date.today()).days

def header(slug):
    def href(h):
        b, _, frag = h.partition("#")
        return b + ".html" + ("#" + frag if frag else "")
    items = ""
    for gi, (key, label, links) in enumerate(NAV_GROUPS):
        here = any(h.split("#")[0] == slug for h, _, _ in links)
        panel = "".join(f'<a href="{href(h)}"{" aria-current=page" if h == slug else ""}><b>{l}</b><span>{d}</span></a>' for h, l, d in links)
        items += f'<li class="dd dd-{key}{" here" if here else ""}"><button class="dd-btn" type="button" aria-expanded="false" aria-controls="dd-{key}">{label}<i aria-hidden="true"></i></button><div class="dd-panel" id="dd-{key}"><div class="dd-in">{panel}</div></div></li>'
        if gi == 1:
            for h, l in NAV_MAIN:
                items += f'<li><a class="nav-plain" href="{href(h)}"{" aria-current=page" if h == slug else ""}>{l}</a></li>'
    return f'''<body class="has-mobile-cta">
<a class="hp" href="#main">Skip to content</a>
<header class="site-header">
  <div class="tricolour"></div>
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="index.html" aria-label="Ghana at 70 UK home"><img class="brand-logo" src="images/brand/ga70-stacked.svg" alt="" width="1648" height="822"><img class="brand-sym" src="images/brand/ga70-symbol.svg" alt="" width="498" height="720"></a>
    <a class="btn gold small nav-book" href="tickets.html" data-pay="pick">Book now</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links"><span class="nt-bars" aria-hidden="true"><i></i><i></i></span><span class="nt-l">Menu</span></button>
    <ul class="nav-links" id="nav-links">{items}<li class="nav-table"><a class="btn line small" href="royal-gala.html#book" data-pay="gala" data-qty="10">Royal tables</a></li><li class="nav-cta"><a class="btn gold small" href="tickets.html" data-pay="pick">Book now</a></li></ul>
    <button class="comfort-btn" type="button" data-comfort aria-pressed="false" title="Comfort view: larger text and calmer visuals"><span aria-hidden="true">Aa</span><span class="sr">Comfort view</span></button>
  </nav>
</header>
<main id="main">'''


# ================= PARTNERS (edit partners.json, never this code) =================
def partner_entries():
    data = json.load(open(os.path.join(SRC, "partners.json")))
    levels = data["levels"]
    out = []
    for e in data.get("partners", []):
        if not e.get("show"):
            continue
        for k in ("name", "level", "logo", "announcement", "announced"):
            if not str(e.get(k, "")).strip():
                raise SystemExit(f"partners.json: {e.get('name', 'an entry')} is missing {k}")
        if e["level"] not in levels:
            raise SystemExit(f"partners.json: {e['name']} has level {e['level']!r}, which is not in levels")
        if not os.path.exists(os.path.join(SRC, "images", "partners", e["logo"])):
            raise SystemExit(f"partners.json: logo images/partners/{e['logo']} for {e['name']} is missing")
        out.append(e)
    out.sort(key=lambda e: (levels.index(e["level"]), "".join(chr(255 - ord(c)) for c in e["announced"])))
    return out


def _plogo(e, cls):
    img = f'<img src="images/partners/{_h.escape(e["logo"])}" alt="{_h.escape(e["name"])}" loading="lazy" class="{cls}">'
    u = e.get("url", "")
    return f'<a href="{_h.escape(u)}" target="_blank" rel="noopener sponsored">{img}</a>' if u else img


def partners_feature(eyebrow="Our partners", title="With the partners who make it possible."):
    ps = partner_entries()
    if not ps:
        return ""
    cards = "".join(
        f'<article class="pf-card"><div class="pf-logo">{_plogo(e, "pf-img")}</div>'
        f'<span class="pf-level">{_h.escape(e["level"])}</span><h3>{_h.escape(e["name"])}</h3><p>{_h.escape(e["announcement"])}</p>'
        + (f'<a class="pf-link" href="{_h.escape(e["url"])}" target="_blank" rel="noopener sponsored">Visit {_h.escape(e["name"])}</a>' if e.get("url") else "")
        + "</article>" for e in ps)
    return (f'<section class="band ivory pf-band" id="our-partners"><div class="wrap">'
            f'<div class="section-head center"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2><div class="divider c"><i></i></div></div>'
            f'<div class="pf-grid">{cards}</div></div></section>')


OPEN_SLOTS = [
    ("Presenting Partner", "One only", "The Royal Jubilee Gala, presented by you"),
    ("Principal Partner", "Banking", "Category exclusive"),
    ("Principal Partner", "Money transfer", "Category exclusive"),
    ("Principal Partner", "Drinks", "Category exclusive"),
    ("Principal Partner", "Telecoms", "Category exclusive"),
    ("Official Partner", "Travel", "Own one experience"),
    ("Official Partner", "Beauty", "Own one experience"),
    ("Official Partner", "Property", "Own one experience"),
]


def partners_wall(open_slots=False):
    """A clean logo wall, four across: signed partners first, then the slots still open."""
    ps = partner_entries()
    cells = [f'<li class="pw-cell" title="{_h.escape(e["level"])}">{_plogo(e, "pw-img")}</li>' for e in ps]
    if open_slots:
        taken = {e["level"] for e in ps}
        slots = [s for s in OPEN_SLOTS if not (s[0] == "Presenting Partner" and s[0] in taken)]
        for lvl, tag, line in slots[: max(0, 8 - len(cells))]:
            cells.append(f'<li class="pw-cell pw-open"><a href="#pack"><span class="pw-lvl">{lvl}</span>'
                         f'<span class="pw-tag">{tag}</span><span class="pw-line">{line}</span><span class="pw-av">Available</span></a></li>')
    if not cells:
        return ""
    sub = ("Every open slot below is available today. Each one closes when it is signed."
           if open_slots else "The brands standing with Ghana at 70 UK.")
    return (f'<section class="band pw-band" id="our-partners"><div class="wrap">'
            f'<div class="pw-head"><h2>Our Partners</h2><p>{sub}</p></div>'
            f'<ul class="pw-grid">{"".join(cells)}</ul></div></section>')


def partners_strip():
    ps = partner_entries()
    if not ps:
        return ""
    logos = "".join(f'<li title="{_h.escape(e["level"])}">{_plogo(e, "ps-img")}</li>' for e in ps)
    return f'<div class="ps-band"><div class="wrap"><span class="ps-h">With thanks to our partners</span><ul class="ps-list">{logos}</ul></div></div>'


def footer():
    import datetime as _dt
    DAYS_LEFT = (_dt.date(2027, 3, 6) - _dt.date.today()).days
    col = lambda title, items: f'<div class="ft-col"><h2 class="ft-h">{title}</h2><ul>' + "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in items) + "</ul></div>"
    return f"""</main>
{partners_strip()}<footer class="site-footer ft">
  <div class="wrap ft-quote">
    <blockquote><p>Ghana, your beloved country, is free forever.</p><cite>Kwame Nkrumah · Old Polo Grounds, Accra · Midnight, 6 March 1957</cite></blockquote>
  </div>
  <div class="wrap ft-call">
    <div class="ft-call-copy">
      <span class="ft-eyebrow">Seventy years to the day</span>
      <h2 class="ft-call-h">Take your seat at the Platinum Jubilee.</h2>
      <p class="ft-count"><b data-days>{DAYS_LEFT}</b><span>days to Independence Day</span></p>
    </div>
    <ul class="ft-tix">
      <li class="ftt-gala"><a href="royal-gala.html#book" data-pay="gala"><span class="ftt-d">Friday 5 March</span><b>The Royal Jubilee Gala</b><span class="ftt-p">GBP 275</span><i aria-hidden="true"></i></a></li>
      <li class="ftt-day"><a href="ghana-day.html#book" data-pay="ghanaday"><span class="ftt-d">Saturday 6 March</span><b>Ghana Day Festival</b><span class="ftt-p">GBP 50</span><i aria-hidden="true"></i></a></li>
      <li class="ftt-sun"><a href="women-of-the-motherland.html#book" data-pay="sunday"><span class="ftt-d">Sunday 7 March</span><b>Women of the Motherland</b><span class="ftt-p">GBP 150</span><i aria-hidden="true"></i></a></li>
    </ul>
  </div>
  <div class="wrap ft-grid">
    <div class="ft-brand">
      <a class="ft-logo" href="index.html" aria-label="Ghana at 70 UK home"><img class="ft-logo-svg" loading="eager" src="images/brand/ga70-stacked.svg" alt="" width="1648" height="822"></a>
      <p class="ft-when"><span>Banking Hall</span><span>14 Cornhill, London EC3V 3ND</span><span>Moments from the Bank of England</span></p>
    </div>
    {col("The weekend", [("royal-gala.html", "The Royal Jubilee Gala"), ("ghana-day.html", "Ghana Day Festival"), ("women-of-the-motherland.html", "Women of the Motherland"), ("tickets.html", "Tickets and passes"), ("gallery.html", "Gallery")])}
    {col("Plan your visit", [("dress-code.html", "What to wear"), ("visit.html", "Times and getting there"), ("stay.html", "Travel and stay"), ("faq.html", "Questions"), ("about.html", "Our story")])}
    <div class="ft-col ft-talk"><h2 class="ft-h">Talk to us</h2>
      <p class="ft-call-line">Call Asantewaa</p>
      <a class="ft-phone" href="tel:+447824555307"><span data-phone>07824 555307</span></a>
      <a class="ft-wa" href="https://wa.me/447824555307?text=Hello%20Asantewaa%2C%20I%20have%20a%20question%20about%20Ghana%20at%2070%20UK" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.6 0-3.1-.4-4.4-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3a.5.5 0 0 0 0-.4l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.1 5.1 0 0 0 1.1 2.7 11.7 11.7 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.2c0-.1-.2-.2-.4-.3Z"/></svg><span>Chat on WhatsApp</span></a>
      <a class="ft-mail" data-email-link href="contact.html"><span data-email>ghanaat70.uk@gmail.com</span></a>
      <ul class="ft-mini"><li><a href="press.html">Tell our story</a></li><li><a href="partners.html">Partners</a></li><li><a href="exhibit.html">Exhibit</a></li></ul>
    </div>
  </div>
  <div class="ft-mark" aria-hidden="true"><svg class="ft-mark-svg" viewBox="4.4 -93.7 550.9 96.9" aria-hidden="true" focusable="false"><path d="M52.98 -35.519999999999996H87.11999999999999V-32.879999999999995H80.22V-19.439999999999998Q78.42 -16.56 75.66 -13.02Q72.89999999999999 -9.48 68.85 -6.24Q64.8 -3.0 59.25 -0.9Q53.699999999999996 1.2 46.379999999999995 1.2Q33.66 1.2 24.75 -4.71Q15.84 -10.62 11.129999999999999 -21.06Q6.42 -31.5 6.42 -45.0Q6.42 -55.14 9.48 -63.6Q12.54 -72.06 18.15 -78.24000000000001Q23.759999999999998 -84.42 31.409999999999997 -87.81Q39.059999999999995 -91.2 48.18 -91.2Q53.879999999999995 -91.2 59.16 -89.22Q64.44 -87.24 68.52 -83.7L76.02 -90.0H78.11999999999999V-64.86H75.72Q75.24 -70.08 73.02 -74.34Q70.8 -78.6 67.17 -81.75Q63.54 -84.89999999999999 59.01 -86.60999999999999Q54.48 -88.32 49.5 -88.32Q42.0 -88.32 36.75 -84.66Q31.5 -81.0 28.32 -74.82Q25.14 -68.64 23.64 -60.9Q22.14 -53.16 22.14 -45.0Q22.14 -36.839999999999996 23.22 -29.04Q24.3 -21.24 26.97 -14.94Q29.64 -8.64 34.379999999999995 -4.92Q39.12 -1.2 46.379999999999995 -1.2Q51.48 -1.2 54.959999999999994 -2.85Q58.44 -4.5 60.599999999999994 -6.87Q62.76 -9.24 63.959999999999994 -11.52Q65.16 -13.799999999999999 65.64 -15.0V-32.879999999999995H52.98ZM201.95999999999998 -90.0V-87.66H191.16V-2.34H201.95999999999998V0.0H166.07999999999998V-2.34H177.78V-43.199999999999996H140.22V-2.34H151.86V0.0H115.92V-2.34H126.78V-87.66H115.92V-90.0H151.86V-87.66H140.22V-45.6H177.78V-87.66H166.07999999999998V-90.0ZM 265.60 -7.73 L 265.60 -7.53 L 265.58 -7.34 L 265.57 -7.14 L 265.55 -6.95 L 265.52 -6.76 L 265.49 -6.57 L 265.45 -6.37 L 265.41 -6.18 L 265.37 -6.00 L 265.32 -5.81 L 265.26 -5.62 L 265.21 -5.44 L 265.14 -5.25 L 265.07 -5.07 L 265.00 -4.89 L 264.93 -4.71 L 264.84 -4.53 L 264.76 -4.36 L 264.67 -4.19 L 264.58 -4.02 L 264.48 -3.85 L 264.38 -3.68 L 264.27 -3.52 L 264.16 -3.36 L 264.05 -3.20 L 263.93 -3.05 L 263.81 -2.90 L 263.68 -2.75 L 263.55 -2.60 L 263.42 -2.46 L 263.29 -2.32 L 263.15 -2.18 L 263.00 -2.05 L 262.86 -1.92 L 262.71 -1.80 L 262.56 -1.68 L 262.40 -1.56 L 262.25 -1.44 L 262.09 -1.33 L 261.92 -1.23 L 261.76 -1.13 L 261.59 -1.03 L 261.42 -0.94 L 261.25 -0.85 L 261.07 -0.76 L 260.89 -0.68 L 260.72 -0.60 L 260.54 -0.53 L 260.35 -0.46 L 260.17 -0.40 L 259.98 -0.34 L 259.80 -0.29 L 259.61 -0.24 L 259.42 -0.19 L 259.23 -0.15 L 259.04 -0.12 L 258.85 -0.09 L 258.65 -0.06 L 258.46 -0.04 L 258.27 -0.02 L 258.07 -0.01 L 257.88 -0.00 L 257.69 0.00 L 257.49 -0.00 L 257.30 -0.01 L 257.10 -0.02 L 256.91 -0.04 L 256.72 -0.06 L 256.52 -0.09 L 256.33 -0.12 L 256.14 -0.15 L 255.95 -0.19 L 255.76 -0.24 L 255.57 -0.29 L 255.39 -0.34 L 255.20 -0.40 L 255.02 -0.46 L 254.83 -0.53 L 254.65 -0.60 L 254.48 -0.68 L 254.30 -0.76 L 254.12 -0.85 L 253.95 -0.94 L 253.78 -1.03 L 253.61 -1.13 L 253.45 -1.23 L 253.28 -1.33 L 253.12 -1.44 L 252.97 -1.56 L 252.81 -1.68 L 252.66 -1.80 L 252.51 -1.92 L 252.37 -2.05 L 252.22 -2.18 L 252.08 -2.32 L 251.95 -2.46 L 251.82 -2.60 L 251.69 -2.75 L 251.56 -2.90 L 251.44 -3.05 L 251.32 -3.20 L 251.21 -3.36 L 251.10 -3.52 L 250.99 -3.68 L 250.89 -3.85 L 250.79 -4.02 L 250.70 -4.19 L 250.61 -4.36 L 250.53 -4.53 L 250.44 -4.71 L 250.37 -4.89 L 250.30 -5.07 L 250.23 -5.25 L 250.16 -5.44 L 250.11 -5.62 L 250.05 -5.81 L 250.00 -6.00 L 249.96 -6.18 L 249.92 -6.37 L 249.88 -6.57 L 249.85 -6.76 L 249.82 -6.95 L 249.80 -7.14 L 249.79 -7.34 L 249.77 -7.53 L 249.77 -7.73 L 249.77 -7.92 L 249.77 -8.11 L 249.77 -8.31 L 249.79 -8.50 L 249.80 -8.70 L 249.82 -8.89 L 249.85 -9.08 L 249.88 -9.27 L 249.92 -9.47 L 249.96 -9.66 L 250.00 -9.84 L 250.05 -10.03 L 250.11 -10.22 L 250.16 -10.40 L 250.23 -10.59 L 250.30 -10.77 L 250.37 -10.95 L 250.44 -11.13 L 250.53 -11.31 L 250.61 -11.48 L 250.70 -11.65 L 250.79 -11.82 L 250.89 -11.99 L 250.99 -12.16 L 251.10 -12.32 L 251.21 -12.48 L 251.32 -12.64 L 251.44 -12.79 L 251.56 -12.94 L 251.69 -13.09 L 251.82 -13.24 L 251.95 -13.38 L 252.08 -13.52 L 252.22 -13.66 L 252.37 -13.79 L 252.51 -13.92 L 252.66 -14.04 L 252.81 -14.16 L 252.97 -14.28 L 253.12 -14.40 L 253.28 -14.51 L 253.45 -14.61 L 253.61 -14.71 L 253.78 -14.81 L 253.95 -14.90 L 254.12 -14.99 L 254.30 -15.08 L 254.48 -15.16 L 254.65 -15.24 L 254.83 -15.31 L 255.02 -15.38 L 255.20 -15.44 L 255.39 -15.50 L 255.57 -15.55 L 255.76 -15.60 L 255.95 -15.65 L 256.14 -15.69 L 256.33 -15.72 L 256.52 -15.75 L 256.72 -15.78 L 256.91 -15.80 L 257.10 -15.82 L 257.30 -15.83 L 257.49 -15.84 L 257.69 -15.84 L 257.88 -15.84 L 258.07 -15.83 L 258.27 -15.82 L 258.46 -15.80 L 258.65 -15.78 L 258.85 -15.75 L 259.04 -15.72 L 259.23 -15.69 L 259.42 -15.65 L 259.61 -15.60 L 259.80 -15.55 L 259.98 -15.50 L 260.17 -15.44 L 260.35 -15.38 L 260.54 -15.31 L 260.72 -15.24 L 260.89 -15.16 L 261.07 -15.08 L 261.25 -14.99 L 261.42 -14.90 L 261.59 -14.81 L 261.76 -14.71 L 261.92 -14.61 L 262.09 -14.51 L 262.25 -14.40 L 262.40 -14.28 L 262.56 -14.16 L 262.71 -14.04 L 262.86 -13.92 L 263.00 -13.79 L 263.15 -13.66 L 263.29 -13.52 L 263.42 -13.38 L 263.55 -13.24 L 263.68 -13.09 L 263.81 -12.94 L 263.93 -12.79 L 264.05 -12.64 L 264.16 -12.48 L 264.27 -12.32 L 264.38 -12.16 L 264.48 -11.99 L 264.58 -11.82 L 264.67 -11.65 L 264.76 -11.48 L 264.84 -11.31 L 264.93 -11.13 L 265.00 -10.95 L 265.07 -10.77 L 265.14 -10.59 L 265.21 -10.40 L 265.26 -10.22 L 265.32 -10.03 L 265.37 -9.84 L 265.41 -9.66 L 265.45 -9.47 L 265.49 -9.27 L 265.52 -9.08 L 265.55 -8.89 L 265.57 -8.70 L 265.58 -8.50 L 265.60 -8.31 L 265.60 -8.11 L 265.61 -7.92 Z M 321.01 0.00 L 281.99 0.00 L 281.99 -3.78 L 287.77 -3.78 L 270.57 -72.00 L 269.69 -77.40 L 293.47 -3.78 L 269.38 -78.37 L 274.08 -91.74 L 278.04 -91.74 L 308.50 -3.78 L 321.01 -3.78 Z M 418.44 1.20 L 362.94 -87.04 L 362.94 -87.84 L 348.00 -87.84 L 348.00 -90.00 L 361.08 -90.00 L 362.76 -90.00 L 377.22 -90.00 L 419.28 -21.96 L 419.28 -87.66 L 405.48 -87.66 L 405.48 -90.00 L 434.34 -90.00 L 434.34 -87.66 L 421.68 -87.66 L 421.68 1.20 Z M 369.45 -7.73 L 369.44 -7.53 L 369.43 -7.34 L 369.41 -7.14 L 369.39 -6.95 L 369.36 -6.76 L 369.33 -6.57 L 369.30 -6.37 L 369.26 -6.18 L 369.21 -6.00 L 369.16 -5.81 L 369.11 -5.62 L 369.05 -5.44 L 368.99 -5.25 L 368.92 -5.07 L 368.85 -4.89 L 368.77 -4.71 L 368.69 -4.53 L 368.60 -4.36 L 368.51 -4.19 L 368.42 -4.02 L 368.32 -3.85 L 368.22 -3.68 L 368.12 -3.52 L 368.01 -3.36 L 367.89 -3.20 L 367.77 -3.05 L 367.65 -2.90 L 367.53 -2.75 L 367.40 -2.60 L 367.27 -2.46 L 367.13 -2.32 L 366.99 -2.18 L 366.85 -2.05 L 366.70 -1.92 L 366.55 -1.80 L 366.40 -1.68 L 366.25 -1.56 L 366.09 -1.44 L 365.93 -1.33 L 365.77 -1.23 L 365.60 -1.13 L 365.43 -1.03 L 365.26 -0.94 L 365.09 -0.85 L 364.92 -0.76 L 364.74 -0.68 L 364.56 -0.60 L 364.38 -0.53 L 364.20 -0.46 L 364.01 -0.40 L 363.83 -0.34 L 363.64 -0.29 L 363.45 -0.24 L 363.27 -0.19 L 363.08 -0.15 L 362.88 -0.12 L 362.69 -0.09 L 362.50 -0.06 L 362.31 -0.04 L 362.11 -0.02 L 361.92 -0.01 L 361.72 -0.00 L 361.53 0.00 L 361.34 -0.00 L 361.14 -0.01 L 360.95 -0.02 L 360.75 -0.04 L 360.56 -0.06 L 360.37 -0.09 L 360.18 -0.12 L 359.98 -0.15 L 359.79 -0.19 L 359.61 -0.24 L 359.42 -0.29 L 359.23 -0.34 L 359.05 -0.40 L 358.86 -0.46 L 358.68 -0.53 L 358.50 -0.60 L 358.32 -0.68 L 358.14 -0.76 L 357.97 -0.85 L 357.80 -0.94 L 357.63 -1.03 L 357.46 -1.13 L 357.29 -1.23 L 357.13 -1.33 L 356.97 -1.44 L 356.81 -1.56 L 356.66 -1.68 L 356.51 -1.80 L 356.36 -1.92 L 356.21 -2.05 L 356.07 -2.18 L 355.93 -2.32 L 355.79 -2.46 L 355.66 -2.60 L 355.53 -2.75 L 355.41 -2.90 L 355.29 -3.05 L 355.17 -3.20 L 355.05 -3.36 L 354.94 -3.52 L 354.84 -3.68 L 354.74 -3.85 L 354.64 -4.02 L 354.55 -4.19 L 354.46 -4.36 L 354.37 -4.53 L 354.29 -4.71 L 354.21 -4.89 L 354.14 -5.07 L 354.07 -5.25 L 354.01 -5.44 L 353.95 -5.62 L 353.90 -5.81 L 353.85 -6.00 L 353.80 -6.18 L 353.76 -6.37 L 353.73 -6.57 L 353.70 -6.76 L 353.67 -6.95 L 353.65 -7.14 L 353.63 -7.34 L 353.62 -7.53 L 353.61 -7.73 L 353.61 -7.92 L 353.61 -8.11 L 353.62 -8.31 L 353.63 -8.50 L 353.65 -8.70 L 353.67 -8.89 L 353.70 -9.08 L 353.73 -9.27 L 353.76 -9.47 L 353.80 -9.66 L 353.85 -9.84 L 353.90 -10.03 L 353.95 -10.22 L 354.01 -10.40 L 354.07 -10.59 L 354.14 -10.77 L 354.21 -10.95 L 354.29 -11.13 L 354.37 -11.31 L 354.46 -11.48 L 354.55 -11.65 L 354.64 -11.82 L 354.74 -11.99 L 354.84 -12.16 L 354.94 -12.32 L 355.05 -12.48 L 355.17 -12.64 L 355.29 -12.79 L 355.41 -12.94 L 355.53 -13.09 L 355.66 -13.24 L 355.79 -13.38 L 355.93 -13.52 L 356.07 -13.66 L 356.21 -13.79 L 356.36 -13.92 L 356.51 -14.04 L 356.66 -14.16 L 356.81 -14.28 L 356.97 -14.40 L 357.13 -14.51 L 357.29 -14.61 L 357.46 -14.71 L 357.63 -14.81 L 357.80 -14.90 L 357.97 -14.99 L 358.14 -15.08 L 358.32 -15.16 L 358.50 -15.24 L 358.68 -15.31 L 358.86 -15.38 L 359.05 -15.44 L 359.23 -15.50 L 359.42 -15.55 L 359.61 -15.60 L 359.79 -15.65 L 359.98 -15.69 L 360.18 -15.72 L 360.37 -15.75 L 360.56 -15.78 L 360.75 -15.80 L 360.95 -15.82 L 361.14 -15.83 L 361.34 -15.84 L 361.53 -15.84 L 361.72 -15.84 L 361.92 -15.83 L 362.11 -15.82 L 362.31 -15.80 L 362.50 -15.78 L 362.69 -15.75 L 362.88 -15.72 L 363.08 -15.69 L 363.27 -15.65 L 363.45 -15.60 L 363.64 -15.55 L 363.83 -15.50 L 364.01 -15.44 L 364.20 -15.38 L 364.38 -15.31 L 364.56 -15.24 L 364.74 -15.16 L 364.92 -15.08 L 365.09 -14.99 L 365.26 -14.90 L 365.43 -14.81 L 365.60 -14.71 L 365.77 -14.61 L 365.93 -14.51 L 366.09 -14.40 L 366.25 -14.28 L 366.40 -14.16 L 366.55 -14.04 L 366.70 -13.92 L 366.85 -13.79 L 366.99 -13.66 L 367.13 -13.52 L 367.27 -13.38 L 367.40 -13.24 L 367.53 -13.09 L 367.65 -12.94 L 367.77 -12.79 L 367.89 -12.64 L 368.01 -12.48 L 368.12 -12.32 L 368.22 -12.16 L 368.32 -11.99 L 368.42 -11.82 L 368.51 -11.65 L 368.60 -11.48 L 368.69 -11.31 L 368.77 -11.13 L 368.85 -10.95 L 368.92 -10.77 L 368.99 -10.59 L 369.05 -10.40 L 369.11 -10.22 L 369.16 -10.03 L 369.21 -9.84 L 369.26 -9.66 L 369.30 -9.47 L 369.33 -9.27 L 369.36 -9.08 L 369.39 -8.89 L 369.41 -8.70 L 369.43 -8.50 L 369.44 -8.31 L 369.45 -8.11 L 369.45 -7.92 Z M 497.92 -7.73 L 497.92 -7.53 L 497.90 -7.34 L 497.89 -7.14 L 497.87 -6.95 L 497.84 -6.76 L 497.81 -6.57 L 497.77 -6.37 L 497.73 -6.18 L 497.69 -6.00 L 497.64 -5.81 L 497.58 -5.62 L 497.53 -5.44 L 497.46 -5.25 L 497.39 -5.07 L 497.32 -4.89 L 497.25 -4.71 L 497.16 -4.53 L 497.08 -4.36 L 496.99 -4.19 L 496.90 -4.02 L 496.80 -3.85 L 496.70 -3.68 L 496.59 -3.52 L 496.48 -3.36 L 496.37 -3.20 L 496.25 -3.05 L 496.13 -2.90 L 496.00 -2.75 L 495.87 -2.60 L 495.74 -2.46 L 495.61 -2.32 L 495.47 -2.18 L 495.32 -2.05 L 495.18 -1.92 L 495.03 -1.80 L 494.88 -1.68 L 494.72 -1.56 L 494.57 -1.44 L 494.41 -1.33 L 494.24 -1.23 L 494.08 -1.13 L 493.91 -1.03 L 493.74 -0.94 L 493.57 -0.85 L 493.39 -0.76 L 493.21 -0.68 L 493.04 -0.60 L 492.86 -0.53 L 492.67 -0.46 L 492.49 -0.40 L 492.30 -0.34 L 492.12 -0.29 L 491.93 -0.24 L 491.74 -0.19 L 491.55 -0.15 L 491.36 -0.12 L 491.17 -0.09 L 490.97 -0.06 L 490.78 -0.04 L 490.59 -0.02 L 490.39 -0.01 L 490.20 -0.00 L 490.01 0.00 L 489.81 -0.00 L 489.62 -0.01 L 489.42 -0.02 L 489.23 -0.04 L 489.04 -0.06 L 488.84 -0.09 L 488.65 -0.12 L 488.46 -0.15 L 488.27 -0.19 L 488.08 -0.24 L 487.89 -0.29 L 487.71 -0.34 L 487.52 -0.40 L 487.34 -0.46 L 487.15 -0.53 L 486.97 -0.60 L 486.80 -0.68 L 486.62 -0.76 L 486.44 -0.85 L 486.27 -0.94 L 486.10 -1.03 L 485.93 -1.13 L 485.77 -1.23 L 485.60 -1.33 L 485.44 -1.44 L 485.29 -1.56 L 485.13 -1.68 L 484.98 -1.80 L 484.83 -1.92 L 484.69 -2.05 L 484.54 -2.18 L 484.40 -2.32 L 484.27 -2.46 L 484.14 -2.60 L 484.01 -2.75 L 483.88 -2.90 L 483.76 -3.05 L 483.64 -3.20 L 483.53 -3.36 L 483.42 -3.52 L 483.31 -3.68 L 483.21 -3.85 L 483.11 -4.02 L 483.02 -4.19 L 482.93 -4.36 L 482.85 -4.53 L 482.76 -4.71 L 482.69 -4.89 L 482.62 -5.07 L 482.55 -5.25 L 482.48 -5.44 L 482.43 -5.62 L 482.37 -5.81 L 482.32 -6.00 L 482.28 -6.18 L 482.24 -6.37 L 482.20 -6.57 L 482.17 -6.76 L 482.14 -6.95 L 482.12 -7.14 L 482.11 -7.34 L 482.09 -7.53 L 482.09 -7.73 L 482.09 -7.92 L 482.09 -8.11 L 482.09 -8.31 L 482.11 -8.50 L 482.12 -8.70 L 482.14 -8.89 L 482.17 -9.08 L 482.20 -9.27 L 482.24 -9.47 L 482.28 -9.66 L 482.32 -9.84 L 482.37 -10.03 L 482.43 -10.22 L 482.48 -10.40 L 482.55 -10.59 L 482.62 -10.77 L 482.69 -10.95 L 482.76 -11.13 L 482.85 -11.31 L 482.93 -11.48 L 483.02 -11.65 L 483.11 -11.82 L 483.21 -11.99 L 483.31 -12.16 L 483.42 -12.32 L 483.53 -12.48 L 483.64 -12.64 L 483.76 -12.79 L 483.88 -12.94 L 484.01 -13.09 L 484.14 -13.24 L 484.27 -13.38 L 484.40 -13.52 L 484.54 -13.66 L 484.69 -13.79 L 484.83 -13.92 L 484.98 -14.04 L 485.13 -14.16 L 485.29 -14.28 L 485.44 -14.40 L 485.60 -14.51 L 485.77 -14.61 L 485.93 -14.71 L 486.10 -14.81 L 486.27 -14.90 L 486.44 -14.99 L 486.62 -15.08 L 486.80 -15.16 L 486.97 -15.24 L 487.15 -15.31 L 487.34 -15.38 L 487.52 -15.44 L 487.71 -15.50 L 487.89 -15.55 L 488.08 -15.60 L 488.27 -15.65 L 488.46 -15.69 L 488.65 -15.72 L 488.84 -15.75 L 489.04 -15.78 L 489.23 -15.80 L 489.42 -15.82 L 489.62 -15.83 L 489.81 -15.84 L 490.01 -15.84 L 490.20 -15.84 L 490.39 -15.83 L 490.59 -15.82 L 490.78 -15.80 L 490.97 -15.78 L 491.17 -15.75 L 491.36 -15.72 L 491.55 -15.69 L 491.74 -15.65 L 491.93 -15.60 L 492.12 -15.55 L 492.30 -15.50 L 492.49 -15.44 L 492.67 -15.38 L 492.86 -15.31 L 493.04 -15.24 L 493.21 -15.16 L 493.39 -15.08 L 493.57 -14.99 L 493.74 -14.90 L 493.91 -14.81 L 494.08 -14.71 L 494.24 -14.61 L 494.41 -14.51 L 494.57 -14.40 L 494.72 -14.28 L 494.88 -14.16 L 495.03 -14.04 L 495.18 -13.92 L 495.32 -13.79 L 495.47 -13.66 L 495.61 -13.52 L 495.74 -13.38 L 495.87 -13.24 L 496.00 -13.09 L 496.13 -12.94 L 496.25 -12.79 L 496.37 -12.64 L 496.48 -12.48 L 496.59 -12.32 L 496.70 -12.16 L 496.80 -11.99 L 496.90 -11.82 L 496.99 -11.65 L 497.08 -11.48 L 497.16 -11.31 L 497.25 -11.13 L 497.32 -10.95 L 497.39 -10.77 L 497.46 -10.59 L 497.53 -10.40 L 497.58 -10.22 L 497.64 -10.03 L 497.69 -9.84 L 497.73 -9.66 L 497.77 -9.47 L 497.81 -9.27 L 497.84 -9.08 L 497.87 -8.89 L 497.89 -8.70 L 497.90 -8.50 L 497.92 -8.31 L 497.92 -8.11 L 497.93 -7.92 Z M 553.33 0.00 L 514.31 0.00 L 514.31 -3.78 L 520.09 -3.78 L 502.89 -72.00 L 502.01 -77.40 L 525.79 -3.78 L 501.70 -78.37 L 506.40 -91.74 L 510.36 -91.74 L 540.82 -3.78 L 553.33 -3.78 Z "/></svg></div>
  <div class="wrap ft-base"><span class="ft-copy"><span>Copyright <span data-year></span> Ghana at 70 UK</span></span><nav aria-label="Legal"><a href="terms.html">Terms</a><a href="privacy.html">Privacy</a><a href="privacy.html#cookies" data-cookie-settings>Cookie settings</a><a href="contact.html">Contact</a><a class="ft-credit" href="credits.html">Photo credits</a></nav></div>
</footer>
{('<div class="tt-cart">' + tt_slot("cart") + '</div>') if tt_slot("cart") else ""}
<div class="mobile-cta" role="region" aria-label="Book now"><a class="btn gold" href="tickets.html" data-pay="pick">Book now</a></div>
<aside class="capture" id="capture" hidden aria-labelledby="cap-title">
  <button class="capture-x" type="button" aria-label="Close">×</button>
  <div class="capture-in">
    <span class="script">Before you go</span>
    <h3 id="cap-title">Tickets are on sale now.</h3>
    <p>Choose your event and book your seats today.</p>
    <div class="stack">
      <a class="btn gold" href="royal-gala.html#book" data-pay="gala">Friday 5 March · The Royal Jubilee Gala</a>
      <a class="btn gold" href="ghana-day.html#book" data-pay="ghanaday">Saturday 6 March · Ghana Day Festival</a>
      <a class="btn gold" href="women-of-the-motherland.html#book" data-pay="sunday">Sunday 7 March · Women of the Motherland</a>
    </div>
  </div>
</aside>
<script src="site.js?v={ASSET_V}"></script>
</body>
</html>"""

SIG = {"stay": "nkonsonkonson", "index": "nsoromma", "royal-gala": "adinkrahene", "ghana-day": "fawohodie", "women-of-the-motherland": "asaseyeduru", "programme": "nsoromma",
       "sessions": "ananse", "visit": "eban", "dress-code": "duafe", "tickets": "besesaka", "exhibit": "tabono", "exhibitors": "tabono", "partners": "nkonsonkonson",
       "get-involved": "nkonsonkonson", "speakers": "ananse", "about": "sankofa", "ghana": "nsoromma", "news": "owiakokroko", "faq": "hwemudua", "contact": "nkonsonkonson",
       "terms": "hwemudua", "privacy": "eban", "accessibility": "eban", "404": "nsoromma"}

DAYKEY = {"royal-gala": "gala", "ghana-day": "ghanaday", "women-of-the-motherland": "sunday"}

REMOVED = {"news", "speakers", "sessions", "exhibitors", "get-involved", "accessibility", "programme", "ghana"}

def _auto_sizes(m):
    """Lazy images size themselves to the slot they really fill, so no photo is ever stretched."""
    tag = m.group(0)
    if 'loading="lazy"' in tag and 'srcset=' in tag and 'sizes="auto' not in tag:
        tag = re.sub(r'sizes="([^"]*)"', r'sizes="auto, \1"', tag, count=1)
    return tag


def page(slug, title, desc, body, extra=""):
    if slug in REMOVED:
        return
    sym = SIG.get(slug, "nsoromma")
    if slug in ("royal-gala", "ghana-day", "women-of-the-motherland"):
        body = body.replace('href="index.html#register"', 'href="#book"')
    B2B = {"partners": '<a class="btn gold" href="#pack">Request the sponsorship pack</a>', "exhibit": '<a class="btn gold" href="#apply">Apply for a stand</a>', "exhibitors": '<a class="btn gold" href="exhibit.html#apply">Apply for a stand</a>'}
    if slug in B2B:
        body = body.replace('<div class="ph-cta"><a class="btn gold" href="tickets.html" data-pay="pick">Book now</a>', '<div class="ph-cta">' + B2B[slug], 1)
    body = body.replace('<div class="section-head"><span class="eyebrow">', f'<div class="section-head"><span class="eyebrow eb-orn">{adl(sym)}')
    body = body.replace('<div class="section-head" style="margin-bottom:0"><span class="eyebrow">', f'<div class="section-head" style="margin-bottom:0"><span class="eyebrow eb-orn">{adl(sym)}')
    body = re.sub(r"<img\b[^>]*>", _auto_sizes, body)
    with open(os.path.join(OUT, slug + ".html"), "w") as f:
        hd, ft = header(slug), footer()
        if slug in ("royal-gala", "ghana-day", "women-of-the-motherland"):
            dk = DAYKEY[slug]
            hd = hd.replace('href="tickets.html" data-pay="pick">Book now</a></li>', f'href="#book" data-pay="{dk}">Book now</a></li>')
            ft = ft.replace('<div class="mobile-cta" role="region" aria-label="Book now"><a class="btn gold" href="tickets.html" data-pay="pick">', f'<div class="mobile-cta" role="region" aria-label="Book now"><a class="btn gold" href="#book" data-pay="{dk}">')
        if slug in AEO_SHORT:
            k = body.find("</section>")
            if k > 0: body = body[:k + 10] + f'<section class="band white aeo" aria-label="In short"><div class="wrap aeo-in"><span class="eyebrow">In short</span><p class="aeo-lead">{AEO_SHORT[slug]}</p></div></section>' + ("\n" + STORY_BAND[slug] if slug in STORY_BAND else "") + body[k + 10:]
        html = head(title, desc, slug, extra + EVENT_LD.get(slug, "") + seo_ld(slug, title, body)) + "\n" + hd + body + ft
        f.write(img_dims(html))

STORY_BAND = {'ghana-day': '<section class="band dstory" id="family"><div class="wrap story-in"><div class="story-head"><span class="eyebrow">Independence Day</span><h2>Born in Kumasi. Born in Birmingham. Born Ghanaian.</h2><div class="divider c"><i></i></div></div><div class="story-body"><p class="story-first">Seventy years to the day, and the whole family under one roof.</p><p>The aunties who argue about the jollof. The cousins who switch to Twi or Ga when they want to keep a secret. The friend from work who has never been, and will never miss it again. Families travelling in from Manchester, Birmingham, Leeds, Milton Keynes, Dublin and beyond.</p><p>A DJ all day, up to forty stands, the dance circle, oware and the Big Ghana Quiz, and five talks for families with two homes. At noon the whole hall stops for the drums and a reading of the declaration of independence. Then the music starts again.</p><p class="story-pull">Today Ghana is seventy. Today Ghana is ours.</p><div class="btn-row" style="justify-content:center;margin-top:24px"><a class="btn gold" href="#book" data-pay="ghanaday">Bring the people who made you</a></div></div></div></section>', 'royal-gala': '<section class="band dstory" id="midnight"><div class="wrap story-in"><div class="story-head"><span class="eyebrow">Independence Eve</span><h2>Midnight, 6 March. Seventy years free.</h2><div class="divider c"><i></i></div></div><div class="story-body"><p class="story-first">In 1957 our grandparents stood under the warm night sky of Accra and waited for midnight.</p><p>On Independence Eve we wait for it together again, in Kente and gold, with guests from every corner of the UK, in a grand banking hall in the City of London, moments from the Bank of England.</p><p>Fontomfrom drums at the door. A Ghanaian inspired dinner at long royal tables. Live highlife and a dance floor. Then, as the clock turns, the whole hall rises, glasses high, for the moment Ghana became free, seventy years on.</p><p class="story-pull">Arrive as royalty. There are only 250 seats.</p><div class="btn-row" style="justify-content:center;margin-top:24px"><a class="btn gold" href="#book" data-pay="gala">Take your seat at the Jubilee</a></div></div></div></section>', 'women-of-the-motherland': '<section class="band dstory" id="mothers"><div class="wrap story-in"><div class="story-head"><span class="eyebrow">Mothering Sunday</span><h2>Bring your mother. She brought you here.</h2><div class="divider c"><i></i></div></div><div class="story-body"><p class="story-first">She ironed the cloth. She sent money home on Friday and still had Sunday dinner on the table.</p><p>Some of our mothers live around the corner. Some came down from Manchester or up from Kent for the day. Some are at home in Ghana, waiting for the photographs.</p><p>On Mothering Sunday, the day after Independence Day, we honour them all: a family afternoon tea, a family portrait, and the Wall of Mothers, where every mother named by a guest is celebrated aloud.</p><p>Our symbol, Akoko Nan, is a mother who shelters and corrects her children, and never lets go. This is her day.</p><div class="btn-row" style="justify-content:center;margin-top:24px"><a class="btn gold" href="#book" data-pay="sunday">Book her seat at the table</a></div></div></div></section>', 'index': '<section class="band dstory" id="motherland"><div class="wrap story-in"><div class="story-head"><span class="eyebrow">Seventy years · One family</span><h2>The Motherland is us.</h2><div class="divider c"><i></i></div></div><div class="story-body"><p class="story-first">Somewhere in Barking tonight, a mother is ironing a Kente cloth she has kept for thirty years.</p><p>She wore it the day she landed. She wore it to every wedding, every outdooring and every graduation. On the fifth of March she will wear it again.</p><p>In Manchester, a young man is choosing a Black Stars shirt. In Birmingham, two aunties are already arguing about whose jollof is best. In Glasgow, a student is booking the train south. In Dublin, a family is booking the flight over. Some of us were born in Osu, some in Kumasi, some in Leeds and others in south London, and every one of us knows the words of that midnight in 1957: Ghana, your beloved country, is free forever.</p><p>On 6 March 1957 our grandparents danced until morning. Now it is our turn. From every corner of the UK and across Europe, Ghanaians are coming together in one great hall for three days: The Royal Jubilee Gala on Independence Eve, the Ghana Day Festival on Independence Day itself, and Women of the Motherland on Mothering Sunday.</p><p>This Platinum Jubilee, as Ghana celebrates seventy years, we are ready. When you see the traffic light, there is something you should know. Red means stop. Yellow means get ready. Green means go, go, go. We are ready to go all out for our beloved Ghana.</p><p class="story-pull">Ghana is seventy. Ghana is ours. Come and celebrate Ghana.</p><div class="btn-row" style="justify-content:center;margin-top:24px"><a class="btn gold" href="tickets.html" data-pay="pick">Take your seat at the Jubilee</a><a class="btn line-dark" href="about.html">Read our story</a></div></div></div></section>'}
AEO_SHORT = {'index': 'Ghana at 70 UK is the UK celebration of the Ghana 70th Platinum Jubilee, held in London: three days at Banking Hall, 5 to 7 March 2027, marking seventy years of Ghanaian independence. The Royal Jubilee Gala on Friday, the Ghana Day Festival on Independence Day itself, and Women of the Motherland, a Mothers Day afternoon tea, on Sunday.', 'royal-gala': 'The Royal Jubilee Gala is the Ghana Independence gala dinner and dance in London. Friday 5 March 2027 at Banking Hall in the City, on the eve of the seventieth Independence Day. Kente or black tie, royal drums, a Ghanaian inspired dinner, live highlife and Afrobeats, and a midnight toast as 6 March begins. GBP 275.', 'ghana-day': 'The Ghana Day Festival is the Ghana Independence Day party in London. Saturday 6 March 2027, seventy years to the day since 6 March 1957. A DJ and dancing from 11:00 to 18:00, forty Ghanaian stands, the dance circle, oware and the Big Ghana Quiz, for families and friends of every age. GBP 50.', 'women-of-the-motherland': 'Women of the Motherland is a Mothers Day afternoon tea for women in London. Mothering Sunday, 7 March 2027, at Banking Hall. Afternoon tea at the table, a family portrait, the networking hour and her name on the Wall of Mothers. For every woman of African heritage, and her family. GBP 150.'}
CRUMB = {"royal-gala": "The Royal Jubilee Gala", "ghana-day": "Ghana Day Festival", "women-of-the-motherland": "Women of the Motherland", "tickets": "Tickets",
         "about": "Our story", "visit": "Plan your visit", "stay": "Travel and stay", "dress-code": "What to wear", "gallery": "Gallery", "faq": "Questions",
         "partners": "Partner with us", "exhibit": "Exhibit", "press": "Tell our story", "contact": "Contact", "terms": "Ticket terms", "privacy": "Privacy"}
def seo_ld(slug, title, body):
    out = []
    if slug in CRUMB:
        out.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ghana at 70 UK", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": CRUMB[slug], "item": SITE_URL + "/" + slug}]})
    if slug == "index":
        out.append({"@context": "https://schema.org", "@type": "EventSeries", "@id": SITE_URL + "/#series", "name": "Ghana at 70 UK, The Platinum Jubilee Celebrations",
            "description": "The UK celebration of the Ghana 70th Platinum Jubilee, held over three days in London: The Royal Jubilee Gala, the Ghana Day Festival on Independence Day and Women of the Motherland.",
            "startDate": "2027-03-05T18:30:00+00:00", "endDate": "2027-03-07T18:30:00+00:00", "location": VENUE_LD, "url": SITE_URL + "/", "image": [SITE_URL + "/images/og.jpg"],
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled", "organizer": {"@id": SITE_URL + "/#org"},
            "offers": {"@type": "Offer", "name": "Weekend Pass, all three days", "price": "435", "priceCurrency": "GBP", "availability": "https://schema.org/InStock", "url": SITE_URL + "/tickets", "validFrom": "2026-11-18T00:00:00+00:00"},
            "subEvent": [{"@type": "Event", "name": n, "startDate": s, "url": SITE_URL + "/" + u} for n, s, u in [
                ("The Royal Jubilee Gala", "2027-03-05T18:30:00+00:00", "royal-gala"), ("Ghana Day Festival", "2027-03-06T11:00:00+00:00", "ghana-day"),
                ("Women of the Motherland", "2027-03-07T11:00:00+00:00", "women-of-the-motherland")]]})
    if slug == "visit":
        out.append({**{"@context": "https://schema.org"}, **VENUE_LD, "@type": "EventVenue"})
    if slug != "faq":
        qa = re.findall(r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>", body, re.S)
        clean = lambda t: re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
        qa = [(clean(q), clean(a)) for q, a in qa if clean(q).endswith("?") and clean(a)]
        if len(qa) >= 2:
            out.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    return "".join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>" for o in out)

from PIL import Image as _PILImage

# Face aware cropping: every photo carries the position of its heads, so site.js never cuts a head
_FACES = json.load(open(os.path.join(SRC, "faces.json"))) if os.path.exists(os.path.join(SRC, "faces.json")) else {}
def _heads_attr(path):
    m = re.match(r"images/((?:photos|look|venue|film|kente)/[a-z0-9-]+?)-\d+\.(?:jpg|webp)$", path)
    if not m: return ""
    f = _FACES.get(m.group(1))
    if not f or not f.get("main"): return ""
    keep = [h for h in f["main"] if h[6] > 0.004 and h[8] < 0.996 and h[7] > 0.004]
    if not keep: return ""
    hb = [min(h[0] for h in keep), min(h[1] for h in keep), max(h[2] for h in keep), max(h[3] for h in keep)]
    fb = [min(h[6] for h in keep), min(h[7] for h in keep), max(h[8] for h in keep), max(h[9] for h in keep)]
    return ' data-heads="' + ",".join(f"{x:.3f}" for x in hb) + ";" + ",".join(f"{x:.3f}" for x in fb) + '"'
_DIMS = {}
def _face_attr(tag):
    """Heads stay in frame: give every photo with people its head area, so site.js positions the crop at every width."""
    if " data-face=" in tag: return tag
    m = re.search(r'src="(images/[^"]+?)-\d+\.(?:jpg|webp)"', tag)
    if not m or m.group(1) not in _FACES: return tag
    return tag[:-1].rstrip("/").rstrip() + ' data-face="' + ";".join(",".join(str(v) for v in f) for f in _FACES[m.group(1)]) + '">'
def img_dims(html):
    """Give every local img an intrinsic width and height so the page never jumps while loading."""
    def fix(m):
        tag = m.group(0)
        src = re.search(r'src="(images/[^"]+)"', tag)
        if src and "data-heads" not in tag:
            ha = _heads_attr(src.group(1))
            if ha: tag = tag[:-1].rstrip("/").rstrip() + ha + ">"
        if " width=" in tag: return tag
        if not src: return tag
        fp = os.path.join(SRC, src.group(1))
        if not os.path.exists(fp) and fp.endswith(".jpg") and os.path.exists(fp[:-4] + ".webp"):
            fp = fp[:-4] + ".webp"
        if not os.path.exists(fp): return tag
        if fp not in _DIMS: _DIMS[fp] = _PILImage.open(fp).size
        w, h = _DIMS[fp]
        return tag[:-1].rstrip("/").rstrip() + f' width="{w}" height="{h}">'
    html = re.sub(r"<img\b[^>]*>", fix, html)
    def _realw(m):
        fp = os.path.join(SRC, m.group(1))
        alt = fp[:-4] + ".jpg" if fp.endswith(".webp") else fp
        for cand in (fp, alt, fp[:-4] + ".webp"):
            if os.path.exists(cand):
                if cand not in _DIMS: _DIMS[cand] = _PILImage.open(cand).size
                return f"{m.group(1)} {_DIMS[cand][0]}w"
        return m.group(0)
    html = re.sub(r"(images/(?:photos|look|venue|kente|film)/[a-z0-9-]+-\d+\.(?:jpg|webp)) \d+w", _realw, html)
    html = re.sub(r"<img\b[^>]*>", lambda m: _face_attr(m.group(0)), html)
    # Lazy load every image after the first screen, decode off the main thread
    first_sec = html.find("</section>", html.find("<main"))
    def lazy(m):
        tag = m.group(0)
        if m.start() < first_sec:
            return tag if "fetchpriority" in tag else tag.replace("<img ", '<img fetchpriority="high" ', 1).replace(' loading="lazy"', "")
        if "loading=" not in tag: tag = tag.replace("<img ", '<img loading="lazy" ', 1)
        if "decoding=" not in tag: tag = tag.replace("<img ", '<img decoding="async" ', 1)
        return tag
    html = re.sub(r"<img\b[^>]*>", lazy, html)
    return webp(html)

def webp(text):
    """Serve WebP wherever a WebP twin exists. Social share images stay JPEG."""
    def sw(m):
        path = m.group(0)
        if path.endswith("images/og.jpg"): return path
        w = path[:-4] + ".webp"
        return w if os.path.exists(os.path.join(SRC, w)) else path
    return re.sub(r"images/[A-Za-z0-9_/.-]+\.jpg", sw, text)

def _event(n, s, e, p, d, u):
    return ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Event", "name": n,
        "startDate": s, "endDate": e, "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": VENUE_LD, "image": [SITE_URL + "/images/og.jpg"], "description": d, "inLanguage": "en-GB", "isAccessibleForFree": False,
        "offers": _offers(p, u), "url": SITE_URL + "/" + u,
        "superEvent": {"@type": "EventSeries", "@id": SITE_URL + "/#series", "name": "Ghana at 70 UK, The Platinum Jubilee Celebrations"},
        "organizer": {"@id": SITE_URL + "/#org", "@type": "Organization", "name": "Ghana at 70 UK", "url": SITE_URL}}) + "</script>")
def _offers(p, u):
    base = {"@type": "Offer", "priceCurrency": "GBP", "url": SITE_URL + "/" + u + "#book", "availability": "https://schema.org/InStock", "validFrom": "2026-11-18T00:00:00+00:00"}
    out = [dict(base, price=p, name="Standard ticket")]
    if p == "275": out.insert(0, dict(base, price="250", name="Early bird", availability="https://schema.org/LimitedAvailability"))
    return out
EVENT_LD = {
    "royal-gala": _event("Ghana at 70 UK: The Royal Jubilee Gala of Kings and Queens", "2027-03-05T18:30:00+00:00", "2027-03-06T00:30:00+00:00", "275", "A Ghanaian gala dinner for kings and queens at Banking Hall, City of London: royal drums, a Ghanaian inspired dinner, live highlife and a midnight toast.", "royal-gala"),
    "ghana-day": _event("Ghana at 70 UK: Ghana Day Festival", "2027-03-06T11:00:00+00:00", "2027-03-06T18:00:00+00:00", "50", "Independence Day at Banking Hall: a DJ and dancing all day, up to forty Ghanaian exhibitors, games, the Big Ghana Quiz and the dance circle.", "ghana-day"),
    "women-of-the-motherland": _event("Ghana at 70 UK: Women of the Motherland", "2027-03-07T11:00:00+00:00", "2027-03-07T18:30:00+00:00", "150", "A Mothering Sunday afternoon tea at Banking Hall for women of African heritage and their families, with the Wall of Mothers, a family portrait, the Motherland Market and the networking hour.", "women-of-the-motherland"),
}

GH = json.load(open(os.path.join(SRC, "ghana_path.json")))
GH_CLIP = "polygon(" + ", ".join(f"{float(a)*100:.2f}% {float(b)*100:.2f}%" for a, b in (p.split(",") for p in open(os.path.join(SRC, "ghana_clip.txt")).read().split())) + ")"

REGIONS = json.load(open(os.path.join(SRC, "ghana_regions.json")))

def ghana_map(cls="map", stroke="#F6DB86", sw=1.6, cities=False, regions=False):
    marks = ""
    if regions:
        marks += '<g class="regions" fill="none" stroke="' + stroke + '" stroke-width=".6" stroke-opacity=".55">' + "".join(f'<path d="{d}"/>' for d in REGIONS) + "</g>"
    if cities:
        for name, x, y, dx in [("Tamale", 151.4, 111.8, 8), ("Kumasi", 104.6, 274.4, -52), ("Accra", 190.5, 342.4, 8), ("Cape Coast", 127.0, 369.5, -74)]:
            marks += f'<g><circle cx="{x}" cy="{y}" r="3.2" fill="#D4A62A"/><circle cx="{x}" cy="{y}" r="7" fill="none" stroke="#D4A62A" stroke-width=".8"/><text x="{x+dx}" y="{y+4}">{name}</text></g>'
        marks += '<polygon transform="translate(176 328) scale(.28)" points="50,4 61.2,37.6 96.6,37.6 68.1,58.6 78.9,92.4 50,71.6 21.1,92.4 31.9,58.6 3.4,37.6 38.8,37.6" fill="#16201B" stroke="#F6DB86" stroke-width="5"/>'
    return f'<svg class="{cls}" viewBox="0 0 {GH["w"]} {GH["h"]}" aria-hidden="true"><path class="outline-path" d="{GH["d"]}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" pathLength="1000"/>{marks}</svg>'



PHOTOS = json.load(open(os.path.join(SRC, "photos.json")))
def _used_photos():
    t = open(__file__).read()
    return {k: m for k, m in PHOTOS.items() if '"' + k + '"' in t and k not in ("dance",)}
CREDITS = ", ".join(sorted({m["by"] + " (" + m["src"] + ")" for m in _used_photos().values() if m.get("src") != "design concept"}))
LDIMS = {'r1': [570, 720], 't1': [325, 720], 'nk': [466, 720], 's1': [606, 720], 's2': [342, 720], 'x': [375, 720], 'a6': [829, 720], 'd1': [1113, 720], 'a4': [891, 720], 'a5': [878, 720], 'a2': [837, 720], 'a3': [837, 720], 'a1': [837, 720], 'q1': [416, 720], 'q2': [476, 720], 'q3': [426, 720], 'q4': [418, 720], 'q5': [449, 720], 'q6': [505, 720], 'q7': [440, 720], 'q8': [427, 720], 'q9': [433, 720], 'q10': [408, 720], 'k1': [372, 720], 'k2': [566, 720], 'k3': [450, 720], 'k4': [540, 720], 'k5': [540, 720], 'k6': [538, 720], 'k7': [456, 720], 'c1': [404, 720], 'c2': [449, 720], 'c3': [450, 720], 'c4': [550, 720], 'b1': [461, 720], 'b2': [509, 720], 'b3': [449, 720], 'b4': [439, 720], 'g1': [408, 720], 'g2': [408, 720], 'g3': [480, 720], 'p1': [357, 720], 'p2': [422, 720], 'p3': [342, 720], 'p4': [411, 720], 'p5': [306, 720], 'p6': [308, 720], 'p7': [319, 720], 'p8': [318, 720], 'p9': [300, 720], 'p10': [373, 720], 'p11': [340, 720]}

def filmstrip(items, label, cls=""):
    tot = len(items)
    lis = "".join(f'<li class="gi" style="--ar:{PHOTOS[k]["w"]}/{PHOTOS[k]["h"]}">' + photo(k, a, "ph gi-ph", pos, "(max-width:760px) 86vw, 40vw") + '</li>' for k, a, pos in items)
    return (f'<div class="gfs {cls}" data-gfs><ul class="gfs-track" data-gfs-track tabindex="0" aria-label="{label}: {tot} images, scroll sideways">{lis}</ul>'
            f'<div class="gfs-bar"><span class="gfs-count"><b data-gfs-n>01</b><span> / {tot:02d}</span></span><span class="gfs-prog" aria-hidden="true"><i data-gfs-p></i></span>'
            f'<button type="button" class="gfs-play" data-gfs-play aria-pressed="false" aria-label="Pause the slideshow"><span class="gfs-ic" aria-hidden="true"></span></button>'
            f'<span class="gfs-arrows"><button type="button" class="gfs-btn" data-gfs-d="-1" aria-label="Previous images">&#8592;</button><button type="button" class="gfs-btn" data-gfs-d="1" aria-label="Next images">&#8594;</button></span></div></div>')


def photo(k, alt, cls="ph", pos="50% 40%", sizes="(max-width:760px) 100vw, 50vw"):
    if k.startswith("venue/"):
        n = k[6:]
        return (f'<figure class="{cls}"><img src="images/venue/{n}-1600.jpg" srcset="images/venue/{n}-800.jpg 800w, images/venue/{n}-1600.jpg 1600w" sizes="{sizes}" '
                f'alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></figure>')
    if k.startswith("look/"):
        n = k[5:]
        w, h = LDIMS[n]
        return (f'<figure class="{cls}"><img src="images/look/{n}-1400.jpg" srcset="images/look/{n}-720.jpg 720w, images/look/{n}-1400.jpg 1400w" sizes="{sizes}" width="{w}" height="{h}" '
                f'alt="{alt}" loading="lazy" decoding="async"></figure>')
    if k.startswith("kente/"):
        n = k[6:]
        return (f'<figure class="{cls}"><img src="images/kente/{n}-1200.jpg" srcset="images/kente/{n}-640.jpg 640w, images/kente/{n}-1200.jpg 1200w" sizes="{sizes}" '
                f'alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></figure>')
    m = PHOTOS[k]
    return (f'<figure class="{cls}"><img src="images/photos/{k}-1600.jpg" srcset="images/photos/{k}-800.jpg 800w, images/photos/{k}-1600.jpg 1600w" sizes="{sizes}" '
            f'width="{m["w"]}" height="{m["h"]}" alt="{alt}" loading="lazy" decoding="async" style="object-position:{pos}"></figure>')



ICONS = {
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "venue": '<path d="M4 21V10a8 8 0 0 1 16 0v11M8 21V11a4 4 0 0 1 8 0v10M2 21h20"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "dress": '<path d="M8 3l4 3 4-3 4 4-3 3v11H7V10L4 7z"/>',
    "ticket": '<path d="M3 7h18v4a2 2 0 0 0 0 4v4H3v-4a2 2 0 0 0 0-4z"/><path d="M15 7v12" stroke-dasharray="2 2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 7l9 6 9-6"/>',
    "cup": '<path d="M5 9h12v4a5 5 0 0 1-5 5h-2a5 5 0 0 1-5-5z"/><path d="M17 10h1.5a2.5 2.5 0 0 1 0 5H17M7 21h10M9 3c0 2 2 2 2 4M13 3c0 2 2 2 2 4"/>',
    "music": '<path d="M9 18V6l10-2v12"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="16" r="2"/>',
    "camera": '<rect x="3" y="7" width="18" height="13" rx="2"/><circle cx="12" cy="13.5" r="4"/><path d="M8 7l2-3h4l2 3"/>',
    "plate": '<circle cx="12" cy="12" r="6.5"/><circle cx="12" cy="12" r="3.5"/><path d="M2.5 3v18M21.5 3v18"/>',
    "star": '<path d="M12 3l2.6 6.2 6.4.5-4.9 4.2 1.5 6.4L12 17l-5.6 3.3 1.5-6.4L3 9.7l6.4-.5z"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M8 21h8"/>',
    "circle": '<circle cx="12" cy="6.5" r="2.6"/><circle cx="5" cy="13" r="2.3"/><circle cx="19" cy="13" r="2.3"/><path d="M8 21a4 4 0 0 1 8 0M2 20a3 3 0 0 1 5-2M22 20a3 3 0 0 0-5-2"/>',
    "drum": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v11c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 9l7 3 7-3M8 2l2 3M16 2l-2 3"/>',
    "book": '<path d="M4 5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M9 7h7M9 11h7"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "door": '<path d="M5 21V8a7 7 0 0 1 14 0v13M3 21h18M12 12v2"/>',
    "dance": '<circle cx="12" cy="4.5" r="2"/><path d="M12 7v6l-3 7M12 13l3 7M7 9l5 1 5-3"/>',
    "gift": '<rect x="3" y="9" width="18" height="12"/><path d="M3 13h18M12 9v12M12 9c-2-4-6-4-6-1.5S9 9 12 9c3 0 6-1 6-1.5S14 5 12 9"/>',
    "people": '<circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20a6 6 0 0 1 12 0M10 20a6 6 0 0 1 12 0"/>',
    "glass": '<path d="M7 3h10l-1 7a4 4 0 0 1-8 0zM12 14v7M8 21h8"/>',
    "umbrella": '<path d="M3 12a9 8 0 0 1 18 0z"/><path d="M12 12v8a2 2 0 0 1-4 0M12 2v2"/><path d="M7.5 12c0-3 2-6.5 4.5-8M16.5 12c0-3-2-6.5-4.5-8"/>',
    "staff": '<path d="M12 22V9"/><circle cx="12" cy="6" r="3"/><path d="M9 4l-2-2M15 4l2-2M10 13h4"/>',
    "stool": '<path d="M3 7q9 4 18 0v2q-9 4-18 0z"/><path d="M9 11v7h6v-7M5 19h14"/>',
    "carriage": '<path d="M4 10h13l2 5H4z"/><path d="M6 10V6h9v4"/><circle cx="7" cy="18" r="2.5"/><circle cx="17" cy="18" r="2.5"/><path d="M10.5 6l-1-3h2z"/><path d="M19 15h2"/>',
    "flower": '<circle cx="12" cy="9" r="2"/><path d="M12 7c-1-3 2-5 2-2.5S12 7 12 7zM12 7c1-3-2-5-2-2.5S12 7 12 7z"/><path d="M14 9c3-1 5 2 2.5 2S14 9 14 9zM10 9c-3-1-5 2-2.5 2S10 9 10 9z"/><path d="M12 11v10M12 17c-3 0-4-2-4-3 2 0 4 1 4 3zM12 15c3 0 4-2 4-3-2 0-4 1-4 3z"/>',
    "trophy": '<path d="M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4M12 14v4M8 21h8M9 18h6"/>',
    "quiz": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7"/><path d="M12 17v.5"/>',
    "game": '<rect x="2" y="8" width="20" height="8" rx="4"/><circle cx="6" cy="10.5" r="1"/><circle cx="10" cy="10.5" r="1"/><circle cx="14" cy="10.5" r="1"/><circle cx="18" cy="10.5" r="1"/><circle cx="6" cy="13.5" r="1"/><circle cx="10" cy="13.5" r="1"/><circle cx="14" cy="13.5" r="1"/><circle cx="18" cy="13.5" r="1"/>',
    "cloth": '<path d="M4 4h16v16H4z"/><path d="M4 9h16M4 15h16M9 4v16M15 4v16"/>',
}
def icon(name):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(name, ICONS["star"])}</svg>'

KEYS = [("tea", "cup"), ("lunch", "plate"), ("banquet", "plate"), ("course", "plate"), ("dinner", "plate"), ("portrait", "camera"), ("photograph", "camera"),
        ("drum", "drum"), ("arrival", "door"), ("doors", "door"), ("welcome", "door"), ("procession", "door"), ("reception", "glass"), ("toast", "glass"),
        ("kete", "drum"), ("adowa", "dance"), ("dance", "dance"), ("highlife", "music"), ("music", "music"), ("honouring", "heart"), ("mothers", "heart"),
        ("keynote", "mic"), ("panel", "mic"), ("conversation", "mic"), ("circle", "circle"), ("workshop", "circle"), ("pledge", "book"), ("village", "people"),
        ("weaving", "cloth"), ("kente", "cloth"), ("runway", "dress"), ("fashion", "dress"), ("moment", "star"), ("independence", "star"), ("anniversary", "star"),
        ("seminar", "mic"), ("farewell", "heart"), ("carriages", "star"), ("blessing", "heart"), ("close", "door")]
def guess_icon(title):
    t = title.lower()
    for k, v in KEYS:
        if k in t:
            return v
    return "star"

DAYINFO = {
    "royal-gala": ("The Royal Jubilee Gala", "Fri 5 March · 18:30", "GBP 275 · early bird GBP 250", "https://calendar.google.com/calendar/render?action=TEMPLATE&amp;text=Ghana%20at%2070%3A%20The%20Royal%20Kente%20Gala&amp;dates=20270305T183000Z/20270306T003000Z&amp;details=Doors%2018%3A30.%20We%20start%20on%20time.%20Your%20golden%20ticket%20arrives%20by%20email.&amp;location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND"),
    "ghana-day": ("Ghana Day Festival", "Sat 6 March · 11:00", "GBP 50", "https://calendar.google.com/calendar/render?action=TEMPLATE&amp;text=Ghana%20at%2070%3A%20Ghana%20Day%20Party&amp;dates=20270306T110000Z/20270306T180000Z&amp;details=Independence%20Day%20at%20Banking%20Hall.%20Your%20golden%20ticket%20arrives%20by%20email.&amp;location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND"),
    "women-of-the-motherland": ("Women of the Motherland", "Sun 7 March · 11:00", "GBP 150", "https://calendar.google.com/calendar/render?action=TEMPLATE&amp;text=Ghana%20at%2070%3A%20Women%20of%20the%20Motherland&amp;dates=20270307T110000Z/20270307T183000Z&amp;details=Mothering%20Sunday%20at%20Banking%20Hall.%20Doors%2011%3A00.%20Your%20golden%20ticket%20arrives%20by%20email.&amp;location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND"),
}

def page_head(eyebrow, title, lead, tone="", symbol="adinkrahene", chips="", script="", day=None):
    sc = f'<span class="script">{script}</span>' if script else ""
    if day in DAYINFO:
        name, when, price, cal = DAYINFO[day]
        paykey = {"royal-gala": "gala", "ghana-day": "ghanaday", "women-of-the-motherland": "sunday"}[day]
        ctas = (f'<div class="ph-cta"><a class="btn gold" href="#book" data-pay="{paykey}">Book now</a>'
                f'<a class="ph-link" href="cal/{ {"gala": "royal-jubilee-gala", "ghanaday": "ghana-day-festival", "sunday": "women-of-the-motherland"}[paykey] }.ics">Add to calendar</a><a class="ph-link" data-share href="https://wa.me/?text=">Share with family</a></div>')
        local = (f'<div class="localnav" data-localnav><div class="wrap localnav-in"><span class="ln-name">{name}</span>'
                 f'<span class="ln-meta">{when} · {price}</span><a class="btn gold small" href="#book" data-pay="{paykey}">Book now</a></div></div>')
    else:
        ctas = '<div class="ph-cta"><a class="btn gold" href="tickets.html" data-pay="pick">Book now</a><a class="ph-link" href="index.html#days">The three days</a></div>'
        local = ""
    return f"""
<section class="page-head {tone}"><div class="watermark">{adl(symbol)}</div><div class="wrap ph-inner"><div class="stack"><span class="eyebrow">{eyebrow}</span>{sc}<h1>{title}</h1><div class="divider"><i></i></div><p class="lead">{lead}</p>{chips}{ctas}</div></div><span class="ph-scroll" aria-hidden="true"></span></section><div class="tricolour"></div>{local}"""

CORNER = '<svg class="cn {c}" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M2 24V8a6 6 0 0 1 6-6h16"/><path d="M6 24V12a6 6 0 0 1 6-6h12"/><path d="M9 9c3 0 4 2 4 4s-2 3-3.5 2S9 12 11 11"/></svg>'

def gt(name, small, detail, price, serial, theme="", sym="adinkrahene", buy=""):
    corners = "".join(CORNER.format(c=c) for c in ("tl", "tr", "bl", "br"))
    return f"""
<div class="gt-wrap"><div class="gt {theme}" aria-label="Buy golden tickets for {name}"{f' data-buy="{buy}" role="button" tabindex="0"' if buy else ""}><span class="gt-mark" aria-hidden="true">{adl(sym)}</span>
  <div class="gt-stub"><span>Admit one</span></div>
  <div class="gt-main">{corners}
    <span class="gt-small">Ghana at 70 UK · {small}</span>
    <span class="gt-title">Golden Ticket</span>
    <span class="gt-dots"></span>
    <span class="gt-name">{name}</span>
    <span class="gt-detail">{detail}</span>
  </div>
  <div class="gt-stub r"><span>{price}</span></div>
</div></div>"""

T_GALA = gt("The Royal Jubilee Gala of Kings and Queens", "Friday", "Friday 5 March 2027 · 18:30 · Banking Hall", "GBP 275", "0001", "gt-black", "adinkrahene", "gala")
T_DAY = gt("Ghana Day Festival", "Independence Day", "Saturday 6 March 2027 · 11:00 · Banking Hall", "GBP 50", "0001", "gt-green", "fawohodie", "ghanaday")
T_SUN = gt("Women of the Motherland", "Mothering Sunday", "Sunday 7 March 2027 · 11:00 · Banking Hall", "GBP 150", "0001", "gt-ruby", "asaseyeduru", "sunday")




# ===== One definitive list of what each ticket includes. Used on every page. =====
VENUE_LINE = "Banking Hall, 14 Cornhill, London EC3V 3ND, moments from the Bank of England. Bank station, two minutes on foot"
INC = {
 "gala": ["The Royal Arrival: Fontomfrom drums and the red carpet",
          "Your red carpet portrait on the Platinum Jubilee wall, delivered within seven days",
          "Sobolo welcome on arrival",
          "A Ghanaian inspired dinner, carried in procession and served at your table",
          "Soft drinks and water all evening",
          "Kete and Adowa, the royal music and dance of the Asante",
          "A live band: highlife, hiplife, Afrobeats and everything in between",
          "The anthem and the midnight toast as Independence Day begins",
          "The royal dance floor until the last dance"],
 "ghanaday": ["Entry all day, 11:00 to 18:00, with a wristband to come and go",
          "A DJ and dancing all day: highlife, hiplife and Afrobeats",
          "The anniversary moment at 12:00",
          "Forty chosen exhibitors, never more than two of a kind",
          "Five expert talks: land, money, wills, pensions and business",
          "Oware, the Big Ghana Quiz and the dance circle",
          "The Ghana at 70 UK runway",
          "The networking hour"],
 "sunday": ["Family afternoon tea, served at your table all afternoon",
          "Tea, coffee and soft drinks",
          "Her name on the Wall of Mothers, read aloud at 14:00",
          "The Resource Village and the Motherland Toolkit",
          "A family portrait, with a print to take home",
          "The networking hour, a table for every region"],
}
NOT_INC = {
 "gala": "Not included: alcohol. The bar serves all evening, by card.",
 "ghanaday": "Not included: food and drink. The bar sells drinks and snacks all day, card only.",
 "sunday": "Not included: alcohol.",
}
INC_SUMMARY = {
 "gala": "Everything on the night: the Royal Arrival and your red carpet portrait, a sobolo welcome, a Ghanaian inspired dinner served at your table, soft drinks and water all evening, Kete and Adowa, a live band, the anthem and the midnight toast. Not included: alcohol, which the bar serves by card.",
 "ghanaday": "The whole day from 11:00 to 18:00: the DJ and dancing, the anniversary moment at 12:00, up to forty exhibitors, five expert talks, oware, the Big Ghana Quiz, the dance circle, the runway and the networking hour. Not included: food and drink. The bar sells drinks and snacks all day, card only.",
 "sunday": "Family afternoon tea at your table with tea, coffee and soft drinks, her name on the Wall of Mothers, the Resource Village and the Motherland Toolkit, a family portrait, Voices of the Motherland and the networking hour. Not included: alcohol.",
}
def inc_sentence(day):
    return INC_SUMMARY[day]


def tt_slot(name):
    import re as _re
    try: raw = open(os.path.join(SRC, "tt", name + ".html")).read()
    except OSError: return ""
    return raw if _re.sub(r"<!--.*?-->", "", raw, flags=_re.S).strip() else ""

TT_BOOKING = '''
<section class="band white" id="all-days" hidden data-tt-show><div class="wrap">
  <div class="section-head"><span class="eyebrow">The box office</span><h2>All three days, one order.</h2><p class="lead">Add the Gala, the Festival and Sunday to one basket and pay once. Places left are shown live for every day.</p></div>
  <div class="tt-box">{TTBOX}</div>
  <p class="tt-fallback" hidden data-tt-fallback>Booking window not opening? <a data-tt-link="boxoffice" href="#">Open the secure box office</a> in its own page.</p>
</div></section>
<section class="band ivory" id="how-booking-works" hidden data-tt-show><div class="wrap">
  <div class="section-head"><span class="eyebrow">How booking works</span><h2>Secure, simple, and yours in two minutes.</h2></div>
  <ol class="tt-steps">
    <li><b>Secure checkout</b><span>Checkout is run by Ticket Tailor and paid through Stripe, in GBP. Card, Apple Pay and Google Pay where your device offers them. Your card details go straight to Stripe and never touch this website.</span></li>
    <li><b>Booking for a group</b><span>Enter each guest by name at checkout. Every guest receives a ticket with their own QR code.</span></li>
    <li><b>Your golden tickets</b><span>They arrive by email at once, with a PDF attached. Forward each guest their own ticket, or print the PDF. Keep your code private: each code admits one guest, once.</span></li>
    <li><b>Dietary and access needs</b><span>For the Gala we ask for dietary needs at checkout, and anything that would make your arrival easier, so the kitchen and our hosts are ready for you.</span></li>
    <li><b>Your choice on news</b><span>One optional box at checkout, left unticked. Tick it only if you would like our news.</span></li>
    <li><b>Refunds</b><span>All sales are final and tickets are transferable to another guest. If we cancel, every ticket is refunded in full. Read our <a href="terms.html">booking terms</a> and <a href="privacy.html">privacy notice</a>.</span></li>
    <li><b>Help with your booking</b><span>Call Asantewaa on <a href="tel:07824555307" data-phone>07824 555307</a> or email <a data-email href="mailto:ghanaat70.uk@gmail.com">ghanaat70.uk@gmail.com</a>.</span></li>
  </ol>
</div></section>'''

VALID = {
    "gala": "This ticket is for The Royal Jubilee Gala only, on Friday 5 March 2027, 18:30 to 00:30. It does not include the Ghana Day Festival or Women of the Motherland.",
    "ghanaday": "This ticket is for the Ghana Day Festival only, on Saturday 6 March 2027, 11:00 to 18:00. It does not include The Royal Jubilee Gala or Women of the Motherland.",
    "sunday": "This ticket is for Women of the Motherland only, on Sunday 7 March 2027, 11:00 to 18:30. It does not include The Royal Jubilee Gala or the Ghana Day Festival.",
    "weekend": "The Weekend Pass gives one entry to each of the three separate events, each on its own date: Friday 5, Saturday 6 and Sunday 7 March 2027.",
}


def ticket_row(ticket, title, items, working, href, cta="Book now", btn="gold", pay=""):
    lis = "".join(f"<li>{i}</li>" for i in items)
    dp = f' data-pay="{pay}"' if pay else ""
    return f'''
<div class="ticket-row">{ticket}<div class="ticket-copy"><h3>{title}</h3><ul>{lis}</ul>{('<p class="not-inc">' + NOT_INC[pay] + '</p>') if pay in NOT_INC else ''}{('<p class="bp-valid">' + VALID[pay] + '</p>') if pay in VALID else ''}<p class="where"><b>Where</b> {VENUE_LINE}</p><p class="working">{working}</p><p class="left" data-left="{pay}" hidden></p><div class="btn-row"><a class="btn {btn}" href="{href}"{dp}>{cta}</a></div><p class="reassure">Two minutes to book · Transferable tickets</p></div></div>'''

def register_form(source="landing", heading="Join the priority list", mother=False, day=None):
    mother_field = f"""
      <div class="field"><label for="f-mother-{source}">The Wall of Mothers: a mother you wish to honour</label><input id="f-mother-{source}" name="motherName" placeholder="For example, Auntie Ama Mensah, Kumasi"></div>""" if mother else ""
    return f"""
<div class="form-card">
  <form data-register novalidate class="stack-lg" aria-labelledby="reg-title-{source}">
    <input type="hidden" name="type" value="guest"><input type="hidden" name="source" value="{source}"><input type="hidden" name="basket" data-basket>
    <div class="stack"><span class="eyebrow">The priority list</span><h3 id="reg-title-{source}">{heading}</h3><p class="muted">Tickets are on sale now. Not ready to book? Join the list for the programme, the speakers and every announcement first. Nothing is reserved until you book and pay.</p></div>
    <div class="row2">
      <div class="field"><label for="f-first-{source}">First name</label><input id="f-first-{source}" name="firstName" autocomplete="given-name" required></div>
      <div class="field"><label for="f-email-{source}">Email</label><input id="f-email-{source}" type="email" name="email" autocomplete="email" required></div>
    </div>
    <fieldset class="field"><legend>Which days would you like</legend>
      <div class="days-pick">
        <label class="pick"><input type="checkbox" name="interests" value="Royal Jubilee Gala"{" checked" if day == "gala" else ""}><span><i>Friday</i>The Royal Jubilee Gala</span></label>
        <label class="pick"><input type="checkbox" name="interests" value="Ghana Day"{" checked" if day == "ghanaday" else ""}><span><i>Saturday</i>Ghana Day Festival</span></label>
        <label class="pick"><input type="checkbox" name="interests" value="Women of the Motherland"{" checked" if mother else ""}><span><i>Sunday</i>Women of the Motherland</span></label>
      </div>
    </fieldset>
    <details class="more"{" open" if mother else ""}><summary>Add your details <span>optional, helps us plan for you</span></summary>
      <div class="stack-lg more-in">
      <div class="row2">
        <div class="field"><label for="f-last-{source}">Last name</label><input id="f-last-{source}" name="lastName" autocomplete="family-name"></div>
        <div class="field"><label for="f-phone-{source}">Mobile</label><input id="f-phone-{source}" type="tel" name="phone" autocomplete="tel"></div>
      </div>
      <div class="row2">
        <div class="field"><label for="f-party-{source}">Party size</label><select id="f-party-{source}" name="partySize"><option>1</option><option selected>2</option><option>3 to 4</option><option>5, a family table</option><option>10, a royal party</option><option>More than 10</option></select></div>
        <div class="field"><label for="f-heard-{source}">How you heard of us</label><select id="f-heard-{source}" name="heardFrom"><option value="">Please choose</option><option>Instagram</option><option>Facebook</option><option>TikTok</option><option>WhatsApp</option><option>Church or community group</option><option>A friend</option><option>Other</option></select></div>
      </div>
      <fieldset class="field"><legend>I would also like</legend>
        <div class="checks">
          <label class="check"><input type="checkbox" name="interests" value="Accommodation"><span>A hotel in London</span></label>
          <label class="check"><input type="checkbox" name="interests" value="Private party or add ons"><span>A private celebration</span></label>
          <label class="check"><input type="checkbox" name="interests" value="Partnering or exhibiting"><span>To partner or exhibit</span></label>
        </div>
      </fieldset>{mother_field}
      </div>
    </details>
    <div class="hp" aria-hidden="true"><label for="f-web-{source}">Leave blank</label><input id="f-web-{source}" name="website" tabindex="-1" autocomplete="off"></div>
    <label class="consent"><input type="checkbox" name="consent" value="yes" required><span>Yes, send me my priority link and news about Ghana at 70 UK. Unsubscribe at any time. <a href="privacy.html">Privacy</a></span></label>
    <div class="form-status" role="status" aria-live="polite"></div>
    <button class="btn gold" type="submit">Join the priority list</button>
    <p class="reassure c">Your details are never sold</p>
  </form>
  <div class="form-done" hidden><span class="eyebrow">You are on the list</span><h3>Medaase. You are on the list.</h3><p class="muted">Watch your inbox for the programme, the speakers and every announcement first. Tickets are on sale now, so book today to choose your seats.</p><div class="btn-row"><a class="btn emerald" href="index.html#days">Explore the programme</a><a class="btn emerald" href="stay.html">We can help you book your hotel stay</a></div></div>
</div>"""

FORMS = {
    "partner": ("Start the conversation", "Partner enquiry", "Tell us what the weekend should achieve for your organisation. We reply within one working day.",
                ["Presenting Partner, GBP 20,000", "Principal Partner, GBP 15,000", "Official Partner, GBP 10,000", "Strategic or community partner", "Support partner for the Resource Village", "Royal Jubilee Gala table for my organisation", "Private party or branded experience"],
                "Your interest", "What would success look like for you", "Send enquiry", "Your enquiry is with our partnerships team. Expect a reply within one working day with a proposal shaped around your objectives.", True),
    "pack": ("Request the sponsorship pack", "Sponsorship pack", "The full pack covers audience, tiers, benefits, extras and key dates. It arrives in your inbox the same day.",
             ["Presenting Partner, GBP 20,000", "Principal Partner, GBP 15,000", "Official Partner, GBP 10,000", "Not sure yet"],
             "Most interested in", "Anything we should know (optional)", "Send me the pack", "The sponsorship pack is on its way to your inbox. A member of our partnerships team will follow up to arrange a call.", True),
    "speaker": ("Register to speak", "Speakers and circle hosts", "Speak at any of our three events, offer to lead a Sunday talk or masterclass, or nominate someone whose voice belongs on our stage.",
                ["Speaker, Women of the Motherland", "Reader, Voices of the Motherland", "Masterclass host", "Expert for one to one advice", "Ghana Day host or quiz master", "Host or MC, Royal Jubilee Gala", "Performer", "Nominating someone else"],
                "I would like to", "Your topic, your story or your nominee", "Send", "Thank you. Our programme team reviews every submission and will be in touch if there is a fit.", False),
    "compete": ("Join the games", "Ghana Day games", "Enter the dance circle, oware games or the Big Ghana Quiz on Saturday 6 March 2027. Entry is included with your Ghana Day ticket.",
                ["Dance circle, solo", "Dance circle, crew of up to five", "Oware games", "Big Ghana Quiz, team of up to six"],
                "I would like to enter", "Crew or team name, and anything we should know", "Enter", "You are entered. Game rules and your timings arrive by email in February 2027.", False),
    "stay": ("Plan my stay", "Accommodation service", "Tell us your dates and we will send hotel options and rates within one working day.",
             ["Hotel only", "Hotel and airport or station transfers", "Hotel, transfers and golden tickets", "A group of rooms for family or friends"],
             "I would like", "Arrival and departure dates, rooms, guests, and the standard of hotel you prefer", "Send my request", "Your request is with our accommodation team. Expect options and rates within one working day.", False),
    "press": ("Request accreditation", "Media and creators", "For journalists, broadcasters, podcasters, photographers, community media and creators covering Ghana at 70 UK. Accreditation is confirmed by email.",
              ["The Royal Jubilee Gala", "Ghana Day Festival", "Women of the Motherland", "All three days"],
              "Accreditation for", "Your outlet or channel, your audience and what you plan to cover", "Request accreditation", "Your request is with our media team. Accreditation is confirmed by email, usually within three working days.", True),
    "village": ("Join the Resource Village", "Resource Village", "For organisations that support women. Tell us who you are and how you help, and we reply within one working day.",
                ["Health and wellbeing", "Legal and family", "Money and housing", "Safety and support", "Faith and community", "Other"], "Your area of support", "How you support women", "Apply to join", "Our partnership team replies within one working day.", True),
    "contact": ("Send us a message", "Contact", "We reply within one working day, Monday to Friday.",
                ["Tickets and booking", "Accommodation", "Accessibility", "Partnership or sponsorship", "Exhibiting", "Press", "Something else"],
                "Your enquiry is about", "Your message", "Send message", "Thank you. Your message is with our team and we will reply within one working day.", False),
    "volunteer": ("Volunteer your support", "Volunteers", "Be part of the team that makes the seventieth happen. Volunteers receive training, a Ghana at 70 UK pass for their shift day and our lasting thanks.",
                  ["Graduate usher, Royal Jubilee Gala", "Guest welcome and registration", "Ghana Day exhibitor support", "Sunday hosting and tables", "Sunday photography, for aspiring women photographers", "Social media", "Any role where I am needed"],
                  "I would like to help with", "Your availability and any experience", "Volunteer", "Medaase. We will be in touch with volunteer briefings and shift options in January 2027.", False),
}

def enquiry_form(kind):
    title, eyebrow, intro, opts, label, msg, btn, done, org_req = FORMS[kind]
    options = "".join(f"<option>{o}</option>" for o in opts)
    org = f'<div class="field"><label for="e-org-{kind}">Organisation{"" if org_req else " (optional)"}</label><input id="e-org-{kind}" name="organisation" autocomplete="organization"{" required" if org_req else ""}></div>'
    return f"""
<div class="form-card">
  <form data-register novalidate class="stack-lg" aria-labelledby="e-title-{kind}">
    <input type="hidden" name="type" value="{kind}">
    <div class="stack"><span class="eyebrow">{eyebrow}</span><h3 id="e-title-{kind}">{title}</h3><p class="muted">{intro}</p></div>
    <div class="row2"><div class="field"><label for="e-name-{kind}">Your name</label><input id="e-name-{kind}" name="firstName" autocomplete="name" required></div>{org}</div>
    <div class="row2"><div class="field"><label for="e-email-{kind}">Email</label><input id="e-email-{kind}" type="email" name="email" autocomplete="email" required></div><div class="field"><label for="e-phone-{kind}">Telephone</label><input id="e-phone-{kind}" type="tel" name="phone" autocomplete="tel"></div></div>
    <div class="field"><label for="e-int-{kind}">{label}</label><select id="e-int-{kind}" name="interests" required><option value="">Please choose</option>{options}</select></div>
    <div class="field"><label for="e-msg-{kind}">{msg}</label><textarea id="e-msg-{kind}" name="message"></textarea></div>
    <div class="hp" aria-hidden="true"><label for="e-web-{kind}">Leave blank</label><input id="e-web-{kind}" name="website" tabindex="-1" autocomplete="off"></div>
    <label class="consent"><input type="checkbox" name="consent" value="yes" required><span>I agree to be contacted about Ghana at 70 UK. See the <a href="privacy.html">privacy notice</a>.</span></label>
    <div class="form-status" role="status" aria-live="polite"></div>
    <button class="btn gold" type="submit">{btn}</button>
  </form>
  <div class="form-done" hidden><span class="eyebrow">Received</span><h3>Medaase. Thank you.</h3><p class="muted">{done}</p></div>
</div>"""

def daycard(cls, sym, num, when, title, text, items, price, go, href):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f"""<a class="day {cls}" href="{href}"><span class="sym">{adl(sym)}</span><span class="num">{num}</span><span class="when">{when}</span><span class="tri"></span><h3>{title}</h3><p class="muted">{text}</p><ul>{lis}</ul><div class="foot"><strong>{price}</strong><span class="go">{go}</span></div></a>"""

def evcard(cls, n, ph, alt, pos, day, mon, wk, title, kicker, time, line, items, price, note, pay, book, href, more):
    lis = "".join(f"<li>{i}</li>" for i in items)
    fig = photo(ph, alt, "ev-ph", pos, "(max-width:900px) 100vw, 33vw")
    return f"""<article class="ev ev-{cls}">
  <div class="ev-top">{fig}<div class="ev-date" aria-hidden="true"><b>{day}</b><span>{mon}</span><i>{wk}</i></div><span class="ev-no">Event {n} of 3</span></div>
  <div class="ev-body">
    <span class="ev-kicker">{kicker}</span>
    <h3><a href="{href}">{title}</a></h3>
    <p class="ev-time">{time}</p>
    <p class="ev-line">{line}</p>
    <ul class="ev-list">{lis}</ul>
    <div class="ev-foot">
      <div class="ev-price"><b>{price}</b><span>{note}</span></div>
      <p class="ev-own">Separate event, its own ticket</p>
      <div class="ev-acts"><a class="btn gold" href="{href}#book" data-pay="{pay}">{book}</a><a class="ev-more" href="{href}">{more}</a></div>
    </div>
  </div>
</article>"""

DAYS = '<div class="evs">' + evcard("gala", 1, "y-two-couples", "A young couple in Kente and black tie laughing with an older couple, champagne in hand, in a grand hall", "50% 30%", "05", "March", "Friday",
    "The Royal Jubilee Gala", "Independence Eve", "18:30 to 00:30 · Banking Hall",
    "Wear the Kente you have been saving. Come for the dinner, get up for the highlife and stay for the midnight toast. If there is one night to get your friends around the same table, make it Independence Eve.",
    ["Fontomfrom drums and the red carpet", "A Ghanaian inspired dinner", "Live band and dancing", "The midnight toast as Independence Day begins"],
    "GBP 275", "per guest · early bird GBP 250", "gala", "Book the Gala", "royal-gala.html", "Discover the Gala") + \
    evcard("fest", 2, "j-four-friends", "Two young men and two young women in Kente print shirts and tops with jeans and white trainers", "50% 15%", "06", "March", "Saturday",
    "Ghana Day Festival", "Independence Day", "11:00 to 18:00 · Banking Hall · Come and go",
    "Meet the companies that want to reach the Ghanaian diaspora, all under one roof. Book fixed 10 minute appointments with the exhibitors you choose, then play the games, dance, network and celebrate Independence Day with fellow Ghanaians.",
    ["The exhibition: up to forty companies for the diaspora", "Fixed 10 minute appointments with exhibitors you choose", "Games, the Big Ghana Quiz, DJ and dancing", "Network and meet fellow Ghanaians"],
    "GBP 50", "per guest · ages 5 and over", "ghanaday", "Book Ghana Day", "ghana-day.html", "Explore the day") + \
    evcard("sun", 3, "n-three-gen", "A grandmother in a Kente headwrap, her daughter and her granddaughter, cheek to cheek and laughing", "50% 30%", "07", "March", "Sunday",
    "Women of the Motherland", "Mothering Sunday", "11:00 to 18:30 · Banking Hall",
    "Bring your mum, your auntie or the woman who raised you. This Mothering Sunday, sit down together for a family afternoon tea. Let her be the one who gets dressed up, takes her seat and is looked after for the afternoon.",
    ["Family afternoon tea at the table", "Her name on the Wall of Mothers", "A family portrait to take home", "The networking hour"],
    "GBP 150", "per guest · tea and soft drinks included", "sunday", "Book afternoon tea", "women-of-the-motherland.html", "See the afternoon") + "</div>"





def countdown():
    return """<div class="countdown" data-countdown aria-label="Countdown to Saturday 6 March 2027">
  <div class="cd-cell"><span class="cd-num" data-d>0</span><span class="cd-lbl">Days</span></div>
  <div class="cd-cell"><span class="cd-num" data-h>00</span><span class="cd-lbl">Hours</span></div>
</div>"""

TL_DT = {"6 March, 11:00": "2027-03-06T11:00", "5 days": "P5D", "19 Feb 2027": "2027-02-19", "14 days": "P14D", "Friday 5 March": "2027-03-05", "6 March, 18:00": "2027-03-06T18:00", "6 March, 08:00": "2027-03-06T08:00", "January 2027": "2027-01"}
def tl_when(t):
    if re.fullmatch(r"\d{2}:\d{2}", t): return f'<time datetime="{t}">{t}</time>'
    if t in TL_DT: return f'<time datetime="{TL_DT[t]}">{t}</time>'
    return f'<span class="tm">{t}</span>'

def tl(items, accent=None):
    out = []
    for it in items:
        tag = f'<span class="tag">{it[3]}</span>' if len(it) > 3 else ""
        out.append(f'<li><span class="ic">{icon(guess_icon(it[1]))}</span>{tl_when(it[0])}<div><h3 class="h4">{it[1]}</h3><p>{it[2]}</p>{tag}</div></li>')
    return '<ol class="timeline">' + "".join(out) + "</ol>"

def info(rows):
    return '<dl class="info">' + "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows) + "</dl>"

def cards(items, cls="", accent=None, icons=None):
    out = []
    for n, it in enumerate(items):
        k, title, body = it[0], it[1], it[2]
        extra = "<ul>" + "".join(f"<li>{x}</li>" for x in it[3]) + "</ul>" if len(it) > 3 else ""
        ic = f'<span class="ci">{icon(icons[n])}</span>' if icons else ""
        out.append(f'<article class="card top">{ic}<span class="k">{k}</span><h3>{title}</h3><p>{body}</p>{extra}</article>')
    return f'<div class="cards {cls}">' + "".join(out) + "</div>"

OBJ = {
    "gala": [("Is this the Ghana Independence dinner and dance in London?", "Yes. The Royal Jubilee Gala is the black tie and Kente dinner dance on the eve of Ghana Independence Day: a Ghanaian inspired dinner, a live band playing highlife and Afrobeats, the dance floor until the last dance, and the midnight toast as 6 March 2027 begins."),
             ("What is included?", inc_sentence("gala")),
             ("What do I wear?", "Royalty Kente or Black Tie Gala. This is a ball. <a href=\"dress-code.html\">What to wear</a>"),
             ("Can I book a table for my group?", "Yes. Parties of ten are seated together at the long royal banqueting tables: 10 x GBP 275 = GBP 2,750. Choose Royal party of 10 when you book.")],
    "ghanaday": [("Where can I celebrate Ghana Independence Day in London?", "At the Ghana Day Festival, Banking Hall, 14 Cornhill, on Saturday 6 March 2027 from 11:00 to 18:00. Seventy years to the day since 6 March 1957, with a DJ, dancing, forty Ghanaian stands and the whole community in one hall."),
                 ("Is there dancing?", "All day. The DJ plays highlife, hiplife and Afrobeats from 11:00, and the dance circle is open to every age. Come and go with your wristband."),
                 ("What is included?", inc_sentence("ghanaday")),
                 ("Can I join the games?", "Yes. Entry is included with your ticket. Sign up at the welcome desk on the day."),
                 ("Can we come as a team?", "Yes. Quiz teams are up to six: 6 x GBP 50 = GBP 300. Choose Quiz team of 6 when you book.")],
    "sunday": [("Is there a Mothers Day event in London for African women?", "Yes. Women of the Motherland is a Mothering Sunday afternoon tea on Sunday 7 March 2027 at Banking Hall, for every woman of African heritage and her family. Mothering Sunday falls on 7 March in 2027."),
               ("Will there be talks or masterclasses?", "Not yet confirmed. We are shaping the sessions with our guests. Tell us what you would want to be part of through the <a href=\"women-of-the-motherland.html#sessions\">register your interest form</a>, and we announce the programme once it is confirmed."),
               ("What is included?", inc_sentence("sunday")),
               ("Can I give it as a gift?", "Yes. Tick This is a gift when you book and tell us whose name goes on the golden ticket. A Mothering Sunday gift she will remember."),
               ("Can we sit together as a family?", "Yes. Family tables seat five: 5 x GBP 150 = GBP 750. Choose Family table of 5 when you book.")],
}
OBJ_ALL = [("Will it really happen?", "Yes. All three days are at Banking Hall, 14 Cornhill, in the City of London, moments from the Bank of England. If we ever cancel, every ticket is refunded in full within 14 days. It is in our terms."), ("Who is behind it?", "The team that produced the opening of the Ghana Passport Office in Aldgate East. <a href=\"index.html#proof\">Watch the film</a>."), ("Is my payment safe?", "Yes. Card, Apple Pay or Google Pay through a secure checkout, or bank transfer. No booking fees. Your golden ticket arrives by email the moment you pay."), ("Are drinks included?", "Gala: the sobolo welcome, soft drinks and water all evening. Sunday: tea, coffee and soft drinks. Saturday: drinks are sold by card at the bar. No ticket includes alcohol, and the bar serves by card on every day."),
           ("Is the programme confirmed?", "The programme shown is the plan we are building to. Performers, speakers and timings are announced as each one is contracted, and every booked guest hears first."),
           ("Can you cater for dietary needs?", "Yes. Tell us when you book. Vegetarian, halal and allergy needs are planned with the caterer for the Gala and Sunday."),
           ("Can I transfer my ticket?", "Yes, at no extra cost. Email us the name of your guest before 17:00 on the day before the event. All sales are final and tickets cannot be refunded."),
           ("Can I pay by bank transfer?", "Yes. Choose bank transfer when you book and we send our account details with your booking reference."),
           ("Who is it for?", "All three days welcome guests aged 5 and over. Under 18s must be with an adult at all times, and every guest, adult or child, holds a ticket. We have no space for high chairs, pushchairs or buggies, so children under 5, including babies in arms, cannot be admitted."),
           ("Where is the venue?", "Banking Hall, 14 Cornhill, in the City of London, moments from the Bank of England. Directions and access details come with your tickets.")]

TRUST = ('<ul class="trust"><li><b>Full refund if we cancel</b><span>Written into our terms</span></li>'
         '<li><b>Transferable</b><span>If you cannot come, send a friend</span></li>'
         '<li><b>No booking fees</b><span>What you see is what you pay</span></li>'
         '<li><b>Golden ticket by email</b><span>The moment you pay</span></li></ul>')

def objections(day):
    return '<div class="obj"><span class="eyebrow">Before you book</span>' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in OBJ_ALL[:2] + OBJ[day] + [OBJ_ALL[4]]) + '<a class="obj-more" href="faq.html">Every other question</a></div>'

def sig_film(eyebrow="Our signature", title="We have done this before.", lead="Dignitaries in Kente and gold. A live saxophone. Every guest looked after.", cta=("Book now", "tickets.html", "pick"), band="dc-dark", sid="proof"):
    return f'''<section class="band {band} proof proof-xl" id="{sid}"><div class="wrap proof-wide">
  <div class="proof-head"><div class="stack"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2></div><p class="lead">{lead}</p></div>
  <figure class="film film-xl" data-film><video src="images/film/passport-office.mp4" poster="images/film/passport-office.jpg" muted loop playsinline preload="none" aria-label="Highlights from the opening of the Ghana Passport Office in Aldgate East"></video>
  <button class="film-sound" type="button" data-film-sound aria-pressed="false">Sound on</button>
  <figcaption><b>Our signature.</b> The opening of the Ghana Passport Office in Aldgate East, produced by the Ghana at 70 UK team.</figcaption></figure>
  <div class="proof-foot">
</div>
</div></section>
'''

def value_band(day, ph, eyebrow, title, lead, quote, items, price, unit, group, extra="", inset=""):
    """The value stack: what the ticket gives, one price, one way in."""
    lis = "".join(f'<li>{x}</li>' for x in items)
    gq, glab, gwork = group
    return f'''<section class="band ivory vb" id="included"><div class="wrap vb-in">
  <div class="vb-art">{photo(ph[0], ph[1], "ph vb-ph", ph[2], "(max-width:900px) 100vw, 46vw")}{inset}<p class="vb-quote">{quote}</p></div>
  <div class="vb-copy">
    <span class="eyebrow">{eyebrow}</span><h2>{title}</h2><p class="lead">{lead}</p>
    <div class="vb-card">
      <span class="vb-k">What your ticket includes</span>
      <ol class="vb-list">{lis}</ol>
      <p class="not-inc">{NOT_INC.get(day, "")}</p>
      <div class="vb-price"><b>GBP {price}</b><span>{unit}</span></div>
      {extra}
      <p class="left" data-left="{day}" hidden></p>
      <div class="vb-acts"><a class="btn gold" href="#book" data-pay="{day}">Book now</a><a class="btn line-dark" href="gallery.html#g-{ {"gala": "gala", "ghanaday": "ghanaday", "sunday": "sunday"}.get(day, "gala") }">See the gallery</a></div>
      <p class="vb-work">{gwork}</p>
      <p class="where"><b>Where</b> {VENUE_LINE}</p>
      <p class="reassure">On sale now · No booking fees added · All sales final · Transferable tickets</p>
    </div>
  </div>
</div></section>'''

def book_band(day, title, line, ticket, extra=""):
    price = {"gala": 275, "ghanaday": 50, "sunday": 150}[day]
    group = {"gala": (10, "Book a royal party of 10"), "ghanaday": (6, "Book a quiz team of 6"), "sunday": (5, "Book a family table of 5")}[day]
    return f'''<section class="band emerald" id="book"><div class="wrap bk-grid">
  <div class="bk-head stack"><span class="eyebrow">Book</span><h2>{title}</h2><p class="lead">{line}</p></div>
  <div class="bk-left">{ticket}{TRUST}</div>
  <div class="rsvp" data-rsvp>
  <div class="rsvp-back" aria-hidden="true"></div>
  <div class="rsvp-flap" aria-hidden="true"><span class="rsvp-seal">{wax_seal("rv" + day)}</span></div>
  <div class="book-panel rsvp-card">
    <span class="rsvp-kicker">R · S · V · P</span>
    <span class="rsvp-line">The honour of your presence is requested at</span>
    <span class="rsvp-event">{ {"gala": "The Royal Jubilee Gala", "ghanaday": "The Ghana Day Festival", "sunday": "Women of the Motherland"}[day] }</span>
    <span class="rsvp-date">{ {"gala": "Friday 5 March 2027 · 18:30 to 00:30", "ghanaday": "Saturday 6 March 2027 · 11:00 to 18:00", "sunday": "Sunday 7 March 2027 · 11:00 to 18:30"}[day] } · Banking Hall</span>
    <p class="bp-valid">This ticket is for this event, on this date, only. The other two events are separate, each with its own ticket, or all three with the Weekend Pass.</p>
    <span class="rsvp-rule" aria-hidden="true"></span>
    <span class="eyebrow">Your places</span>
    <p class="bp-price">GBP {price} <span>{"per guest, or GBP 250 early bird while early bird tickets last" if day == "gala" else "per guest"}. No booking fees added. { {"gala": "Alcohol is not included, the bar serves by card", "ghanaday": "Food and drink are not included. The bar sells drinks and snacks, card only", "sunday": "Afternoon tea, tea, coffee and soft drinks included. Alcohol is not included"}[day] }</span></p>
    <p class="working">Two guests: 2 x GBP {price} = GBP {2 * price:,}</p>
    {extra}
    <p class="left" data-left="{day}" hidden></p><p class="left" data-booked hidden></p><p class="left" data-deadline hidden></p>
    <a class="btn gold bp-btn" href="#book" data-pay="{day}">Book now</a>
    <a class="btn line bp-btn" href="#book" data-pay="{day}" data-qty="{group[0]}">{group[1]}</a>
    <ol class="bp-steps"><li>Choose your guests</li><li>Add your details</li><li>Pay, then receive your golden tickets by email</li></ol>
    <p class="reassure c">Card, Apple Pay, Google Pay or bank transfer<br>All sales final · Transferable tickets</p>
  </div>
  <div class="rsvp-pocket" aria-hidden="true"></div>
  </div>
  <div class="bk-obj">{objections(day)}</div>
</div></section>'''



ADDONS = cards([
    ("Private parties", "Your own celebration within the venue", "A birthday, an anniversary, a reunion or a company night. Reserve a private room or a hosted area and celebrate in your own space, with the weekend all around you."),
    ("Royal tables", "Personalised for your party", "Your family or company name on your section of the long table, personalised place cards, Kente table runners in your colours and a dedicated host."),
    ("Celebration packages", "Cake, a toast and surprises", "A celebration cake, a toast at your table, a table announcement or a song from the band, arranged quietly in advance."),
    ("Portrait packages", "Prints, frames and family albums", "Extended sittings at the royal portrait studio and the family portrait studio, with framed prints delivered to your door."),
    ("Branded experiences", "For companies and partners", "Hospitality suites, branded tables, gift bags and client evenings designed around your brand."),
    ("Kente and gold", "Dress for the occasion", "Kente sashes, stoles and accessories from our exhibitors, reserved for collection on the night."),
], icons=["door", "people", "glass", "camera", "star", "cloth"])

def kband(seed, cls="kband", palette=""):
    pal = f' data-palette="{palette}"' if palette else ""
    return f'<canvas class="{cls}" data-kente="{seed}"{pal} aria-hidden="true"></canvas>'

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for f in ("site.css", "site.js"):
        with open(os.path.join(SRC, f)) as a, open(os.path.join(OUT, f), "w") as b:
            b.write(webp(a.read()) if f.endswith(".css") else a.read())
    def _skip_jpg(d, names):
        return [n for n in names if n.endswith(".jpg") and n != "og.jpg" and os.path.exists(os.path.join(d, n[:-4] + ".webp"))]
    shutil.copytree(os.path.join(SRC, "images"), os.path.join(OUT, "images"), ignore=_skip_jpg)


    # ================= INDEX =================
    page("index", "Ghana at 70 UK | Ghana Independence Day 2027 Celebration in London", "Ghana at 70 UK, London, 5 to 7 March 2027: The Royal Jubilee Gala, the Ghana Day Festival on Independence Day and Women of the Motherland. Tickets on sale.", f'''
<section class="hero">
  {kband(11, "drape l")}{kband(29, "drape r")}
  {ghana_map("map")}
  <canvas data-weave aria-hidden="true"></canvas>
  {skyline("skyline hero-sky", "skh")}
  <div class="wrap">
    <div class="arch rise">
      <div class="arch-inner">
        <span class="eyebrow">Ghana Independence Day 2027 in London</span>
        <span class="script">The Platinum Jubilee of</span>
        <h1 class="hero-title">Ghana at<span class="sr-only"> 70</span></h1>
        {LOCKUP}
        <div class="divider c"><i></i></div>
        <p class="hero-sub"><b class="hero-sale">Where will you be when Ghana turns 70?</b> 5 to 7 March 2027 · Banking Hall, London. Three events, each with its own ticket. Tickets on sale now.</p>
        <ol class="hero-events"><li><a href="royal-gala.html"><b>Friday 5 March</b><span>The Royal Jubilee Gala</span><em>GBP 275</em></a></li><li><a href="ghana-day.html"><b>Saturday 6 March</b><span>Ghana Day Festival</span><em>GBP 50</em></a></li><li><a href="women-of-the-motherland.html"><b>Sunday 7 March</b><span>Women of the Motherland</span><em>GBP 150</em></a></li></ol>
        <span class="eyebrow"><b>Friday 5 March 2027</b> to <b>Sunday 7 March 2027</b> · London</span>
        <div class="btn-row" style="justify-content:center"><a class="btn gold" href="tickets.html" data-pay="pick">Take your seat at the Jubilee</a><a class="btn line" href="#days">Discover the three events</a></div>
      </div>
      {kband(5, "arch-band")}
    </div>
    <div class="hero-below">
      <div class="hero-days rise d2">
        <a href="royal-gala.html"><span>Friday 5 March</span><strong>The Royal Jubilee Gala</strong></a>
        <a href="ghana-day.html"><span>Saturday 6 March</span><strong>Ghana Day Festival</strong></a>
        <a href="women-of-the-motherland.html"><span>Sunday 7 March</span><strong>Women of the Motherland</strong></a>
      </div>
      <span class="eyebrow">Until Independence Day</span>{countdown()}
      <p class="left c" data-booked hidden></p><p class="left c" data-deadline hidden></p>
    </div>
  </div>
</section>
{kband(17)}
<section class="band ivory arrive" id="arrive"><div class="wrap arrive-in">
  {photo("look/a6", "A king in emerald, blue and gold Kente wrapped over one shoulder with a gold armlet, hand in hand with a queen in an emerald beaded corset and Kente mermaid gown, before a columned City of London facade", "arrive-ph", "50% 50%", "(max-width:900px) 92vw, 55vw")}
  <div class="arrive-copy"><span class="eyebrow">Friday 5 March 2027 · The Royal Jubilee Gala</span><h2>Arrive as royalty.</h2><div class="divider"><i></i></div>
    <p class="lead">Kente, gold and drums beneath the columns of the City.</p>
    <div class="btn-row"><a class="btn gold" href="tickets.html" data-pay="pick">Take your seat at the Jubilee</a><a class="btn line-dark" href="dress-code.html">What to wear</a></div></div>
</div></section>

{sig_film()}
<section class="band manifesto" id="manifesto"><div class="wrap">
  <div class="mf-frame">
    <svg class="cn tl" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M2 24V8a6 6 0 0 1 6-6h16"/><path d="M6 24V12a6 6 0 0 1 6-6h12"/><path d="M9 9c3 0 4 2 4 4s-2 3-3.5 2S9 12 11 11"/></svg><svg class="cn tr" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M2 24V8a6 6 0 0 1 6-6h16"/><path d="M6 24V12a6 6 0 0 1 6-6h12"/><path d="M9 9c3 0 4 2 4 4s-2 3-3.5 2S9 12 11 11"/></svg><svg class="cn bl" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M2 24V8a6 6 0 0 1 6-6h16"/><path d="M6 24V12a6 6 0 0 1 6-6h12"/><path d="M9 9c3 0 4 2 4 4s-2 3-3.5 2S9 12 11 11"/></svg><svg class="cn br" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M2 24V8a6 6 0 0 1 6-6h16"/><path d="M6 24V12a6 6 0 0 1 6-6h12"/><path d="M9 9c3 0 4 2 4 4s-2 3-3.5 2S9 12 11 11"/></svg>
    <span class="eyebrow">Our Motherland. Our People. Our Story.</span>
    <p class="mf-script">Seventy years</p>
    <div class="divider c"><i></i></div>
    <p class="mf-line">We are the children of those who left home with a suitcase and courage.</p>
    <p class="mf-gold">And we have never forgotten home.</p>
    <p class="mf-line">This celebration is for you.</p>
    <div class="btn-row" style="justify-content:center"><a class="btn gold" href="tickets.html" data-pay="pick">Take your seat at the Jubilee</a><a class="btn line" href="about.html#our-story">Read our story</a></div>
  </div>
</div></section>
{kband(23)}


<section class="band white" id="days">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Choose your event and book</span><h2>Where will you be when Ghana turns 70?</h2><p class="lead">On Friday night at Banking Hall, the drums will welcome you in. There will be Kente across the room, a Ghanaian inspired dinner and live highlife. At midnight, we will raise a glass together as Independence Day begins.</p><p class="lead">That is how the weekend starts. Bring the whole family on Saturday, then make Sunday an afternoon for the woman who has always brought yours together.</p><p class="lead">Each event has its own ticket. The Weekend Pass covers all three for GBP 435.</p></div>
    {DAYS}
  </div>
</section>
{partners_wall()}

<section class="bh-full" id="banking-hall">
  <img src="images/venue/bh-gala-night-1600.jpg" srcset="images/venue/bh-gala-night-800.jpg 800w, images/venue/bh-gala-night-1600.jpg 1600w" sizes="100vw" alt="Banking Hall set for a gala dinner, candlelit round tables beneath the marble columns" loading="lazy">
  <div class="bh-full-in wrap"><div class="bh-full-copy"><span class="eyebrow">Friday 5 to Sunday 7 March 2027 · The setting</span><h2>Banking Hall, City of London.</h2>
    <p class="lead">Grade II listed marble, moments from the Bank of England. For one weekend, it belongs to Ghana.</p>
    <div class="btn-row"><a class="btn gold" href="royal-gala.html#venue">See the hall</a></div></div></div>
</section>

<section class="band emerald satin-frame" id="tickets">
  <div class="wrap">
    <div class="section-head">{wax_seal("tk","wax wax-head")}<span class="eyebrow">Golden tickets</span><h2>Your seat at the seventieth.</h2><p class="lead">The Royal Jubilee Gala GBP 275, early bird GBP 250. Ghana Day Festival GBP 50. Women of the Motherland GBP 150. All three days with the Weekend Pass: GBP 435.</p></div>
    <div class="tickets">{T_GALA}{T_DAY}{T_SUN}</div>
    <p class="working" style="color:var(--gold-hi);text-align:center;margin-top:28px"><b>The Weekend Pass: GBP 435.</b> One entry to each of the three separate events, for one guest. Bought separately at full price: GBP 275 + GBP 50 + GBP 150 = GBP 475. You save GBP 475 less GBP 435 = GBP 40</p>
    <div class="btn-row" style="margin-top:28px;justify-content:center"><a class="btn gold" href="tickets.html" data-pay="weekend">Book the Weekend Pass, save GBP 40</a><a class="btn line" href="tickets.html" data-pay="pick">Choose one day</a></div>
  </div>
</section>



<section class="band emerald satin-frame" id="royal-name"><div class="wrap split mid">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Your royal invitation</span><h2>What is your royal name?</h2><p class="lead">In Ghana, the day you are born gives you your name. Three taps and we write your royal invitation.</p></div>
    <form class="rn-form" data-rn novalidate>
      <ol class="rn-steps" aria-hidden="true"><li data-rn-step="1"><i>1</i>Name</li><li data-rn-step="2"><i>2</i>Birthday</li><li data-rn-step="3"><i>3</i>Reveal</li></ol>
      <div class="field"><label for="rn-name"><b class="rn-n">1</b>Your first name</label><input id="rn-name" name="n" autocomplete="given-name" maxlength="24" placeholder="For example, Abena"></div>
      <fieldset class="field rn-dob"><legend><b class="rn-n">2</b>Your birthday</legend>
        <div class="rn-dob-row">
          <select id="rn-dd" aria-label="Day of the month" autocomplete="bday-day"><option value="">Day</option>{"".join(f'<option value="{i}">{i}</option>' for i in range(1, 32))}</select>
          <select id="rn-mm" aria-label="Month" autocomplete="bday-month"><option value="">Month</option>{"".join(f'<option value="{i+1}">{m}</option>' for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"]))}</select>
          <select id="rn-yy" aria-label="Year" autocomplete="bday-year"><option value="">Year</option>{"".join(f'<option value="{y}">{y}</option>' for y in range(2026, 1919, -1))}</select>
        </div>
        <p class="rn-or">Or tap the day you were born</p>
        <div class="rn-days" role="group" aria-label="The day of the week you were born">{"".join(f'<button type="button" class="rn-day" data-rn-day="{i}" aria-pressed="false">{d}</button>' for i, d in [(1,"Mon"),(2,"Tue"),(3,"Wed"),(4,"Thu"),(5,"Fri"),(6,"Sat"),(0,"Sun")])}</div>
      </fieldset>
      <fieldset class="field rn-kq"><legend><b class="rn-n">3</b>Invite me as</legend><label class="check"><input type="radio" name="k" value="king"><span>A king</span></label><label class="check"><input type="radio" name="k" value="queen" checked><span>A queen</span></label></fieldset>
      <div class="rn-reveal" data-rn-reveal hidden><span class="rn-reveal-k" data-rn-rk></span><b data-rn-rn></b><span class="rn-reveal-m" data-rn-rm></span></div>
      <p class="rn-err" data-rn-err role="alert"></p>
      <button class="btn gold" type="submit">Write my invitation</button>
      <p class="muted rn-note">Your birthday stays on your device. It is never sent to us.</p>
    </form>
  </div>
  <div class="rn-preview" aria-live="polite"><div class="rn-gh" style="--ghana:{GH_CLIP}">
    <div class="rn-gh-shadow"></div><div class="paper"></div>{ghana_map("outline", "#B8891F", 3)}<span class="rn-seal" aria-hidden="true">{wax_seal("rn")}</span>
    <div class="content">
      <span class="rn-pc-s">Ghana at 70 UK</span>
      <span class="rn-star" aria-hidden="true">{star("#B8891F", "#B8891F", 0)}</span>
      <span class="rn-pc-t" data-rnp-t>Her Royal Highness</span>
      <span class="rn-pc-n" data-rnp-n>Nana Yaa</span>
      <span class="rn-pc-f" data-rnp-f>Asantewaa</span>
      <span class="rn-pc-s" data-rnp-b>born on a Thursday</span>
      <span class="rn-pc-l"></span>
      <span class="rn-pc-s">is invited to</span>
      <span class="rn-pc-g">The Royal Jubilee Gala</span><span class="rn-pc-d">Friday 5 March 2027<br>Banking Hall · London</span>
    </div></div>
    <p class="rn-says">Your invitation writes itself as you type, in the shape of home.</p></div>
  <div class="rn-out" data-rn-out hidden>
    <canvas class="rn-card" width="1080" height="1350" data-gh="{open(os.path.join(SRC, "ghana_clip.txt")).read().strip()}" aria-label="Your royal invitation" role="img"></canvas>
    <p class="rn-says" data-rn-says></p>
    <div class="btn-row"><a class="btn gold" href="royal-gala.html#book" data-pay="gala">Take my seat</a><a class="btn line" data-rn-share href="#" target="_blank" rel="noopener">Share on WhatsApp</a><button class="btn line" type="button" data-rn-save>Save the image</button></div>
  </div>
</div></section>

<section class="band white gal-tease" id="see-yourself"><div class="wrap">
  <div class="sy-head"><div class="stack"><span class="eyebrow">Celebrate with us</span><h2>See yourself there.</h2><p class="lead">Picture the moment you walk in: the drums, the gold, a familiar face across the hall. Come on your own, with your love, your sisters or the whole family. Every generation has a seat.</p></div>
    <div class="sy-nav"><button class="sy-btn" type="button" data-sy="-1" aria-label="Previous photos">&#8249;</button><button class="sy-btn" type="button" data-sy="1" aria-label="Next photos">&#8250;</button></div></div>
  <ul class="sy-track" data-sy-track tabindex="0" aria-label="Gallery photos">{"".join(f'<li class="sy-card">{photo(k, alt, "ph sy-ph", pos, "(max-width:760px) 72vw, 22vw")}<span class="sy-cap">{cap}</span></li>' for k, alt, pos, cap in [
    ("y-single-man", "A young gentleman in a black smock with a Kente stole, smiling", "50% 25%", "Come as you are"),
    ("g-gala-guests", "Guests in Kente and black tie laughing together at the Gala", "50% 30%", "Bring the girls"),
    ("g-elder-kente", "An elder gentleman in full Kente cloth in a marble hall", "50% 25%", "Honour the elders"),
    ("n-young-woman", "A young woman in a Kente gown smiling at a Gala table", "50% 25%", "First Gala"),
    ("r-three-women", "Three women in Kente and lace gowns, glasses raised", "50% 30%", "The aunties"),
    ("n-couple-dance", "A young couple laughing on the dance floor, she in Kente, he in black tie", "50% 30%", "Date night"),
    ("n-mother-daughter", "A mother and daughter in Kente embracing and laughing", "50% 30%", "Bring your mother"),
    ("gal-velvet", "A gentleman in an emerald velvet dinner jacket with a Kente stole", "50% 20%", "Black tie, with Kente"),
    ("g-table-queens", "A table of women of every age in Kente and black gowns", "50% 30%", "The whole table"),
    ("gal-kente-couple", "An older couple in matching gold Kente in a marble hall", "50% 25%", "Still dancing"),
    ("r-toast-group", "Guests of every age in Kente and suits raising their glasses", "50% 30%", "Every generation"),
    ("r-hall-gathering", "Guests in Kente, gold and black tie gathered in the banking hall", "50% 30%", "One hall"),
    ("g-colour-line", "Women in bright Ankara print dresses lined up together", "50% 30%", "Ghana Day in print")])}</ul>
  <div class="btn-row" style="justify-content:center"><a class="btn line-dark" href="gallery.html">Open the gallery</a><a class="btn gold" href="tickets.html" data-pay="pick">Book now</a></div>
</div></section>
<section class="band ivory" id="register"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">On sale now</span><h2>Pick your day. Book your seats.</h2><p class="lead">Every ticket is on sale today, on this website only. No booking fees added.</p></div>
  <div class="btn-row" style="justify-content:center"><a class="btn gold" href="royal-gala.html#book" data-pay="gala">Book the Gala</a><a class="btn gold" href="ghana-day.html#book" data-pay="ghanaday">Book Ghana Day</a><a class="btn gold" href="women-of-the-motherland.html#book" data-pay="sunday">Book afternoon tea</a><a class="btn line-dark" href="tickets.html" data-pay="pick">All tickets and the Weekend Pass</a></div>
</div></section>
''')

    # ================= ROYAL GALA =================
    page("royal-gala", "The Royal Jubilee Gala | Ghana Independence Gala Dinner London 2027", "The Royal Jubilee Gala, Friday 5 March 2027, Banking Hall, London. Royal drums, a Ghanaian inspired dinner, live highlife and a midnight toast to Independence Day.",
         page_head("Friday 5 March 2027 · 18:30 to 00:30", "The Royal Jubilee Gala", "Royal drums, a Ghanaian inspired dinner, live highlife and a midnight toast.", "black gala-hero", "adinkrahene",
                   '<div class="chips"><span class="chip">Royalty Kente or Black Tie</span><span class="chip">Banking Hall, moments from the Bank of England</span><span class="chip">250 seats</span><span class="chip">GBP 275 · early bird GBP 250</span><span class="chip">Long royal banqueting tables</span><span class="chip">A separate event, with its own ticket</span></div>', "You are cordially invited to", day="royal-gala") + f'''
{kband(3)}

<section class="band emerald bh" id="venue"><div class="wrap">
  <div class="bh-head"><div class="stack"><span class="eyebrow">The setting</span><h2>Banking Hall, City of London.</h2></div>
    <p class="lead">A Grade II listed Art Deco banking hall on Cornhill, moments from the Bank of England and the Royal Exchange. For one night, a royal palace.</p></div>
  <figure class="bh-ph bh-hero"><img src="images/venue/bh-dressed-1600.jpg" srcset="images/venue/bh-dressed-800.jpg 800w, images/venue/bh-dressed-1600.jpg 1600w" sizes="100vw" alt="Banking Hall dressed for the Royal Jubilee Gala, with Kente runners, gold candelabra and Black Star banners" loading="lazy"><figcaption>Banking Hall dressed in Kente and gold for the Royal Jubilee Gala.</figcaption></figure>
  <div class="bh-grid">
    <figure class="bh-ph"><img src="images/venue/bh-entrance-1600.jpg" srcset="images/venue/bh-entrance-800.jpg 800w, images/venue/bh-entrance-1600.jpg 1600w" sizes="(max-width:760px) 100vw, 50vw" alt="The arched stone entrance of Banking Hall on Cornhill" loading="lazy"></figure>
    <figure class="bh-ph"><img src="images/venue/bh-staircase-1600.jpg" srcset="images/venue/bh-staircase-800.jpg 800w, images/venue/bh-staircase-1600.jpg 1600w" sizes="(max-width:760px) 100vw, 50vw" alt="The sweeping marble staircase at Banking Hall, with the black horse mosaic set into the floor" loading="lazy"></figure>
  </div>
  <div class="bh-facts">
    <div><span class="k">Address</span><b>14 Cornhill, London EC3V 3ND</b></div>
    <div><span class="k">Heritage</span><b>Grade II listed 1930s Art Deco, once a Lloyds Bank headquarters</b></div>
    <div><span class="k">Seats</span><b>250 only, long royal tables</b></div>
    <div><span class="k">Nearest station</span><b>Bank, about two minutes on foot</b></div>
  </div>
  <div class="bh-stations"><span class="k">Getting there</span><p><b>Bank</b> Central, Northern, Waterloo and City lines and the DLR, about two minutes on foot. <b>Monument</b> District and Circle lines. <b>Mainline rail</b> Cannon Street, Fenchurch Street and Liverpool Street, with the Elizabeth line at Liverpool Street.</p></div>
  <div class="bh-strip-head"><span class="eyebrow">Dressed for a night of royals</span></div>
  <div class="bh-marquee" aria-label="Banking Hall gallery"><div class="bh-track"><figure class="bh-shot"><img src="images/venue/bh-empty-hall-1600.jpg" srcset="images/venue/bh-empty-hall-800.jpg 800w, images/venue/bh-empty-hall-1600.jpg 1600w" sizes="86vw" alt="The Main Hall at Banking Hall: fluted columns, a coffered skylight ceiling and a chequered marble floor" loading="lazy"><figcaption>The Main Hall</figcaption></figure><figure class="bh-shot"><img src="images/venue/bh-gold-table-1600.jpg" srcset="images/venue/bh-gold-table-800.jpg 800w, images/venue/bh-gold-table-1600.jpg 1600w" sizes="86vw" alt="A table laid in black and gold, with gold chargers and etched crystal" loading="lazy"><figcaption>Black and gold</figcaption></figure><figure class="bh-shot"><img src="images/venue/banking-hall-hall-1600.jpg" srcset="images/venue/banking-hall-hall-800.jpg 800w, images/venue/banking-hall-hall-1600.jpg 1600w" sizes="86vw" alt="Long tables down the length of the Main Hall towards the staircase" loading="lazy"><figcaption>Down the hall</figcaption></figure><figure class="bh-shot"><img src="images/venue/banking-hall-table-1600.jpg" srcset="images/venue/banking-hall-table-800.jpg 800w, images/venue/banking-hall-table-1600.jpg 1600w" sizes="86vw" alt="Candelabra on the tables beside the staircase" loading="lazy"><figcaption>At the staircase</figcaption></figure><figure aria-hidden="true" class="bh-shot"><img src="images/venue/bh-empty-hall-1600.jpg" srcset="images/venue/bh-empty-hall-800.jpg 800w, images/venue/bh-empty-hall-1600.jpg 1600w" sizes="86vw" data-alt="The Main Hall at Banking Hall: fluted columns, a coffered skylight ceiling and a chequered marble floor" loading="lazy" alt=""><figcaption>The Main Hall</figcaption></figure><figure aria-hidden="true" class="bh-shot"><img src="images/venue/bh-gold-table-1600.jpg" srcset="images/venue/bh-gold-table-800.jpg 800w, images/venue/bh-gold-table-1600.jpg 1600w" sizes="86vw" data-alt="A table laid in black and gold, with gold chargers and etched crystal" loading="lazy" alt=""><figcaption>Black and gold</figcaption></figure><figure aria-hidden="true" class="bh-shot"><img src="images/venue/banking-hall-hall-1600.jpg" srcset="images/venue/banking-hall-hall-800.jpg 800w, images/venue/banking-hall-hall-1600.jpg 1600w" sizes="86vw" data-alt="Long tables down the length of the Main Hall towards the staircase" loading="lazy" alt=""><figcaption>Down the hall</figcaption></figure><figure aria-hidden="true" class="bh-shot"><img src="images/venue/banking-hall-table-1600.jpg" srcset="images/venue/banking-hall-table-800.jpg 800w, images/venue/banking-hall-table-1600.jpg 1600w" sizes="86vw" data-alt="Candelabra on the tables beside the staircase" loading="lazy" alt=""><figcaption>At the staircase</figcaption></figure></div></div>
</div></section>

{value_band("gala", ("y-young-couple", "A young couple at the Gala: he in black tie, she in a Kente gown", "45% 25%"),
   "The evening", "A party of royals.",
   "Drums, banquet, dancing and midnight.",
   "For those who came before us. For those who walk beside us. For those who will follow.",
   INC["gala"],
   275, "per guest, or GBP 250 early bird while early bird tickets last", (10, "Book a royal party of 10", "Party of ten: 10 x GBP 275 = GBP 2,750, or 10 x GBP 250 = GBP 2,500 while early bird tickets last"), "")}


<section class="band ink rc" id="red-carpet"><div class="wrap rc-in">
  <div class="section-head center"><span class="eyebrow">Friday 5 March · from 18:30</span><h2>The red carpet.</h2><div class="divider"><i></i></div>
  <p class="lead">Arrive to Fontomfrom drums and the flash of cameras. Every guest is photographed against the Platinum Jubilee wall, gold on Motherland green, and your portrait is delivered within seven days.</p></div>
  {photo("rc-wall", "The Ghana Platinum Jubilee media wall, the gold Akoko Nan seal repeated on Motherland green, above a red carpet", "ph rc-fig", "50% 40%", "(max-width:760px) 100vw, 1200px")}
  <p class="rc-note">Press are welcome on the carpet from 18:30. <a href="press.html">Request accreditation</a></p>
</div></section>
<section class="band ivory feast" id="banquet"><div class="wrap feast-in">
  <figure class="feast-ph">{photo("venue/gala-feast", "A Ghanaian inspired dinner plate on a gold charger at a candlelit table", "ph feast-img", "50% 55%", "(max-width:900px) 92vw, 52vw")}<figcaption>The menu is revealed on the night.</figcaption></figure>
  <div class="feast-copy">
    <span class="eyebrow">20:10 · The Royal Banquet</span>
    <h2>A feast fit for royalty.</h2>
    <div class="divider"><i></i></div>
    <p class="lead">Three courses of Ghana, plated for royalty and carried to every table in procession, to the beat of the drums.</p>
    <ol class="feast-list">
      <li><b>I</b><span>A welcome of sobolo as you arrive</span></li>
      <li><b>II</b><span>Three courses, served to the whole hall at once</span></li>
      <li><b>III</b><span>Every dietary need asked for when you book</span></li>
    </ol>
    <div class="btn-row"><a class="btn gold" href="#book" data-pay="gala">Take your royal seat</a></div>
  </div>
</div></section>
<section class="bh-full" id="midnight-toast">
  <img src="images/venue/gala-toast-1600.jpg" srcset="images/venue/gala-toast-800.jpg 800w, images/venue/gala-toast-1600.jpg 1600w" sizes="100vw" alt="Kings in traditional Kente cloth worn toga style and queens in Kente gowns, at long candlelit tables beneath marble columns, every glass raised for the midnight toast" loading="lazy">
  <div class="bh-full-in wrap"><div class="bh-full-copy"><span class="eyebrow">Saturday 6 March 2027 · 00:00</span><h2>At midnight, the hall rises.</h2>
    <p class="lead">The moment Ghana became independent. Every glass raised in sobolo.</p>
    <div class="btn-row"><a class="btn gold" href="tickets.html" data-pay="gala">Take your seat at the Jubilee</a></div></div></div>
</section>
<section class="band ivory arrive" id="dress"><div class="wrap arrive-in rev">
  {photo("g-black-tie-group", "Young and older guests together at the Gala, men in black tie and Kente, women in Kente and black gowns", "arrive-ph", "50% 35%", "(max-width:900px) 92vw, 55vw")}
  <div class="arrive-copy"><span class="eyebrow">Dress as royalty</span><h2>Kente, gold and black tie.</h2><div class="divider"><i></i></div>
    <p class="lead">Royalty Kente or Black Tie. This is a ball.</p>
    <div class="btn-row"><a class="btn gold" href="dress-code.html">See the dress code</a><a class="btn line-dark" href="dress-code.html#kente">How to wear Kente</a></div></div>
</div></section>
<section class="band emerald">
  <div class="wrap split">
    <div class="sticky-date"><span class="eyebrow">Order of the evening</span>
      <div class="bigdate"><b>5</b><span>March<br>2027</span></div>
      <p class="bd-day">Friday · 18:30 to 00:30</p>
      <h2>From royal drums to the midnight toast.</h2>
      <p class="bd-note">Royalty Kente or Black Tie Gala</p>
    </div>
    {tl([
        ("18:30", "The Royal Arrival", "Fontomfrom drums, a red carpet and a gold reception.", "Red carpet"),
        ("19:00", "The royal portrait", "Your gala photograph on the royal chair.", "Photography"),
        ("19:45", "The drums begin", "Drummers lead every guest to table in procession. Seated by 20:00."),
        ("20:10", "The Royal Banquet", "The drums call the first course into the hall, in procession."),
        ("20:40", "Kete and Adowa", "The royal music and dance of the Asante, between the courses."),
        ("22:00", "The tribute to 1957", "Dessert, and a short tribute to those who won independence."),
        ("22:20", "Highlife, live", "The band takes the stage.", "Dancing"),
        ("23:15", "Afrobeats and everything in between", "The royal dance floor. The last dance at 23:30."),
        ("23:45", "The hall rises", "Glasses charged, the whole hall gathered for midnight."),
        ("00:00", "The midnight toast", "The anthem, the countdown and one toast as Independence Day begins."),
        ("00:15", "Carriages", "Goodnight, Your Majesties."),
    ])}
  </div>
</section>





{book_band("gala", "Take your royal seat.", "250 seats, one night. GBP 275, or GBP 250 early bird.", T_GALA)}
''')

    # ================= GHANA DAY =================
    page("ghana-day", "Ghana Day Festival | Ghana Independence Day London, 6 March 2027", "The Ghana Day Festival on Independence Day, Saturday 6 March 2027, London. An exhibition of companies reaching the Ghanaian diaspora, fixed 10 minute appointments with exhibitors, games, dancing and networking.",
         page_head("Saturday 6 March 2027 · 11:00 to 18:00", "Ghana Day Festival", "Independence Day, seventy years to the day. 11:00 to 18:00. Meet up to forty companies reaching the diaspora, book 10 minute appointments with the ones you choose, then play, dance and network. GBP 50.", "green", "fawohodie",
                   '<div class="chips"><span class="chip">The exhibition</span><span class="chip">10 minute appointments</span><span class="chip">DJ and dancing</span><span class="chip">Ages 5 and over</span><span class="chip">Come and go all day</span><span class="chip">GBP 50</span><span class="chip">Games included</span><span class="chip">A separate event, with its own ticket</span></div>', "Seventy years to the day", day="ghana-day") + f'''
{kband(8)}

<section class="cine" aria-label="Independence Day">{photo("g-prints-line", "Women in bold Ankara print and headwraps in a sunlit garden", "ph cine-ph", "50% 35%", "100vw")}
  <div class="cine-t"><span class="eyebrow">Saturday 6 March 2027</span><p>The day Ghana was born.<br>Come and dance like it.</p></div></section>

{value_band("ghanaday", ("j-wide-denim", "A woman in a red and gold Kente print top with wide blue jeans", "50% 30%"),
   "The day", "A whole day of Ghana, for GBP 50.",
   "Meet, network, dance and play until six.",
   "A day when a conversation can become a partnership, and an introduction can become an opportunity.",
   INC["ghanaday"],
   50, "per guest, the whole day", (6, "Book a quiz team of 6", "Quiz team: 6 x GBP 50 = GBP 300"))}


<section class="band emerald">
  <div class="wrap split">
    <div class="sticky-date"><span class="eyebrow">Order of the day</span>
      <div class="bigdate"><b>6</b><span>March<br>2027</span></div>
      <p class="bd-day">Saturday · 11:00 to 18:00</p>
      <h2>Independence Day, hour by hour.</h2>
      <p class="bd-note">Ages 5 and over · DJ and dancing · GBP 50</p>
      <div class="btn-row"><a class="btn line" href="#compete">Join the games</a></div>
    </div>
    {tl([
        ("11:00", "Doors open", "Forty exhibitors and the Ghana Games Arena open together."),
        ("11:15", "Expert talks begin", "Five talks through the day in the Talks Room: land, money, wills, pensions and business. <a href=\"#talks\">See the talks</a>", "Talks"),
        ("12:00", "The anniversary moment", "The whole hall pauses together for drumming and a reading of the declaration of independence."),
        ("12:30", "The DJ takes over", "Highlife, hiplife and Afrobeats until close. The dance floor is open all day, and the bar sells drinks and snacks, card only."),
        ("13:30", "Oware games", "Open games on the Ghana Games Arena. Everyone plays.", "Games"),
        ("14:30", "The networking hour", "Hosted introductions by interest: enterprise, creative, professional and community."),
        ("15:30", "The Big Ghana Quiz", "Teams of up to six, for the joy of knowing Ghana best.", "Games"),
        ("16:30", "The Ghana at 70 UK runway", "Fashion from our exhibitors on the runway."),
        ("17:00", "The dance circle", "Azonto, Kpanlogo and Afrobeats. Crews and solo dancers, cheered on by the whole hall.", "Games"),
        ("18:00", "Doors close", "The day ends here. There is no Saturday evening programme."),
    ])}
  </div>
</section>

<section class="band ivory story-band" id="wear">
  <div class="wrap story">
    <span class="eyebrow">What to wear on Saturday</span>
    <h2>Print and denim. Or your Black Stars shirt.</h2>
    <p class="story-open">A print top with your best jeans, Ankara from head to toe, or the Black Stars shirt you wore for every match. Saturday is for colour, comfort and dancing all day.</p>
  </div>
  <div class="wrap wear-strip">{filmstrip([
      ("j-four-friends", "Four friends in Kente print shirts and tops with jeans and white trainers", "50% 20%"),
      ("s-ankara-crop", "A young woman in a bold Ankara print crop top and skirt among palm leaves", "50% 20%"),
      ("j-green-shirt", "A gentleman in a green and Kente print shirt with blue jeans", "50% 20%"),
      ("s-print-elder", "An older woman in a print top with a black bead necklace, smiling", "50% 30%"),
      ("j-duo", "Two young women in Kente print tops and wide dark jeans", "50% 20%"),
      ("s-market-walk", "A woman in a gold Ankara print dress and wrap walking through a busy market lane", "60% 30%"),
      ("j-couple-blue", "A couple in matching Kente print with blue jeans and trainers", "50% 20%"),
      ("s-print-collar", "A young woman in a blue print top with a crisp white collar", "50% 20%")], "What to wear on Saturday", "gfs-tall")}</div>
  <div class="wrap story"><p class="story-turn">Print and denim on Saturday. The full Kente cloth waits for the Gala.<br><em><a href="dress-code.html">See the full dress code</a></em></p></div>
</section>

<section class="band ivory"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Who you will meet</span><h2>Forty stands, never more than two of a kind.</h2><p class="lead">Exhibitors will be announced from January 2027. Here is what is coming.</p></div>
  <div class="mini-cats">{"".join(f'<a class="mini" href="exhibit.html"><b>{gn}</b><span>{", ".join(c[1] for c in CATEGORIES if c[4] == gk)}</span></a>' for gk, gn, _, _ in CAT_GROUPS)}</div>
  <div class="btn-row" style="margin-top:28px"><a class="btn emerald" href="exhibit.html">See the exhibitors</a><a class="btn gold" href="exhibit.html">Exhibit on Saturday</a></div>
</div></section>

<section class="band ivory" id="talks"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">The Talks Room · from 11:15</span><h2>Five talks, between the dancing.</h2><div class="divider"><i></i></div><p class="lead">Practical answers for families with two homes. Included with your ticket. Come and go as you please.</p></div>
  <ol class="talks">
    <li><b>Land</b><span>Buying, registering and protecting land in Ghana, without the heartache.</span></li>
    <li><b>Money</b><span>Saving, sending and investing across Britain and Ghana.</span></li>
    <li><b>Wills</b><span>Wills and family property in both countries, explained plainly.</span></li>
    <li><b>Pensions</b><span>Your UK pension, and what happens if you retire home.</span></li>
    <li><b>Business</b><span>Starting, growing and trading between London and Accra.</span></li>
  </ol>
  <p class="muted c">Speakers and times will be announced on this website from January 2027.</p>
</div></section>
<section class="band white" id="compete"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Join in</span><h2>Dance, play and laugh on Independence Day.</h2><p class="lead">The dance circle, oware games and the Big Ghana Quiz come with your Ghana Day ticket. Played for the joy of it, with no prizes.</p></div>
  {info([("Dance", "Azonto, Kpanlogo and Afrobeats. Solo or crews of up to five, for the joy of it"), ("Oware", "Open games from 13:30"), ("Quiz", "Teams of up to six from 15:30")])}</div>
  {enquiry_form("compete")}
</div></section>
{book_band("ghanaday", "Be in the room on Independence Day.", "Ages 5 and over. GBP 50. Bring the people who made you.", T_DAY)}
''')

    # ================= WOMEN OF THE MOTHERLAND =================
    page("women-of-the-motherland", "Women of the Motherland | Mothering Sunday Tea London 2027", "Women of the Motherland: a Mothering Sunday afternoon tea in London, Sunday 7 March 2027, for women of African heritage and their families. GBP 150.",
         page_head("Sunday 7 March 2027 · Mothering Sunday · 11:00 to 18:30", "Women of the Motherland", "For every woman of African heritage, and the family she carried. Rooted and rising.", "ruby", "sankofa",
                   '<div class="chips"><span class="chip">Family afternoon tea</span><span class="chip">The Wall of Mothers</span><span class="chip">A family portrait</span><span class="chip">The whole family</span><span class="chip">GBP 150</span><span class="chip">A separate event, with its own ticket</span></div>', "Rooted and Rising", day="women-of-the-motherland") + f'''
{kband(14)}

<section class="band ivory story-band">
  <div class="wrap story">
    <span class="story-sym">{adl("aya")}</span>
    <span class="eyebrow">Daughters of the Motherland</span>
    <h2>Formidable, and this Sunday is hers.</h2>
    <p class="story-open">Seven on a Sunday morning in Barking. Payroll signed, her mother called from Kumasi, Lagos or Harare, her finest wrapper pressed for church.</p>
    <p>She built careers, homes and whole communities. She is rarely celebrated in a room built for her.</p>
    <div class="faces faces-3">{photo("embrace", "Two friends in green and blue print gowns, hugging and laughing", "ph", "50% 20%", "33vw")}{photo("n-mother-daughter", "A mother and daughter in Kente, cheek to cheek and laughing", "ph", "50% 25%", "33vw")}{photo("r-headwrap-elder", "An elder in a Kente headwrap and print gown, smiling warmly", "ph", "50% 20%", "33vw")}</div>
    <p class="story-turn">On Mothering Sunday, the day after Ghana turns seventy, Ghana opens its doors to every woman of African heritage.<br><em>From Accra to Lagos, Nairobi to Kingston. A family afternoon tea, at Banking Hall.</em></p>
  </div>
</section>

{value_band("sunday", ("g-headwrap-portrait", "A woman in a print headwrap and matching dress, smiling softly", "50% 20%"),
   "Mothering Sunday afternoon", "An afternoon worthy of her.",
   "Tea, her family around her, and her name read aloud.",
   "The women who carried us. The women who believed in us. The women who made a way when there seemed to be no way.",
   INC["sunday"],
   150, "per guest, 11:00 to 18:30", (5, "Book a family table of 5", "Family table: 5 x GBP 150 = GBP 750"),
   '<p class="founding vb-found">Giving it as a Mothering Sunday gift? Tick This is a gift when you book</p>')}

<section class="band white arrive" id="sunday-best"><div class="wrap arrive-in rev">
  {photo("blue-lace", "A woman in blue lace with a matching headwrap, dressed in her Sunday best", "arrive-ph", "50% 35%", "(max-width:900px) 92vw, 55vw")}
  <div class="arrive-copy"><span class="eyebrow">Sunday 7 March 2027 · Dress code</span><h2>Your Sunday best.</h2><div class="divider"><i></i></div>
    <p class="lead">Brocade, lace and gold. Dress for her.</p>
    <div class="btn-row"><a class="btn gold" href="tickets.html" data-pay="sunday">Book her seat</a><a class="btn line-dark" href="dress-code.html#sunday">See the Sunday dress code</a></div></div>
</div></section>
<section class="band ivory bh bh-sun" id="seating"><div class="wrap">
  <div class="bh-head"><div class="stack"><span class="eyebrow">Your family table</span><h2>The whole family, at one table.</h2></div>
    <p class="lead">Every family at one table, served from the first cup to the last.</p></div>
  <div class="bh-grid bh-land">
    <figure class="bh-ph"><img src="images/venue/bh-sunday-tables-1600.jpg" srcset="images/venue/bh-sunday-tables-800.jpg 800w, images/venue/bh-sunday-tables-1600.jpg 1600w" sizes="(max-width:760px) 100vw, 50vw" alt="The Main Hall at Banking Hall laid with family tables in rows down the chequered marble floor" loading="lazy"><figcaption>Family tables down the length of the hall</figcaption></figure>
    <figure class="bh-ph"><img src="images/venue/bh-sunday-rounds-1600.jpg" srcset="images/venue/bh-sunday-rounds-800.jpg 800w, images/venue/bh-sunday-rounds-1600.jpg 1600w" sizes="(max-width:760px) 100vw, 50vw" alt="Guests seated at tables in the Main Hall at Banking Hall, the marble staircase behind" loading="lazy"><figcaption>One room, one sitting, everyone together</figcaption></figure>
  </div>
  <p class="bh-note">Banking Hall, photographed at earlier events. Your table will be dressed for Women of the Motherland.</p>
</div></section>

<section class="band white">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">The afternoon, in full</span><h2>From the first cup to the last goodbye.</h2><p class="lead">One sitting. Doors 11:00 to 18:30.</p></div>
    <div class="split">
    {tl([
        ("11:00", "Doors open", "Saxophone and sobolo. Family portraits, the Motherland Market and the Resource Village open. Elders seated first.", "Arrival"),
        ("12:00", "The Market and the portrait studio", "Browse the Motherland Market, visit the Resource Village and sit for your family portrait.", "Arrival"),
        ("13:00", "Afternoon tea", "The whole family at the table, with tea served all afternoon.", "Afternoon tea"),
        ("14:00", "The Wall of Mothers", "Every name revealed and honoured, with the whole room together."),
        ("14:30", "Time together", "Tea continues at the table. Family portraits, the Market and the Resource Village stay open.", "Afternoon tea"),
    ])}
    {tl([
        ("16:00", "The networking hour", "A table for every nation of the Motherland, and hosts who make every introduction.", "Networking"),
        ("17:00", "Voices of the Motherland", "Poems and stories from three generations.", "Spoken word"),
        ("17:45", "Honouring our mothers", "Saxophone, song and a standing tribute."),
        ("18:10", "The closing blessing", "Your Century Pledge, and the Sister Circle."),
        ("18:30", "Farewell", "Taxis called at the door."),
    ])}
    </div>
  </div>
</section>

<section class="band emerald" id="sessions">
  <div class="wrap split">
    <div class="stack-lg"><div class="stack"><span class="eyebrow">Shape the afternoon</span><h2>Tell us what you want to be part of.</h2><p class="lead">We are planning talks, a seminar and masterclasses for Mothering Sunday, and we want to build them around you. Nothing is confirmed yet. Register your interest and tell us what you would love, and we will make it happen.</p></div>
      <p class="muted">We announce each session here once it is confirmed. Registering does not reserve a place or change your ticket.</p></div>
    <div class="form-card">
      <form data-register novalidate class="stack-lg" aria-labelledby="ses-title">
        <input type="hidden" name="type" value="sessions"><input type="hidden" name="source" value="women-of-the-motherland">
        <div class="stack"><span class="eyebrow">Register your interest</span><h3 id="ses-title">The session I would attend</h3></div>
        <div class="row2"><div class="field"><label for="ses-first">First name</label><input id="ses-first" name="firstName" autocomplete="given-name" required></div><div class="field"><label for="ses-email">Email</label><input id="ses-email" type="email" name="email" autocomplete="email" required></div></div>
        <fieldset class="field"><legend>I would like to attend</legend><div class="checks">
          <label class="check"><input type="checkbox" name="interests" value="Seminar or talk"><span>A seminar or talk</span></label>
          <label class="check"><input type="checkbox" name="interests" value="Panel discussion"><span>A panel discussion</span></label>
          <label class="check"><input type="checkbox" name="interests" value="Masterclass"><span>A masterclass</span></label>
          <label class="check"><input type="checkbox" name="interests" value="One to one advice"><span>One to one advice</span></label>
        </div></fieldset>
        <div class="field"><label for="ses-msg">What would you want to be part of</label><textarea id="ses-msg" name="message" placeholder="For example, a session on wills and property back home, or a masterclass you would love" required></textarea></div>
        <div class="hp" aria-hidden="true"><label for="ses-web">Leave blank</label><input id="ses-web" name="website" tabindex="-1" autocomplete="off"></div>
        <label class="consent"><input type="checkbox" name="consent" value="yes" required><span>Yes, tell me when sessions are confirmed and send me news about Ghana at 70 UK. Unsubscribe at any time. <a href="privacy.html">Privacy</a></span></label>
        <div class="form-status" role="status" aria-live="polite"></div>
        <button class="btn gold" type="submit">Register my interest</button>
      </form>
      <div class="form-done" hidden><span class="eyebrow">Received</span><h3>Medaase. We hear you.</h3><p class="muted">Your ideas go straight to our programme team. We tell you first when sessions are confirmed.</p></div>
    </div>
  </div>
</section>

<section class="band goldwash">
  <div class="wrap split">
    <div class="stack-lg"><div class="stack"><span class="eyebrow">Real support, beyond the day</span><h2>The Resource Village.</h2><p class="lead">Trusted support partners, open throughout the afternoon. Speak privately, take information home, and leave knowing exactly where to turn.</p></div>
      {info([("Health", "Health information for women, wellbeing checks and screening guidance"), ("Legal", "Wills, family matters and property in Britain and back home"), ("Money", "Pensions, savings and financial guidance"), ("Safety", "Confidential signposting for anyone facing abuse at home"), ("Community", "Faith groups, networks and mentoring for women")])}
      <p class="muted">The Village and the Motherland Market sit in the two side aisles, so every family keeps its table. Support partners will be announced from January 2027. Organisations serving women can <a href="#village">apply to join the Village</a>, and brands can <a href="exhibit.html#sunday">book a Sunday market stand</a>.</p>
    </div>
    <div class="pledge"><span class="eyebrow">The Motherland Toolkit</span><p class="big">A printed guide every guest takes home.</p>
      <ol style="margin:0;padding-left:22px;display:grid;gap:8px"><li>A health checklist for every decade</li><li>A money and wills checklist for Britain and back home</li><li>A directory of support organisations and helplines</li><li>Your pledge card and the Sister Circle details</li></ol>
      <p class="muted">If you or someone you know is affected by abuse at home, the National Domestic Abuse Helpline is open 24 hours on 0808 2000 247.</p></div>
  </div>
</section>

<section class="band white" id="village"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">The Resource Village</span><h2>Support that finds her on the day.</h2><p class="lead">Six places in the side aisles for organisations that serve women: health, legal, money, safety and community.</p></div>
  {info([("Who", "Charities, community groups and services that support women"), ("Where", "The side aisles of Banking Hall, Sunday 7 March 2027"), ("How", "Apply below. Our partnership team replies within one working day")])}</div>
  {enquiry_form("village")}
</div></section>
{book_band("sunday", "Book her seat at the table.", "She carried you. Her name on the Wall of Mothers at 14:00.", T_SUN)}
''')


    # ================= SPEAKERS =================


    # ================= TICKETS =================
    page("tickets", "Tickets | Ghana Independence Day 2027 London | Ghana at 70 UK", "Golden tickets for Ghana at 70 UK: the Royal Jubilee Gala, the Ghana Day Festival and Women of the Motherland. Prices, inclusions, add ons and booking.",
         page_head("Golden tickets", "Three separate events. Choose one, two or all three.", "Each event has its own ticket. Every price shown in full. Nothing added at checkout.", "gold", "adinkrahene", "") + f'''
<section class="band emerald"><div class="wrap tickets"><h2 class="sr">Golden tickets</h2>
  <div id="gala">{ticket_row(T_GALA, "What your ticket includes", INC["gala"], "Party of ten: 10 x GBP 275 = GBP 2,750", "#gala", pay="gala")}</div>
  <div id="ghana-day">{ticket_row(T_DAY, "What your ticket includes", INC["ghanaday"], "Two guests: 2 x GBP 50 = GBP 100", "#ghana-day", pay="ghanaday")}</div>
  <div id="sunday">{ticket_row(T_SUN, "What your ticket includes", INC["sunday"], "Family table of five: 5 x GBP 150 = GBP 750", "#sunday", pay="sunday")}</div>
  <div class="weekend-row"><p class="working" style="color:var(--gold-hi);margin:0"><b>The Weekend Pass: GBP 435.</b> One entry to each of the three separate events, for one guest. Bought separately at full price: GBP 275 + GBP 50 + GBP 150 = GBP 475. You save GBP 475 less GBP 435 = GBP 40</p><a class="btn gold" href="#all-days" data-pay="weekend">Book the Weekend Pass, save GBP 40</a></div>
{TRUST}
  <p class="tt-fallback" hidden data-tt-fallback>Booking window not opening? Open the box office for <a data-tt-link="gala" href="#">the Gala</a>, <a data-tt-link="ghanaday" href="#">the Festival</a> or <a data-tt-link="sunday" href="#">Sunday</a> in its own page.</p></div></section>
{TT_BOOKING.replace("{TTBOX}", tt_slot("boxoffice") or '<div class="btn-row"><a class="btn gold" data-tt-link="boxoffice" href="#">Open the box office</a></div>')}
<section class="band white arrive" id="invitation"><div class="wrap arrive-in rev">
  {photo("look/a1", "A king and queen in gold Kente, beads and gold, walking arm in arm before a columned City of London facade", "arrive-ph", "50% 50%", "(max-width:900px) 92vw, 55vw")}
  <div class="arrive-copy"><span class="eyebrow">Your golden ticket</span><h2>Every ticket is a royal invitation.</h2><div class="divider"><i></i></div>
    <p class="lead">A red carpet, drums, a royal banquet and midnight.</p>
    <div class="btn-row"><a class="btn gold" href="#gala" data-pay="pick">Take your seat at the Jubilee</a><a class="btn line-dark" href="dress-code.html">What to wear</a></div></div>
</div></section>
<section class="band ivory" id="gifts"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Gifts and company tables</span><h2>Give the seventieth.</h2><p class="lead">A gift with a date in it.</p></div>
  <div class="duo">
    <a class="duo-card" href="#gifts" data-pay="sunday"><span class="duo-sym">{adl("akoma")}</span><span class="eyebrow">Mothering Sunday</span><h3>Give her the afternoon.</h3><p>Afternoon tea, a family portrait and her name on the Wall of Mothers. 1 x GBP 150 = GBP 150.</p><span class="tk-link">Book her seat<i aria-hidden="true"></i></span></a>
    <a class="duo-card" href="#gifts" data-pay="gala" data-qty="10"><span class="duo-sym">{adl("adinkrahene")}</span><span class="eyebrow">For your company or family</span><h3>Host a royal party.</h3><p>Ten seats together at the long royal tables, your name on the place cards and one invoice. 10 x GBP 275 = GBP 2,750.</p><span class="tk-link">Book a royal table<i aria-hidden="true"></i></span></a>
  </div>
</div></section>

<section class="band ivory" id="stay"><div class="wrap split mid">
  <div class="stack"><span class="eyebrow">Coming from outside London?</span><h2>Hotel, travel card and tickets, in one booking.</h2><p class="lead">Partner rates at hotels of three and four stars, a Visitor Oyster card waiting at your hotel and your golden tickets.</p></div>
  <div class="btn-row"><a class="btn gold" href="stay.html#plan">Plan my stay</a><a class="btn line-dark" href="stay.html#from-ghana">Coming from Ghana</a></div>
</div></section>
<section class="band white" id="personalise"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Personalise your weekend</span><h2>Once you have booked, make it yours.</h2><p class="lead">Once your tickets are paid, add the touches that make it yours. Extras are priced on request and confirmed in writing.</p></div>
  {ADDONS}
  <div class="btn-row" style="margin-top:36px"><a class="btn gold" href="contact.html">Request extras</a><a class="btn emerald" href="partners.html#pack">Branded experiences</a></div>
</div></section>
''')

    # ================= TRAVEL AND STAY =================
    page("stay", "Travel and Stay in London | Ghana at 70 UK London 2027", "Coming to Ghana at 70 UK from outside London? Partner rates at hotels of three and four stars, a Visitor Oyster card and golden tickets in one request.",
         page_head("Travel and stay · 5 to 7 March 2027", "Coming from across the UK or from Ghana? We plan the journey.", "Your hotel, your travel card and your golden tickets, arranged in one booking, at your own cost.", "green", "nkonsonkonson",
                   '<div class="chips"><span class="chip">Partner hotel rates</span><span class="chip">Breakfast included</span><span class="chip">Oyster card at your hotel</span><span class="chip">Visa and flights from Ghana</span></div>', "Plan my stay") + f"""
<section class="band ivory" id="hotels"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Your hotel</span><h2>Two ways to stay.</h2><div class="divider"><i></i></div><p class="lead">We are agreeing weekend rates with hotels close to Banking Hall. The hotels and their rates are named in your options email.</p></div>
  <div class="st-hotels">
    <article class="st-hotel"><span class="st-stars" role="img" aria-label="Three stars">{"".join(star("#B8891F","#B8891F",0) for _ in range(3))}</span><span class="eyebrow">The Comfort Stay</span><h3>Three stars, kind to the budget.</h3>
      <ul><li>Partner rate for Ghana at 70 UK guests</li><li>Breakfast included</li><li>Direct Tube links to Bank station</li><li>Single, double, twin and family rooms</li></ul></article>
    <article class="st-hotel st-gold"><span class="st-stars" role="img" aria-label="Four stars">{"".join(star("#F3D27A","#F3D27A",0) for _ in range(4))}</span><span class="eyebrow">The Royal Stay</span><h3>Four stars, minutes from the hall.</h3>
      <ul><li>Partner rate for Ghana at 70 UK guests</li><li>Breakfast included</li><li>Minutes from Banking Hall</li><li>A car home after the Gala, on request</li></ul></article>
  </div>
  <p class="st-extra">Add a Visitor Oyster card waiting at reception, an arrival transfer or a car home after the Gala. Tell us where you are travelling from and we plan the rest.</p>
  <p class="muted st-note" style="text-align:center">Booked and paid by you, at our partner rate, confirmed in writing before you pay. Partner rooms are limited.</p>
</div></section>
<section class="band ghana-travel" id="from-ghana"><div class="wrap split mid">
  <div class="stack-lg"><div class="stack"><a class="gh-logo" href="https://adansitravels.com/" target="_blank" rel="noopener"><img src="images/partners/adansi.png" width="520" height="329" alt="Adansi Travels, our travel partner in Ghana" loading="lazy"></a><span class="eyebrow">Travelling from Ghana</span><h2>From Accra to Banking Hall, with ease.</h2><div class="divider"><i></i></div>
    <p class="lead">Adansi Travels is our travel partner in Ghana. Guests and exhibitors coming from the Motherland are guided through the UK visa application and flights to London, at their own cost. We look after your stay from the moment you land.</p></div>
    <ol class="st-steps gh-steps"><li><b>Your UK visa</b><span>Adansi Travels guides your visitor visa application from start to finish.</span></li><li><b>Your flights</b><span>Accra to London, booked for the weekend you want.</span></li><li><b>Your stay</b><span>Hotel, Oyster card and arrival transfer, arranged by us in London.</span></li></ol>
    <p class="gh-tip"><b>Apply early.</b> Start your visa application by the end of December 2026. On request, we send a letter confirming your paid ticket and the event dates. It confirms your booking only, and is not an invitation, sponsorship or offer of financial support.</p>
    <p class="st-cost"><b>At your own cost.</b> Visa fees, flights and Adansi Travels service fees are paid by you, directly to them. Ghana at 70 UK does not pay for, sponsor or guarantee any visa, flight or travel.</p>
  </div>
  <div class="form-card">
    <form data-register novalidate class="stack-lg" aria-labelledby="gh-title">
      <input type="hidden" name="type" value="ghana-travel"><input type="hidden" name="partner" value="Adansi Travels">
      <div class="stack"><span class="eyebrow">With Adansi Travels</span><h3 id="gh-title">I am coming from Ghana</h3></div>
      <div class="row2"><div class="field"><label for="gh-name">Your name</label><input id="gh-name" name="firstName" autocomplete="name" required></div><div class="field"><label for="gh-city">City in Ghana</label><input id="gh-city" name="travelFrom" placeholder="For example, Accra or Kumasi" required></div></div>
      <div class="row2"><div class="field"><label for="gh-email">Email</label><input id="gh-email" type="email" name="email" autocomplete="email" required></div><div class="field"><label for="gh-phone">WhatsApp number</label><input id="gh-phone" type="tel" name="phone" autocomplete="tel" placeholder="+233" required></div></div>
      <fieldset class="field"><legend>I am coming as</legend><div class="st-radios"><label class="check"><input type="radio" name="attendingAs" value="Guest" checked required><span>A guest</span></label><label class="check"><input type="radio" name="attendingAs" value="Exhibitor"><span>An exhibitor</span></label><label class="check"><input type="radio" name="attendingAs" value="Partner"><span>A partner</span></label></div></fieldset>
      <fieldset class="field"><legend>Help me with</legend><div class="st-checks">
        <label class="check"><input type="checkbox" name="extras" value="UK visa application" checked><span>My UK visa</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Flights Ghana to London" checked><span>Flights to London</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Hotel in London" checked><span>My hotel in London</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Visitor Oyster card"><span>A Visitor Oyster card</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Ticket confirmation letter for visa"><span>A ticket letter for my visa</span></label></div></fieldset>
      <div class="row2"><div class="field"><label for="gh-guests">Travellers</label><select id="gh-guests" name="guests">{"".join(f'<option{" selected" if n==1 else ""}>{n}</option>' for n in range(1,11))}<option>More than 10</option></select></div><div class="field"><label for="gh-in">Arriving in London</label><input id="gh-in" type="date" name="arrival" min="2027-02-25" max="2027-03-07" value="2027-03-04"></div></div>
      <div class="hp" aria-hidden="true"><label for="gh-web">Leave blank</label><input id="gh-web" name="website" tabindex="-1" autocomplete="off"></div>
      <label class="consent"><input type="checkbox" name="consent" value="yes" required><span>I understand that visa fees, flights and Adansi Travels fees are paid by me, and I agree that my details are shared with Adansi Travels to help with my visa and flights. See the <a href="privacy.html">privacy notice</a>.</span></label>
      <div class="form-status" role="status" aria-live="polite"></div>
      <button class="btn gold" type="submit">Start my journey</button>
      <p class="reassure c">Adansi Travels replies on WhatsApp or email · <a href="https://adansitravels.com/" target="_blank" rel="noopener">adansitravels.com</a> · Visa decisions rest with UK Visas and Immigration</p>
    </form>
    <div class="form-done" hidden><span class="eyebrow">Received</span><h3>Medaase. London awaits you.</h3><p class="muted">Adansi Travels will contact you about your visa and flights, and we follow up about your stay in London.</p></div>
  </div>
</div></section>
<section class="band ivory" id="plan"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Plan my stay</span><h2>Tell us your dates. We do the rest.</h2><p class="lead">Your options and rates within one working day. Nothing is booked until you approve it.</p></div>
    <ol class="st-steps"><li><b>Tell us</b><span>Your dates, your guests and the bundle you like.</span></li><li><b>Choose</b><span>Your hotel options and rates by email, within one working day.</span></li><li><b>Confirm</b><span>Approve and pay. Your confirmation follows by email.</span></li></ol>
    <p class="muted">Questions? Call Asantewaa on <span data-phone>07824 555307</span>.</p></div>
  <div class="form-card">
    <form data-register novalidate class="stack-lg st-form" aria-labelledby="st-title">
      <input type="hidden" name="type" value="stay">
      <div class="stack"><span class="eyebrow">Accommodation request</span><h3 id="st-title">Plan my stay</h3></div>
      <div class="row2"><div class="field"><label for="st-name">Your name</label><input id="st-name" name="firstName" autocomplete="name" required></div><div class="field"><label for="st-from">Travelling from</label><input id="st-from" name="travelFrom" placeholder="For example, Manchester, Dublin or Milan" list="st-cities" required><datalist id="st-cities"><option>Manchester</option><option>Leeds</option><option>Birmingham</option><option>Milton Keynes</option><option>Northampton</option><option>Dublin</option><option>Belfast</option><option>Amsterdam</option><option>Brussels</option><option>Paris</option><option>Milan</option><option>Rome</option><option>Hamburg</option><option>New York</option><option>Washington</option><option>Houston</option><option>Atlanta</option><option>Toronto</option><option>Accra</option><option>Kumasi</option></datalist></div></div>
      <div class="row2"><div class="field"><label for="st-email">Email</label><input id="st-email" type="email" name="email" autocomplete="email" required></div><div class="field"><label for="st-phone">Mobile</label><input id="st-phone" type="tel" name="phone" autocomplete="tel" required></div></div>
      <div class="row2"><div class="field"><label for="st-in">Arriving</label><input id="st-in" type="date" name="arrival" min="2027-03-01" max="2027-03-07" value="2027-03-05" required></div><div class="field"><label for="st-out">Leaving</label><input id="st-out" type="date" name="departure" min="2027-03-05" max="2027-03-12" value="2027-03-08" required></div></div>
      <div class="row2"><div class="field"><label for="st-guests">Guests</label><select id="st-guests" name="guests">{"".join(f'<option{" selected" if n==2 else ""}>{n}</option>' for n in range(1,11))}<option>More than 10</option></select></div><div class="field"><label for="st-rooms">Rooms</label><select id="st-rooms" name="rooms">{"".join(f"<option>{n}</option>" for n in range(1,7))}<option>More than 6</option></select></div></div>
      <fieldset class="field"><legend>Your hotel</legend><div class="st-radios"><label class="check"><input type="radio" name="hotelTier" value="3 star" required><span>Three stars</span></label><label class="check"><input type="radio" name="hotelTier" value="4 star"><span>Four stars</span></label><label class="check"><input type="radio" name="hotelTier" value="Show me both" checked><span>Show me both</span></label></div></fieldset>
      <div class="field"><label for="st-bundle">I would like</label><select id="st-bundle" name="bundle"><option>Hotel only</option><option>Hotel and Visitor Oyster card</option><option selected>Hotel, Oyster card and golden tickets</option></select></div>
      <fieldset class="field"><legend>Add to my booking</legend><div class="st-checks">
        <label class="check"><input type="checkbox" name="extras" value="Group coach from my city"><span>A group coach from my city, for 20 guests or more</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Visitor Oyster card for each guest" checked><span>Visitor Oyster card for each guest</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Arrival transfer"><span>Arrival transfer</span></label>
        <label class="check"><input type="checkbox" name="extras" value="Car home after the Gala"><span>Car home after the Gala</span></label></div></fieldset>
      <fieldset class="field"><legend>Golden tickets for</legend><div class="st-checks">
        <label class="check"><input type="checkbox" name="interests" value="Royal Jubilee Gala" checked><span>The Royal Jubilee Gala, Friday</span></label>
        <label class="check"><input type="checkbox" name="interests" value="Ghana Day"><span>Ghana Day Festival, Saturday</span></label>
        <label class="check"><input type="checkbox" name="interests" value="Women of the Motherland"><span>Women of the Motherland, Sunday</span></label></div></fieldset>
      <div class="field"><label for="st-msg">Anything we should know</label><textarea id="st-msg" name="message" placeholder="Room types, a budget, arrival times or access needs"></textarea></div>
      <div class="hp" aria-hidden="true"><label for="st-web">Leave blank</label><input id="st-web" name="website" tabindex="-1" autocomplete="off"></div>
      <label class="consent"><input type="checkbox" name="consent" value="yes" required><span>I agree to be contacted about my stay. See the <a href="privacy.html">privacy notice</a>.</span></label>
      <div class="form-status" role="status" aria-live="polite"></div>
      <button class="btn gold" type="submit">Send my travel request</button>
      <p class="reassure c">Options within one working day · Paid by you, nothing booked until you approve</p>
    </form>
    <div class="form-done" hidden><span class="eyebrow">Received</span><h3>Medaase. Your journey is in hand.</h3><p class="muted">Your hotel options and rates arrive by email within one working day.</p></div>
  </div>
</div></section>
""")

    # ================= PARTNERS =================
    TIERS_SP = [
        ("headline", "GBP 20,000", "One only", "Presenting Partner", "The Royal Jubilee Gala, presented by you.",
         ["The Gala presented by your brand", "The midnight toast in your name, as Independence Day begins", "An address of five minutes from the stage", "A table of ten: 10 x GBP 275 = GBP 2,750 in seats", "Full stage and screen branding", "The back cover of the commemorative Ghana at 70 UK passport book"]),
        ("", "GBP 15,000", "One per sector", "Principal Partner", "A headline experience, yours alone.",
         ["Your name on a headline experience: the Royal Welcome, the Highlife Band, the Ghana Day stage or the Wall of Mothers", "Category exclusive in your sector", "Eight seats: 8 x GBP 275 = GBP 2,200 in seats", "A feature stand on Saturday and Sunday", "The inside front cover of the passport book"]),
        ("", "GBP 10,000", "Limited", "Official Partner", "One experience, in your name.",
         ["Your name on one experience: the Portrait Studio, the dance floor or the Ghana at 70 UK film", "Six seats: 6 x GBP 275 = GBP 1,650 in seats", "A stand on Saturday and Sunday", "A full page in the passport book"]),
    ]
    def tier_html(t):
        cls, price, avail, name, lead, items = t
        lis = "".join(f"<li>{x}</li>" for x in items)
        return (f'<article class="sp-tier {cls}"><div class="sp-top"><span class="sp-avail">{avail}</span><span class="sp-price">{price}</span></div>'
                f'<h3>{name}</h3><p class="sp-lead">{lead}</p><ul>{lis}</ul><a class="btn {"gold" if cls else "line"}" href="#pack">Request the {name} pack</a></article>')
    MOMENTS_SP = [
        ("The Royal Arrival", "Fontomfrom drums and the red carpet. The first thing every guest sees carries your name."),
        ("The welcome reception", "Guests arrive to drums and a welcome drink, presented by you."),
        ("The live band", "Highlife, hiplife, Afrobeats and everything in between, presented by you."),
        ("Kete and Adowa", "The royal music and dance of the Asante, performed in your name."),
        ("The Royal Banquet dessert", "The sweetest course of the night carries your name to every table."),
        ("The royal portrait", "Your brand on the portrait wall every guest is photographed against."),
        ("The Ghana map menu and stationery", "The keepsake every guest takes home."),
        ("The guest gift", "Your product in the hand of every guest as they leave."),
    ]
    page("partners", "Sponsorship | The Royal Jubilee Gala | Ghana at 70 UK London 2027", "Sponsor the Royal Jubilee Gala, Ghana at 70 UK: one night at Banking Hall in the City of London, 5 March 2027. Presenting partnership GBP 20,000.",
         page_head("Sponsorship · Friday 5 March 2027", "Partner the Royal Jubilee Gala.", "One night, moments from the Bank of England. Your brand at the centre.", "black sp-hero", "besesaka",
                   '<div class="chips"><span class="chip">250 guests</span><span class="chip">Banking Hall, moments from the Bank of England</span><span class="chip">Presenting Partner GBP 20,000</span><span class="chip">Commemorative passport book</span></div>', "Sponsorship") + partners_feature("Announced partners", "Our partners for the Platinum Jubilee.") + f"""
<section class="band ivory sp-intro"><div class="wrap">
  <div class="sp-split">
    {photo("look/g2", "Kings and queens at a long candlelit banqueting table, dressed in Kente and gold", "sp-ph", "50% 0%", "(max-width:900px) 92vw, 40vw")}
    <div class="sp-copy"><span class="eyebrow">The opportunity</span><h2>Seventy years of independence. One night that matters.</h2>
      <p class="lead">Toasted at midnight in the City of London, by the people who made it matter.</p>
      <p class="sp-invite">We invite you to stand with us.</p>
      <p>A royal banquet and ball for the kings and queens of the Motherland: long candlelit tables, Kente and black tie, live royal drums, and a hall that rises as one at midnight. Our partners are woven into the evening itself, and remembered with it.</p>
      <div class="sp-stats"><div><b>250</b><span>guests at long royal tables</span></div><div><b>1</b><span>night, one room, every eye</span></div><div><b>00:00</b><span>the midnight toast</span></div><div><b>70</b><span>years of independence</span></div></div>
    </div>
  </div>
</div></section>
<section class="band white" id="business-case"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">The business case</span><h2>Be the name the diaspora remembers.</h2><div class="divider"><i></i></div><p class="lead">Three days when a community feels seen, honoured and at home. The brand standing beside them in that moment is the one they trust, talk about and choose for years.</p></div>
  <div class="bc-market"><article><h3>A market that moves money every month</h3><p class="bc-fact">USD 7.8 billion was sent home to Ghana in 2025, and the UK sent 17.5 percent of it from January to September 2025.</p><p class="bc-so"><b>What it means.</b> Your future clients already live between two homes. The name that stands beside them at seventy is the one they will remember when they choose. (Bank of Ghana)</p></article><article><h3>A community large enough to build a book of business</h3><p class="bc-fact">132,577 people born in Ghana lived in England and Wales at the 2021 census, with many more of Ghanaian heritage.</p><p class="bc-so"><b>What it means.</b> A community of real depth, in every region of the UK, and loyal to the brands that honour it. (ONS Census 2021)</p></article><article><h3>Two homes, one wallet</h3><p class="bc-fact">52,845 visitors arrived in Ghana from the UK in 2024, the third largest source market. Across all visitors, 22 percent came to see family and friends.</p><p class="bc-so"><b>What it means.</b> Travel, property, insurance, telecoms and banking are chosen for two countries at once. One relationship, warmly begun, serves both. (Ghana Tourism Authority)</p></article></div>
  <div class="section-head center bc-mid"><span class="eyebrow">What the Gala alone delivers</span><h2>Ten returns from one night.</h2></div>
  <ol class="bc-grid"><li><span class="bc-k">Reach</span><b>250 guests, one room, six hours</b><p>The undivided attention of the room. Presenting Partner: GBP 20,000 / 250 guests = GBP 80 per guest for a whole evening in their company, with ten seats of your own included.</p></li><li><span class="bc-k">Qualified leads</span><b>Introductions by consent</b><p>Guests opt in at checkout to meet our partners in banking, property and money transfer. You receive named introductions to guests who have asked to meet you.</p></li><li><span class="bc-k">Measurable return</span><b>Your own tracked offer</b><p>A guest offer with its own code and link, printed in the passport book and on your table cards. Every redemption is counted and reported to you.</p></li><li><span class="bc-k">Audience data</span><b>Who is in the room</b><p>Guests may tell us their sector when they book. You receive the anonymised profile of the room before the night, so your team arrives with a plan.</p></li><li><span class="bc-k">Exclusivity</span><b>Category exclusivity</b><p>One bank, one money transfer brand, one developer. In your category, the room is yours.</p></li><li><span class="bc-k">Brand building</span><b>108 days in market</b><p>From 17 November 2026 to 5 March 2027 (13 + 31 + 31 + 28 + 5 = 108 days), with tickets on sale from 18 November 2026 and the countdown of the final seventy days from 26 December, our campaign, retargeting audiences and email list carry your name: 108 days in their thoughts before the doors open.</p></li><li><span class="bc-k">The moment</span><b>The midnight toast</b><p>At 00:00 the hall rises for Independence Day. The Presenting Partner owns the moment every guest films and shares.</p></li><li><span class="bc-k">Content you keep</span><b>Content rights</b><p>Photography and film of your branded moments, cleared for your own channels, newsletters and annual report.</p></li><li><span class="bc-k">Renewal</span><b>Proof after the night</b><p>Your partner report within seven days: guests, consented introductions, code redemptions, reach and images. The evidence your board needs to renew.</p></li><li><span class="bc-k">Social value</span><b>Community investment you can stand behind</b><p>Young graduates serve as ushers, women photographers cover Sunday. Social value to stand behind in your community and ESG reporting.</p></li></ol>
  <div class="bc-cta"><p>Banking, money transfer, property, telecoms, travel, law and food and drink: one partner in each. Each category is offered once.</p><a class="btn gold" href="#pack">Claim your category</a><a class="btn line-dark" href="#tiers">See the tiers</a></div>
  <p class="muted bc-src">Market figures: Bank of Ghana, Office for National Statistics 2021 census, Ghana Tourism Authority.</p>
</div></section>
<section class="band dc-dark"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Who is in the room</span><h2>The diaspora at its most distinguished.</h2><div class="divider"><i></i></div></div>
  <div class="sp-aud">
    <div><b>Diaspora professionals</b><span>Finance, law, medicine, property and technology, building wealth across the UK and Ghana.</span></div>
    <div><b>Founders and business owners</b><span>Decision makers who buy, invest and hire, in the UK and in Ghana.</span></div>
    <div><b>Community and faith leaders</b><span>The voices families listen to, in London and across the regions.</span></div>
    <div><b>Friends of Ghana</b><span>Partners, supporters and guests who share the celebration.</span></div>
  </div>
  <p class="sp-note">Reach beyond the room: photography and film of every branded moment, shared with guests and across our social channels in the UK, Ghana and the wider diaspora.</p>
</div></section>
<section class="band ivory" id="tiers"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Partnership tiers</span><h2>Three ways to stand at the centre.</h2><div class="divider"><i></i></div><p class="lead">Every level is limited. All prices plus VAT. Payment in full by 15 January 2027.</p></div>
  <div class="sp-tiers">{"".join(tier_html(t) for t in TIERS_SP)}</div>
</div></section>
<section class="band white sp-mom" id="moments"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Sponsor a moment</span><h2>Your name on the moment guests remember.</h2><div class="divider"><i></i></div><p class="lead">Add a moment to any partnership. One partner per moment, first confirmed, first served. The midnight toast belongs to the Presenting Partner.</p></div>
  <ol class="sp-moments">{"".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in MOMENTS_SP)}</ol>
</div></section>
<section class="band white" id="heritage-wall"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">The Heritage Wall</span><h2>Put your name beside the people who came before us.</h2><div class="divider"><i></i></div><p class="lead">Ten true stories, ten panels, all three days. Each partner takes one story.</p></div>
  <ol class="hw-grid"><li><span class="hw-yr">1555</span><b>Shama to London</b><span>The first trade link between the Gold Coast and London</span><em>Made for: Trade finance, shipping and logistics</em></li><li><span class="hw-yr">1749</span><b>The Royal African</b><span>A prince of Anomabu in Georgian London</span><em>Made for: Heritage, arts and culture</em></li><li><span class="hw-yr">1754</span><b>A boy from Cape Coast</b><span>The first African ordained in the Church of England</span><em>Made for: Churches and faith organisations</em></li><li><span class="hw-yr">1882</span><b>The fastest man in Britain</b><span>Arthur Wharton, the first Black professional footballer</span><em>Made for: Sport, football clubs and sportswear</em></li><li><span class="hw-yr">1896</span><b>A lawyer for a nation</b><span>Casely Hayford at the Inner Temple</span><em>Made for: Law firms and chambers</em></li><li><span class="hw-yr">1925</span><b>Africa in Camden</b><span>The West African Students Union</span><em>Made for: Universities and student housing</em></li><li><span class="hw-yr">1927</span><b>The doctor of philosophy</b><span>Danquah, the first West African PhD from a British university</span><em>Made for: Education and professional bodies</em></li><li><span class="hw-yr">1945</span><b>Burghley Road, Kentish Town</b><span>Nkrumah in London</span><em>Made for: Publishing, media and public institutions</em></li><li><span class="hw-yr">1948</span><b>The soldiers who came home</b><span>The Gold Coast Regiment</span><em>Made for: Insurance, security and causes for veterans</em></li><li><span class="hw-yr">1957</span><b>Independence, and the journey continues</b><span>132,577 people born in Ghana, living in England and Wales</span><em>Made for: Banks and money transfer, the closing panel</em></li></ol>
  <div class="hw-deal">
    <div><span class="eyebrow">Each panel</span><b class="hw-price">Included</b><span>With every Presenting, Principal and Official partnership</span></div>
    <ol><li>Your name and logo on your story, seen by every guest on all three days: Gala, Ghana Day Festival and Mothering Sunday</li><li>Your story shared on our social channels during the final seventy day countdown, with your name</li><li>A full page in the Ghana at 70 UK passport book</li><li>Your panel to keep after the event, for your office or reception</li></ol>
    <a class="btn gold" href="#pack">Choose your story</a>
  </div>
  <p class="muted hw-note">Every story is checked against published sources: London Museum, English Heritage, the Inner Temple and the Office for National Statistics. Panels are allocated in order of signed agreement.</p>
</div></section>
<section class="band dc-dark"><div class="wrap">
  <div class="sp-split rev">
    <div class="sp-copy"><span class="eyebrow">What you receive</span><h2>Delivered, documented, reported.</h2>
      <ol class="kl-keys"><li><b>Before the night</b><span>Your brand on invitations, tickets, the website and guest emails from the day you confirm.</span></li><li><b>On the night</b><span>Your moment delivered on stage, on screen and at the tables, with your guests seated in the royal room.</span></li><li><b>After the night</b><span>Photographs of every branded moment and a partner report with attendance and reach.</span></li></ol>
      <div class="btn-row" style="margin-top:28px"><a class="btn gold" href="#pack">Request the sponsorship pack</a><a class="ph-link" href="contact.html">Speak to us</a></div></div>
    {photo("venue/bh-candlelit", "Candlelit long tables beneath the columns and the great clock at Banking Hall", "sp-ph", "50% 50%", "(max-width:900px) 92vw, 40vw")}
  </div>
</div></section>
{partners_wall(True)}
<section class="band ivory" id="pack"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">The sponsorship pack</span><h2>Request the pack.</h2><p class="lead">Every tier, every moment and the dates that matter, in your inbox the same day.</p><p class="muted">Exhibiting on Saturday instead? <a href="exhibit.html">See exhibitor stands</a>.</p></div></div>
  {enquiry_form("pack")}
</div></section>
""")

    # ================= ABOUT =================
    page("about", "Our Story | Ghana Platinum Jubilee, 70 Years | Ghana at 70 UK", "Ghana turns seventy on 6 March 2027. The story of Ghana at 70 UK, The Platinum Jubilee Celebrations in London, 5 to 7 March 2027, and the team behind it.",
         page_head("Our story", "The Ghana Platinum Jubilee.", "On 6 March 1957 the Black Star rose over an independent Ghana. On 6 March 2027 the nation reaches seventy years, its Platinum Jubilee, and the whole of the UK will celebrate it in style, with three days in London. <a href=\"#who-we-are\">Meet the team</a> or <a href=\"#join\">join us</a>.", "green", "nsoromma", "", "Freedom and Justice") + f'''
<section class="band dstory" id="our-story"><div class="wrap story-in">
  <div class="story-head"><span class="eyebrow">1957 · 2027 · Seventy years</span><h2>A Platinum Jubilee for the Motherland.</h2><div class="divider c"><i></i></div></div>
  <div class="story-body"><p class="story-first">At midnight on 6 March 1957, tens of thousands stood under the warm night sky of Accra and waited.</p>
    <p>Then Kwame Nkrumah spoke the words a continent had waited a lifetime to hear: &#8220;Ghana, your beloved country, is free forever.&#8221; The crowds celebrated through the night. That morning the Duchess of Kent, representing the Queen, read her message to the new nation: &#8220;The hopes of many, especially in Africa, hang on your endeavours.&#8221;</p>
    <p class="story-pull">Ghana carried those hopes. Ghana carries them still.</p>
    <p>Seventy years on, the children of that midnight are everywhere, and so many of us call the United Kingdom home, from London and Milton Keynes to Birmingham, Manchester, Leeds and Glasgow, and many more across the water in Dublin. Our parents arrived with a suitcase, a winter coat that was never quite warm enough and an extraordinary amount of courage. They worked the night shifts, studied after long days, filled the church halls on Sunday and sent money home on Friday. They built careers, businesses and families, and they raised us to know exactly where we come from.</p>
    <p class="story-pull">We have never forgotten home.</p>
    <p>Some of us were born in Kumasi, some in Lewisham, in Manchester or in Milton Keynes. Some of us speak Twi, Ga, Ewe, Fante or Dagbani. Some of us only understand it when our mothers are angry.</p>
    <p>Every one of us carries a Ghana of our own: waakye on a Saturday morning, a grandmother calling us by our day name, the first highlife record at a family party, the cousin who taught us to dance Azonto. And every one of us knows the words of that midnight.</p>
    <p>That is why our symbol is Akoko Nan, the leg of the hen. An Akan proverb says the hen treads on her chicks, but she does not kill them. It is the love of a mother who shelters and corrects, firm and gentle at once, and never lets go. Its two curls are the chicks held close, its crescent the line that shields them, and its point faces forward, because a mother meets danger before it reaches her children. Gold for the Gold Coast, green for the land.</p>
    <p class="story-pull">Ghana is ours, and we are Ghana. The Motherland is us.</p>
    <p>Seventy years is a platinum jubilee. In June 2022 Britain showed the world how such a milestone is honoured. For Queen Elizabeth II, the first British monarch to reign for seventy years, the nation gave a four day bank holiday weekend, from 2 to 5 June. More than 1,500 beacons blazed across the country. A Service of Thanksgiving was held in the City of London. Streets became banqueting halls, with more than 70,000 Big Jubilee Lunches, and some 5,000 performers carried the Platinum Jubilee Pageant past Buckingham Palace.</p>
    <p class="story-pull">Now it is the turn of Ghana.</p>
    <p>The two stories were always joined. Elizabeth II came to the throne in 1952. Five years into her reign, Ghana became independent with her as Queen of Ghana, until the nation declared itself a Republic on 1 July 1960. In November 1961 she came to Accra as the guest of President Kwame Nkrumah, and the two danced together at the farewell ball, a moment still remembered in both countries.</p>
    <p>On 6 March 2027 Ghana reaches a Platinum Jubilee of its own: seventy years as a sovereign nation. It deserves the same ceremony, the same pride and the same joyful noise. So Ghanaians from across the United Kingdom will gather in one great hall, Banking Hall in the City of London, moments from the Bank of England, for Ghana at 70 UK, The Platinum Jubilee Celebrations.</p>
  </div>
  <div class="pj">
    <h3 class="pj-h">Britain gave the Queen four days. We give Ghana three.</h3>
    <ol class="pj-rows">
      <li><span class="pj-then"><i>The Queen, June 2022</i>A four day bank holiday weekend</span><span class="pj-now"><i>Ghana at 70 UK, March 2027</i>Three days at Banking Hall, 5 to 7 March</span></li>
      <li><span class="pj-then"><i>The Queen, June 2022</i>Beacons lit across the land</span><span class="pj-now"><i>Ghana at 70 UK, March 2027</i>The midnight toast as Independence Day begins</span></li>
      <li><span class="pj-then"><i>The Queen, June 2022</i>The Platinum Party at the Palace</span><span class="pj-now"><i>Ghana at 70 UK, March 2027</i>The Royal Jubilee Gala, a banquet and a ball</span></li>
      <li><span class="pj-then"><i>The Queen, June 2022</i>The Big Jubilee Lunch in every street</span><span class="pj-now"><i>Ghana at 70 UK, March 2027</i>The Ghana Day Festival for the whole community</span></li>
      <li><span class="pj-then"><i>The Queen, June 2022</i>The Platinum Jubilee Pageant</span><span class="pj-now"><i>Ghana at 70 UK, March 2027</i>The runway and the dance circle</span></li>
    </ol>
  </div>
  <div class="story-body"><p>A platinum jubilee asks two questions: what have these seventy years given us, and what will we give the next seventy? We gather to honour the Ghana we came from, to shape the one our children will inherit, and to lift one another while we do it.</p>
    <p>For those who came before us. For those who walk beside us. For those who will follow.</p></div>
  <div class="story-days">
    <a href="royal-gala.html"><span class="eyebrow">Friday 5 March 2027</span><b>The Royal Jubilee Gala</b><span>A Ghanaian inspired dinner, a ball and a toast at midnight.</span><em>Take your seat</em></a>
    <a href="ghana-day.html"><span class="eyebrow">Saturday 6 March 2027</span><b>Ghana Day Festival</b><span>Independence Day with the whole community.</span><em>Be in the room</em></a>
    <a href="women-of-the-motherland.html"><span class="eyebrow">Sunday 7 March 2027</span><b>Women of the Motherland</b><span>For the women who carried us.</span><em>Book her seat</em></a>
  </div>
  <div class="story-body"><p class="story-sign">Three days. One people. One Platinum Jubilee.</p>
    <div class="btn-row" style="justify-content:center"><a class="btn gold" href="tickets.html" data-pay="pick">Take your seat at the Platinum Jubilee</a><a class="btn line-dark" href="partners.html">Partner with us</a></div>
    <p class="muted pj-src">Sources: contemporary reports of 6 March 1957, published records of the Platinum Jubilee weekend of 2 to 5 June 2022, and histories of the 1961 state visit to Ghana.</p>
  </div>
</div></section>
<section class="band white pjm" id="platinum-jubilee"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">The meaning</span><h2>What is a platinum jubilee?</h2><div class="divider"><i></i></div>
    <p class="lead">A jubilee is a great anniversary, kept with ceremony, thanksgiving and joy. Each has its own name, and seventy years has the finest of all: platinum.</p></div>
  <ol class="pjm-ladder" aria-label="The jubilees of Ghana">
    <li><b>Silver</b><span>25 years</span><i>1982</i></li>
    <li><b>Golden</b><span>50 years</span><i>2007</i></li>
    <li><b>Diamond</b><span>60 years</span><i>2017</i></li>
    <li><b>Sapphire</b><span>65 years</span><i>2022</i></li>
    <li class="on"><b>Platinum</b><span>70 years</span><i>6 March 2027</i></li>
  </ol>
  <div class="pjm-cols">
    <div class="pjm-col"><h3>The sound of the horn</h3>
      <p>The word jubilee comes from the ancient Hebrew <em>yobel</em>, the horn of a ram. In the old law, a horn was sounded every fiftieth year to open a year of restoration: land returned to its families, debts were set aside, and those held in bondage were released.</p>
      <blockquote class="pjm-q">&#8220;Proclaim liberty throughout all the land unto all the inhabitants thereof.&#8221;<cite>Leviticus 25:10</cite></blockquote>
      <p>For a nation that lit the way to independence for a continent, no word could be more fitting. A jubilee was always a celebration of liberty, of homecoming and of a people restored to themselves.</p></div>
    <div class="pjm-col"><h3>What a platinum jubilee asks of us</h3>
      <ol class="pjm-asks">
        <li><b>Give thanks.</b><span>For seventy years of nationhood, and for everyone who paid for it.</span></li>
        <li><b>Remember.</b><span>The names, the sacrifices and the songs, so that our children know them by heart.</span></li>
        <li><b>Come together.</b><span>Every region, every faith and every generation, in one hall, across three days.</span></li>
        <li><b>Look ahead.</b><span>To the Ghana of the next seventy years, which we will help to build.</span></li>
      </ol></div>
  </div>
  <div class="pjm-ours">
    <h3>Our Platinum Jubilee</h3>
    <p>Seventy years ago a people stood together at midnight and claimed their future. Seventy years on, we honour every generation that carried the Black Star forward: the farmers and the teachers, the nurses and the soldiers, the market women and the scholars, and the mothers and fathers who crossed the sea so that their children could stand tall in Britain.</p>
    <p>This is our seventy years of service, of sacrifice and of faith. It deserves its own beacon, its own banquet and its own pageant, in the heart of London, in our finest cloth.</p>
    <p class="pjm-call">Sound the horn. Light the beacon. Lay the table.<br>Seventy years of Ghana.</p>
  </div>
  <p class="muted pjm-src">Sources: World Wide Words on the history of the word jubilee, and Leviticus 25 in the King James Version.</p>
</div></section>
<section class="band white who" id="who-we-are"><div class="wrap">
  <div class="who-intro">{photo("four-sisters", "Four women of the Motherland, laughing together in a studio portrait", "ph who-ph", "50% 30%", "(max-width:900px) 100vw, 46vw")}
    <div class="who-intro-txt"><span class="eyebrow">Who we are</span><h2>We build rooms where our people are honoured.</h2><div class="divider"><i></i></div>
      <p class="lead">Ghana at 70 UK is made by two joint founders, Asantewaa and Adwoa, who have spent their working lives bringing the diaspora together, across the UK, in Accra and everywhere in between.</p>
      <p>Every year on 6 March, Ghana celebrates the night it stood before the world and lit the way for a continent. For the seventieth, we are bringing that night to the UK: three days, one hall in London, and a welcome for every family of the Motherland, wherever in Britain they live.</p>
      <p>We are not a committee and we are not a brand. We are daughters of the Motherland who believe our people deserve the finest room in the country, and the warmest welcome in it.</p></div>
  </div>
  <p class="who-joint">Together they opened the new Ghana Passport Office in Aldgate East. Together they founded Accra Konnect. Together they bring you Ghana at 70 UK.</p>
  <div class="who-founders">
    <article class="who-card"><div class="who-mono" aria-hidden="true">{adl("adinkrahene", "who-adk")}<span>AGA</span></div><div class="who-txt"><span class="eyebrow">Joint founder</span><h3>Asantewaa-Gloria Ayim</h3><p>Joint founder of Accra Konnect, and together with Adwoa opened the new Ghana Passport Office in Aldgate East. Twenty years delivering events at the highest level, for Pirelli, the Spanish national football team and Champions League clubs.</p><p class="who-say">She builds the room.</p></div></article>
    <article class="who-card"><div class="who-mono" aria-hidden="true">{adl("nkonsonkonson", "who-adk")}<span>AA</span></div><div class="who-txt"><span class="eyebrow">Joint founder</span><h3>Adwoa Agyemang</h3><p>Joint founder of Accra Konnect, and together with Asantewaa opened the new Ghana Passport Office in Aldgate East. Founded Ghanaian Londoners Network in 2009 and has delivered over thirty community events since. Created the Women in Enterprise Awards, spent nine years in PR and media in Accra, and sits on the Ghana Nigeria Business Council Executive Committee.</p><p class="who-say">She fills it with our people.</p></div></article>
  </div>
  <figure class="who-letter"><div class="who-letter-in"><span class="eyebrow">A message from Asantewaa and Adwoa</span>
    <blockquote><p>Four years ago we opened the new Ghana Passport Office in Aldgate East. We saw what it means to our people to be received with dignity, in a room made for them. That is what we are building again.</p>
    <p>A platinum jubilee is not an anniversary. It is a homecoming. Our parents crossed oceans so that we could stand tall in this city, and in March we will stand together, in Kente and in our Sunday best, in one of the most beautiful halls in London.</p>
    <p>Bring your mother. Bring your children. Bring the friend who has never been. There is a seat at our table for every one of you.</p></blockquote>
    <p class="who-from"><span class="who-sig">Asantewaa and Adwoa</span><span>Asantewaa-Gloria Ayim and Adwoa Agyemang, joint founders</span></p></div></figure>
  <ol class="who-proof">
    <li><b>2009</b><span>Ghanaian Londoners Network founded</span></li>
    <li><b>30+</b><span>community events delivered</span></li>
    <li><b>20</b><span>years producing events at the highest level</span></li>
    <li><b>1957</b><span>the night we celebrate, seventy years on</span></li>
  </ol>
  <div class="who-promise">
    <h3 class="h4 c">What we promise every guest</h3>
    <ol>
      <li>{adl("hwemudua")}<b>Excellence, as standard</b><span>Seventy years deserves the finest room, the finest service and nothing less.</span></li>
      <li>{adl("akoma")}<b>Welcomed by name</b><span>A host meets you at the door. Every guest is a guest of honour.</span></li>
      <li>{adl("owiakokroko")}<b>On time, as promised</b><span>A published running order, kept to the minute.</span></li>
      <li>{adl("nkonsonkonson")}<b>Our people at the centre</b><span>Families, associations, churches and businesses, all in one hall.</span></li>
    </ol>
  </div>
</div></section>
<section class="band ivory" id="meaning"><div class="wrap">
  {photo("arch", "Independence Arch, Black Star Square, Accra", "ph wide-banner", "50% 40%", "100vw")}
  <div class="section-head"><span class="eyebrow">The flag</span><h2>Designed in 1957 by Theodosia Okoh.</h2><p class="lead">Red, gold and green, with the Black Star at its heart. In 2026 the Bank of Ghana honoured her as the designer of the national flag, unveiling her portrait on the new GH¢50 note that November.</p></div>
  <div class="flagkey">
    <div class="fk"><span class="sw sw-r"></span><h3>Red</h3><p>The blood of those who fought for independence.</p></div>
    <div class="fk"><span class="sw sw-g"></span><h3>Gold</h3><p>The mineral wealth of the land.</p></div>
    <div class="fk"><span class="sw sw-n"></span><h3>Green</h3><p>The forests and the fields.</p></div>
    <div class="fk"><span class="sw sw-s">{star("#111", "#111", 0)}</span><h3>The Black Star</h3><p>The lodestar of African freedom.</p></div>
  </div>
</div></section>
<section class="band white" id="before"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Before 1957</span><h2>Our diaspora story.</h2><div class="divider"><i></i></div><p class="lead">Long before independence, our people were crossing oceans to Britain: princes and priests, scholars and sprinters, lawyers, soldiers and the students who would lead a nation to independence. These are some of those who came before us.</p></div>
  <ol class="bf-line"><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M14 62h52l-8 12H22z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 62V14" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 18l20 18H40M40 22L24 40h16" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 80c8 4 16 4 24 0s16-4 24 0 16 4 24 0" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1555</span><div><h3>Shama to London</h3><p>Five men from Shama, on the Gold Coast, come to London to learn English for the gold trade. Nearly five centuries of Ghanaians in Britain begin.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><rect x="18" y="10" width="44" height="60" rx="4" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="25" y="17" width="30" height="46" rx="15" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="40" cy="34" r="7" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M29 58c2-9 20-9 22 0" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1749</span><div><h3>The Royal African</h3><p>William Ansah Sessarakoo of Anomabu, sold into slavery and freed, arrives in London as a guest of the Earl of Halifax. His portrait hangs in the National Portrait Gallery.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M40 8v14M34 14h12" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 72V40l20-16 20 16v32z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M34 72V56a6 6 0 0 1 12 0v16" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 72h56" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1754</span><div><h3>A boy from Cape Coast</h3><p>Philip Quaque leaves Cape Coast to study in England. In 1765 he becomes the first African ordained in the Church of England.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><circle cx="40" cy="40" r="26" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 22l10 8-4 12H34l-4-12z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 22v-8M50 30l12-4M46 42l6 10M34 42l-6 10M30 30l-12-4" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1882</span><div><h3>The fastest man in Britain</h3><p>Arthur Wharton of Jamestown, Accra, equals the 100 yards world record, then becomes the first Black professional footballer in the world.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M40 12v58M26 70h28M18 22h44" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M18 22l-8 18h16zM62 22l-8 18h16z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 40a8 6 0 0 0 16 0M54 40a8 6 0 0 0 16 0" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1896</span><div><h3>A lawyer for a nation</h3><p>J. E. Casely Hayford is called to the Bar in London, and later writes one of the first novels in English by an African.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M12 38L40 14l28 24" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M18 34v36h44V34" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="34" y="50" width="12" height="20" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="24" y="42" width="8" height="8" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="48" y="42" width="8" height="8" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1925</span><div><h3>Africa in Camden</h3><p>The West African Students Union is founded in London, with J. B. Danquah its first president. Its Africa House becomes a home from home.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M8 32l32-14 32 14-32 14z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M22 38v14c0 6 36 6 36 0V38" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M72 32v18" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1927</span><div><h3>The doctor of philosophy</h3><p>J. B. Danquah becomes the first West African to earn a doctorate from a British university.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><circle cx="40" cy="40" r="28" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="40" cy="40" r="22" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M28 36h24M30 44h20M33 52h14" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1945</span><div><h3>Burghley Road, Kentish Town</h3><p>Kwame Nkrumah rents a room at 60 Burghley Road, Kentish Town, and helps organise the Fifth Pan African Congress. A blue plaque marks the house.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M28 8l12 22 12-22" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="40" cy="48" r="20" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 36l3.5 7.5 8 1-6 5.5 1.5 8-7-4-7 4 1.5-8-6-5.5 8-1z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1948</span><div><h3>The soldiers who came home</h3><p>Veterans of the Gold Coast Regiment, marching for promised benefits, are fired on in Accra. Their deaths set the nation on the road to freedom.</p></div></li><li><span class="bf-yr"><svg class="bf-ic" viewBox="0 0 80 84" aria-hidden="true"><path d="M40 10l8.8 18 19.6 2.8-14.2 13.8 3.4 19.6L40 54.8 22.4 64.2l3.4-19.6L11.6 30.8 31.2 28z" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>1957</span><div><h3>Independence, and the journey continues</h3><p>Ghana is independent, under a flag of red, gold and green designed by Theodosia Okoh. At the 2021 census, 132,577 people born in Ghana lived in England and Wales.</p></div></li></ol>
  <p class="bf-wall">All ten stories stand on the Heritage Wall at Banking Hall across the three days, so every guest walks past the people who came before them. <a href="partners.html#heritage-wall">Partner a story</a>.</p>
  <p class="muted bf-src">Sources: London Museum, English Heritage, the Inner Temple, the Office for National Statistics 2021 census and published histories.</p>
</div></section>
<section class="band dc-dark arrive" id="midnight-1957"><div class="wrap arrive-in">
  {photo("look/nk", "Kwame Nkrumah, seated, in a Kente cloth over a white shirt", "arrive-ph", "50% 20%", "(max-width:900px) 92vw, 45vw")}
  <div class="arrive-copy"><span class="eyebrow">Midnight, 6 March 1957 · Accra</span><h2>&#8220;Ghana, your beloved country, is free forever.&#8221;</h2><div class="divider"><i></i></div>
    <p class="lead">Kwame Nkrumah, at the stroke of midnight. Seventy years on, we raise a glass at the same moment.</p>
    <div class="btn-row"><a class="btn gold" href="royal-gala.html#midnight">The midnight toast</a></div></div>
</div></section>
<section class="band emerald join" id="join"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Join us</span><h2>Not a ticket. A homecoming.</h2><div class="divider"><i></i></div><p class="lead">Seventy years comes once. Take your place in it, however you choose to stand with us.</p></div>
  <div class="join-grid">
    <a class="join-card" href="tickets.html">{adl("adinkrahene")}<b>Take your seat</b><span>The Gala, Ghana Day, Sunday or the whole weekend.</span><i>Book now</i></a>
    <a class="join-card" href="contact.html">{adl("besesaka")}<b>Bring your people</b><span>Associations, churches and alumni: a table of ten, and the chance to present who you are.</span><i>Book a table</i></a>
    <a class="join-card" href="contact.html">{adl("ananse")}<b>Speak or host</b><span>Lead a masterclass, a clinic or a conversation.</span><i>Put yourself forward</i></a>
    <a class="join-card" href="contact.html">{adl("tabono")}<b>Volunteer</b><span>Ushers, hosts and young photographers. Be part of the crew that makes history.</span><i>Join the crew</i></a>
    <a class="join-card" href="exhibit.html">{adl("dwennimmen")}<b>Exhibit</b><span>A stand among forty businesses from Ghana and across the diaspora.</span><i>See the stands</i></a>
    <a class="join-card" href="partners.html">{adl("fawohodie")}<b>Partner with us</b><span>Put your name beside the seventieth.</span><i>Request the pack</i></a>
  </div>
</div></section>
<section class="band ivory" id="register"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">On sale now</span><h2>Take your seat at the Jubilee.</h2><p class="lead">Every ticket is on sale today, on this website only. No booking fees added.</p></div>
  <div class="btn-row" style="justify-content:center"><a class="btn gold" href="royal-gala.html#book" data-pay="gala">Book the Gala</a><a class="btn gold" href="ghana-day.html#book" data-pay="ghanaday">Book Ghana Day</a><a class="btn gold" href="women-of-the-motherland.html#book" data-pay="sunday">Book afternoon tea</a><a class="btn line-dark" href="tickets.html" data-pay="pick">All tickets and the Weekend Pass</a></div>
</div></section>
''')

    # ================= GALLERY =================
    GCH = [
        ("gala", "Friday 5 March · The Royal Jubilee Gala", "Kings and queens of the Motherland.", "Dinner, dancing and a toast at midnight. 250 seats, one night only.", "royal-gala.html", "Take your royal seat", "gala", [
            ("r-hall-reception", "Guests in Kente and gold sharing a toast in the banking hall beneath the clock", "f"),
            ("gal-kente-four", "Four women in Kente gowns of gold, red and purple in a marble hall", "p"),
            ("y-two-couples", "Two couples, one young and one older, sharing a toast at the Gala", "s"),
            ("n-elders-table", "Older guests in black tie and Kente laughing at a candlelit table", "s"),
            ("y-generations", "Three generations laughing together at a candlelit Gala table", "s"),
            ("r-speech", "A speaker in Kente addresses a full hall of seated guests beneath marble columns", "h"),
            ("d-kente-circle", "A gentleman in Kente cloth dances at the centre of a circle of guests", "h"),
            ("g-black-tie-group", "Gentlemen in black tie and Kente sashes with their partners in a marble hall", "s"),
            ("g-seated-queens", "Five women in Kente and black lace laughing together at a candlelit table", "s"),
            ("d-tux-dance", "Gentlemen in black tie dancing with women in Kente and gold gowns", "h"),
            ("g-wheel-dance", "Guests in Kente and black tie dancing together, a woman in emerald dancing from her wheelchair", "h"),]),
        ("young", "Friday 5 March · The new generation", "Your friends. Your night.", "Graduates, young professionals and guests at their very first Gala, dressed to be remembered.", "royal-gala.html", "Book with your friends", "gala", [
            ("n-green-group", "Young guests in black tie, emerald and Kente laughing together with champagne", "f"),
            ("n-her-laugh", "A young woman in a Kente gown laughing with friends in black tie", "p"),
            ("n-dance-floor", "A young couple dancing, she in Kente, he in black tie", "s"),
            ("n-toast-pair", "A young couple sharing a toast, he in a Kente dinner jacket", "s"),
            ("n-grand-hall", "Young guests in black tie and gowns mingling beneath chandeliers", "h"),
            ("n-dance-mix", "Guests of every age dancing together in Kente and black tie", "h"),
            ("m-kente-mermaid", "A woman in a blue and orange Kente mermaid gown with a sculpted shoulder", "p"),]),
        ("men", "For the gentlemen", "Black tie, with Kente.", "Walk in wearing black tie. Leave as royalty.", "dress-code.html", "See the dress code", "", [
            ("g-tux-man", "A gentleman in black tie with a Kente waistcoat and lapels", "p"),
            ("g-sash-men", "Gentlemen in black tie with Kente sashes, and an elder in Kente cloth", "h"),
            ("g-kente-men", "Four gentlemen in Kente cloth talking in a marble hall", "h"),
            ("g-table-talk", "Two women in Kente and black and a gentleman in a Kente bow tie laughing at their table", "h"),]),
        ("ghanaday", "Saturday 6 March · Ghana Day Festival", "Independence Day, in Ankara print.", "Dance on the day Ghana was born. A DJ all day, up to forty stands and the whole community. GBP 50.", "ghana-day.html", "Book Ghana Day", "ghanaday", [
            ("d-ankara-dance", "Guests in bright Ankara print dancing together in the hall", "f"),
            ("g-headwrap-portrait", "A woman in a print headwrap and matching dress", "p"),
            ("sisters-headwrap", "Three women in bold print headwraps, smiling together", "s"),
            ("j-couple-black", "A couple in black and Kente print, he in jeans, she in a print wrap", "s"),
            ("g-prints-line", "Women in bold Ankara print and headwraps in a sunlit garden", "f"),
            ("j-dark-denim", "A woman in a print corset top and wide dark jeans", "s"),
            ("j-black-shirt", "A gentleman in a black shirt with a Kente print panel and white trainers", "s"),
            ("j-print-tunic", "A gentleman in a black tunic with a Kente print panel, smiling", "s")]),
        ("sunday", "Sunday 7 March · Women of the Motherland", "A Sunday for her.", "Give her the afternoon she has given you a thousand times. Tea at the table and her name read aloud. GBP 150.", "women-of-the-motherland.html", "Book her seat", "sunday", [
            ("n-mother-daughter", "A mother and daughter in Kente, cheek to cheek and laughing", "p"),
            ("n-three-gen", "A grandmother, her daughter and her granddaughter laughing together", "s"),
            ("r-headwrap-elder", "An elder in a Kente headwrap, smiling softly", "s"),
            ("r-woven", "A woman in Kente and black lace, seated among woven baskets", "s"),
            ("m-tea", "An afternoon tea stand of sandwiches, scones and cakes", "s"),
            ("embrace", "Two friends in green and blue, hugging and laughing", "s")]),
    ]
    def gitem(k, alt, shape, label, href, day, n, tot):
        w, h = PHOTOS[k]["w"], PHOTOS[k]["h"]
        fig = photo(k, alt, "ph gi-ph", "50% 30%", "(max-width:760px) 86vw, 46vw").replace("<figure ", "<span ").replace("</figure>", "</span>")
        return (f'<li class="gi" style="--ar:{w}/{h}"><button class="gi-btn" type="button" data-gi-full="images/photos/{k}-1600.jpg" data-gi-cap="{label}" data-gi-day="{day}" data-gi-href="{href}" aria-label="Open: {alt}">{fig}</button></li>')
    ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]
    def gchapter(i, c):
        cid, eb, h, lead, href, cta, day, items = c
        pay = f' data-pay="{day}"' if day else ""
        tot = len(items)
        lis = "".join(gitem(k, a, sh, h.rstrip("."), href, day, n + 1, tot) for n, (k, a, sh) in enumerate(items))
        return (f'<section class="gch" id="g-{cid}"><div class="gch-head"><span class="gch-n" aria-hidden="true">{ROMAN[i]}</span><div class="stack"><span class="eyebrow">{eb}</span><h2>{h}</h2><p class="lead">{lead}</p></div>'
                f'<a class="btn line-dark small gch-cta" href="{href}"{pay}>{cta}</a></div>'
                f'<div class="gfs" data-gfs><ul class="gfs-track" data-gfs-track tabindex="0" aria-label="{h.rstrip(".")}: {tot} images, scroll sideways">{lis}</ul>'
                f'<div class="gfs-bar"><span class="gfs-count"><b data-gfs-n>01</b><span> / {tot:02d}</span></span><span class="gfs-prog" aria-hidden="true"><i data-gfs-p></i></span>'
                f'<button type="button" class="gfs-play" data-gfs-play aria-pressed="false" aria-label="Pause the slideshow"><span class="gfs-ic" aria-hidden="true"></span></button>'
                f'<span class="gfs-arrows"><button type="button" class="gfs-btn" data-gfs-d="-1" aria-label="Previous images">&#8592;</button><button type="button" class="gfs-btn" data-gfs-d="1" aria-label="Next images">&#8594;</button></span></div></div></section>')
    gnav = "".join(f'<a href="#g-{c[0]}">{c[2].rstrip(".")}</a>' for c in GCH)
    page("gallery", "Gallery | The Look of the Jubilee | Ghana at 70 UK", "The look of Ghana at 70 UK: Kente gowns, black tie, Ankara print and Sunday best for three days in London, 5 to 7 March 2027.",
         page_head("Gallery", "See yourself there.", "Picture it. Kente and gold on Friday, Ankara print on Saturday, Sunday best for her. This is the room that is waiting for you.", "black", "duafe") + f'''
<section class="band white gal" id="gallery"><div class="wrap">
  <nav class="gal-nav" aria-label="Gallery chapters">{gnav}</nav>
  <div class="gal-intro"><p class="gal-big">One hall. Three days. And a seat with your name on it.</p><p class="gal-sub">Every guest is photographed, so next March the faces are yours.</p></div>
  {"".join(gchapter(i, c) for i, c in enumerate(GCH))}
</div></section>
<section class="band emerald gal-cta"><div class="wrap gal-cta-in">
  <div class="stack"><span class="eyebrow">Your portrait</span><h2>Be in the next gallery.</h2><p class="lead">Every guest is photographed across the weekend. Portraits are delivered within seven days, ready to frame and share.</p></div>
  <div class="gal-cta-days">
    <a href="royal-gala.html" class="gcd"><span class="eyebrow">Friday 5 March</span><b>The Royal Jubilee Gala</b><i>From GBP 250</i></a>
    <a href="ghana-day.html" class="gcd"><span class="eyebrow">Saturday 6 March</span><b>Ghana Day Festival</b><i>GBP 50</i></a>
    <a href="women-of-the-motherland.html" class="gcd"><span class="eyebrow">Sunday 7 March</span><b>Women of the Motherland</b><i>GBP 150</i></a>
  </div>
  <div class="btn-row"><a class="btn gold" href="tickets.html" data-pay="pick">Book now</a><a class="btn line" href="dress-code.html">See the dress code</a></div>
</div></section>
<dialog class="lb" data-lb aria-label="Gallery image">
  <button class="lb-x" type="button" data-lb-x aria-label="Close">&#215;</button>
  <button class="lb-nav lb-prev" type="button" data-lb-prev aria-label="Previous image">&#8249;</button>
  <figure class="lb-fig"><img data-lb-img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt=""><figcaption><b data-lb-cap></b><span class="lb-acts"><a class="btn gold small" data-lb-book href="tickets.html">Book this day</a><a class="btn line small" href="dress-code.html">Get the look</a></span></figcaption></figure>
  <button class="lb-nav lb-next" type="button" data-lb-next aria-label="Next image">&#8250;</button>
</dialog>
''')


    # ================= FAQ =================
    groups = [
        ("general", "General", [
            ("What is Ghana at 70 UK?", "The UK celebration of the Ghana 70th Platinum Jubilee: a series of three separate events in London, each with its own ticket, marking seventy years of Ghanaian independence: the Royal Jubilee Gala on Friday 5 March 2027, the Ghana Day Festival on Saturday 6 March 2027, and Women of the Motherland on Sunday 7 March 2027."),
            ("Can I attend if I am not Ghanaian?", "Of course. Ghana at 70 UK welcomes the Ghanaian community and friends of Ghana from every background."),
            ("Can I come to just one day?", "Yes. Each day is ticketed separately and is complete on its own."),
            ("How is the programme timed?", "Every day is planned to a published running order, sent to ticket holders before the event, so you can relax and enjoy it."),
            ("Is there a virtual option?", "No. Ghana at 70 UK is a celebration held in person."),
            ("How do I book?", "Choose your event on the Tickets page and book. Every ticket is on sale now, on this website only, with no booking fees added."),
        ]),
        ("tickets", "Tickets and payment", [
            ("When do tickets go on sale?", "Now. Every ticket is on sale today, on this website only. The Gala early bird price is GBP 250 while early bird tickets last, so book early."),
            ("Can I get a refund?", "No. All sales are final and tickets cannot be refunded. If you cannot attend, transfer your ticket to someone else at no extra cost by emailing us their name before 17:00 on the day before. If we cancel the event, you are refunded in full."),
            ("Can I pay by bank transfer?", "Yes. Choose bank transfer when you book and we send our account details with your booking reference. Tickets are issued once payment arrives."),
            ("Can I add extras or host a private party?", "Yes. Once your tickets are paid you can add private parties, royal parties, celebration packages and portrait packages. Extras are priced on request."),
                        ("Where should I book?", "Only on this website, through the Book now buttons or your private priority link. Tickets bought anywhere else are not valid."),
        ]),
        ("gala", "The Royal Jubilee Gala", [
            ("What is the dress code?", "Royalty Kente or Black Tie Gala. Come as royalty in Kente, or in full black tie. Gold is encouraged."),
            ("Can I book for a group of ten?", "Yes. Parties of ten sit together at the long royal tables. 10 x GBP 275 = GBP 2,750. Choose Royal party of 10 when you book."),
            ("Are there awards?", "No. Ghana at 70 UK is a celebration of Ghana, not an awards night. There are no awards, prizes or judging on any day."),
        ]),
        ("ghana-day", "Ghana Day Festival", [
            ("Can I bring children?", "Yes. All three days welcome guests aged 5 and over. Under 18s must be with an adult at all times, and every guest, adult or child, holds a ticket. We have no space for high chairs, pushchairs or buggies, so children under 5, including babies in arms, cannot be admitted."),
            ("Is there food and drink?", "Saturday is a festival, not a meal. The bar sells drinks and snacks all day, card only. Food is not included in the GBP 50 ticket, and food and drink cannot be brought in. Over 18s only at the bar, and we follow Challenge 25."),
            ("How do I join the games?", "Entry to the dance circle, oware games and Big Ghana Quiz is included with your ticket. Enter at the welcome desk on the day."),
            ("Is anything on Saturday evening?", "No. The party closes at 18:00."),
        ]),
        ("sunday", "Women of the Motherland", [
            ("Who is Sunday for?", "Every woman of African heritage, wherever her roots lie, with her family and her allies. Ghanaian, Nigerian, Kenyan, Caribbean and beyond. Mothers, fathers, sons, daughters and grandparents are all welcome at family tables."),
            ("Does everyone pay the same?", "Yes. GBP 150 per guest covers afternoon tea, the Wall of Mothers, the toolkit, a family portrait and the networking hour, whether or not you drink alcohol."),
            ("Will there be a seminar or masterclasses?", "Not yet confirmed. Tell us what you would want to be part of through the <a href=\"women-of-the-motherland.html#sessions\">register your interest form</a>, and we announce sessions once they are confirmed."),
            ("Is there more than one sitting?", "No. There is one sitting and the whole room is together all day. Doors open at 11:00 and we close at 18:30."),
        ]),
        ("involved", "Partners, speakers and volunteers", [
            ("How do I get the sponsorship pack?", "Request it on the Partners page. It arrives in your inbox the same day."),
                        ("What does a stand cost?", "A market stand is GBP 250 + VAT and a feature stand is GBP 600 + VAT, both including the stand build. Royal Jubilee Gala seats are not included and are offered at the exhibitor rate. See <a href=exhibit.html#costs>stands and prices</a>."),
            ("How can I speak, host or lead a session?", "Get in touch through our contact page. Speakers, hosts, masterclass hosts and clinic experts are welcome."),
                        ("Can I volunteer?", "Yes. Get in touch through our contact page. Shift options follow in January 2027 and a briefing in February 2027."),
        ]),
        ("venue", "Venue and access", [
            ("Where is the venue?", "All three days are at Banking Hall, 14 Cornhill, London EC3V 3ND, in the City of London, moments from the Bank of England."), ("I do not live in London. Can you arrange my stay?", "Yes. We book a hotel close to the venue or within your budget, plus airport and station transfers. Send a request from the Travel and stay page and receive your options within one working day."),
                        ("Is the venue accessible?", "Banking Hall is a historic building and the event is held over two floors connected by stairs only, so the event may not be suitable for guests who cannot use stairs. Please call us before booking and we will tell you honestly what is possible. See the <a href=visit.html#access>access guide</a>."),
                        ("Will I be photographed?", "Photography takes place throughout the weekend and portraits are delivered within seven days. If you prefer not to be photographed, tell a host on arrival."),
        ]),
    ]
    nav = "".join(f'<a href="#{k}">{g}</a>' for k, g, _ in groups)
    faq_ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for _, _, items in groups for q, a in items]}) + '</script>'
    body = "".join(f'<div class="faq-group" id="{k}"><h2 class="h3">{g}</h2><div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div></div>" for k, g, items in groups)
    page("faq", "Questions | Tickets, Dress and Children | Ghana at 70 UK London 2027", "Questions answered about tickets, dress code, food, children, games, partners and the venue for Ghana at 70 UK.",
         page_head("Questions answered", "Everything you need to know.", "Cannot find your answer? Email us and we will reply within one working day.", "", "eban") + f'''
<section class="band white"><div class="wrap faq-layout"><nav class="faq-nav" aria-label="FAQ sections">{nav}</nav><div>{body}<p class="muted">Email <span data-email>ghanaat70.uk@gmail.com</span> or call Asantewaa on <span data-phone>07824 555307</span>.</p></div></div></section>
''', faq_ld)

    # ================= TERMS =================
    page("terms", "Ticket Terms | Ghana at 70 UK", "Ticket terms for Ghana at 70 UK: all sales final, transfers to a named guest, a full refund if we cancel, and entry conditions.",
         page_head("The small print", "Ticket terms.", "Clear terms, so every guest knows where they stand.", "green", "hwemudua") + '''
<section class="band white"><div class="wrap legal">
  <h2 class="h3">Terms of sale at a glance</h2>
  <ol>
    <li><b>All sales are final.</b> Tickets cannot be refunded or exchanged once paid.</li>
    <li><b>Tickets are transferable.</b> If you cannot attend, pass your ticket to another guest. Email us their name before 17:00 on the day before the event.</li>
    <li><b>Full refund only if we cancel.</b> If we cancel an event, every ticket holder for that event is refunded the full ticket price.</li>
    <li><b>Bank transfer within 24 hours.</b> Payment by bank transfer must arrive in full within 24 hours of booking, or the booking is released.</li>
    <li><b>Ages 5 and over.</b> We have no space for high chairs, pushchairs or buggies, so children under 5, including babies in arms, cannot be admitted on any day.</li>
  </ol>
  <div class="final-box" id="final-sale"><span class="eyebrow">Please read before you book</span><h3>All sales are final.</h3>
    <ol><li><b>No refunds.</b> Once you have paid, your ticket cannot be refunded or exchanged.</li><li><b>Transfer it to a friend.</b> If you cannot attend, give your ticket to someone else. Email us their name before 17:00 on the day before the event.</li><li><b>If we cancel, you are refunded in full.</b> If the event is cancelled by us, every ticket holder receives a full refund of the ticket price.</li></ol>
    <p>You confirm all three points at checkout before you pay.</p></div>
  <p class="muted">These terms were last updated on <b>19 November 2026</b>. They form the contract between you and the organiser when you buy a ticket. Please read them before you pay.</p>
  <h2 class="h3">1. Who we are</h2>
  <ol>
    <li>Ghana at 70 UK is organised by INTEROPA Holidays Ltd, registered in England and Wales, company number 01190602, registered office Room 540, Linen Hall, 162 to 168 Regent Street, London W1B 5TF ("the organiser", "we").</li>
    <li>"You" means the person who buys a ticket (the lead booker) and every guest who uses a ticket.</li>
  </ol>
  <h2 class="h3">2. Buying a ticket</h2>
  <ol>
    <li>Prices: the Royal Jubilee Gala GBP 275 per guest, with an early bird price of GBP 250 while early bird tickets last. The Ghana Day Festival GBP 50 per guest. Women of the Motherland GBP 150 per guest. The Weekend Pass GBP 435 per guest: one ticket for each of the three days, issued to the same guest. The early bird price cannot be combined with the Weekend Pass. Prices include VAT and booking fees. No fee is added at checkout.</li>
    <li>Ghana at 70 UK is a series of three separate events. Each ticket is valid only for the event and date printed on it: The Royal Jubilee Gala on Friday 5 March 2027, the Ghana Day Festival on Saturday 6 March 2027, or Women of the Motherland on Sunday 7 March 2027. A ticket for one event gives no entry to the others. The Weekend Pass is one ticket for each of the three events.</li>
    <li>Your contract is formed when we confirm your booking by email after full payment is received. Until then, no place is guaranteed.</li>
    <li>Bank transfers must arrive in full, in GBP, within 24 hours of booking. Any bank or currency charges are paid by you. Unpaid places are released to other guests without further notice.</li>
    <li>Early bird and other offers are limited, apply only while stated and cannot be applied to a booking already made.</li>
    <li>If a price is shown in obvious error, we may cancel the booking and refund in full, or offer the correct price.</li>
    <li>The lead booker is responsible for every ticket in the booking, for passing these terms to each guest and for the accuracy of the details given.</li>
    <li>We may limit the number of tickets per person, and may cancel bookings made in breach of these terms or for resale.</li>
  </ol>
  <h2 class="h3">3. All sales are final</h2>
  <ol>
    <li><b>No refunds.</b> Owing to the nature of the event, tickets are not refundable and cannot be exchanged once payment is made. This includes, without limitation, a change of plans, illness, travel disruption, a refused visa, bad weather, late arrival, refused admission under these terms, or any other reason you are unable to attend or choose not to.</li>
    <li><b>No right to cancel within 14 days.</b> Tickets are for leisure services on a specific date. Under regulation 28(1)(g) of the Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013, the right to cancel within 14 days does not apply.</li>
    <li><b>Chargebacks.</b> If you dispute a payment with your bank or card provider for a ticket that remains valid, the tickets in that booking are cancelled and entry is refused. We will provide your bank with your booking record, including your confirmation that all sales are final, and recover the amount and any costs as a debt.</li>
  </ol>
  <h2 class="h3">4. Transferring a ticket</h2>
  <ol>
    <li>A ticket may be transferred to another guest at no extra cost. Email us the booking reference and the full name of the new guest before 17:00 on the day before the event. We reissue the ticket in the new name and the original ticket no longer works.</li>
    <li>The new guest holds the ticket on these terms and must be aged 5 or over.</li>
    <li>Tickets may not be resold for profit, offered on resale or auction sites, or used in a promotion or competition without our written consent. Tickets found to be resold in breach of this clause may be cancelled without refund.</li>
  </ol>
  <h2 class="h3">5. If we cancel or change the event</h2>
  <ol>
    <li><b>If we cancel.</b> If we cancel an event, every ticket holder for that event receives a full refund of the ticket price paid, to the original method of payment, within 14 days of the cancellation notice.</li>
    <li><b>If we move the date or the venue.</b> Your ticket is valid for the new date or venue. If you cannot attend, you may ask for a full refund of the ticket price by emailing us within 14 days of our notice. After that, the ticket stands for the new date or venue.</li>
    <li>Changes to the programme, running order, speakers, performers, menu or décor do not entitle a guest to a refund.</li>
    <li>If an event cannot take place, or must stop, because of events beyond our reasonable control, such as government restrictions, severe weather, strikes, a venue emergency or an instruction from the police or authorities, we will refund the ticket price if the event does not take place and cannot be rescheduled. If an event starts but must end early for these reasons, no refund is due.</li>
    <li>Our liability to you is limited to the ticket price you paid. We are not responsible for travel, accommodation or other costs you incur, except where these are booked through our accommodation service, which has its own terms. Nothing in these terms limits liability for death or personal injury caused by negligence, for fraud, or any other liability that cannot be limited by law.</li>
  </ol>
  <h2 class="h3">6. Entry on the day</h2>
  <ol>
    <li>Each ticket admits one guest, once, on the day shown, on scanning its personal QR code. Copied or duplicated tickets are refused, and only the first ticket scanned is admitted. Keep your ticket private.</li>
    <li>The name on the ticket may be checked against photo ID. Please bring it.</li>
    <li><b>Ages 5 and over.</b> All three days are for guests aged 5 and over. Children under 5, including babies in arms, cannot be admitted. Every guest, child or adult, holds a ticket. Under 18s must be with a responsible adult at all times, who is responsible for them throughout the event. The bar serves over 18s only, and we follow Challenge 25. Admission of under 18s is subject to the conditions of the venue licence.</li>
    <li>Doors close at the last entry time shown for that day. Late arrivals may not be admitted, and no refund is due.</li>
    <li>Saturday guests may leave and return wearing their wristband. Wristbands are fitted by our hosts with a lock that cannot be opened without cutting. A wristband that is cut, damaged, loose, transferred or not worn on the wrist is not valid for coming back in, and a new ticket must be bought.</li>
    <li>The dress code for each day is published on this website. Guests not dressed to the code for the Royal Jubilee Gala may be asked to change before entry.</li>
    <li>Bags may be searched. Food and drink may not be brought in. Items we judge unsafe may be refused.</li>
    <li>We may refuse entry, or ask a guest to leave, where behaviour is unsafe, abusive, intoxicated or disruptive, or breaks these terms or the rules of the venue. No refund is due.</li>
  </ol>
  <h2 class="h3">7. Access and the venue</h2>
  <ol>
    <li><b>Access.</b> Owing to the nature of the venue, the event is held over two floors connected by stairs only. We have no space for high chairs, pushchairs or buggies on any day. If you have access needs, please call us before booking so we can tell you honestly what is possible.</li>
    <li>A staffed cloakroom is available. Items are left at your own risk, and valuables should be kept with you. Lost property is held for 30 days.</li>
    <li><b>Travel, visas and accommodation.</b> Travel, flights, visas, accommodation and travel cards are arranged and paid for by each guest, exhibitor or partner, at their own cost. Where our accommodation service or Adansi Travels, our travel partner in Ghana, helps you, they do so on their own terms and fees. The organiser does not sponsor, pay for or guarantee any visa, flight or accommodation, and any letter we provide confirms your booking only. A refused visa does not entitle a refund of your ticket, which you may transfer under section 4.</li>
    <li>Photography and filming take place throughout the event. By attending, guests agree that images in which they appear may be used to promote Ghana at 70 UK.</li>
  </ol>
  <h2 class="h3">8. Gifts and extras</h2>
  <ol>
    <li>Gift tickets are issued in the name you give us and follow these terms.</li>
    <li>Extras are priced on request, confirmed in writing and payable in full in advance. They are final sales on the same basis as tickets.</li>
  </ol>
  <h2 class="h3">9. Your agreement and the law</h2>
  <ol>
    <li><b>Your agreement.</b> Before payment, every lead booker confirms at checkout that all sales are final and that they have read and agree to these terms. Your confirmation, with the date and time, is recorded with your booking.</li>
    <li>If any part of these terms is found unenforceable, the rest remains in force.</li>
    <li>Questions or complaints: email us or call Asantewaa. We reply within one working day.</li>
    <li>These terms are governed by the law of England and Wales, and the courts of England and Wales have jurisdiction.</li>
    <li>Nothing in these terms affects your statutory rights.</li>
  </ol>
  <h2 class="h3" id="privacy">Privacy</h2>
  <p>How we use your details is set out in our <a href="privacy.html">privacy notice</a>.</p>
</div></section>
''')

    page("thank-you", "Thank you | Ghana at 70 UK", "Thank you for booking Ghana at 70 UK. Your golden tickets arrive by email, with everything you need for the day.",
         page_head("Booking confirmed", "Medaase. We will see you there.", "Ayekoo. You are in the room. Your golden tickets are on their way, with your QR code.", "gold", "adinkrahene") + f'''
<section class="band white" data-thanks><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Your booking</span><h2 class="h3" data-ty-what>Your golden tickets</h2><p class="bp-valid" data-ty-valid hidden></p>
    <p class="lead">You are now part of the seventy years. Running order, seating and directions follow by email before the day. Send this to the person who should be there with you.</p></div>
    <div class="btn-row"><a class="btn gold" href="#save-date-gala" data-ty-cal>Add to calendar</a><a class="btn emerald" data-share href="https://wa.me/?text=">Tell your people</a><a class="btn line" href="stay.html">We can help you book your hotel stay</a></div></div>
  <div class="stack-lg"><span class="eyebrow">Make it a weekend</span>
    <a class="duo-card" data-ty-x="gala" href="royal-gala.html" data-pay="gala"><span class="eyebrow">Friday 5 March</span><h3>The Royal Jubilee Gala</h3><p>GBP 275 per guest</p></a>
    <a class="duo-card" data-ty-x="ghanaday" href="ghana-day.html" data-pay="ghanaday"><span class="eyebrow">Saturday 6 March</span><h3>Ghana Day Festival</h3><p>GBP 50 per guest</p></a>
    <a class="duo-card" data-ty-x="sunday" href="women-of-the-motherland.html" data-pay="sunday"><span class="eyebrow">Sunday 7 March</span><h3>Women of the Motherland</h3><p>GBP 150 per guest. Bring your mother.</p></a></div>
</div></section>
{save_date('gala', SITE_URL, '07824 555307', 'ivory', 'save-date-gala', True, True)}{save_date('ghanaday', SITE_URL, '07824 555307', 'ivory', 'save-date-ghanaday', True, True)}{save_date('sunday', SITE_URL, '07824 555307', 'ivory', 'save-date-sunday', True, True)}''', '<meta name="robots" content="noindex">')

    page("404", "Page not found · Ghana at 70 UK", "This page could not be found. Return to Ghana at 70 UK for the three days of celebration in London, 5 to 7 March 2027.",
         page_head("Page not found", "This page has wandered off.", "The page you were looking for is not here. The weekend still is.", "", "nsoromma") +
         '<section class="band white"><div class="wrap btn-row"><a class="btn gold" href="index.html">Back to Ghana at 70 UK</a><a class="btn emerald" href="index.html#days">The programme</a></div></section>', '<meta name="robots" content="noindex">')


    # ================= VISIT =================
    page("visit", "Plan Your Visit | Banking Hall, Bank, London | Ghana at 70 UK", "Plan your visit to Ghana at 70 UK in London, 5 to 7 March 2027: opening times, getting there, access, arrival, dress code and age policy.",
         page_head("Plan your visit", "Everything you need, before you need it.", "Times, travel, arrival and access. Read it once, arrive relaxed.", "green", "eban", '<div class="chips"><a class="chip" href="#opening">Opening times</a><a class="chip" href="#directions">Getting there</a><a class="chip" href="#arrival">On arrival</a><a class="chip" href="#access">Accessibility</a><a class="chip" href="#policies">Good to know</a></div>', "Welcome") + f'''
<section class="band white" id="opening"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Opening times</span><h2>Three days, to the minute.</h2><p class="lead">Please arrive while the doors are open, so that we can seat and serve everyone together.</p></div>
  <div class="hours-grid">
    <article class="hcard"><span class="k">Friday 5 March 2027</span><h3>The Royal Jubilee Gala</h3>{hours_table([("Doors and red carpet", "18:30"), ("Last entry", "19:45"), ("Seated for dinner", "20:00"), ("Dancing ends", "23:30"), ("Midnight toast", "00:00"), ("Venue closes", "00:30")])}<p class="muted">Dress code: Royalty Kente or Black Tie Gala.</p></article>
    <article class="hcard"><span class="k">Saturday 6 March 2027</span><h3>Ghana Day Festival</h3>{hours_table([("Doors open", "11:00"), ("Anniversary moment", "12:00"), ("DJ and dancing", "12:30 to 18:00"), ("Last entry", "16:30"), ("Doors close", "18:00")])}<p class="muted">Ages 5 and over. No high chairs, pushchairs or buggies. Your wristband lets you come and go all day.</p></article>
    <article class="hcard"><span class="k">Sunday 7 March 2027</span><h3>Women of the Motherland</h3>{hours_table([("Doors", "11:00"), ("Afternoon tea", "13:00"), ("Wall of Mothers", "14:00"), ("Networking hour", "16:00"), ("Close", "18:30")])}<p class="muted">Ages 5 and over. Under 18s must be accompanied by an adult.</p></article>
  </div>
</div></section>

<section class="band ivory" id="directions"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Getting there</span><h2>All three days at Banking Hall, moments from the Bank of England.</h2><p class="lead">Banking Hall stands on Cornhill at Bank Junction, the heart of the City of London, moments from the Bank of England and the Royal Exchange. A Grade II listed 1930s Art Deco hall, once a Lloyds Bank headquarters.</p><p class="lead"><b>Nearest station: Bank</b>, about two minutes on foot.</p><p class="lead">Banking Hall, 14 Cornhill, London EC3V 3ND. All three days.</p></div>
    <div class="btn-row"><a class="btn gold" href="index.html#register">Be told first</a><a class="btn emerald" href="https://tfl.gov.uk/plan-a-journey/" rel="noopener">TfL journey planner</a></div></div>
  {info([("Where it is", "On Cornhill at Bank Junction, moments from the Bank of England and the Royal Exchange"), ("Nearest station", "Bank: Central, Northern, Waterloo and City lines and the DLR, about two minutes on foot. Monument: District and Circle lines. Check accessible routes on the TfL journey planner"), ("Mainline rail", "Cannon Street, Fenchurch Street and Liverpool Street, with the Elizabeth line at Liverpool Street"), ("Bus", "Many routes stop on Cornhill, Threadneedle Street and King William Street"), ("Car and taxi", "The City has very little parking. We recommend a taxi to the door on Cornhill"), ("Travelling from outside London", 'Our accommodation service books hotels and transfers. <a href="stay.html">Plan your stay</a>')])}
</div></section>

<section class="band white" id="arrival"><div class="wrap">
  <div class="section-head"><span class="eyebrow">On arrival</span><h2>From the door to your seat in minutes.</h2></div>
  {cards([
      ("01", "Have your golden ticket ready", "Your golden ticket arrives by email with a personal QR code. Show it on your phone or printed. One ticket per guest."),
      ("02", "Welcome desk", "Our hosts scan your ticket, hand you your programme and, on Saturday, your wristband."),
      ("03", "Cloakroom", "A staffed cloakroom is open from doors until close. Please keep valuables with you."),
      ("04", "Bag checks", "For the safety of every guest, bags may be checked at the door. Please travel light."),
      ("05", "Seating", "Gala and Sunday seating plans are emailed seven days before. Hosts guide every table to its seat."),
      ("06", "Help on the day", "Look for hosts in green and gold. They are there to help with anything, from directions to a quiet word."),
  ], icons=["ticket", "door", "gift", "star", "people", "heart"])}
</div></section>

<section class="band emerald" id="access"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Access</span><h2>Please read before you book.</h2><p class="lead">Banking Hall is a Grade II listed building. We want every guest to arrive knowing exactly what to expect.</p></div>
    </div>
  <div class="stack-lg"><span class="eyebrow">The access guide</span>
    <ol class="access-list">
      <li><b>Arrival</b><span>The entrance is at 14 Cornhill, steps from Bank station. Hosts meet every guest at the door.</span></li>
      <li><b>Inside</b><span>The event is held over two floors joined by stairs only.</span></li>
      <li><b>Seating</b><span>Every guest has a seat at the Gala and on Sunday. On Saturday, seating is available around the hall.</span></li>
      <li><b>Under 5s, pushchairs and buggies</b><span>We have no space for high chairs, pushchairs or buggies, so children under 5, including babies in arms, cannot be admitted.</span></li>
      <li><b>Cloakroom</b><span>Fully staffed on all three days, so you do not carry coats or bags on the stairs.</span></li>
      <li><b>Before you book</b><span>Call Asantewaa on 07824 555307 and we will tell you honestly what is possible.</span></li>
    </ol></div>
</div></section>

<section class="band white" id="policies"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Good to know</span><h2>The small print, made simple.</h2></div>
  {info([("Dress code", 'Friday: Royalty Kente or Black Tie Gala. Saturday: print and denim, or a Black Stars shirt. Sunday: Sunday best or traditional dress. <a href="dress-code.html">What to wear</a>'),
         ("Age", "Ages 5 and over, every day. Under 18s with an adult at all times. Over 18s only at the bar, and we follow Challenge 25"), ("Pushchairs", "The event is over two floors with stairs, so pushchairs and buggies cannot be accommodated on any day. Children under 5, including babies in arms, cannot be admitted."),
         ("Food and dietary needs", "Dinner is included at the Gala and afternoon tea on Sunday. On Saturday the bar sells drinks and snacks, card only. Tell us your dietary needs when you book"),
         ("Photography", "Our photographers capture the weekend. Tell a host if you prefer not to be photographed"),
         ("Coming and going", "Saturday guests may leave and return, wearing their wristband. A wristband that has been cut or removed is not valid"),
         ("Lost property", "Handed to the welcome desk on the day, then held for 30 days. Email us to claim"),
         ("Respect", "We want every guest to feel safe and welcome. Anyone whose behaviour endangers or disrupts others may be asked to leave"),
         ("Tickets", "All sales are final, with no refunds. Every ticket can be transferred to another guest at no extra cost by emailing us their name. If we cancel, you are refunded in full")])}
</div></section>
''')

    # ================= EXHIBIT =================
    total_stands = sum(c[3] for c in CATEGORIES)
    cat_cards = "".join(
        f'<div class="catgroup"><div class="cg-head"><span class="cg-sym">{adl(gs)}</span><div><h3>{gn}</h3><p>{gd}</p></div><span class="cg-n">{sum(c[3] for c in CATEGORIES if c[4] == gk)} stands</span></div><ul class="cg-list">'
        + "".join(f'<li data-cat="{k}"><div><b>{name}</b><span>{d}</span></div><span class="cg-cap">{n} stands</span></li>' for k, name, d, n, g in CATEGORIES if g == gk)
        + '</ul></div>' for gk, gn, gs, gd in CAT_GROUPS)
    page("exhibit", "Exhibit at the Ghana Day Festival | Independence Day London 2027", "Exhibit at the Ghana Day Festival, Saturday 6 March 2027, London. Forty chosen stands, never more than two of a kind. Stand types, inclusions and how to apply.",
         page_head("Saturday 6 March 2027 · Independence Day", "Exhibit at the Ghana Day Festival.", "Forty chosen stands on Independence Day, at Banking Hall, moments from the Bank of England.", "green", "fawohodie", '<div class="chips"><a class="chip" href="#wanted">Categories open</a><a class="chip" href="#costs">Stands and prices</a><a class="chip" href="#sunday">Sunday stands</a><a class="chip" href="#timeline">Key dates</a><a class="chip" href="#rules">Exhibitor rules</a><a class="chip" href="#apply">Apply</a></div>', "Forty stands only") + f'''
<section class="band white"><div class="wrap split mid">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Why exhibit</span><h2>Meet buyers who came to buy.</h2><p class="lead">Paying guests, on Independence Day. The warmest audience of the year.</p></div></div>
  {cards([
      ("Audience", "A paying audience", "Ghanaian families, professionals and friends of Ghana from across the UK, in the mood to celebrate and to shop."),
      ("Curation", "Never more than two of a kind", "Up to twenty kinds of exhibitor, never more than two of each. Every stand is seen, and no stand competes with five others."),
      ("Exposure", "Before, during and after", "A listing in the online directory, a mention in guest emails, and photography of the day you can use."),
      ("Fair", "One clear price", "GBP 250 + VAT for a market stand, GBP 600 + VAT for a feature stand. Build included, no extras."),
  ], "two", icons=["people", "star", "camera", "gift"])}
</div></section>

<section class="band ivory" id="wanted"><div class="wrap">
  <div class="strip3">{photo("beads", "Ghanaian glass beads in every colour", "ph", "50% 50%", "33vw")}{photo("wares", "A trader beneath a tower of colourful wares", "ph", "50% 40%", "33vw")}{photo("orange", "A woman in a flowing orange gown above a city", "ph", "50% 40%", "33vw")}</div>
  <div class="section-head"><span class="eyebrow">Categories open now</span><h2>Twenty kinds of exhibitor. Never more than two of each.</h2><p class="lead">So every stand is seen, and none competes with its neighbour.</p></div>
  <div class="catgroups">{cat_cards}</div>
  <p class="muted" style="margin-top:24px">{total_stands} market and feature stands. Food and drink in the hall come only from the venue bar, so food exhibitors sell sealed, labelled products to take home.</p>
</div></section>



<section class="band emerald" id="costs"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Stands and prices</span><h2>Two kinds of stand. One clear price.</h2><p class="lead">One price covers your stand, its build and everything listed below. No build charges, no extras.</p></div>
  <div class="costs">
    <article class="cost"><span class="cost-n">GBP 250</span><span class="cost-sym">{adl("tabono")}</span><h3>Market stand</h3><p>A dressed table with two chairs and your name card. For makers, authors and small brands.</p><span class="cost-k">GBP 250 + VAT at 20% (GBP 50) = GBP 300</span></article>
    <article class="cost"><span class="cost-n">GBP 600</span><span class="cost-sym">{adl("hwemudua")}</span><h3>Feature stand</h3><p>A built stand with walls and name fascia, a spotlight and power, a table and two chairs. For brands that want to be seen.</p><span class="cost-k">GBP 600 + VAT at 20% (GBP 120) = GBP 720</span></article>
    <article class="cost cost-gala cost-red"><span class="cost-n">Optional</span><span class="cost-sym">{adl("adinkrahene")}</span><h3>The Royal Jubilee Gala</h3><p>Not included with a stand. Anyone in the room on Friday evening holds a Gala ticket. Exhibitors book seats at the exhibitor rate, below the public price of GBP 275.</p><span class="cost-k">Exhibitor rate, book early</span></article>
  </div>
  <div class="pledge" style="margin-top:40px"><span class="eyebrow">Every stand includes</span><ol style="margin:0;padding-left:22px;display:grid;gap:8px;columns:2"><li>Two Saturday exhibitor passes</li><li>Your stand number and map in the exhibitor manual</li><li>A listing in the online exhibitor directory</li><li>A mention in guest emails before the day</li><li>Professional photographs of the day</li><li>Hosts on hand from build to pack down</li></ol></div>
</div></section>

<section class="band white" id="sunday"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Saturday and Sunday compared</span><h2>Saturday is a festival. Sunday is a dining room.</h2><p class="lead">On Saturday the stands are part of the festival. On Sunday they move to the aisles.</p></div>
  <div class="fp-compare">
    <article><span class="eyebrow">Saturday 6 March</span><h3>The Ghana Day Festival</h3><ol><li>Forty stands, never more than two of a kind</li><li>Market stand GBP 250 + VAT, feature stand GBP 600 + VAT</li><li>Trading 11:00 to 18:00, all day</li><li>A festival with a DJ: guests come and go all day and walk the hall between the dance floor, the quiz, the runway and the dance circle</li></ol></article>
    <article><span class="eyebrow">Sunday 7 March</span><h3>Women of the Motherland</h3><ol><li>Twelve stands: six Motherland Market, six Resource Village</li><li>Market stands only, one of each kind: flowers, perfume and beauty, jewellery and gold, Kente and fashion, books, cocoa and gifts</li><li>GBP 150 + VAT at 20% (GBP 30) = GBP 180, the price of one Sunday seat</li><li>A dressed table, two chairs, your name card and two exhibitor passes. Afternoon tea is for seated guests only</li><li>Trading 11:00 to 18:30, quiet during the Wall of Mothers</li><li>Guests visit the aisles while the other half of the room is at afternoon tea</li></ol></article>
    <article class="fp-both"><span class="eyebrow">Both days</span><h3>One brand, two audiences</h3><ol><li>A market stand on Saturday and on Sunday</li><li>GBP 250 + GBP 150 = GBP 400 + VAT at 20% (GBP 80) = GBP 480</li><li>Sunday places go to Saturday exhibitors first, in the kinds that suit Mothering Sunday</li></ol><a class="btn gold" href="#apply">Apply for a stand</a></article>
  </div>
</div></section>

<section class="band white" id="promise"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Our promise to exhibitors</span><h2>Everything exhibitors ask for, built in.</h2><p class="lead">Real buyers, steady footfall, real leads.</p></div>
  {cards([
      ("Buyers, not browsers", "Every guest has paid to be there", "Families and friends hold a GBP 50 day ticket, and are told in advance to bring a card for the bar and the stands."),
      ("No dead corners", "The day walks guests past you", "The dance floor, the bar, the Big Ghana Quiz, the runway and the dance circle all happen in the same hall, so guests circulate past every stand all day."),
      ("The passport trail", "A reason to stop at every stand", "Every guest receives a Ghana at 70 UK passport. They collect a stamp at each stand they visit, and keep the passport as a souvenir of the day."),
      ("Leads you keep", "Your QR code on your stand", "Each stand receives a printed QR code that links to your page in the online exhibitor directory, so guests can save you, follow you and order later."),
      ("Seen before the day", "Promotion from the moment you are confirmed", "Your listing in the exhibitor directory, a mention in guest emails and a feature on our social channels in the weeks before 6 March."),
      ("A simple day", "One pack, one contact, no surprises", "Build on Friday 5 March, your exhibitor pack six weeks before with loading times, power and access, and one named contact on the day."),
      ("Never next to a twin", "Two of a kind, placed apart", "No more than two exhibitors of the same kind, and never side by side."),
      ("After the day", "Proof you can use", "Professional photographs of your stand and a short summary of the day, so you can show your team and your customers what you achieved."),
  ], icons=["people", "star", "book", "ticket", "mail", "clock", "heart", "camera"])}
</div></section>
<section class="band goldwash" id="rising"><div class="wrap split mid">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Rising Stars</span><h2>Two stands, on us, for new Ghanaian businesses.</h2><p class="lead">Two stands for Ghanaian businesses under two years old.</p></div>
    <div class="btn-row"><a class="btn emerald" href="#apply">Apply for Rising Stars</a></div></div>
  {info([("Who", "Businesses owned by Ghanaians and trading for less than two years"), ("What", "A complimentary market stand, worth GBP 250 + VAT"), ("How", "Apply with the form below and choose Rising Stars"), ("Chosen by", "Our team shortlists, and guests vote")])}
</div></section>

<section class="band white" id="timeline"><div class="wrap split">
  <div class="stack"><span class="eyebrow">Key dates</span><h2>From application to Independence Day.</h2><p class="lead">Every date, known now.</p></div>
  {tl([("Now", "Applications open", "Apply in your category. Each kind closes when its two stands are confirmed."), ("5 days", "Your answer", "We confirm your place within five working days of applying."), ("14 days", "Secure your stand", "Full payment within 14 days of confirmation secures your stand."), ("January 2027", "Exhibitor manual", "Your stand number, delivery, power and insurance details."), ("19 Feb 2027", "Final details", "Stand staff names, power needs and your directory listing."), ("Friday 5 March", "Build day", "Stands are built on Friday. Building ends before Gala guests arrive. Exact build times are in the exhibitor manual."), ("6 March, 08:00", "Final dressing", "Stock and dress your stand from 08:00. All stands ready by 10:30."), ("6 March, 11:00", "Doors open", "Seventy years to the day. The festival runs until 18:00."), ("6 March, 18:00", "Pack down", "From 18:00 only, finished by 20:00.")])}
</div></section>

<section class="band white" id="faq-exhibit"><div class="wrap split">
  <div class="stack"><span class="eyebrow">Exhibitor questions</span><h2>Before you apply.</h2><p class="lead">The questions exhibitors ask most.</p><div class="btn-row"><a class="btn gold" href="#apply">Apply for a stand</a></div></div>
  <div class="faq">
    <details><summary>Who visits the Ghana Day Festival?</summary><p>Families, friends and the whole community, every one holding a GBP 50 ticket. We are planning for around 500 visitors through the day, the level a comparable community show of forty exhibitors has drawn. Every visitor has chosen to spend the day with Ghanaian brands, so the people at your stand arrive ready to buy.</p></details>
    <details><summary>How many visitors will there be?</summary><p>We are planning for around 500 visitors across the day. Entry is managed so the hall never holds more than its safe limit at one time, and that limit is confirmed by the venue. We report the real number to every exhibitor after the day.</p></details>
    <details><summary>What if my category is full?</summary><p>Apply anyway. If that category is full, you are offered the first stand released.</p></details>
    <details><summary>How much does a stand cost?</summary><p>A market stand is GBP 250 + VAT (GBP 300 in total) and a feature stand is GBP 600 + VAT (GBP 720 in total). Both prices include the stand build.</p></details>
    <details><summary>Can I exhibit on Friday or Sunday?</summary><p>Not on Friday: the hall is the Gala. On Sunday, yes, with twelve stands in the side aisles. Six are Motherland Market stands, one of each kind, at GBP 150 + VAT (GBP 180 in total), the price of one Sunday seat. Six are Resource Village stands for organisations that support women, arranged through our <a href="partners.html#pack">partnership team</a>. See <a href="#sunday">Saturday and Sunday compared</a>.</p></details><details><summary>Why are there fewer stands on Sunday?</summary><p>On Sunday the hall is a dining room. Every family is seated for afternoon tea, so stands only go where no table can: the two side aisles between the columns. No table is moved and no seat is lost for a stand.</p></details>
    <details><summary>Can I sponsor as well as exhibit?</summary><p>Yes. Sponsorship sits with our <a href="partners.html">partners</a> and can include a stand. Request the sponsorship pack.</p></details>
  </div>
</div></section>

<section class="band ivory" id="rules"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Exhibitor rules</span><h2>The standards that keep the hall beautiful.</h2></div>
  {info([("Curation", "Every exhibitor is approved by category. Products must match the application"), ("Market stand food", "Sealed, labelled products to take home only, with allergen information and registration with your local authority as a food business"), ("Insurance", "Public liability insurance is required. Send your certificate with your final details"), ("Electrics", "Electrical items must be safety tested and suitable for indoor use"), ("Payments", "Bring a card reader with its own mobile data. Do not rely on venue wifi"), ("Build and pack down", "Stands are staffed from doors to close. Nothing is packed away before 18:00"), ("Property, money and legal", "Estate agents, developers, financial and legal exhibitors must hold the registrations the law requires and send proof with their application, so our guests are protected"), ("The Gala", "Exhibiting does not include the Royal Jubilee Gala. Stand teams on site on Friday evening need a Gala ticket, at the exhibitor rate"), ("Cancellation", "Stand fees cannot be refunded once paid. Your stand can be transferred to another approved business")])}
</div></section>

<section class="band emerald" id="apply"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Apply</span><h2>Your stand on Independence Day.</h2><p class="lead">Applications are reviewed in the order they arrive. When a category is full, it closes.</p></div>
    {info([("Reply", "Within five working days"), ("Prices", "Market stand: GBP 250 + VAT<br>Feature stand: GBP 600 + VAT<br>Stand build included<br>Royal Jubilee Gala seats: exhibitor rate, optional"), ("Questions", '<span data-email>ghanaat70.uk@gmail.com</span>')])}
    <p class="gh-tip" style="color:var(--ink)"><b>Exhibiting from Ghana?</b> Adansi Travels, our travel partner in Ghana, supports your UK visa application and flights. <a href="stay.html#from-ghana">Start your journey</a></p></div>
  {exhibitor_form()}
</div></section>
''')

    # ================= EXHIBITORS DIRECTORY =================
    ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]

    # ================= CONTACT =================
    page("contact", "Contact | Ghana at 70 UK", "Contact the Ghana at 70 UK team about tickets, accommodation, accessibility, partnership, exhibiting or press.",
         page_head("Contact", "We are here to help.", "Tickets, accommodation, accessibility, partnership or press. Write to us and a real person replies within one working day.", "black", "nkonsonkonson") + f'''
<section class="band white"><div class="wrap split">
  <div class="stack-lg">
    <h2 class="sr">Contact details</h2>
    {info([("Email", '<span data-email>ghanaat70.uk@gmail.com</span>'), ("Call Asantewaa", '<span data-phone>07824 555307</span>'), ("WhatsApp", '<a href="https://wa.me/447824555307?text=Hello%20Asantewaa%2C%20I%20have%20a%20question%20about%20Ghana%20at%2070%20UK" target="_blank" rel="noopener">Chat on WhatsApp</a>'), ("Reply time", "Within one working day")])}
    <div class="stack"><span class="eyebrow">Quick answers</span><div class="btn-row"><a class="btn emerald" href="faq.html">Questions answered</a><a class="btn emerald" href="visit.html">Plan your visit</a></div></div>
  </div>
  {enquiry_form("contact")}
</div></section>
<section class="band ivory" id="press"><div class="wrap split">
  <div class="stack"><span class="eyebrow">Press and media</span><h2>Covering Ghana at 70 UK.</h2><p class="lead">The press release, fact sheet, images, social copy and accreditation are all in one place.</p></div>
  <div class="btn-row"><a class="btn gold" href="press.html">Open the press kit</a></div>
</div></section>
''')

    # ================= PRESS =================
    PR_RELEASE = """FOR IMMEDIATE RELEASE

Ghana at 70 UK: London to mark seventy years of Ghanaian independence with three days at Banking Hall

London, 17 November 2026. On 6 March 2027 Ghana turns seventy. The whole of the UK will mark it with Ghana at 70 UK, held in London, The Platinum Jubilee Celebrations: three days at Banking Hall, 14 Cornhill, the Grade II listed hall moments from the Bank of England.

Friday 5 March, The Royal Jubilee Gala. Independence Eve. Fontomfrom drums and a red carpet at 18:30, a Ghanaian inspired dinner, live highlife and, at midnight, the whole hall rising for the moment Ghana became independent in 1957. 250 seats. Royalty Kente or Black Tie.

Saturday 6 March, the Ghana Day Festival. Independence Day itself. A DJ all day, forty Ghanaian and African businesses, five practical talks on land, money, wills, pensions and business, and the anniversary moment at 12:00 with drumming and a reading of the declaration of independence. Ages 5 and over.

Sunday 7 March, Women of the Motherland. Mothering Sunday falls the day after the anniversary. A family afternoon tea open to every woman of African heritage and her family, with the Wall of Mothers, where every mother named by a guest is celebrated aloud, Voices of the Motherland and a family portrait. Talks and masterclasses are being shaped with guests and are not yet confirmed.

Ghana at 70 UK is created by joint founders Asantewaa-Gloria Ayim and Adwoa Agyemang, who together opened the new Ghana Passport Office in Aldgate East and founded Accra Konnect.

"Seventy years is not an anniversary. It is a homecoming," say Asantewaa and Adwoa. "Bring your mother. Bring your children. Bring the friend who has never been. There is a seat at our table for every one of you."

Tickets: Royal Jubilee Gala GBP 275, Ghana Day Festival GBP 50, Women of the Motherland GBP 150, Weekend Pass GBP 435. Tickets are on sale now at SITEURL.

ENDS

Media contact: Asantewaa, 07824 555307, ghanaat70.uk@gmail.com
Interviews, images and accreditation: SITEURL/press"""
    PR_RELEASE = PR_RELEASE.replace("SITEURL", SITE_URL)
    PR_ABOUT = "Ghana at 70 UK, The Platinum Jubilee Celebrations, marks seventy years of Ghanaian independence with three days at Banking Hall in the City of London, from Friday 5 to Sunday 7 March 2027: The Royal Jubilee Gala, the Ghana Day Festival and Women of the Motherland. It is created by joint founders Asantewaa-Gloria Ayim and Adwoa Agyemang."
    PR_FOUNDERS = "Asantewaa-Gloria Ayim and Adwoa Agyemang are joint founders of Ghana at 70 UK and of Accra Konnect, and together opened the new Ghana Passport Office in Aldgate East. Asantewaa has spent twenty years delivering events at the highest level, for Pirelli, the Spanish national football team and Champions League clubs. Adwoa founded Ghanaian Londoners Network in 2009, has delivered more than thirty community events, spent nine years in PR and media in Accra and sits on the Ghana Nigeria Business Council Executive Committee."
    SOCIAL = [
        ("Instagram and TikTok", "Seventy years ago tonight, Ghana stood before the world. On 5 March 2027 we stand together again, in Kente and gold, at Banking Hall, moments from the Bank of England. Three days. One hall. Every family of the Motherland. #GhanaAt70UK #GhanaAt70London"),
        ("X", "Ghana turns 70 on 6 March 2027. London marks it with three days at Banking Hall: The Royal Jubilee Gala, the Ghana Day Festival and a Mothering Sunday for women of African heritage. #GhanaAt70UK SITEURL"),
        ("LinkedIn", "Ghana at 70 UK brings the diaspora together at Banking Hall, moments from the Bank of England, from 5 to 7 March 2027. Independence Eve gala, an Independence Day festival with forty businesses and talks on land, money, wills, pensions and business, and a Mothering Sunday afternoon for women of African heritage. #GhanaAt70UK SITEURL"),
        ("WhatsApp", "Ghana is 70 on 6 March 2027 and London is celebrating at Banking Hall, moments from the Bank of England, 5 to 7 March. Gala, Ghana Day Festival and a Mothering Sunday tea. Tickets on sale now: SITEURL"),
    ]
    SOCIAL = [(a, b.replace("SITEURL", SITE_URL)) for a, b in SOCIAL]
    ANGLES = [
        ("Seventy years, in the City", "The seventieth anniversary of Ghanaian independence, marked in a Grade II listed banking hall moments from the Bank of England."),
        ("Independence Eve, at midnight", "At 00:00 on 6 March the whole hall rises for the moment Ghana became independent, seventy years on."),
        ("Mothering Sunday, the day after", "The anniversary and Mothering Sunday fall on the same weekend. Sunday honours the women who carried a nation, of every African heritage."),
        ("Wealth across two homes", "Saturday talks on land, money, wills, pensions and business for families with roots in Britain and Ghana."),
        ("The founders", "Two women who opened the new Ghana Passport Office in Aldgate East now bring the diaspora its seventieth."),
        ("Kente in the City", "Kente and gold on Friday, Ankara print and Black Stars shirts on Saturday, Sunday best for her. A visual story on every day."),
    ]
    PR_IMG = [("g-band-dance", "Couples dancing before the live band at the Royal Jubilee Gala"),
              ("p-black-star-square", "Black Star Square, Accra, where independence was celebrated in 1957")]
    def pimg(k, a):
        d = PHOTOS.get(k, {}) if isinstance(PHOTOS, dict) else {}
        cr = d.get("by", "Ghana at 70 UK") if d.get("src") == "design concept" else f'{d.get("by", "Ghana at 70 UK")} · {d.get("src", "")}'.strip(" ·")
        return (f'<li class="pr-img">{photo(k, a, "ph pr-ph", "50% 35%", "(max-width:760px) 100vw, 33vw")}'
                f'<p><span>{a}</span><small>Credit: {cr}</small><a class="ph-link" href="images/photos/{k}-1600.jpg" target="_blank" rel="noopener">Open full size</a></p></li>')
    page("press", "Press and Creators | Ghana Independence London 2027 | Ghana at 70 UK", "Press kit for Ghana at 70 UK, Banking Hall, London, 5 to 7 March 2027: press release, fact sheet, story angles, images and accreditation for media.",
         page_head("Tell our story", "The story, ready to tell.", "For everyone who tells stories: national titles, broadcasters, podcasters, community and diaspora media, photographers and creators of every size. The story, the facts, the images and the people are all here. Use them without charge, with credit.", "black", "nkonsonkonson",
                   '<div class="chips"><a class="chip" href="#release">Press release</a><a class="chip" href="#facts">Fact sheet</a><a class="chip" href="#angles">Story angles</a><a class="chip" href="#images">Images</a><a class="chip" href="#social">Social copy</a><a class="chip" href="#accreditation">Accreditation</a></div>') + f'''
<section class="band white" id="facts"><div class="wrap split">
  <div class="stack"><span class="eyebrow">Fact sheet</span><h2>At a glance.</h2><p class="lead">Ghana turns seventy on 6 March 2027. The UK celebrates in London across three days in one hall.</p>
    <div class="btn-row"><a class="btn gold" href="#release">Read the press release</a><a class="ph-link" href="#accreditation">Request accreditation</a></div></div>
  {info([("Event", "Ghana at 70 UK, The Platinum Jubilee Celebrations"), ("Dates", "Friday 5 to Sunday 7 March 2027"), ("Venue", "Banking Hall, 14 Cornhill, London EC3V 3ND, moments from the Bank of England"),
         ("Friday", "The Royal Jubilee Gala, 18:30 to 00:30. 250 seats. GBP 275"), ("Saturday", "Ghana Day Festival, 11:00 to 18:00. Up to forty stands, five talks. GBP 50"),
         ("Sunday", "Women of the Motherland, Mothering Sunday, 11:00 to 18:30. GBP 150"), ("Weekend Pass", "GBP 435, all three days"),
         ("Tickets", "On sale now, on the official website only"),
         ("Founders", "Asantewaa-Gloria Ayim and Adwoa Agyemang"), ("Hashtag", "#GhanaAt70UK")])}
</div></section>

<section class="band ivory" id="angles"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Story angles</span><h2>Six ways in.</h2></div>
  <ol class="pr-angles">{"".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in ANGLES)}</ol>
</div></section>

<section class="band white" id="release"><div class="wrap pr-copy">
  <div class="section-head"><span class="eyebrow">Press release</span><h2>Ready to publish.</h2><p class="lead">Copy it whole, or take what you need.</p></div>
  <div class="pr-box"><pre class="pr-text" id="pr-release">{_h.escape(PR_RELEASE)}</pre><button class="btn gold small" type="button" data-copy="#pr-release">Copy the press release</button></div>
  <div class="pr-two">
    <div class="pr-box"><h3>About Ghana at 70 UK</h3><p id="pr-about">{PR_ABOUT}</p><button class="btn line small" type="button" data-copy="#pr-about">Copy</button></div>
    <div class="pr-box"><h3>About the founders</h3><p id="pr-founders">{PR_FOUNDERS}</p><button class="btn line small" type="button" data-copy="#pr-founders">Copy</button></div>
  </div>
  <p class="sd-ok" role="status" aria-live="polite" data-copy-ok></p>
</div></section>

<section class="band ivory" id="moments"><div class="wrap split">
  <div class="stack"><span class="eyebrow">For photographers and crews</span><h2>The moments to capture.</h2><p class="lead">Accredited press are briefed on positions before each moment.</p></div>
  {info([("Fri 18:30", "The Royal Arrival: Fontomfrom drums and the red carpet"), ("Fri 19:45", "The drums begin: drummers lead every guest to table"), ("Sat 00:00", "The midnight toast: the hall rises as Independence Day begins"),
         ("Sat 12:00", "The anniversary moment: drumming and a reading of the declaration of independence"), ("Sat 17:00", "The dance circle: Azonto, Kpanlogo and Afrobeats"), ("Sun 14:00", "The Wall of Mothers: every name honoured aloud")])}
</div></section>

<section class="band white" id="images"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Images</span><h2>Use them with credit.</h2><p class="lead">Photographs from the night follow within seven days.</p></div>
  <ul class="pr-imgs pr-imgs2">{"".join(pimg(k, a) for k, a in PR_IMG)}</ul>\n  <p class="muted" style="margin-top:18px">Portraits of Asantewaa and Adwoa and further images are sent on request.</p>
</div></section>

<section class="band ivory" id="social"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Social copy</span><h2>Post it as it is.</h2><p class="lead">Hashtags: <b>#GhanaAt70UK</b> and <b>#GhanaAt70London</b>.</p></div>
  <div class="pr-social">{"".join(f'<div class="pr-box"><h3>{a}</h3><p id="pr-s{i}">{b}</p><button class="btn line small" type="button" data-copy="#pr-s{i}">Copy</button></div>' for i, (a, b) in enumerate(SOCIAL))}</div>
  <p class="sd-ok" role="status" aria-live="polite" data-copy-ok></p>
</div></section>

<section class="band white" id="accreditation"><div class="wrap split">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">Accreditation and interviews</span><h2>Cover it in person.</h2><p class="lead">Journalists, broadcasters, podcasters, photographers, community and diaspora media, and creators of every size can request accreditation for one or all three days. Interviews with Asantewaa and Adwoa are available on request.</p></div>
    {info([("Call Asantewaa", '<span data-phone>07824 555307</span>'), ("Email", '<span data-email>ghanaat70.uk@gmail.com</span>'), ("Reply", "Accreditation confirmed within three working days")])}</div>
  {enquiry_form("press")}
</div></section>
''')


    # ================= WHAT TO WEAR =================
    def dc_list(title, items, cls=""):
        return f'<div class="dc-col {cls}"><h3 class="h4">{title}</h3><ul>' + "".join(f"<li>{x}</li>" for x in items) + "</ul></div>"
    def dc_chapter(anchor, tone, num, day, code, lead, ph1, ph2, cols, note, pay, label, mood=None):
        pics = ('<div class="dc-mood">' + "".join(f'<figure class="dc-mood-f">{photo(*m[0])}<figcaption>{m[1]}</figcaption></figure>' for m in mood) + '</div>') if mood else f'<div class="dc-frame f1">{photo(*ph1)}</div><div class="dc-frame f2">{photo(*ph2)}</div>'
        return f"""<article class="dcx-slide{' has-mood' if mood else ''}" id="{anchor}" aria-label="{num} of III, {day}"><div class="dc-in">
  <div class="dc-photos">{pics}<span class="dc-num">{num}</span></div>
  <div class="dc-copy"><span class="eyebrow">{day}</span><h2>{code}</h2><div class="dc-rule"><i></i>{adl("adinkrahene")}<i></i></div><p class="lead">{lead}</p>
    <div class="dc-cols">{cols}</div>
    <p class="dc-note">{note}</p>
    <div class="btn-row"><a class="btn gold" href="tickets.html" data-pay="{pay}">{label}</a></div></div>
</div></article>"""
    FRI = dc_chapter("friday", "dc-dark", "I", "Friday 5 March 2027 · The Royal Jubilee Gala", "Royalty Kente or Black Tie Gala.",
        "Kente, gold and black tie. Nothing less.",
        ("look/a2", "A king in a black suit with Kente panels and a queen in a Kente mermaid gown, arm in arm before a columned City facade", "ph", "50% 0%", "(max-width:900px) 50vw, 24vw"), ("look/a5", "A king in a Kente print dinner jacket with black lapels and a queen in a one shoulder Kente print gown with a high slit and matching headwrap", "ph", "50% 0%", "(max-width:900px) 50vw, 24vw"),
        dc_list("Queens", ["Kente kaba and slit", "Long evening gown", "Gold and beads"])
        + dc_list("Kings", ["Full Kente, toga style", "Black tie", "Black tie with Kente"]),
        "Long gowns, please, no short dresses. Last entry 19:45.", "gala", "Take your royal seat",
        mood=[(("look/t1", "A crowned queen in traditional Kente cloth wrapped over one shoulder and a white lace skirt, with gold beads, seated on a carved stool", "ph"), "Traditional Kente"),
              (("look/a2", "A king in black with Kente panels and a queen in a Kente mermaid gown", "ph"), "Black tie with Kente"),
              (("look/a5", "A king in a Kente print dinner jacket and a queen in a one shoulder Kente print gown", "ph"), "Kente print")])
    SAT = dc_chapter("saturday", "dc-ivory", "II", "Saturday 6 March 2027 · Ghana Day Festival", "Print and denim.",
        "Relaxed. Ready to dance.",
        ("look/s1", "A woman in a blue and green print peplum jacket and wide trousers", "ph", "50% 0%", "(max-width:900px) 50vw, 24vw"), ("look/s2", "A man in a green and cream print short sleeve shirt with black trousers", "ph", "50% 0%", "(max-width:900px) 50vw, 24vw"),
        dc_list("Her", ["A print top with jeans", "Print trouser suit or midi dress", "Black Stars shirt, flats or block heels"])
        + dc_list("Him", ["Print shirt or Black Stars shirt", "Jeans or chinos", "Loafers or clean trainers"]),
        "Dancing? Wear what moves.", "ghanaday", "Book Saturday")
    SUN = dc_chapter("sunday", "dc-white", "III", "Sunday 7 March 2027 · Women of the Motherland", "Sunday best.",
        "Straight from church.",
        ("look/p7", "A woman in an emerald print gown with puff sleeves and a matching headwrap", "ph", "50% 0%", "(max-width:900px) 50vw, 24vw"), ("look/p9", "A woman in a violet print peplum suit with flared sleeves", "ph", "50% 0%", "(max-width:900px) 50vw, 24vw"),
        dc_list("Her", ["Lace or print", "Church best", "Duku, gele or headwrap"])
        + dc_list("Family", ["Toning colours", "Smart shirts or suits", "Gold and beads"]),
        "Already dressed.", "sunday", "Book Sunday")
    def kl_row(names, alts, rev=""):
        D = LDIMS
        def fig(n, a, hidden):
            w, h = D[n]
            at = ' aria-hidden="true"' if hidden else ''
            return f'<figure class="kl-shot"{at}><img src="images/look/{n}-720.jpg" srcset="images/look/{n}-720.jpg 720w, images/look/{n}-1400.jpg 1400w" sizes="(max-width:760px) 70vw, 34vw" width="{w}" height="{h}" alt="{"" if hidden else a}" loading="eager" decoding="async"></figure>'
        items = "".join(fig(n, a, False) for n, a in zip(names, alts, strict=True))
        dup = "".join(fig(n, a, True) for n, a in zip(names, alts, strict=True))
        reps = max(1, -(-12 // len(names)))
        return f'<div class="kl-row{rev}"><div class="kl-track">{items}{dup * (2 * reps - 1)}</div></div>'
    QUEENS = ["A crowned queen in gold Kente with layered gold jewellery", "Bright Kente wrap with a gold headpiece and bangles", "A Kente corset dress with coral bead necklaces", "A Kente kaba with gold beads and a gold crown band", "An off the shoulder Kente dress with coral and gold beads", "Kente wrapped and draped, gold beads, seated", "Strapless Kente with layered gold necklaces", "An off the shoulder Kente bodice with white beads", "A Kente mermaid gown with a gold headpiece", "A Kente gown with a dramatic peplum in bold colours"]
    KINGS = ["Full Kente worn over the left shoulder, with gold", "Green and gold Kente cloth, worn the royal way", "Bold Kente cloth carried with a cane", "Two friends in full Kente with gold", "Three friends in Kente cloth in a garden", "Kente cloth with gold bracelets, seated"]
    PRINTS = ["A plum and print gown with ruffled shoulders", "A teal print mermaid gown with lace and ruffles", "A red and gold zigzag print gown with a black velvet bodice", "A brocade print two piece with a sculpted collar", "A violet print peplum suit with flared sleeves", "A teal print peplum gown with lace sleeves", "A magenta print gown with bishop sleeves"]
    COUPLES = ["A couple in gold: a sculpted gown and a Kente jacket", "A queen in Kente and gold beside a king in a Kente dinner jacket", "A couple in gold Kente, a fan in her hand", "A couple in purple Kente: a strapless gown and an agbada"]
    LOOKBOOK = f"""<section class="band dc-dark kl-band" id="lookbook"><div class="wrap">
  <div class="kl-intro">
    {photo("look/q1", "A crowned queen in gold Kente with layered gold jewellery", "kl-hero", "50% 0%", "(max-width:900px) 92vw, 44vw")}
    <div class="kl-intro-copy"><span class="eyebrow">Dress inspiration</span><h2>We are going all out. Do the same.</h2><div class="dc-rule"><i></i>{adl("adinkrahene")}<i></i></div>
      <p class="lead">Candlelight, gold and Kente. Every guest sets the standard.</p>
      <ol class="kl-keys"><li><b>Go royal</b><span>Full Kente, a long evening gown or immaculate black tie.</span></li><li><b>Add gold</b><span>Krobo beads, gold bangles, a crown band or cufflinks.</span></li><li><b>Dress for the portrait</b><span>Your royal portrait is taken from 19:00.</span></li></ol></div>
  </div>
  <h3 class="kl-h">For queens</h3>
  {kl_row(["q4","q5","q6","q7","q9"], QUEENS[3:7] + [QUEENS[8]])}
  <h3 class="kl-h">For kings and royal couples</h3>
  {kl_row(["k2","k3","k4","k5","k6","c1","c3"], KINGS[1:] + [COUPLES[0], "A couple in matching gold Kente: a tailored suit and a sculpted mermaid gown"], " rev")}
  <h3 class="kl-h">Print and polish, for the Gala and every day</h3>
  {kl_row(["p4","p5","p2","p8","p10","p11"], PRINTS[:2] + ["A fitted patchwork Kente print gown with an off the shoulder neckline"] + [PRINTS[3]] + PRINTS[5:], " rev")}
  <!--BT-->
</div></section>
"""
    KSVG = '''<defs><pattern id="kp" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="#E2A72E"/><rect width="6" height="6" fill="#0E5238"/><rect x="6" y="6" width="6" height="6" fill="#B3261E"/><rect x="0" y="5" width="12" height="2" fill="#14110D"/></pattern></defs>'''
    kfig_n = [0]
    def kfig(cloth):
        kfig_n[0] += 1
        k = f"kp{kfig_n[0]}"
        return kfig_raw(cloth.replace("url(#kp)", f"url(#{k})"), KSVG.replace('id="kp"', f'id="{k}"'))
    def kfig_raw(cloth, KSVG):
        return f'<svg viewBox="0 0 120 160" aria-hidden="true">{KSVG}<circle cx="60" cy="26" r="13" fill="#5A3A26"/><path d="M38 48 Q60 40 82 48 L88 104 Q60 110 32 104 Z" fill="#5A3A26"/><path d="M40 104 L44 150 M80 104 L76 150" stroke="#5A3A26" stroke-width="9" stroke-linecap="round"/><path d="M38 52 Q26 76 30 100 M82 52 Q94 76 90 100" stroke="#5A3A26" stroke-width="8" stroke-linecap="round" fill="none"/>{cloth}</svg>'
    STEPS = [
        ("Open the cloth", "Hold the cloth open behind you, the top edge level with your shoulders.", kfig('<rect x="18" y="44" width="84" height="66" fill="url(#kp)" opacity=".95"/><circle cx="60" cy="26" r="13" fill="#5A3A26"/>')),
        ("Under the right arm", "Bring the right end under your right arm and across the chest. The right shoulder stays bare.", kfig('<path d="M34 62 L86 50 L90 112 L32 112 Z" fill="url(#kp)"/>')),
        ("Over the left shoulder", "Throw the long end over your left shoulder so it falls down your back.", kfig('<path d="M34 64 L74 44 L90 44 L92 118 L30 116 Z" fill="url(#kp)"/><path d="M74 44 L92 40 L98 96 L88 100 Z" fill="url(#kp)" opacity=".85"/>')),
        ("Gather and hold", "Gather the folds over your left arm and hold them in your left hand. Walk slowly, like royalty.", kfig('<path d="M34 64 L74 44 L90 44 L92 132 L30 130 Z" fill="url(#kp)"/><path d="M88 60 Q104 82 92 112 L84 108 Q94 84 82 62 Z" fill="#14110D" opacity=".25"/><circle cx="90" cy="104" r="5" fill="#5A3A26"/>')),
    ]
    PINS = [("1", "24%", "56%"), ("2", "9%", "25%"), ("3", "45%", "17%"), ("4", "17%", "88%"), ("5", "71%", "21%"), ("6", "74%", "33%"), ("7", "80%", "62%"), ("8", "70%", "95%")]
    HIM = [("The full cloth", "One full cloth, woven strip by strip and sewn together. Every pattern has a name and a meaning."), ("Right shoulder bare", "The cloth passes under the right arm, so the right shoulder stays bare, the way the chiefs wear it."), ("Over the left shoulder", "The long end is thrown over the left shoulder and falls down the back."), ("Ahenema sandals", "Royal leather sandals, handmade. With black tie, polished shoes.")]
    HER = [("The headpiece", "A gold band or a sculpted duku, tall and proud for the Gala."), ("Beads and gold", "Krobo beads at the neck, gold at the wrist and the arm. Wear the pieces handed down to you."), ("Two cloths", "A wrapped cloth to the ankle and an upper cloth across the body, or a kaba and slit in Kente."), ("Jewelled sandals", "Ahenema or jewelled evening sandals, never trainers.")]
    def kg_list(items, start):
        return "".join(f'<li><span class="kg-n">{start+i}</span><div><b>{t}</b><p>{d}</p></div></li>' for i, (t, d) in enumerate(items))
    BTSVG = '''<svg class="bt-ill" viewBox="0 0 300 466" role="img" aria-label="Illustration of a classic black dinner jacket with a black bow tie and white dress shirt"><defs><radialGradient id="btg" cx="50%" cy="30%" r="80%"><stop offset="0" stop-color="#14523A"/><stop offset="1" stop-color="#062619"/></radialGradient></defs><rect width="300" height="466" fill="url(#btg)"/>
<path d="M150 86 L118 96 L64 122 Q44 132 42 168 L36 420 L264 420 L258 168 Q256 132 236 122 L182 96 Z" fill="#0B0B0B" stroke="#D4A62A" stroke-width="1.6"/>
<path d="M126 100 L150 300 L174 100 Z" fill="#F4EFE4"/>
<path d="M118 96 Q96 190 150 300 Q122 210 134 104 Z" fill="#1A1A1A" stroke="#D4A62A" stroke-width="1.2"/><path d="M182 96 Q204 190 150 300 Q178 210 166 104 Z" fill="#1A1A1A" stroke="#D4A62A" stroke-width="1.2"/>
<path d="M130 104 L150 116 L170 104 L170 128 L150 118 L130 128 Z" fill="#0B0B0B" stroke="#D4A62A" stroke-width="1.2"/><rect x="145" y="111" width="10" height="12" rx="2" fill="#0B0B0B" stroke="#D4A62A" stroke-width="1"/>
<circle cx="150" cy="160" r="3.2" fill="#0B0B0B"/><circle cx="150" cy="196" r="3.2" fill="#0B0B0B"/><circle cx="150" cy="232" r="3.2" fill="#0B0B0B"/>
<circle cx="150" cy="316" r="5" fill="#0B0B0B" stroke="#D4A62A" stroke-width="1.2"/>
<path d="M204 196 L232 192 L230 202 L206 205 Z" fill="#F4EFE4"/><path d="M42 168 L30 410 M258 168 L270 410" stroke="#D4A62A" stroke-width="1" opacity=".5"/>
<path d="M120 420 L120 446 M180 420 L180 446" stroke="#D4A62A" stroke-width="1" opacity=".4"/></svg>'''
    BT = [("b4", "The Kente dinner jacket", "Full Kente, black satin lapels and a black bow tie. The boldest choice.")]
    KGUIDE = f"""<section class="band kg-band" id="kente"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">The style guide</span><h2>The art of wearing Kente.</h2><div class="divider"><i></i></div><p class="lead">Read it like a map. Every detail has a meaning.</p></div>
  <div class="kg">
    <div class="kg-side"><h3 class="kg-h">For kings</h3><ol class="kg-list">{kg_list(HIM, 1)}</ol></div>
    <figure class="kg-art"><img src="images/kente/kente-guide-1200.jpg" srcset="images/kente/kente-guide-640.jpg 415w, images/kente/kente-guide-1200.jpg 830w" sizes="(max-width:900px) 92vw, 34vw" width="830" height="1110" alt="Illustration of a king in full Kente over the left shoulder with ahenema sandals, and a queen in two Kente cloths with beads, a gold headband and sandals" loading="lazy">{"".join(f'<span class="kg-pin" style="left:{x};top:{y}" aria-hidden="true">{n}</span>' for n, x, y in PINS)}</figure>
    <div class="kg-side"><h3 class="kg-h">For queens</h3><ol class="kg-list" start="5">{kg_list(HER, 5)}</ol></div>
  </div>
  <h3 class="kg-sub">How to wrap the cloth, in four moves.</h3>
  <ol class="kg-steps">{"".join(f'<li><div class="kg-fig">{svg}</div><span class="kg-n">{i}</span><b>{t}</b><p>{d}</p></li>' for i, (t, d, svg) in enumerate(STEPS, 1))}</ol>
</div></section>
"""
    BTBLOCK = f"""<div class="kl-bt">
  <h3 class="kg-sub">Black tie, with or without Kente.</h3>
  <p class="kg-subl">No Kente? Classic black tie is always correct. Have Kente? Let it do the talking.</p>
  <div class="kg-bt"><figure class="bt-classic">{BTSVG}<figcaption><b>Classic black tie</b><span>Dinner jacket, black bow tie, white shirt and polished shoes.</span></figcaption></figure>{"".join(f'<figure><img src="images/look/{k}-720.jpg" srcset="images/look/{k}-720.jpg 720w, images/look/{k}-1400.jpg 1400w" sizes="(max-width:760px) 50vw, 25vw" width="{LDIMS[k][0]}" height="{LDIMS[k][1]}" alt="{t}" loading="lazy"><figcaption><b>{t}</b><span>{d}</span></figcaption></figure>' for k, t, d in BT)}</div>
</div>"""
    page("dress-code", "What to Wear | Royal Dress Code for Ghana at 70 UK London 2027", "The dress code for Ghana at 70 UK: Royalty Kente or Black Tie on Friday, Ankara print on Independence Day and Sunday best on Mothering Sunday.",
         page_head("What to wear", "Dress as royalty.", "Three days, three dress codes, and the art of wearing Kente. Everything you need to arrive certain, and magnificent.", "black", "duafe",
                   '<div class="chips"><a class="chip" href="#friday">Friday: Royalty Kente or Black Tie</a><a class="chip" href="#saturday">Saturday: print and denim</a><a class="chip" href="#sunday">Sunday best</a><a class="chip" href="#lookbook">Dress inspiration</a><a class="chip" href="#kente">How to wear Kente</a></div>', "The royal dress code") + f"""
<section class="band dc-dark dcx-band" id="dress-codes"><div class="wrap">
  <div class="dcx" data-xc data-xc-auto="7000">
    <div class="xc-top"><div class="xc-tabs dcx-tabs" role="tablist" aria-label="The three dress codes">
      <button type="button" role="tab" class="xc-tab on" aria-selected="true" data-xc-go="0"><span>I</span>Friday · Royalty Kente or Black Tie</button>
      <button type="button" role="tab" class="xc-tab" aria-selected="false" data-xc-go="1"><span>II</span>Saturday · Ankara print</button>
      <button type="button" role="tab" class="xc-tab" aria-selected="false" data-xc-go="2"><span>III</span>Sunday · Sunday best</button></div>
      <div class="xc-arrows"><button type="button" class="xc-btn" data-xc-prev aria-label="Previous dress code"><i></i></button><button type="button" class="xc-btn next" data-xc-next aria-label="Next dress code"><i></i></button></div></div>
    <div class="xc-track dcx-track" data-xc-track tabindex="0" aria-label="Dress codes for the three days, swipe or use the arrows">{FRI}{SAT}{SUN}</div>
    <div class="xc-bar"><i data-xc-bar></i></div>
  </div>
</div></section>
{LOOKBOOK.replace("<!--BT-->", BTBLOCK)}{KGUIDE}
<section class="band dc-dark dc-colours"><div class="wrap">
  <div class="section-head center"><span class="eyebrow">Colours and their meaning</span><h2>Colours with meaning.</h2><div class="divider"><i></i></div></div>
  <div class="dc-sw">
    <div><span class="sw-c" style="background:linear-gradient(135deg,#F3D27A,#B8862B)"></span><b>Gold</b><p>Royalty, wealth and the Gold Coast. The colour of the Gala.</p></div>
    <div><span class="sw-c" style="background:#F7F3EA"></span><b>White</b><p>Joy, purity and victory. A colour of celebration.</p></div>
    <div><span class="sw-c" style="background:#0E5238"></span><b>Green</b><p>The forests and the fields of home.</p></div>
    <div><span class="sw-c" style="background:linear-gradient(90deg,#CE1126 33%,#FCD116 33%,#FCD116 66%,#006B3F 66%)"></span><b>Red, gold and green</b><p>The flag, worn together. A celebration.</p></div>
  </div>
</div></section>
<section class="band white" id="dress-faq"><div class="wrap split">
  <div class="stack"><span class="eyebrow">Dress code questions</span><h2>Before you dress.</h2><p class="lead">Still unsure? Call Asantewaa on <span data-phone>07824 555307</span> and she will help.</p></div>
  <div class="faq-list">
    <details><summary>Do I have to wear Kente to the Gala?</summary><p>No. Royalty Kente or Black Tie Gala means either is perfect. A long evening gown, a dinner jacket or a fugu smock are all welcome.</p></details>
    <details><summary>Can I wear a short dress to the Gala?</summary><p>The Gala is a long gown evening. Please choose a floor length or ankle length gown, or Kente cloth, rather than a short dress. Black is always welcome.</p></details>
    <details><summary>I am not Ghanaian. Can I wear Kente?</summary><p>Yes. Kente and Ghanaian cloth are for everyone, worn with respect and joy. New to Kente? Add it when you book and we help you wear it properly.</p></details>
    <details><summary>Can I wear the dress of another African nation?</summary><p>Yes. Wear your heritage proudly. Agbada, boubou, kitenge and every royal dress of the continent belong at the Gala.</p></details>
    <details><summary>Where can I find Kente in time?</summary><p>Add Kente and gold when you book and our Kente partners will hold sashes, stoles and accessories for you, ready to collect.</p></details>
    <details><summary>I am in mourning. Can I still come?</summary><p>Yes, and you are very welcome. Come as you are. Black is always welcome, and so is your mourning cloth. This is a family celebration, and family includes everyone.</p></details>
    <details><summary>What do I wear on my head?</summary><p>A headwrap or gele is the crown of this event. Keep it clear of the view of the guests behind you.</p></details>
    <details><summary>Is there a cloakroom?</summary><p>Yes, staffed from the moment doors open on every day.</p></details>
    <details><summary>Will I be refused entry?</summary><p>We would rather welcome you than turn you away. Please follow the dress code: guests in sportswear at the Gala may be asked to change.</p></details>
  </div>
</div></section>
""")



    # ================= PRIVACY =================
    page("credits", "Photo Credits | Ghana at 70 UK", "Photo and film credits for the Ghana at 70 UK website: venue photography and licensed photographs, with thanks to each photographer.",
         page_head("Credits", "With thanks.", "The photographers and partners whose images help tell this story.", "gold", "nsoromma") + f'''
<section class="band white"><div class="wrap prose credits-page">
  <p>Some images on this site are design concepts created for Ghana at 70 UK.</p>
  <h2 class="h3">Venue</h2><p>Venue photography courtesy of Banking Hall, London.</p>
    <h2 class="h3">Photographs</h2><p>Used under the Unsplash and Pixabay licences. They are not photographs of Ghana at 70 UK guests, speakers or partners. With thanks to {CREDITS}.</p>
  <h2 class="h3">Film</h2><p>The opening of the Ghana Passport Office in Aldgate East, produced by the Ghana at 70 UK team.</p>
</div></section>
''', '<meta name="robots" content="noindex">')
    page("privacy", "Privacy Notice | Ghana at 70 UK", "How Ghana at 70 UK uses the details you share through this website, how long we keep them and how to ask us to change or delete them.",
         page_head("Privacy notice", "Your details, handled with care.", "What we collect, why, who helps us, how long we keep it and how to reach us.", "green", "eban") + '''
<section class="band white"><div class="wrap legal">
  <h2 class="h3">Who we are</h2>
  <p>INTEROPA Holidays Ltd is the data controller for details shared through this website. Registered in England and Wales, company number 01190602. Registered office: C/O Citycas, Room 540, Linen Hall, 162 to 168 Regent Street, London W1B 5TF. Trading address: 21 to 23 Chilworth Street, London W2 3HA.</p>
  <h2 class="h3">What we collect</h2>
  <p class="muted">Last updated <b>19 November 2026</b>.</p>
  <ol><li><b>When you book:</b> your name, email and mobile, the tickets you choose, how you pay, the name of a guest if the ticket is a gift, and your confirmation that you accept the terms of sale. Card details are entered on the secure pages of our payment provider. We never see or store your card number.</li>
    <li><b>When you send a form:</b> your name and email, and anything else you choose to add, such as your mobile, party size, how you heard about us, the Sunday sessions you would like and your message.</li>
    <li>For exhibitors, partners, speakers and press: your organisation, website and the details of your application.</li>
    <li>For the Wall of Mothers: the name you ask us to display.</li>
    <li>How you reached us: the page you arrived on, the website that referred you and any campaign tag in the link.</li>
    <li><b>At the event:</b> your ticket scan at the door. Photographers and film crews work throughout the event, so you may appear in photos and film.</li></ol>
  <h2 class="h3">Why we use it</h2>
  <ol><li>To take your booking and payment, issue your tickets, check you in and send ticket and event information. This is needed to provide what you bought.</li>
    <li>To answer your enquiry or application. This is needed to provide what you asked for.</li>
    <li>To send news about Ghana at 70 UK, only where you have agreed. You can unsubscribe from any email.</li>
    <li>To arrange visa support and flights from Ghana with Adansi Travels, our travel partner in Ghana, only where you ask for it on our travel form.</li>
    <li>To introduce you to our partners in banking, property and money transfer, only where you tick the box at booking. We share your name, email and phone with one partner in each of those categories and no one else, and you can withdraw at any time.</li>
    <li>Your sector, only if you choose to tell us at booking. We share it with partners only as an anonymised total for the room, never with your name.</li>
    <li>To understand which channels bring guests to us, so we spend our marketing well. This is in our legitimate interest.</li>
    <li>To use photos and film of the event to share and promote Ghana at 70 UK. This is in our legitimate interest. If you would rather not appear, tell our photographers on the day, or ask us afterwards to remove an image of you that we have published.</li>
    <li>To keep booking and payment records as tax and company law requires.</li></ol>
  <h2 class="h3">Who helps us</h2>
  <p>We never sell your details. We share them only with the providers who run the service for us, and only what each one needs:</p>
  <ol><li>Ticket Tailor, which issues tickets and runs check in.</li><li>Stripe, which takes card payments.</li><li>GoHighLevel, our customer relationship and email platform.</li><li>Cloudflare, which hosts this website and receives the forms.</li><li>Adansi Travels and our partners in banking, property and money transfer, only where you ask us to introduce you, as set out above.</li></ol>
  <p>Some of these providers are based in the United States, and your details are transferred under the safeguards UK law requires.</p>
  <h2 class="h3">On your device</h2>
  <h2 id="cookies">Cookies and measurement</h2>
  <p>Your browser stores a few small preferences: whether Comfort view is on, whether you closed the booking card, your cookie choice and your ticket selection while you book, so you can finish later. Fonts load from Google Fonts, which receives your IP address.</p>
  <p><b>Without cookies, from your first visit.</b> We count visits to improve this site: pages viewed, the country and city your connection comes from, the website or advert that brought you, your device type and how far you scroll. Cloudflare Web Analytics does this without cookies. Google Analytics runs in a cookieless mode until you choose. Nothing identifies you by name.</p>
  <p><b>With your permission.</b> If you choose Accept all, Google Analytics, Google Ads, Meta, TikTok, LinkedIn, Snapchat and Microsoft Clarity may set cookies to measure our adverts and see how pages are used, including anonymised recordings of clicks and scrolling. If you choose Reject all, none of these load.</p>
  <p><b>When you send a form.</b> We record the page you used, the campaign or advert that brought you, your device, language and time zone, and the country, region and city of your connection, alongside the details you give us, so we know which channels bring guests.</p>
  <p>Change your choice at any time with <a href="#cookies" data-cookie-settings>Cookie settings</a>, also in the footer of every page.</p>
  <h2 class="h3">How long we keep it</h2>
  <ol><li>Enquiries and form details are kept until 31 May 2027, then deleted, unless you bought a ticket or agreed to hear from us.</li><li>If you agreed to hear from us, we keep your name and email until you unsubscribe.</li><li>Booking and payment records are kept for six years after the event, as UK tax law requires.</li></ol>
  <h2 class="h3">Your rights</h2>
  <p>You can ask to see, correct or delete your details, object to their use or withdraw consent at any time. We reply within one month. You may also complain to the ICO, the UK data protection regulator, at ico.org.uk.</p>
  <p class="muted">Contact: <span data-email>ghanaat70.uk@gmail.com</span>, or write to INTEROPA Holidays Ltd, 21 to 23 Chilworth Street, London W2 3HA.</p>
</div></section>
''')


    # ================= ASSETS =================
    os.makedirs(os.path.join(OUT, "cal"), exist_ok=True)
    for slug, k in (("royal-jubilee-gala", "gala"), ("ghana-day-festival", "ghanaday"), ("women-of-the-motherland", "sunday")):
        with open(os.path.join(OUT, "cal", slug + ".ics"), "w", newline="") as f:
            f.write(sd_ics(k, SITE_URL, "07824 555307"))
    with open(os.path.join(OUT, "llms.txt"), "w") as f:
        f.write(f"""# Ghana at 70 UK

> The UK celebration of the Ghana 70th Platinum Jubilee, held over three days in London, 5 to 7 March 2027.

## Events
- The Royal Jubilee Gala of Kings and Queens: Friday 5 March 2027, Banking Hall, 14 Cornhill, City of London, moments from the Bank of England, 18:30 to 00:30. A spectacular Ghanaian gala dinner and party of royals with highlife, hiplife, Afrobeats and everything in between, live, and a midnight toast. Dress code Royalty Kente or Black Tie Gala. GBP 275 per guest, early bird GBP 250. {SITE_URL}/royal-gala
- Ghana Day Festival: Saturday 6 March 2027 (Ghana Independence Day), Banking Hall, 11:00 to 18:00. The Ghana Day Festival: DJ and dancing all day, forty chosen stands, quiz and dance circle, bar, come and go all day. Ages 5 and over, no pushchairs or buggies. GBP 50. {SITE_URL}/ghana-day
- Women of the Motherland: Sunday 7 March 2027 (Mothering Sunday), Banking Hall, for women of African heritage and their families, doors 11:00, one sitting with everyone together from 12:00, networking hour at 16:00, close 18:30. Afternoon tea, the Wall of Mothers, Voices of the Motherland poems and stories, a family portrait and the networking hour. Talks and masterclasses not yet confirmed: guests register their interest. GBP 150 per guest. {SITE_URL}/women-of-the-motherland

## Booking
- Book golden tickets, on sale now: {SITE_URL}/tickets
- Sponsorship pack: {SITE_URL}/partners#pack
- Contact: Asantewaa, 07824 555307, ghanaat70.uk@gmail.com

## Quick answers
- What is Ghana at 70 UK? The UK celebration of the Ghana 70th Platinum Jubilee, held in London over three days at Banking Hall, 5 to 7 March 2027, marking seventy years of Ghanaian independence.
- When is Ghana Independence Day 2027? Saturday 6 March 2027, seventy years after 6 March 1957. In London it is marked by the Ghana Day Festival, 11:00 to 18:00.
- Where is it? Banking Hall, 14 Cornhill, London EC3V 3ND, moments from the Bank of England. Bank station is about two minutes on foot. Two floors connected by stairs only.
- How much are tickets? The Royal Jubilee Gala GBP 275 (early bird GBP 250). Ghana Day Festival GBP 50. Women of the Motherland GBP 150. Weekend Pass for all three days GBP 435, which saves GBP 40 on GBP 275 + GBP 50 + GBP 150 = GBP 475.
- Are there booking fees? No. Every price shown is the full price.
- Where do I buy tickets? Only on the official website, {SITE_URL}/tickets. All sales are final, tickets can be transferred to a named guest, and every ticket is refunded in full if the event is cancelled.
- What is the dress code? Friday: Royalty Kente or Black Tie. Saturday: print and denim, Ankara or a Black Stars shirt. Sunday: Sunday best.
- Can children come? Ages 5 and over on all three days, under 18s with an adult and every guest with a ticket. No under 5s, high chairs, pushchairs or buggies. The bar is for over 18s only.
- Is there a Ghana Independence party or dance in London in 2027? Yes. The Royal Jubilee Gala is the dinner and dance on the eve, Friday 5 March, and the Ghana Day Festival is the daytime party with a DJ and dancing on Independence Day, Saturday 6 March.
- Is there a Mothers Day event for African women in London? Yes. Women of the Motherland, a Mothering Sunday afternoon tea for women of African heritage and their families, Sunday 7 March 2027.
- Is alcohol included? No ticket includes alcohol. The bar takes card only.
- Can a group sit together? Yes. Choose Royal party of 10 when booking the Gala: 10 x GBP 275 = GBP 2,750.
- Can I exhibit? Yes, on Saturday and Sunday only. Market stand GBP 250 + VAT, feature stand GBP 600 + VAT. {SITE_URL}/exhibit
- Media and creators: accreditation and the press kit at {SITE_URL}/press

## Pages
- Our story: {SITE_URL}/about
- Plan your visit: {SITE_URL}/visit
- Travel and stay: {SITE_URL}/stay
- What to wear: {SITE_URL}/dress-code
- Questions: {SITE_URL}/faq
""")

    with open(os.path.join(OUT, "favicon.svg"), "w") as f:
        f.write(brandlogo.symbol_tile())
    with open(os.path.join(OUT, "og.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">' + GOLD_DEF.format(id="g") +
                '<rect width="1200" height="630" fill="#0B3D2C"/><rect width="1200" height="14" fill="#D4A62A"/><rect x="0" y="0" width="400" height="14" fill="#CE1126"/><rect x="800" y="0" width="400" height="14" fill="#006B3F"/>'
                f'<g transform="translate(860 60) scale(1.3)" opacity=".35"><path d="{GH["d"]}" fill="none" stroke="#F6DB86" stroke-width="1.5"/></g>'
                '<text x="80" y="190" font-family="Arial Narrow,Arial,sans-serif" font-weight="800" font-size="60" letter-spacing="18" fill="#F6DB86">GHANA AT</text>'
                '<text x="70" y="500" font-family="Georgia,serif" font-weight="700" font-size="360" fill="url(#g)">7</text>'
                '<circle cx="420" cy="380" r="120" fill="none" stroke="url(#g)" stroke-width="18"/><circle cx="420" cy="380" r="72" fill="none" stroke="url(#g)" stroke-width="8"/>'
                '<polygon transform="translate(380 338) scale(.8)" points="50,4 61.2,37.6 96.6,37.6 68.1,58.6 78.9,92.4 50,71.6 21.1,92.4 31.9,58.6 3.4,37.6 38.8,37.6" fill="#16201B" stroke="#D4A62A" stroke-width="3"/>'
                '<text x="620" y="330" font-family="Georgia,serif" font-style="italic" font-size="44" fill="#FFFFFF">London</text>'
                '<text x="620" y="390" font-family="Arial,sans-serif" font-weight="700" font-size="30" letter-spacing="4" fill="#F6DB86">5 TO 7 MARCH 2027</text>'
                '<text x="620" y="450" font-family="Arial,sans-serif" font-size="24" fill="#E3E8DF">The Royal Jubilee Gala · Ghana Day Festival</text>'
                '<text x="620" y="486" font-family="Arial,sans-serif" font-size="24" fill="#E3E8DF">Women of the Motherland</text>'
                '<rect y="600" width="1200" height="30" fill="#D4A62A"/><rect x="560" y="606" width="80" height="18" fill="#006B3F"/><rect x="586" y="610" width="28" height="10" fill="#CE1126"/></svg>')
    pages = ["", "royal-gala", "ghana-day", "women-of-the-motherland", "about", "tickets", "stay", "visit", "dress-code", "gallery", "faq", "partners", "exhibit", "contact", "press", "terms", "privacy"]
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE_URL}/{p}</loc><lastmod>{__import__('datetime').date.today().isoformat()}</lastmod></url>\n" for p in pages) + "</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot", "Applebot-Extended", "facebookexternalhit", "meta-externalagent"]
        f.write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /thank-you\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    # Cloudflare Pages settings: security headers, caching, calendar files
    with open(os.path.join(OUT, "_headers"), "w") as f:
        f.write("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
                "\n/site.css\n  Cache-Control: public, max-age=3600\n/site.js\n  Cache-Control: public, max-age=3600\n/images/*\n  Cache-Control: public, max-age=2592000\n"
                "\n/cal/*\n  Content-Type: text/calendar; charset=utf-8\n  Content-Disposition: attachment\n")


if __name__ == "__main__":
    build()
    print("built", OUT)
