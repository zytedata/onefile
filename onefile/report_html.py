from parsel import Selector
import logging
from datetime import datetime
import os

from onefile import init_onefile

init_onefile()


class TestResult:
    def __init__(
        self,
        result: str = "",
        test: str = "",
        duration: float = 0.0,
        log_msg: str = "",
    ) -> None:
        self.result = result
        self.test = test
        self.duration = duration
        self.log_msg = log_msg

    def __repr__(self):
        return (
            f"TestResult(result='{self.result}', test='{self.test}', "
            f"duration='{self.duration}', log_msg='{self.log_msg}')"
        )


class TestRunSummary:
    def __init__(
        self,
        pytest_html_version: str = "",
        timestamp: datetime = None,
        total_tests: int = 0,
        total_test_run_time: float = 0,
        total_passed_tests: int = 0,
        total_skipped_tests: int = 0,
        total_failed_tests: int = 0,
        total_errors: int = 0,
        total_xfail_tests: int = 0,
        total_xpassed_tests: int = 0,
        total_rerun: int = 0,
    ) -> None:
        self.pytest_html_version = pytest_html_version
        self.timestamp = timestamp
        self.total_tests = total_tests
        self.total_test_run_time = total_test_run_time
        self.total_passed_tests = total_passed_tests
        self.total_skipped_tests = total_skipped_tests
        self.total_failed_tests = total_failed_tests
        self.total_errors = total_errors
        self.total_xfail_tests = total_xfail_tests
        self.total_xpassed_tests = total_xpassed_tests
        self.total_rerun = total_rerun
        self.test_results: list[TestResult] = []

    def add_test_result(self, test_result: TestResult) -> None:
        self.test_results.append(test_result)

    def __repr__(self):
        return (
            f"TestRunSummary("
            f"pytest_html_version='{self.pytest_html_version}', "
            f"timestamp='{self.timestamp}', "
            f"total_tests='{self.total_tests}', "
            f"total_test_run_time='{self.total_test_run_time}', "
            f"total_passed_tests='{self.total_passed_tests}', "
            f"total_skipped_tests='{self.total_skipped_tests}', "
            f"total_failed_tests='{self.total_failed_tests}', "
            f"total_xfail_tests='{self.total_xfail_tests}', "
            f"total_xpassed_tests='{self.total_xpassed_tests}', "
            f"total_rerun='{self.total_rerun}', "
            f"test_results='{self.test_results}')"
        )


class TestRunSummeries:
    def __init__(self) -> None:
        self.test_run_summaries: list[TestRunSummary] = []

    def add_test_run_summary(self, test_run_summary: TestRunSummary) -> None:
        self.test_run_summaries.append(test_run_summary)

    def __repr__(self):
        return (
            f"TestRunSummeries(test_run_summaries={self.test_run_summaries})"
        )


def parse_report_html_files(file_paths: list[str]) -> TestRunSummeries:
    logging.info("Parse report.html files into classes")
    test_run_summaries = TestRunSummeries()

    for file_path in file_paths:
        with open(file_path) as fp:
            html_text = fp.read()
        selector = Selector(text=html_text)

        logging.debug("Parse test run summary")
        date_time_str = selector.xpath(
            "normalize-space(substring-before(substring-after(//p/text(), "
            '"Report generated on "), " by"))'
        ).get()
        date_time_format = "%d-%b-%Y at %H:%M:%S"

        test_run_summary = TestRunSummary(
            pytest_html_version=str(
                selector.xpath(
                    '//p[contains(text(), "Report generated")]/a/following-sibling::text()'
                ).get()
            ),
            timestamp=datetime.strptime(date_time_str, date_time_format),
            total_tests=int(
                selector.xpath(
                    "//h2[text()='Summary']/following-sibling::p[1]/text()"
                )
                .get()
                .split(" ")[0]
            ),
            total_test_run_time=float(
                selector.xpath(
                    "//h2[text()='Summary']/following-sibling::p[1]/text()"
                )
                .get()
                .split(" ")[4]
            ),
            total_passed_tests=int(
                selector.css("span.passed::text").get().split(" ")[0]
            ),
            total_skipped_tests=int(
                selector.css("span.skipped::text").get().split(" ")[0]
            ),
            total_failed_tests=int(
                selector.css("span.failed::text").get().split(" ")[0]
            ),
            total_errors=int(
                selector.css("span.error::text").get().split(" ")[0]
            ),
            total_xfail_tests=int(
                selector.css("span.xfailed::text").get().split(" ")[0]
            ),
            total_xpassed_tests=int(
                selector.css("span.xpassed::text").get().split(" ")[0]
            ),
            total_rerun=int(
                selector.css("span.rerun::text").get().split(" ")[0]
            ),
        )

        logging.debug("Parse test results")
        for result_table_row in selector.css("tbody.results-table-row"):
            test_result = TestResult(
                result=result_table_row.css("td.col-result::text").get(),
                test=result_table_row.css("td.col-name::text").get(),
                duration=result_table_row.css("td.col-duration::text").get(),
                log_msg=result_table_row.css("div.log::text").get(),
            )
            test_run_summary.add_test_result(test_result)

        test_run_summaries.add_test_run_summary(test_run_summary)

    return test_run_summaries


