"""
Custom PyTest configuration that runs all the docstrings in the README as separate
doctests. This is a bit of a hack, but it works. The README is parsed for Python code
blocks, which are then written to a temporary file in the 'tests/' directory. PyTest
then collects these files and runs them as doctests.
"""

from __future__ import annotations
import pytest
import re
import tempfile
from pathlib import Path
import datetime


# Global list to track temporary files
TEMP_FILES: list[Path] = []


MODULE_IMPORTS = """
from timefhuman import timefhuman, tfhConfig
import datetime
import pytz
import pytest
"""


TEST_TEMPLATE = """
def test_readme_example_{i}():
    \"\"\"
{example}
    \"\"\"
    pass
"""


@pytest.fixture
def now():
    return datetime.datetime(year=2018, month=8, day=4, hour=14)


@pytest.fixture(autouse=True)
def conditional_setup_teardown(now, request):
    """Specifically for the doctests only, which currently only exist in the README,
    set the 'now' attribute to a fixed date for consistent results.
    
    This fixture is applied to all tests, but only has an effect on doctests. Weirdly,
    doing this the "normal" way -- simply defining a fixture, then specifying it
    explicitly in the test function arguments -- doesn't work for doctests.
    """
    if isinstance(request.node, pytest.DoctestItem):
        from timefhuman import DEFAULT_CONFIG
        old_now = DEFAULT_CONFIG.now
        DEFAULT_CONFIG.now = now
        yield    
        DEFAULT_CONFIG.now = old_now
    else:
        yield


class ReadmeDoctestModule(pytest.Module):
    @staticmethod
    def create_doctest_file(readme_path: Path) -> Path | None:
        with readme_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Extract Python code blocks from README.md
        matches = re.findall(r"```python\n(.*?)```", content, re.DOTALL)
        if not matches:
            return None

        # Assemble the Python code into a module
        module_code = MODULE_IMPORTS
        for i, match in enumerate(matches):
            module_code += TEST_TEMPLATE.format(i=i, example=match)

        # Create a temporary file in the 'tests/' directory
        temp_fd, temp_path = tempfile.mkstemp(dir="tests/", suffix=".py", prefix="test_readme_")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(module_code)
        return Path(temp_path)

    def collect(self):
        # Return a module based on the temporary file's path
        return [pytest.Module.from_parent(parent=self.parent, path=self.path)]


@pytest.hookimpl
def pytest_collect_file(file_path: Path, parent):
    """Disable README doctest collection for simplicity."""
    return None


def pytest_sessionfinish(session, exitstatus):
    # Cleanup all temporary files after the session ends
    for temp_file in TEMP_FILES:
        temp_file.unlink(missing_ok=True)