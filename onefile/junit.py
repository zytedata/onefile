from datetime import datetime
from lxml import etree
from typing import Optional
import logging
import os

from onefile import init_onefile

init_onefile()


class Message:
    def __init__(self, message: str, text: Optional[str] = None):
        self.message: str = message
        self.text: str = text

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(message='{self.message}', text='{self.text}')"
        )


class Error(Message):
    pass


class Failure(Message):
    pass


class Skipped(Message):
    def __init__(self, skip_type: str, message: str, text: str):
        super().__init__(message, text)
        self.type = skip_type

    def __repr__(self):
        return (
            f"Skipped(message='{self.message}', type='{self.type}', text='{self.text})"
        )


class TestCase:
    def __init__(
        self,
        classname: str = "",
        name: str = "",
        time: float = 0.0,
        error: Optional[Error] = None,
        failure: Optional[Failure] = None,
        skipped: Optional[Skipped] = None,
    ):
        self.classname = classname
        self.name = name
        self.time = time
        self.error = error
        self.failure = failure
        self.skipped = skipped

    def __repr__(self):
        return (
            f"TestCase(classname='{self.classname}', name='{self.name}', "
            f"time='{self.time}', error='{self.error}', failure='{self.failure}', "
            f"skipped='{self.skipped}')"
        )


class TestSuite:
    def __init__(
        self,
        name: str = "",
        errors: int = 0,
        failures: int = 0,
        skipped: int = 0,
        tests: int = 0,
        time: float = 0.0,
        timestamp: datetime = None,
        hostname: str = "",
    ):
        self.name = name
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.tests = tests
        self.time = time
        self.timestamp = timestamp
        self.hostname = hostname
        self.test_cases: list[TestCase] = []

    def add_test_case(self, test_case: TestCase) -> None:
        self.test_cases.append(test_case)

    def __repr__(self):
        return (
            f"TestSuite(name='{self.name}', errors={self.errors}, "
            f"failures={self.failures}, skipped={self.skipped}, "
            f"tests={self.tests}, time={self.time}, timestamp='{self.timestamp}', "
            f"hostname='{self.hostname}', testcases={self.test_cases})"
        )


class TestSuites:
    def __init__(self):
        self.test_suites: list[TestSuite] = []

    def add_test_suite(self, test_suite: TestSuite) -> None:
        self.test_suites.append(test_suite)

    def __repr__(self):
        return f"TestSuites(test_suites={self.test_suites})"


def parse_junit_xml(file_paths: list[str]) -> TestSuites:
    logging.info("Parse junit XML files into classes")
    test_suites = TestSuites()
    for file_path in file_paths:
        tree = etree.parse(file_path)
        root = tree.getroot()

        for test_suite_elem in root:
            test_suite = TestSuite(
                name=test_suite_elem.get("name", ""),
                errors=int(test_suite_elem.get("errors", 0)),
                failures=int(test_suite_elem.get("failures", 0)),
                skipped=int(test_suite_elem.get("skipped", 0)),
                tests=int(test_suite_elem.get("tests", 0)),
                time=float(test_suite_elem.get("time", 0.0)),
                timestamp=(
                    datetime.fromisoformat(test_suite_elem.get("timestamp"))
                    if test_suite_elem.get("timestamp")
                    else datetime.now()
                ),
                hostname=test_suite_elem.get("hostname", ""),
            )

            for test_case_elem in test_suite_elem:
                error, failure, skipped = None, None, None
                if (error_elem := test_case_elem.find("error")) is not None:
                    error = Error(
                        message=error_elem.get("message", ""), text=error_elem.text
                    )
                if (failure_elem := test_case_elem.find("failure")) is not None:
                    failure = Failure(
                        message=failure_elem.get("message", ""), text=failure_elem.text
                    )
                if (skipped_elem := test_case_elem.find("skipped")) is not None:
                    skipped = Skipped(
                        skip_type=skipped_elem.get("type", ""),
                        message=skipped_elem.get("message", ""),
                        text=skipped_elem.text,
                    )

                test_case = TestCase(
                    classname=test_case_elem.get("classname", ""),
                    name=test_case_elem.get("name", ""),
                    time=float(test_case_elem.get("time", 0.0)),
                    error=error,
                    failure=failure,
                    skipped=skipped,
                )
                test_suite.add_test_case(test_case)

            test_suites.add_test_suite(test_suite)
    return test_suites