def merge_test_runs(test_run_summaries: TestRunSummeries) -> TestRunSummary:
    logging.info("Merge test run summaries")
    final_test_run_summary = TestRunSummary()

    for test_run_summary in test_run_summaries.test_run_summaries:
        final_test_run_summary.pytest_html_version = (
            test_run_summary.pytest_html_version
        )

        logging.debug("Sum all the test suite time")
        final_test_run_summary.total_test_run_time += (
            test_run_summary.total_test_run_time
        )

        logging.debug("Find the latest timestamp")
        is_timestamp_updated = False
        if (
            final_test_run_summary.timestamp is None
            or test_run_summary.timestamp > final_test_run_summary.timestamp
        ):
            final_test_run_summary.timestamp = test_run_summary.timestamp
            is_timestamp_updated = True

        for test_result in test_run_summary.test_results:
            logging.debug(f"Loaded TestResult: {test_result}")
            existing_tr_index = next(
                (
                    index
                    for index, tr in enumerate(
                        final_test_run_summary.test_results
                    )
                    if tr.test == test_result.test
                ),
                None,
            )

            if existing_tr_index is not None:
                logging.debug("Test result found!")
                if is_timestamp_updated:
                    logging.debug("Test run timestamp is updated!")
                    logging.debug(
                        "Update final test run errors, failures, skipped"
                    )
                    existing_tr = final_test_run_summary.test_results[
                        existing_tr_index
                    ]

                    result_mapping = {
                        "Passed": (
                            "total_passed_tests",
                            "Increase Passed attribute!",
                            "Decrease Passed attribute!",
                        ),
                        "Failed": (
                            "total_failed_tests",
                            "Increase Failed attribute!",
                            "Decrease Failed attribute!",
                        ),
                        "Error": (
                            "total_errors",
                            "Increase Error attribute!",
                            "Decrease Error attribute!",
                        ),
                        "XFailed": (
                            "total_xfail_tests",
                            "Increase XFailed attribute!",
                            "Decrease XFailed attribute!",
                        ),
                        "XPassed": (
                            "total_xpassed_tests",
                            "Increase XPassed attribute!",
                            "Decrease XPassed attribute!",
                        ),
                        "Skipped": (
                            "total_skipped_tests",
                            "Increase Skipped attribute!",
                            "Decrease Skipped attribute!",
                        ),
                        "Rerun": (
                            "total_rerun",
                            "Increase Rerun attribute!",
                            "Decrease Rerun attribute!",
                        ),
                    }

                    for result_type, (
                        attr_name,
                        inc_msg,
                        dec_msg,
                    ) in result_mapping.items():

                        if (
                            test_result.result == result_type
                            and existing_tr.result != result_type
                        ):
                            logging.debug(inc_msg)
                            setattr(
                                final_test_run_summary,
                                attr_name,
                                getattr(final_test_run_summary, attr_name) + 1,
                            )
                        elif (
                            test_result.result != result_type
                            and existing_tr.result == result_type
                        ):
                            logging.debug(dec_msg)
                            setattr(
                                final_test_run_summary,
                                attr_name,
                                getattr(final_test_run_summary, attr_name) - 1,
                            )
                else:
                    logging.debug("Test suite timestamp is NOT updated!")
            else:
                logging.debug("Test result NOT found!")
                results_to_attributes = {
                    "Passed": "total_passed_tests",
                    "Failed": "total_failed_tests",
                    "Skipped": "total_skipped_tests",
                    "XFailed": "total_xfail_tests",
                    "XPassed": "total_xpassed_tests",
                    "Error": "total_errors",
                    "Rerun": "total_rerun",
                }

                attribute_name = results_to_attributes.get(test_result.result)
                if attribute_name:
                    setattr(
                        final_test_run_summary,
                        attribute_name,
                        getattr(final_test_run_summary, attribute_name) + 1,
                    )
                final_test_run_summary.total_tests += 1

                final_test_run_summary.add_test_result(test_result)

    return final_test_run_summary


