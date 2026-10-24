import datetime
import json
import sys
import unittest

from pdfmetajson import pdf_utils


class ConvertDateTestCase(unittest.TestCase):

    def test_full_date_with_timezone_offset(self):
        result = pdf_utils.convert_date("D:20250608231824-05'00'")
        expected_tz = datetime.timezone(datetime.timedelta(hours=-5))
        self.assertEqual(result, datetime.datetime(2025, 6, 8, 23, 18, 24, tzinfo=expected_tz))

    def test_positive_offset_with_minutes(self):
        result = pdf_utils.convert_date("D:20250608231824+0530")
        expected_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        self.assertEqual(result, datetime.datetime(2025, 6, 8, 23, 18, 24, tzinfo=expected_tz))

    def test_date_only(self):
        self.assertEqual(pdf_utils.convert_date("D:20250608"), datetime.datetime(2025, 6, 8))

    def test_missing_day_defaults_to_first(self):
        self.assertEqual(pdf_utils.convert_date("D:202506"), datetime.datetime(2025, 6, 1))

    def test_iso_like_date(self):
        self.assertEqual(pdf_utils.convert_date("2025-06-08"), datetime.datetime(2025, 6, 8))

    def test_invalid_returns_none(self):
        self.assertIsNone(pdf_utils.convert_date("not a date"))
        self.assertIsNone(pdf_utils.convert_date(""))


class CleanTextTestCase(unittest.TestCase):

    def test_index_line_is_compacted(self):
        self.assertEqual(
            pdf_utils.clean_index_text("Introduction ..................... 1"),
            "Introduction: 1.",
        )

    def test_index_line_without_title_is_kept(self):
        self.assertEqual(pdf_utils.clean_index_text("....... 12"), "....... 12")

    def test_hyphenated_words_are_joined(self):
        self.assertEqual(pdf_utils.join_separated_words("infor-\nmation"), "information")

    def test_whitespace_collapsed_and_accents_kept(self):
        self.assertEqual(pdf_utils.clean_text("  Café  \n\n\n next   line "), "Café\n next line")

    def test_spanish_letters_and_dashes_are_kept(self):
        text = "Guía para la Gestión de Riesgos – Pequeñas Entidades"
        self.assertEqual(pdf_utils.clean_text(text), text)

    def test_unicode_is_normalized_to_nfc(self):
        # "o" followed by a combining acute accent becomes the single character "ó"
        self.assertEqual(pdf_utils.clean_text("Gestión"), "Gestión")

    def test_known_artifacts_are_replaced(self):
        self.assertEqual(pdf_utils.clean_text("año/uni00A02019"), "año 2019")

    def test_quotes_and_backslashes_survive_json_round_trip(self):
        text = pdf_utils.clean_text('He said "hi" in C:\\temp')
        self.assertEqual(text, 'He said "hi" in C:\\temp')
        self.assertEqual(json.loads(json.dumps(text)), text)


class LongPathTestCase(unittest.TestCase):

    @unittest.skipUnless(sys.platform == "win32", "the prefix only applies on Windows")
    def test_windows_paths_get_extended_length_prefix(self):
        self.assertEqual(pdf_utils.long_path("C:\\books\\a.pdf"), "\\\\?\\C:\\books\\a.pdf")
        self.assertEqual(
            pdf_utils.long_path("\\\\server\\share\\a.pdf"), "\\\\?\\UNC\\server\\share\\a.pdf"
        )
        self.assertEqual(pdf_utils.long_path("\\\\?\\C:\\a.pdf"), "\\\\?\\C:\\a.pdf")

    @unittest.skipIf(sys.platform == "win32", "other systems have no MAX_PATH limit")
    def test_other_systems_keep_the_path(self):
        self.assertEqual(pdf_utils.long_path("/books/a.pdf"), "/books/a.pdf")


if __name__ == "__main__":
    unittest.main()
