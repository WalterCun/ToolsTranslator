#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup configuration for translation-tools"""
from setuptools import setup, find_packages
import os

# Leer el contenido del README
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="translation-tools",
    version="0.1.5",
    description="Una librería de soporte para traducir archivos i18n.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Walter Cun Bustamante",
    author_email="waltercunbustamante@gmail.com",
    url="https://github.com/WalterCun/ToolsTranslator",
    packages=find_packages(include=['translator', 'translator.*']),
    package_data={
        'translator': ['**/*.py'],
    },
    include_package_data=True,
    install_requires=[
        "requests>=2.32.3",
        "requests-cache>=1.2.1",
        "pydantic-settings>=2.8.0",
    ],
    extras_require={
        'dev': [
            "pytest",
            "black",
            "flake8",
            "build>=1.2.2.post1",
            "twine",
        ],
        'yml': [
            "pyyaml>=6.0.2",
        ]
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Utilities",
        "Topic :: Text Processing :: Linguistic",
        "Environment :: Console",
        "Natural Language :: English",
        "Natural Language :: Spanish",
    ],
    keywords=["translate", "i18n", "automation"],
    license="MIT",
)