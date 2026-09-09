import tempfile
import unittest
from pathlib import Path

from sorter import build_extension_map, sort_folder, unique_destination


class FileSorterTests(unittest.TestCase):
    def test_extension_map(self):
        categories = {"Images": [".png", ".jpg"], "Code": [".py"]}
        result = build_extension_map(categories)

        self.assertEqual(result[".png"], "Images")
        self.assertEqual(result[".py"], "Code")

    def test_unique_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            original = folder / "report.pdf"
            original.touch()

            result = unique_destination(original)

            self.assertEqual(result.name, "report (1).pdf")

    def test_sort_folder_moves_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir)

            (source / "photo.jpg").write_text("image", encoding="utf-8")
            (source / "notes.txt").write_text("notes", encoding="utf-8")
            (source / "mystery.xyz").write_text("other", encoding="utf-8")

            result = sort_folder(source)

            self.assertEqual(result.moved, 3)
            self.assertTrue((source / "Images" / "photo.jpg").exists())
            self.assertTrue((source / "Documents" / "notes.txt").exists())
            self.assertTrue((source / "Other" / "mystery.xyz").exists())

    def test_dry_run_does_not_move_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir)
            file_path = source / "photo.jpg"
            file_path.write_text("image", encoding="utf-8")

            result = sort_folder(source, dry_run=True)

            self.assertEqual(result.moved, 1)
            self.assertTrue(file_path.exists())
            self.assertFalse((source / "Images").exists())


if __name__ == "__main__":
    unittest.main()
