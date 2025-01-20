import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

tests_require = ['pytest==8.3.4', 'pytest-cov==6.0.0', 'coverage==7.6.10', 'coveralls==4.0.1']
install_requires = ['lark==1.2.2', 'babel==2.16.0', 'pytz==2024.2', 'python-dateutil==2.9.0.post0']


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


VERSION = '0.1.1'

setup(
    name="timefhuman",
    version=VERSION,
    author="Alvin Wan",
    author_email='hi@alvinwan.com',
    description=("Extract datetimes, datetime ranges, and datetime lists from natural language text"),
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license="Apache 2.0",
    url="https://github.com/alvinwan/timefhuman",
    packages=['timefhuman'],
    tests_require=tests_require,
    install_requires=install_requires,
    download_url='https://github.com/alvinwan/timefhuman/archive/%s.zip' % VERSION,
    extras_require={"test":tests_require},
    include_package_data=True,
    classifiers=[
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
)
