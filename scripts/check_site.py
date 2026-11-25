"""Release checks for the Ghana at 70 UK website. No installs needed.

    python scripts/check_site.py            check the site folder
    python scripts/check_site.py --base main  also report protected files changed against main

Exit code 1 if any rule fails. Runs on every pull request (.github/workflows/checks.yml).
"""
import glob, html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
fails, notes = [], []


def text_of(raw):
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)))


# House rules on the words guests read. Each: name, pattern, pages where it is allowed.
WORDS = [
    ("Reserve: the call to action is Book now", r"\breserv(e|ed|ing|ation)\b(?<!rights reserved)", []),
    ("Sobolo is removed", r"\bsobolo\b", []),
    ("UnityLink is not on the site", r"unity ?link", []),
    ("No Weekend Pass", r"weekend pass", []),
    ("No early bird wording", r"early ?bird", []),
    ("No places left or scarcity claims", r"places left|tickets remaining|selling fast|almost sold out|only \d+ left", []),
    ("No capacity numbers", r"\bfirst \d+\b|\b\d+ (tables|seats|stands|visitors)\b|up to fifty", []),
    ("Venue not sold: Bank of England only in the directions", r"bank of england|a few steps from", ["visit.html"]),
    ("Venue not sold: no heritage selling", r"grand banking hall|1930s banking hall|art deco", []),
    ("More than one partner per category", r"one partner in each|only one bank", []),
    ("No pound sign, write GBP", "£", []),
    ("No exclamation marks", r"[A-Za-z]!", []),
    ("No dashes in text", r"\s[–—]\s|[A-Za-z]—[A-Za-z]|\s-\s", []),
    ("No apostrophes", r"[A-Za-z]['’][A-Za-z]", []),
    ("No placeholders", r"\blorem\b|\bTODO\b|\bTBC\b|\bTBD\b|\bXXX\b", []),
]
TIMES = [  # facts that must stay the same on every page
    ("Carriages are at 00:30", r"00:15"),
    ("Drums and DJ start at 11:00", r"(drums|the dj)[^.]{0,30}12:00"),
    ("Ghana Day is 08:30 to 17:00", r"11:00 to 18:00"),
]

pages = sorted(glob.glob(os.path.join(SITE, "*.html")))
all_text = ""
for path in glob.glob(os.path.join(SITE, "**", "*"), recursive=True):
    if os.path.isfile(path) and path.endswith((".html", ".css", ".js", ".txt", ".xml", ".json", ".svg", ".ics")):
        all_text += open(path, encoding="utf-8", errors="ignore").read()

for path in pages:
    name = os.path.basename(path)
    raw = open(path, encoding="utf-8").read()
    txt = text_of(raw)
    for label, pat, allowed in WORDS:
        if name in allowed:
            continue
        for m in re.finditer(pat, txt, re.I if pat.isascii() else 0):
            if "rights reserved" in txt[max(0, m.start() - 10):m.end() + 10].lower():
                continue
            fails.append(f"{name}: {label}: ...{txt[max(0, m.start() - 50):m.end() + 50]}...")
    for label, pat in TIMES:
        if re.search(pat, txt, re.I):
            fails.append(f"{name}: {label}")
    # Links, images, anchors, structured data, title, description
    for href in re.findall(r'href="([^"#?:]+\.html)', raw):
        if not os.path.exists(os.path.join(SITE, href)):
            fails.append(f"{name}: broken link {href}")
    for src in re.findall(r'(?:src|srcset)="([^"]+)"', raw):
        if src.startswith("data:"):
            continue
        for u in src.split(","):
            u = u.strip().split(" ")[0]
            if u and not u.startswith(("http", "data:", "//", "#")) and not os.path.exists(os.path.join(SITE, u.split("?")[0])):
                fails.append(f"{name}: missing file {u}")
    ids = set(re.findall(r'id="([^"]+)"', raw))
    for a in re.findall(r'<a[^>]*href="#([^"]+)"', raw):
        if a not in ids:
            fails.append(f"{name}: link to missing section #{a}")
    dup = {i for i in re.findall(r'id="([^"]+)"', raw) if re.findall(r'id="%s"' % re.escape(i), raw).__len__() > 1}
    for i in sorted(dup):
        fails.append(f"{name}: id used twice: {i}")
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            json.loads(m.group(1))
        except ValueError as e:
            fails.append(f"{name}: structured data is not valid JSON: {e}")
    if not re.search(r"<title>[^<]+</title>", raw):
        fails.append(f"{name}: no title")
    if 'name="description"' not in raw:
        fails.append(f"{name}: no meta description")

# Dead files: every image must be used somewhere (og.jpg is kept for old social shares)
for path in glob.glob(os.path.join(SITE, "images", "**", "*"), recursive=True):
    if os.path.isfile(path):
        rel = os.path.relpath(path, SITE).replace(os.sep, "/")
        if rel not in all_text and os.path.basename(path) not in all_text and rel != "images/og.jpg":
            fails.append(f"unused file, delete it: site/{rel}")

# Secrets must never be in the repository
for path in subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split():
    if path.startswith("site/images/") or not os.path.isfile(os.path.join(ROOT, path)):
        continue
    body = open(os.path.join(ROOT, path), encoding="utf-8", errors="ignore").read()
    if re.search(r"sk_live_[0-9A-Za-z]{10,}|rk_live_[0-9A-Za-z]{10,}|whsec_[0-9A-Za-z]{10,}|re_[0-9A-Za-z]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY", body):
        fails.append(f"{path}: looks like a secret key. Remove it and rotate the key.")

# Protected files: listed for the developer, not failed
if "--base" in sys.argv:
    base = sys.argv[sys.argv.index("--base") + 1]
    changed = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for p in changed:
        if p.startswith(("api/", "functions/")) or p == "vercel.json":
            notes.append(f"protected file changed, developer review: {p}")
    diff = subprocess.run(["git", "diff", f"{base}...HEAD", "--", "site/site.js"], cwd=ROOT, capture_output=True, text=True).stdout
    if re.search(r"^[-+].*ticketTailor", diff, re.M):
        notes.append("SITE_CONFIG.ticketTailor changed, developer review")

for n in notes:
    print("NOTE", n)
for f in fails:
    print("FAIL", f)
print(f"{len(pages)} pages checked, {len(fails)} problems, {len(notes)} notes")
sys.exit(1 if fails else 0)
