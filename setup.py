from setuptools import setup

tests_require = []
install_requires = []

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
