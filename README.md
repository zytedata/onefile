# onefile
Merge multiples files into one!

Current supported files to merge:

- junit.xml (Ref.: [JUnitXML file](https://docs.pytest.org/en/7.1.x/how-to/output.html#creating-junitxml-format-files))
- report.html (Ref.: [self-contained HTML report file](https://pytest-html.readthedocs.io/en/latest/user_guide.html#enhancing-reports))

Example for junit.xml file merge:

```
from onefile.junit import merge_junit_files

merge_junit_files(["junit_1.xml", "junit_2.xml", "junit_3.xml"])
```

Example for report.html file merge:

```
from onefile.report_html import merge_report_html_files

merge_junit_files(["report_html_1.xml", "report_html_2.xml", "report_html_3.xml"])
```