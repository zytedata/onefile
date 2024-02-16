import unittest
import os
import glob

from onefile.junit import parse_junit_xml, merge_test_suites, create_junit_file

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data", "junit")


class TestParse(unittest.TestCase):
    def test_skipped(self):
        test_file = glob.glob(os.path.join(TEST_DIR, "junit_2.xml"))
        test_suites = parse_junit_xml(test_file)
        for test_suite in test_suites.test_suites:
            assert test_suite.skipped == 1
            for test_case in test_suite.test_cases:
                assert (
                    test_case.skipped.message == "The tiger doesn't want to be a puppet"
                )
                assert test_case.skipped.type == "pytest.xfail"
                assert test_case.skipped.text is None

    def test_errors(self):
        test_file = glob.glob(os.path.join(TEST_DIR, "junit_1.xml"))
        test_suites = parse_junit_xml(test_file)
        for test_suite in test_suites.test_suites:
            assert test_suite.errors == 1
            for test_case in test_suite.test_cases:
                if test_case.error is not None:
                    assert (
                        test_case.error.message == "There is no small dog in the town"
                    )
                    assert test_case.error.text is None
                    break

    def test_failures(self):
        test_file = glob.glob(os.path.join(TEST_DIR, "junit_1.xml"))
        test_suites = parse_junit_xml(test_file)
        for test_suite in test_suites.test_suites:
            assert test_suite.failures == 1
            for test_case in test_suite.test_cases:
                if test_case.failure is not None:
                    assert (
                        test_case.failure.message
                        == "AssertionError: Locator expected to be visible"
                    )
                    assert test_case.failure.text == "AssertionError!!!"
                    break


class TestMerge(unittest.TestCase):
    def test_merge(self):
        files = glob.glob(os.path.join(TEST_DIR, "junit_*.xml"))
        test_suites = parse_junit_xml(files)
        final_test_suite = merge_test_suites(test_suites)
        assert final_test_suite.name == "pytest"
        assert final_test_suite.errors == 1
        assert final_test_suite.failures == 1
        assert final_test_suite.skipped == 1
        assert final_test_suite.tests == 9
        assert final_test_suite.time == 401.446
        assert str(final_test_suite.timestamp) == "2024-01-07 18:50:09.552277"
        assert final_test_suite.hostname == "localhost"
        for test_case in final_test_suite.test_cases:
            if test_case.name == "test_dog[small]":
                error = test_case.error
                assert error.message == "There is no small dog in the town"
                assert error.text is None
            elif test_case.name == "test_dog[white]":
                failure = test_case.failure
                assert (
                    failure.message == "AssertionError: Locator expected to be visible"
                )
                assert failure.text == "AssertionError!!!"
            elif test_case.name == "test_tiger":
                skipped = test_case.skipped
                assert skipped.type == "pytest.xfail"
                assert skipped.message == "The tiger doesn't want to be a puppet"
                assert skipped.text is None
            else:
                assert test_case.error is None
                assert test_case.failure is None
                assert test_case.skipped is None


class TestCreateJunitFile(unittest.TestCase):
    def test_create_junit_file(self):
        files = glob.glob(os.path.join(TEST_DIR, "junit_*.xml"))
        test_suites = parse_junit_xml(files)
        final_test_suite = merge_test_suites(test_suites)
        create_junit_file(final_test_suite)


if __name__ == "__main__":
    unittest.main()
