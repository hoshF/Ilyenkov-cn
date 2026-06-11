import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_public.py"
SPEC = importlib.util.spec_from_file_location("export_public", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ExportPublicTests(unittest.TestCase):
    def test_unapproved_corpus_markdown_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kedrov_markdown/kedrov_md/work.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                '---\ncreated: "2026-06-11"\ntext_role: "author_original"\n'
                'redistribution_approved: "false"\n---\n# Work\n',
                encoding="utf-8",
            )
            self.assertEqual(MODULE.export_decision(path, root, {}), (False, "redistribution_not_approved"))

    def test_approved_corpus_markdown_is_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kedrov_markdown/kedrov_md/work.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                '---\ncreated: "2026-06-11"\ntext_role: "author_original"\n'
                'redistribution_approved: "true"\n---\n# Work\n',
                encoding="utf-8",
            )
            self.assertEqual(MODULE.export_decision(path, root, {}), (True, "redistribution_approved=true"))

    def test_unlisted_pdf_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "existing_translations/book.pdf"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"%PDF-test")
            self.assertFalse(MODULE.export_decision(path, root, {})[0])

    def test_project_document_is_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            path.write_text("---\ncreated: 2026-06-11\n---\n# Readme\n", encoding="utf-8")
            self.assertEqual(MODULE.export_decision(path, root, {}), (True, "project_file"))

    def test_unapproved_image_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "assets/images/portrait.jpg"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"image")
            self.assertEqual(
                MODULE.export_decision(path, root, {}),
                (False, "asset_without_redistribution_approval"),
            )

    def test_unapproved_tex_body_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "translation/book.tex"
            path.parent.mkdir(parents=True)
            path.write_text("\\chapter{Text}\n", encoding="utf-8")
            self.assertEqual(
                MODULE.export_decision(path, root, {}),
                (False, "text_without_redistribution_approval"),
            )

    def test_repository_metadata_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ".DS_Store"
            path.write_bytes(b"metadata")
            self.assertEqual(
                MODULE.export_decision(path, root, {}),
                (False, "repository_metadata"),
            )

    def test_corpus_readme_does_not_bypass_rights_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kedrov_markdown/kedrov_md/work/README.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\ncreated: 2026-06-11\n---\n# Work\n", encoding="utf-8")
            self.assertEqual(
                MODULE.export_decision(path, root, {}),
                (False, "corpus_markdown_without_redistribution_approval"),
            )

    def test_build_preserves_git_pointer_and_exports_all_approved_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = root / "kedrov_markdown/kedrov_md/work.md"
            approved.parent.mkdir(parents=True)
            approved.write_text(
                '---\ncreated: "2026-06-11"\ntext_role: "author_original"\n'
                'core_corpus_eligible: "false"\nredistribution_approved: "true"\n---\n# Work\n',
                encoding="utf-8",
            )
            rejected = root / "kedrov_markdown/kedrov_md/rejected.md"
            rejected.write_text(
                '---\ncreated: "2026-06-11"\ntext_role: "author_original"\n'
                'core_corpus_eligible: "true"\nredistribution_approved: "false"\n---\n# Rejected\n',
                encoding="utf-8",
            )
            output = root / "dist/public"
            output.mkdir(parents=True)
            (output / ".git").write_text("gitdir: ../.public.git\n", encoding="utf-8")
            (output / "stale.txt").write_text("stale", encoding="utf-8")

            audit = MODULE.build_export(root, output)

            self.assertEqual((output / ".git").read_text(), "gitdir: ../.public.git\n")
            self.assertTrue((output / approved.relative_to(root)).is_file())
            self.assertFalse((output / rejected.relative_to(root)).exists())
            self.assertFalse((output / "stale.txt").exists())
            MODULE.verify_export_tree(audit, root, output)


if __name__ == "__main__":
    unittest.main()
