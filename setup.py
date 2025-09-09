#!/usr/bin/env python3
"""
Setup script for HexShell
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hexshell",
    version="1.0.0",
    author="HexShell Team",
    author_email="",
    description="Cyberpunk terminal interface for technical note-taking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/popShell/HexShell",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Editors",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.40.0",
        "watchdog>=3.0.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "libtmux>=0.25.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "hexshell=hexshell.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hexshell": ["*.css", "templates/*/*.md"],
    },
)