def create_report_html_file(test_run_summary: TestRunSummary) -> None:
    template_text = ""
    with open(
        os.path.join(os.path.dirname(__file__), "template.html")
    ) as template_f:
        template_text = template_f.read()

    pre_text = f"""
        <p>Report generated on {test_run_summary.timestamp} by <a href="https://pypi.python.org/pypi/pytest-html">pytest-html</a>{test_run_summary.pytest_html_version}</p>
        <h2>Summary</h2>
        <p>{test_run_summary.total_tests} tests ran in {test_run_summary.total_test_run_time} seconds. </p>
        <p class="filter" hidden="true">(Un)check the boxes to filter the results.</p>
        <input checked="true" class="filter" data-test-result="passed" {'disabled="true"' if test_run_summary.total_passed_tests == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="passed">{test_run_summary.total_passed_tests} passed</span>, 
        <input checked="true" class="filter" data-test-result="skipped" {'disabled="true"' if test_run_summary.total_skipped_tests == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="skipped">{test_run_summary.total_skipped_tests} skipped</span>, 
        <input checked="true" class="filter" data-test-result="failed" {'disabled="true"' if test_run_summary.total_failed_tests == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="failed">{test_run_summary.total_failed_tests} failed</span>, 
        <input checked="true" class="filter" data-test-result="error" {'disabled="true"' if test_run_summary.total_errors == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="error">{test_run_summary.total_errors} errors</span>, 
        <input checked="true" class="filter" data-test-result="xfailed" {'disabled="true"' if test_run_summary.total_xfail_tests == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="xfailed">{test_run_summary.total_xfail_tests} expected failures</span>, 
        <input checked="true" class="filter" data-test-result="xpassed" {'disabled="true"' if test_run_summary.total_xpassed_tests == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="xpassed">{test_run_summary.total_xpassed_tests} unexpected passes</span>, 
        <input checked="true" class="filter" data-test-result="rerun" {'disabled="true"' if test_run_summary.total_rerun == 0 else ""} hidden="true" name="filter_checkbox" onChange="filterTable(this)" type="checkbox"/>
        <span class="rerun">{test_run_summary.total_rerun} rerun</span>
        <h2>Results</h2>
        <table id="results-table">
        <thead id="results-table-head">
            <tr>
                <th class="sortable result initial-sort" col="result">Result</th>
                <th class="sortable" col="name">Test</th>
                <th class="sortable" col="duration">Duration</th>
                <th class="sortable links" col="links">Links</th></tr>
            <tr hidden="true" id="not-found-message">
                <th colspan="4">No results found. Try to check the filters</th></tr></thead>
    """
    logging.debug("Pre text:" + pre_text)

    tbodies = ""

    for test_result in test_run_summary.test_results:
        tbodies += f"""
            <tbody class="{test_result.result.lower()} results-table-row">
            <tr>
                <td class="col-result">{test_result.result}</td>
                <td class="col-name">{test_result.test}</td>
                <td class="col-duration">{test_result.duration}</td>
                <td class="col-links"></td></tr>
            <tr>
                <td class="extra" colspan="4">
                <div class="empty log">{test_result.log_msg}</div></td></tr></tbody>
        """
    logging.debug("tbodies: " + tbodies)

    post_text = """</table></body></html>"""

    final_html_text = template_text + pre_text + tbodies + post_text

    with open("report.html", "w") as report_html:
        report_html.write(final_html_text)


def merge_report_html_files(file_paths: list[str]) -> None:
    test_run_summaries = parse_report_html_files(file_paths)
    test_run_summary = merge_test_runs(test_run_summaries)
    create_report_html_file(test_run_summary)
