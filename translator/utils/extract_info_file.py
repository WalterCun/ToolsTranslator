# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/utils/extract_info_file.py """

import re
from pathlib import Path

LANG_PATTERN = re.compile(r"\b([a-z]{2}(-[a-z]{2})?)\b", re.IGNORECASE)

def extract_lang_info_from_filename(path: Path) -> dict[str, str or Path]:
    """
    Extracts language and other metadata from a file's path.

    This function processes the given file path to decompose it into
    useful components: the full path as a string, the parent directory,
    the file extension, the full filename, and an optionally extracted
    language code if present in the filename.

    :param path: The file path to be analyzed.
    :type path: Path
    :return: A dictionary containing the file path, directory, file
        extension, full filename, and an optional detected language code.
    :rtype: dict[str, str]
    """
    directory = path.parent
    file, ext = path.name.split(".", 1)
    match = LANG_PATTERN.search(file)

    return {
        "path": path,
        "directory": directory,
        "lang": str(match.group(1)) if match else None,
        "ext": ext,
        "name": path.name
    }