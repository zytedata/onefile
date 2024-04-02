import unittest
import os
import glob
from parsel import Selector

from onefile.report_html import (
    parse_report_html_files,
    merge_test_runs,
    create_report_html_file,
)

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data", "report_html")


class TestParse(unittest.TestCase):
    def test_parse(self):
        test_files = glob.glob(os.path.join(TEST_DIR, "report_*.html"))
        print(test_files)
        test_run_summaries = parse_report_html_files(test_files)
        assert len(test_run_summaries.test_run_summaries) == 2


class TestMerge(unittest.TestCase):
    def test_merge(self):
        test_files = glob.glob(os.path.join(TEST_DIR, "report_*.html"))
        test_run_summaries = parse_report_html_files(test_files)
        test_run_summary = merge_test_runs(test_run_summaries)
        assert len(test_run_summary.test_results) == 7


class TestCreateReportHtmlFile(unittest.TestCase):
    def test_create_file(self):
        test_files = glob.glob(os.path.join(TEST_DIR, "report_*.html"))
        test_run_summaries = parse_report_html_files(test_files)
        test_run_summary = merge_test_runs(test_run_summaries)
        create_report_html_file(test_run_summary)
        with open("report.html") as report_html:
            report_text = report_html.read()
        selector = Selector(text=report_text)
        assert selector.css("span.passed::text").get() == "4 passed"
        assert selector.css("span.skipped::text").get() == "1 skipped"
        assert selector.css("span.failed::text").get() == "0 failed"
        assert selector.css("span.error::text").get() == "0 errors"
        assert (
            selector.css("span.xfailed::text").get() == "1 expected failures"
        )
        assert (
            selector.css("span.xpassed::text").get() == "1 unexpected passes"
        )
        assert selector.css("span.rerun::text").get() == "0 rerun"
