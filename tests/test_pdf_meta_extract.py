import unittest
from pathlib import Path

from src.pdf_meta_extract import PdfMetadataExtractor


class MyTestCase(unittest.TestCase):

    def test_pdf_exists(self):
        path_file = Path(__file__).parent / "data" / "sample.pdf"

        self.assertTrue(path_file.exists(), f"File {path_file} does't exist")

        try:
            with path_file.open("rb") as archivo:
                content = archivo.read(10)  # try to read the first 10 bytes
                self.assertGreater(
                    len(content), 0, "The file it's empty or can't be readed"
                )
        except Exception as e:
            self.fail(f"Unable to open file for reading: {e}")

    def test_pdf_metadata_extraction(self):
        try:
            filename = "sample.pdf"
            path_file = Path(__file__).parent / "data" / filename
            pdf_me = PdfMetadataExtractor(file_path=path_file)
            num_file = 1
            info = pdf_me.process(num_file)
            print(info)
            self.assertIsNotNone(info)
            self.assertEqual(info["file_num"], num_file)
            self.assertEqual(info["file_name_original"], filename)
            self.assertEqual(info["file_date"], "2025-06-08 23:18:24")
            self.assertEqual(info["num_pages"], 1)
            self.assertIsNotNone(info["metadata"])
            self.assertEqual(info["metadata"]["author"], "Lorem Master")
            self.assertEqual(
                info["metadata"]["software"], "Microsoft® Word para Microsoft 365"
            )
            self.assertEqual(info["metadata"]["title"], "Lorem Ipsum Test")
            self.assertEqual(info["metadata"]["subject"], "A Simple TEst")
            self.assertEqual(info["metadata"]["keywords"], "Tag01;Test")
            self.assertEqual(info["metadata"]["creation_date"], "2025-06-08")
            self.assertEqual(info["metadata"]["modification_date"], "2025-06-08")
            self.assertIsNotNone(info["content_sample"])
            self.assertIsNotNone(info["content_sample"]["page_1"])

        except Exception as e:
            self.fail(f"Unable to extract metadata from file. {e}")


if __name__ == "__main__":
    unittest.main()
