#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" bk/utils/searches.py """

from pathlib import Path
from typing import Union, List


def search_path(search_pattern: Path, base_dir: Path = None, all_matches: bool = False) -> Union[
    Path, List[Path], None]:
    """
    Searches for a path pattern in the base directory and returns the first match
    or all matches.

    Args:
        base_dir: Base directory where to start the search
        search_pattern: Pattern or file name to search for
        all_matches: If True, returns all matches; otherwise,
                     returns only the first match. Default is False.

    Returns:
        A path (Path) if all_matches=False and there's a match,
        a list of paths if all_matches=True, or None if there are no matches.

    Raises:
        ValueError: If the base directory doesn't exist or is not a directory
    """

    # Verify that the directory exists
    if (not base_dir.exists() or not base_dir.is_dir())  :
        raise ValueError(f"The base directory '{base_dir}' doesn't exist or is not a directory")

    # Convert the search pattern to a string for comparisons
    pattern_text = str(search_pattern)
    matches = []

    # Use glob to search for files recursively (more efficient than os.walk)
    for path in base_dir.glob("**/*"):
        if pattern_text in str(path):
            matches.append(path)
            if not all_matches:
                return path

    # Return all matches or None if no match was found
    if all_matches:
        return matches if matches else None
    return None
