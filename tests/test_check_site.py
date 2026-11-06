from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_site", ROOT / "scripts" / "check_site.py")
assert SPEC and SPEC.loader
CHECK_SITE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK_SITE
SPEC.loader.exec_module(CHECK_SITE)


class CheckSiteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.site = Path(self.temporary.name) / "site"
        shutil.copytree(ROOT / "tests" / "fixtures" / "good-site", self.site)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_good_site_passes(self) -> None:
        self.assertEqual([], CHECK_SITE.validate_site(self.site))

    def test_broken_canonical_fails(self) -> None:
        replacement = ROOT / "tests" / "fixtures" / "broken-canonical" / "index.html"
        shutil.copy2(replacement, self.site / "index.html")
        errors = CHECK_SITE.validate_site(self.site)
        self.assertTrue(any("canonical must use" in error for error in errors), errors)

    def test_broken_internal_link_fails(self) -> None:
        replacement = ROOT / "tests" / "fixtures" / "broken-link" / "index.html"
        shutil.copy2(replacement, self.site / "index.html")
        errors = CHECK_SITE.validate_site(self.site)
        self.assertTrue(any("broken internal link" in error for error in errors), errors)

    def test_cross_canonical_fails(self) -> None:
        replacement = ROOT / "tests" / "fixtures" / "cross-canonical" / "index.html"
        shutil.copy2(replacement, self.site / "index.html")
        errors = CHECK_SITE.validate_site(self.site)
        self.assertTrue(any("canonical must be self-referential" in error for error in errors), errors)

    def test_redirect_target_must_match_canonical(self) -> None:
        replacement = ROOT / "tests" / "fixtures" / "broken-redirect" / "index.html"
        shutil.copy2(replacement, self.site / "index.html")
        errors = CHECK_SITE.validate_site(self.site)
        self.assertTrue(any("redirect canonical must match" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
