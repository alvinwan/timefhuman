import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

tests_require = ['pytest', 'pytest-cov==2.5.1', 'coverage == 3.7.1', 'coveralls == 1.1']
install_requires = []


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


VERSION = '0.0.1'

setup(
    name="timefhuman",
    version=VERSION,
    author="Alvin Wan",
    author_email='hi@alvinwan.com',
    description=("Convert human-readable date-like string to datetime object"),
    license="BSD",
    url="https://github.com/alvinwan/timefhuman",
    packages=['timefhuman'],
    tests_require=tests_require,
    install_requires=install_requires + tests_require,
    download_url='https://github.com/alvinwan/timefhuman/archive/%s.zip' % VERSION,
    classifiers=[
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
)
