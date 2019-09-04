import setuptools
from stibium import __version__, __author__

with open("README.rst", "r") as fh:
    long_description = fh.read()


with open('requirements.txt', 'r') as fh:
    requirements = [line.rstrip('\n') for line in fh.readlines()]

setuptools.setup(
    name="stibium",
    version=__version__,
    author=__author__,
    author_email="szymszl@firemail.cc",
    description="A framework for FB Messenger bots",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/szymonszl/stibium",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

