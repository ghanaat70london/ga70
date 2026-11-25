"""Set site.js?v= and site.css?v= on every page to the content of the files. Run before every commit that changes site.js or site.css.

    python scripts/bump_version.py
"""
import glob, hashlib, os, re

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
for asset in ("site.js", "site.css"):
    v = hashlib.md5(open(os.path.join(SITE, asset), "rb").read()).hexdigest()[:8]
    for path in glob.glob(os.path.join(SITE, "*.html")):
        s = open(path, encoding="utf-8").read()
        t = re.sub(re.escape(asset) + r"\?v=[a-z0-9]+", asset + "?v=" + v, s)
        if t != s:
            open(path, "w", encoding="utf-8").write(t)
    print(asset, v)
