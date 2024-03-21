from parsel import Selector


class TestRunSummary:
    def __init__(
        self,
        total_tests: int = 0,
        total_test_run_time: float = 0,
        total_passed_tests: int = 0,
        total_skipped_tests: int = 0,
        total_failed_tests: int = 0,
        total_xfail_tests: int = 0,
        total_unexpected_passed_tests: int = 0,
        total_rerun: int = 0,
    ) -> None:
        self.total_tests = total_tests
        self.total_test_run_time = total_test_run_time
        self.total_passed_tests = total_passed_tests
        self.total_skipped_tests = total_skipped_tests
        self.total_failed_tests = total_failed_tests
        self.total_xfail_tests = total_xfail_tests
        self.total_unexpected_passed_tests = total_unexpected_passed_tests
        self.total_rerun = total_rerun

    def __repr__(self):
        return (
            f"TestRunSummary(total_tests='{self.total_tests}', total_test_run_time='{self.total_test_run_time}', "
            f"total_passed_tests='{self.total_passed_tests}', total_skipped_tests='{self.total_skipped_tests}', "
            f"total_failed_tests='{self.total_failed_tests}', total_xfail_tests='{self.total_xfail_tests}', "
            f"total_unexpected_passed_tests='{self.total_unexpected_passed_tests}', total_rerun='{self.total_rerun}')"
        )
