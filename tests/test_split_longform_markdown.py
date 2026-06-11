import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "split_longform_markdown.py"
SPEC = importlib.util.spec_from_file_location("split_longform_markdown", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SplitLongformMarkdownTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, bytes, dict]:
        registry = {
            "schema_version": 1,
            "max_chapter_bytes": 1000,
            "works": [{"source_path": "kedrov_markdown/kedrov_md/work.md", "levels": [2], "mode": "level"}],
        }
        registry_path = root / "metadata/longform_split_registry.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        source = root / "kedrov_markdown/kedrov_md/work.md"
        source.parent.mkdir(parents=True)
        data = (
            '---\nid: "work"\ntitle: "Work"\ncreated: "2026-06-11"\ntext_role: "author_original"\n'
            'core_corpus_eligible: "true"\nllm_wiki_eligible: "true"\nsource_format: "html"\n'
            'source_license: "not_stated"\nredistribution_approved: "false"\n'
            'rights_review_status: "unreviewed"\ntext_status: "html_conversion_unverified"\n'
            'source_url: "https://example.test"\n---\n# Work\n\n## Contents\n\n- A\n\n## Chapter A\n\nAlpha.\n\n'
            '### Notes\n\nNote A.\n\n## Chapter B\n\nBeta.\n'
        ).encode("utf-8")
        source.write_bytes(data)
        return source, data, registry["works"][0]

    def test_split_is_losslessly_reconstructable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, original, spec = self.fixture(root)
            MODULE.split_bytes(original, source, spec, root=root, max_bytes=1000)
            self.assertFalse(source.exists())
            self.assertEqual(MODULE.reconstruct(source), original)
            manifest = MODULE.verify_work(source, root=root)
            self.assertEqual(len(manifest["chapters"]), 3)
            self.assertTrue(all((source.with_suffix("") / item["file"]).stat().st_size < 1000 for item in manifest["chapters"]))

    def test_unapproved_hard_split_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, original, spec = self.fixture(root)
            with self.assertRaisesRegex(ValueError, "no approved heading boundary"):
                MODULE.split_bytes(original, source, spec, root=root, max_bytes=350)

    def test_refresh_metadata_references_tracks_chapter_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, original, spec = self.fixture(root)
            MODULE.split_bytes(original, source, spec, root=root, max_bytes=1000)
            metadata = root / "kedrov_markdown" / "metadata" / "state.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(
                json.dumps({"output_path": "kedrov_md/work.md", "status": "done"}),
                encoding="utf-8",
            )

            self.assertEqual(MODULE.refresh_metadata_references(root=root), 1)
            refreshed = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(refreshed["work_manifest"], "kedrov_md/work/work_manifest.json")
            self.assertEqual(refreshed["chapter_count"], 3)
            self.assertEqual(len(refreshed["chapter_files"]), 3)


if __name__ == "__main__":
    unittest.main()
