"""Build the offline help app from the website's Quick answers module.

    python3 tools/build.py ../seconwind-site/index.html

The knowledge base and matching logic are copied from the live site's index.html,
so the help app and the website always give the same answers. Output: dist/index.html
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools/template.html"
OUT = ROOT / "dist/index.html"
EMAIL = "hello@seconwind.com"


def extract(site_html: str) -> dict:
    root = re.search(r":root\s*\{.*?\}", site_html, re.S)
    css = re.search(r"/\* -+ GUIDES WIDGET -+ \*/(.*?)(?=/\* =+ )", site_html, re.S)
    js = re.search(r"<script>\s*(/\* =+\s*\n\s*GUIDES MODULE.*?)</script>", site_html, re.S)
    missing = [n for n, m in (("CSS variables", root), ("Guides CSS", css), ("Guides script", js)) if not m]
    if missing:
        raise SystemExit("Could not find in index.html: " + ", ".join(missing) + ". Has the Guides module moved?")
    script = js.group(1)
    # Offline: the escalation goes to email instead of the website's contact form.
    script, n = re.subn(
        r"""'<a href="#contact" class="g-help-link" onclick="closeGuides\(\)">[^<]*</a>'""",
        """'<a href="' + window.helpMailto() + '" class="g-help-link">Email Michael →</a>'""",
        script,
    )
    if n != 1:
        raise SystemExit("Could not rewrite the 'Send Michael a message' link. Has its markup changed?")
    script = script.replace("Drop a message through the contact form", "Send an email")
    kb_count = len(re.findall(r"^\s*id: '\d+',", script, re.M))
    return {"root": root.group(0), "css": css.group(1), "js": script, "kb_count": kb_count}


def build(site_index: Path) -> Path:
    parts = extract(site_index.read_text())
    page = TEMPLATE.read_text()
    page = page.replace("/*ROOT_VARS*/", parts["root"]).replace("/*GUIDES_CSS*/", parts["css"])
    page = page.replace("/*GUIDES_JS*/", parts["js"]).replace("{{EMAIL}}", EMAIL)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    print(f"Built {OUT} with {parts['kb_count']} guides")
    return OUT


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    build(Path(sys.argv[1]))
