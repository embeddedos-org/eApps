"""Unit tests for scripts/validate_apps.py — the marketplace metadata gate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_apps import validate, load_registry


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


class TestFieldTypes(unittest.TestCase):
    """Fields the schema types as strings: a wrong type is a violation, and
    the validator reports it instead of raising."""

    def errors_for(self, doc):
        return validate(doc, registry={})

    def test_non_string_app_id_is_reported(self):
        errs = self.errors_for(good_doc(apps=[good_app(id=7)]))
        self.assertTrue(any("slug" in e for e in errs), errs)

    def test_app_id_with_trailing_newline_is_not_a_slug(self):
        errs = self.errors_for(good_doc(apps=[good_app(id="my-app\n")]))
        self.assertTrue(any("slug" in e for e in errs), errs)

    def test_non_string_category_is_reported(self):
        errs = self.errors_for(good_doc(apps=[good_app(category=["c1"])]))
        self.assertTrue(any("category must be a string" in e for e in errs), errs)

    def test_non_string_category_id_is_reported(self):
        errs = self.errors_for(good_doc(categories=[{"id": ["c1"], "name": "Cat"}]))
        self.assertTrue(any("id must be a string" in e for e in errs), errs)

    def test_non_string_names_are_reported(self):
        errs = self.errors_for(good_doc(categories=[{"id": "c1", "name": 3}],
                                        apps=[good_app(name=5)]))
        self.assertTrue(any("categories[0] name must be a string" in e
                            for e in errs), errs)
        self.assertTrue(any("apps[0] (my-app) name must be a string" in e
                            for e in errs), errs)

    def test_meta_that_is_not_an_object_is_reported(self):
        errs = self.errors_for(good_doc(meta=[1]))
        self.assertTrue(any("meta must be an object" in e for e in errs), errs)

    def test_platform_entries_must_be_non_empty_strings(self):
        for plats in ([1], [""], ["web", None]):
            errs = self.errors_for(good_doc(apps=[good_app(platform=plats)]))
            self.assertTrue(any("platform entries" in e for e in errs),
                            (plats, errs))

    def test_tags_must_be_non_empty_strings(self):
        for tags in ([""], [2], ["ok", {}]):
            errs = self.errors_for(good_doc(apps=[good_app(tags=tags)]))
            self.assertTrue(any("tags must be non-empty strings" in e
                                for e in errs), (tags, errs))


# Curated vocabulary for the AI-capability tests below: a fail-closed registry
# must reject anything it does not list.
TEST_REGISTRY = {
    "camera_frames": {"description": "camera", "default_access": "none"},
    "inference.local": {"description": "on-device", "default_access": "read"},
}


class TestAiCapabilities(unittest.TestCase):
    def test_unknown_ai_capability_rejected(self):
        a = good_app(ai_capabilities={"teleport": "read"})
        errs = validate(good_doc(apps=[a]), registry=TEST_REGISTRY)
        self.assertTrue(any("unknown ai_capability" in e and "teleport" in e
                            for e in errs), errs)

    def test_dotted_unknown_ai_capability_rejected(self):
        a = good_app(ai_capabilities={"inference.quantum": "read"})
        errs = validate(good_doc(apps=[a]), registry=TEST_REGISTRY)
        self.assertTrue(any("unknown ai_capability" in e for e in errs), errs)

    def test_bad_ai_capability_level_rejected(self):
        a = good_app(ai_capabilities={"camera_frames": "execute"})
        errs = validate(good_doc(apps=[a]), registry=TEST_REGISTRY)
        self.assertTrue(any("bad ai_capability level" in e for e in errs), errs)

    def test_known_ai_capability_accepted(self):
        a = good_app(ai_capabilities={"camera_frames": "none",
                                       "inference.local": "read"})
        self.assertEqual(validate(good_doc(apps=[a]),
                                  registry=TEST_REGISTRY), [])

    def test_registry_loads_curated_vocabulary(self):
        reg = load_registry()
        expected = {"camera_frames", "mic_frames", "speaker_frames",
                    "inference.local", "inference.cloud", "npu",
                    "location", "contacts"}
        self.assertEqual(set(reg), expected)
        self.assertEqual(reg["camera_frames"]["default_access"], "none")
        self.assertEqual(reg["inference.local"]["default_access"], "read")
        self.assertEqual(reg["npu"]["default_access"], "read")

    def test_current_apps_json_passes_registry(self):
        repo = Path(__file__).resolve().parent.parent
        with open(repo / "data" / "apps.json", encoding="utf-8") as f:
            import json
            data = json.load(f)
        self.assertEqual(validate(data, registry=load_registry()), [])


if __name__ == "__main__":
    unittest.main()
