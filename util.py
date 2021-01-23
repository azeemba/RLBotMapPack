"""
Helpers for both publish and download
"""

import json
from pathlib import Path
import os


def parse_index(filepath, root=None):
    with open(filepath) as fh:
        data = json.load(fh)

    return data


def add_full_paths(index_data, root=None):
    if root is None:
        root = Path.cwd()

    for item in index_data["maps"]:
        item["full_path"] = root / Path(item["path"])

    return index_data


def find_locally_existing(index_items):
    """
    Returns items that already exist locally
    """

    def exists(item):
        item["full_path"].exists()

    return list(filter(exists, index_items))


def fetch_latest_maps(index_items):
    """
    [{path, revision}] is the input
    For each one, download from the latest release
    """
    if len(index_items) > 0:
        raise NotImplementedError("I don't know how to pull releases yet")