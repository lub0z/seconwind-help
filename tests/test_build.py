import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

SAMPLE = """<style>:root { --paper: #fff; }
/* ---------- GUIDES WIDGET ---------- */
.guides-btn { color: red; }
/* ============ NEXT ============ */</style>
<script>
/* ============================================================
   GUIDES MODULE - test
   ============================================================ */
const KB_RAW = [
  {
    id: '01',
    title: 'x',
  },
];
x = '<a href="#contact" class="g-help-link" onclick="closeGuides()">Send Michael a message →</a>';
y = 'Drop a message through the contact form';
</script>"""


class BuildTests(unittest.TestCase):
    def test_extract_rewrites_contact_link(self):
        parts = build.extract(SAMPLE)
        self.assertIn("--paper", parts["root"])
        self.assertIn(".guides-btn", parts["css"])
        self.assertNotIn(".NEXT", parts["css"])
        self.assertNotIn("#contact", parts["js"])
        self.assertIn("window.helpMailto()", parts["js"])
        self.assertIn("Send an email", parts["js"])
        self.assertEqual(parts["kb_count"], 1)

    def test_missing_module_fails_loudly(self):
        with self.assertRaises(SystemExit):
            build.extract("<html></html>")

    def test_committed_build_is_offline(self):
        page = (ROOT / "dist/index.html").read_text()
        self.assertNotIn("#contact", page)
        self.assertNotIn("fonts.googleapis.com", page)
        self.assertNotIn("http://", page.replace("http://www.w3.org", ""))
        self.assertIn("KB_RAW", page)


if __name__ == "__main__":
    unittest.main()
