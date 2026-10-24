import datetime
import json
import unittest

from pdfmetajson import pdf_utils


class ConvertDateTestCase(unittest.TestCase):

    def test_full_date_with_timezone_offset(self):
        result = pdf_utils.convert_date("D:20250608231824-05'00'")
        expected_tz = datetime.timezone(datetime.timedelta(hours=-5))
        self.assertEqual(result, datetime.datetime(2025, 6, 8, 23, 18, 24, tzinfo=expected_tz))

    def test_positive_offset_with_minutes(self):
        result = pdf_utils.convert_date("D:20250608231824+0530")
        self.assertEqual(result.utcoffset(), datetime.timedelta(hours=5, minutes=30))

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

    def test_accents_removed_and_whitespace_collapsed(self):
        self.assertEqual(pdf_utils.clean_text("  Café  \n\n\n next   line "), "Cafe\n next line")

    def test_quotes_and_backslashes_survive_json_round_trip(self):
        text = pdf_utils.clean_text('He said "hi" in C:\\temp')
        self.assertEqual(text, 'He said "hi" in C:\\temp')
        self.assertEqual(json.loads(json.dumps(text)), text)


if __name__ == "__main__":
    unittest.main()
