import unittest
import os
import glob

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data", "report_html")


class TestParse(unittest.TestCase):
    def test_parse(self):
        test_files = glob.glob(os.path.join(TEST_DIR, "*.html"))
        print(test_files)
