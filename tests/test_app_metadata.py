"""Unit tests for scripts/validate_apps.py — the marketplace metadata gate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_apps import validate


def good_app(**over):
    a = {"id": "my-app", "name": "My App", "category": "c1",
         "version": "1.2.3", "platform": ["web"], "tags": ["t"]}
    a.update(over)
    return a


def good_doc(**over):
    d = {"meta": {"total_apps": 1, "version": "1.0.0"},
         "categories": [{"id": "c1", "name": "Cat"}],
         "apps": [good_app()]}
    d.update(over)
    return d


class TestValidateApps(unittest.TestCase):
    def test_valid_document_passes(self):
        self.assertEqual(validate(good_doc()), [])

    def test_missing_top_level_key(self):
        d = good_doc()
        del d["apps"]
        self.assertTrue(any("apps" in e for e in validate(d)))

    def test_duplicate_app_id(self):
        d = good_doc(apps=[good_app(), good_app()])
        self.assertTrue(any("duplicate app id" in e for e in validate(d)))

    def test_bad_app_id_slug(self):
        self.assertTrue(any("slug" in e for e in
                            validate(good_doc(apps=[good_app(id="Bad_ID")]))))

    def test_missing_name(self):
        a = good_app()
        del a["name"]
        self.assertTrue(any("missing name" in e for e in
                            validate(good_doc(apps=[a]))))

    def test_unknown_category(self):
        self.assertTrue(any("unknown category" in e for e in
                            validate(good_doc(apps=[good_app(category="nope")]))))

    def test_duplicate_category_id(self):
        d = good_doc(categories=[{"id": "c1", "name": "A"},
                                 {"id": "c1", "name": "B"}])
        self.assertTrue(any("duplicate category id" in e for e in validate(d)))

    def test_bad_version(self):
        self.assertTrue(any("bad version" in e for e in
                            validate(good_doc(apps=[good_app(version="v1")]))))

    def test_empty_platform_list(self):
        self.assertTrue(any("platform" in e for e in
                            validate(good_doc(apps=[good_app(platform=[])]))))

    def test_bad_test_status(self):
        self.assertTrue(any("bad test_status" in e for e in
                            validate(good_doc(apps=[good_app(test_status="meh")]))))

    def test_total_apps_mismatch(self):
        d = good_doc()
        d["meta"]["total_apps"] = 99
        self.assertTrue(any("total_apps" in e for e in validate(d)))

    def test_optional_fields_may_be_absent(self):
        a = {"id": "slim", "name": "Slim", "category": "c1"}
        self.assertEqual(validate(good_doc(apps=[a])), [])


if __name__ == "__main__":
    unittest.main()
