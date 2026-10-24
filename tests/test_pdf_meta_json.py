import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pdfmetajson.pdf_meta_json import PdfMetaJson
from pdfmetajson.validators import ValidationError


class PdfMetaJsonTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.sample_pdf = Path(__file__).parent / "data" / "sample.pdf"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_missing_directory_raises_validation_error(self):
        with self.assertRaises(ValidationError), self.assertLogs(level="ERROR"):
            PdfMetaJson(input_dir=str(self.tmp_dir / "missing"))

    def test_process_directory_writes_batches(self):
        for name in ("a.pdf", "b.PDF", "c.pdf"):
            shutil.copy(self.sample_pdf, self.tmp_dir / name)

        PdfMetaJson(input_dir=str(self.tmp_dir), record_limit=2).process_directory()

        basename = f"out_{self.tmp_dir.name}"
        first = json.loads((self.tmp_dir / f"{basename}_01.json").read_text(encoding="utf-8"))
        second = json.loads((self.tmp_dir / f"{basename}_02.json").read_text(encoding="utf-8"))
        self.assertEqual(len(first), 2)
        self.assertEqual(len(second), 1)
        names = {record["file_name_original"] for record in first + second}
        self.assertEqual(names, {"a.pdf", "b.PDF", "c.pdf"})

    def test_exact_multiple_of_limit_writes_no_empty_batch(self):
        for name in ("a.pdf", "b.pdf"):
            shutil.copy(self.sample_pdf, self.tmp_dir / name)

        PdfMetaJson(input_dir=str(self.tmp_dir), record_limit=2).process_directory()

        outputs = sorted(p.name for p in self.tmp_dir.glob("out_*.json"))
        self.assertEqual(outputs, [f"out_{self.tmp_dir.name}_01.json"])


if __name__ == "__main__":
    unittest.main()
