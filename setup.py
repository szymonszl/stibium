import setuptools
from carbonium import __version__, __author__

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="carbonium",
    version=__version__,
    author=__author__,
    author_email="szymszl@firemail.cc",
    description="A framework for FB Messenger bots",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/szymonszl/carbonium",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)