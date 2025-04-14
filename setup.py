#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""  """
from setuptools import setup, find_packages

setup(
    name="translation-tools",
    version="0.1.0",
    description="Una librería de soporte para traducir archivos i18n.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Walter Cun Bustamante",
    author_email="waltercunbustamante@gmail.com",
    url="https://github.com/waltercun/ToolsTranslator",
    license="MIT",
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
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
    keywords=["traducción", "i18n", "automatización"],
    packages=find_packages(where="translator", exclude=["tests*", "docs*", "struct_files*", "examples*"]),
    install_requires=[
        "pydantic-settings>=2.8.0",
        "setuptools>=75.8.2",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "build>=1.2.2.post1",
            "twine",
        ],
        "autotranslate": [
            "requests>=2.32.3",
            "requests-cache>=1.2.1",
        ],
        "yml": [
            "pyyaml>=6.0.2",
        ],
        "all": [
            "requests>=2.32.3",
            "requests-cache>=1.2.1",
            "pyyaml>=6.0.2",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/waltercun/ToolsTranslator",
        "Repository": "https://github.com/waltercun/ToolsTranslator",
    },
)