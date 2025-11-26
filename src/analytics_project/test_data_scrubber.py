import unittest
import pandas as pd

from analytics_project.data_scrubber import DataScrubber


class TestDataScrubber(unittest.TestCase):
    def setUp(self):
        # Small toy DataFrame to test with
        self.df = pd.DataFrame(
            {
                "name": [" Alice ", "BOB", "Alice ", None],
                "age": [25, 30, 25, None],
                "score": [10, 999, 15, 20],
            }
        )
        self.scrubber = DataScrubber(self.df.copy())

    def test_remove_duplicate_records(self):
        df_dup = pd.concat([self.scrubber.df, self.scrubber.df.iloc[[0]]], ignore_index=True)
        scrubber2 = DataScrubber(df_dup)
        before = len(scrubber2.df)
        scrubber2.remove_duplicate_records()
        after = len(scrubber2.df)
        self.assertLess(after, before)

    def test_handle_missing_data_fill(self):
        scrubbed = self.scrubber.handle_missing_data(fill_value=0)
        self.assertFalse(scrubbed.isnull().any().any())

    def test_handle_missing_data_drop(self):
        scrubber2 = DataScrubber(self.df.copy())
        scrubbed = scrubber2.handle_missing_data(drop=True)
        self.assertFalse(scrubbed.isnull().any().any())
        self.assertLess(len(scrubbed), len(self.df))

    def test_format_column_strings_to_lower_and_trim(self):
        scrubbed = self.scrubber.format_column_strings_to_lower_and_trim("name")
        self.assertIn("alice", scrubbed["name"].tolist())
        self.assertIn("bob", scrubbed["name"].tolist())

    def test_format_column_strings_to_upper_and_trim(self):
        scrubber2 = DataScrubber(self.df.copy())
        scrubbed = scrubber2.format_column_strings_to_upper_and_trim("name")
        self.assertIn("ALICE", scrubbed["name"].tolist())
        self.assertIn("BOB", scrubbed["name"].tolist())

    def test_parse_dates_to_add_standard_datetime(self):
        df_dates = pd.DataFrame({"order_date": ["2024-01-01", "2024-02-15"]})
        scrubber3 = DataScrubber(df_dates)
        scrubbed = scrubber3.parse_dates_to_add_standard_datetime("order_date")
        self.assertIn("StandardDateTime", scrubbed.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(scrubbed["StandardDateTime"]))

    def test_rename_and_reorder_columns(self):
        df_small = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        scrubber4 = DataScrubber(df_small)
        scrubber4.rename_columns({"A": "first", "B": "second"})
        self.assertIn("first", scrubber4.df.columns)
        self.assertIn("second", scrubber4.df.columns)

        scrubber4.reorder_columns(["second", "first"])
        self.assertEqual(list(scrubber4.df.columns), ["second", "first"])


if __name__ == "__main__":
    unittest.main()