def merge_test_suites(test_suites: TestSuites) -> TestSuite:
    """Merge all test suites into one test suite and return it"""
    logging.info("Let's merge test suites!")
    final_test_suite = TestSuite()
    for test_suite in test_suites.test_suites:
        logging.debug(f"Test suite: {test_suite}")
        final_test_suite.name = test_suite.name
        final_test_suite.hostname = test_suite.hostname

        logging.debug("Sum all the test suite time")
        final_test_suite.time += test_suite.time

        logging.debug("Find the latest timestamp")
        is_test_suite_timestamp_updated = False
        if (
            final_test_suite.timestamp is None
            or test_suite.timestamp > final_test_suite.timestamp
        ):
            final_test_suite.timestamp = test_suite.timestamp
            is_test_suite_timestamp_updated = True

        for loaded_testcase in test_suite.test_cases:
            logging.debug(f"Loaded Test case: {loaded_testcase}")
            existing_tc_index = next(
                (
                    index
                    for index, tc in enumerate(final_test_suite.test_cases)
                    if tc.classname == loaded_testcase.classname
                    and tc.name == loaded_testcase.name
                ),
                None,
            )

            if existing_tc_index is not None:
                logging.debug(f"Test case found!")
                if is_test_suite_timestamp_updated:
                    logging.debug("Test suite timestamp is updated!")
                    logging.debug("Update final test suite errors, failures, skipped")
                    existing_tc = final_test_suite.test_cases[existing_tc_index]

                    if loaded_testcase.error and not existing_tc.error:
                        logging.debug("Increase errors attribute!")
                        final_test_suite.errors += 1
                    elif not loaded_testcase.error and existing_tc.error:
                        logging.debug("Decrease errors attribute!")
                        final_test_suite.errors -= 1

                    if loaded_testcase.failure and not existing_tc.failure:
                        logging.debug("Increase failures attribute!")
                        final_test_suite.failures += 1
                    elif not loaded_testcase.failure and existing_tc.failure:
                        logging.debug("Decrease failures attribute!")
                        final_test_suite.failures -= 1

                    if loaded_testcase.skipped and not existing_tc.skipped:
                        logging.debug("Increase skipped attribute!")
                        final_test_suite.skipped += 1
                    elif not loaded_testcase.skipped and existing_tc.skipped:
                        logging.debug("Decrease skipped attribute!")
                        final_test_suite.skipped -= 1

                    existing_tc.time = loaded_testcase.time
                    existing_tc.error = loaded_testcase.error
                    existing_tc.failure = loaded_testcase.failure
                    existing_tc.skipped = loaded_testcase.skipped
                else:
                    logging.debug("Test suite timestamp is NOT updated!")
            else:
                logging.debug(f"Test case NOT found!")
                if loaded_testcase.error:
                    final_test_suite.errors += 1
                if loaded_testcase.failure:
                    final_test_suite.failures += 1
                if loaded_testcase.skipped:
                    final_test_suite.skipped += 1
                final_test_suite.tests += 1
                final_test_suite.test_cases.append(loaded_testcase)

    return final_test_suite


def create_junit_file(test_suite: TestSuite) -> None:
    logging.info("Create junit.xml file")
    root = etree.Element("testsuites")

    logging.debug("Create the testsuite element")
    test_suite_elem = etree.SubElement(root, "testsuite")

    logging.debug("Add attributes to the testsuite element")
    test_suite_elem.set("name", test_suite.name)
    test_suite_elem.set("errors", str(test_suite.errors))
    test_suite_elem.set("failures", str(test_suite.failures))
    test_suite_elem.set("skipped", str(test_suite.skipped))
    test_suite_elem.set("tests", str(test_suite.tests))
    test_suite_elem.set("time", str(test_suite.time))
    test_suite_elem.set("timestamp", str(test_suite.timestamp))
    test_suite_elem.set("hostname", test_suite.hostname)

    for test_case in test_suite.test_cases:
        test_case_elem = etree.SubElement(test_suite_elem, "testcase")
        test_case_elem.set("classname", test_case.classname)
        test_case_elem.set("name", test_case.name)
        test_case_elem.set("time", str(test_case.time))

        if test_case.error is not None:
            tc_error: Optional[Error] = test_case.error
            error_elem = etree.SubElement(test_case_elem, "error")
            if tc_error.message:
                error_elem.set("message", tc_error.message)
            if tc_error.text:
                error_elem.text = tc_error.text

        if test_case.failure is not None:
            tc_failure: Optional[Failure] = test_case.failure
            failure_elem = etree.SubElement(test_case_elem, "failure")
            if tc_failure.message:
                failure_elem.set("message", tc_failure.message)
            if tc_failure.text:
                failure_elem.text = tc_failure.text

        if test_case.skipped is not None:
            tc_skipped: Optional[Skipped] = test_case.skipped
            skipped_elem = etree.SubElement(test_case_elem, "skipped")
            if tc_skipped.type:
                skipped_elem.set("type", tc_skipped.type)
            if tc_skipped.message:
                skipped_elem.set("message", tc_skipped.message)
            if tc_skipped.text:
                skipped_elem.text = tc_skipped.text

    xml_tree = etree.ElementTree(root)
    xml_tree.write(
        os.path.join(os.getcwd(), "junit.xml"),
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )


def merge_junit_files(file_paths: list[str]) -> None:
    test_suites = parse_junit_xml(file_paths)
    final_test_suite = merge_test_suites(test_suites)
    create_junit_file(final_test_suite)
