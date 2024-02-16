# onefile
Merge multiples files into one!

Current supported files to merge:

- junit.xml

Example:

```
from onefile.junit import merge_junit_files

merge_junit_files(["junit_1.xml", "junit_2.xml", "junit_3.xml"])
```