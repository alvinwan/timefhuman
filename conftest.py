from __future__ import annotations
import pytest
import re
import tempfile
from pathlib import Path

# Global list to track temporary files
TEMP_FILES: list[Path] = []

class ReadmeDoctestModule(pytest.Module):
    @staticmethod
    def create_doctest_file(readme_path: Path) -> Path | None:
        with readme_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Extract Python code blocks from README.md
        matches = re.findall(r"```python\n(.*?)```", content, re.DOTALL)
        if not matches:
            return None

        module_code = """
from timefhuman import timefhuman, tfhConfig
import datetime
import pytz
        """
        for i, match in enumerate(matches):
            module_code += f'''
def test_readme_example_{i}():
    """
{match}
    """
    pass
'''

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
    if file_path.name == "README.md":
        doctest_file = ReadmeDoctestModule.create_doctest_file(file_path)
        if doctest_file:
            # Track the temporary file for cleanup later
            TEMP_FILES.append(doctest_file)
            return ReadmeDoctestModule.from_parent(parent=parent, path=doctest_file)
    return None

def pytest_sessionfinish(session, exitstatus):
    # Cleanup all temporary files after the session ends
    for temp_file in TEMP_FILES:
        temp_file.unlink(missing_ok=True)