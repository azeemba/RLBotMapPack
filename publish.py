"""
publish.py will publish a new release.

It relies on a `gh-cli` being available on the path and
already being configured. You should also have push + release
privileges on the repo
"""

import argparse
import json
import sys
import shutil
import os

from pathlib import Path
from subprocess import run
from typing import List
from tempfile import TemporaryDirectory


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dry", action="store_true")
    parser.add_argument(
        "map_paths",
        nargs="+",
        metavar="map_relpaths",
        help="Relative paths from the root of maps to replace. Should match index.json",
    )

    return parser.parse_args()


def warn_about_local_replacements(static_items):
    """Given the list of maps that are not being updated
    we check if they exist locally and are goign to be
    replaced by versions available in a release"""
    locally_available = find_locally_existing(static_items)
    if locally_available:
        print("The following local files will be replaced:")
        for item in locally_available:
            print("\t" + str(item["path"]))
        user_choice = input("Is that okay? (y/N)")
        if user_choice.capitalize() != "Y":
            print("Aborting...")
            sys.exit(2)


def update_index_revisions(map_paths: List[str], filepath):
    with open(filepath) as fh:
        data = json.load(fh)

    data["revision"] += 1

    for item in data["maps"]:
        if item["path"] in map_paths:
            item["revision"] += 1

    with open(filepath, "w") as fh:
        json.dump(data, fh, indent=4)

    return add_full_paths(data)


def push_index(message, filepath):
    cmd = ["git", "add", filepath]
    run(cmd, check=True)

    cmd = ["git", "commit", "-m", message]
    run(cmd, check=True)

    cmd = ["git", "push"]
    run(cmd, check=True)


def push_release(updated_maps, updated_index):
    revision = updated_index["revision"]
    note = "Maps updated in release: \n"
    for map_path in updated_maps:
        note += f"- {map_path} \n"

    cmd = [
        "gh",
        "release",
        "create",
        f"v{revision}",
        "--title",
        "Update maps",
        "--notes",
        note,
    ]
    for item in updated_index["maps"]:
        cmd.append(str(item["full_path"]))

    run(cmd, check=True)


def parse_index(filepath, root=None):
    with open(filepath) as fh:
        data = json.load(fh)

    return add_full_paths(data, root)


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
        return item["full_path"].exists()

    return list(filter(exists, index_items))


def fetch_latest_maps(index_items, revision):
    """
    [{path, revision}] is the input
    For each one, download from the latest release
    """
    if len(index_items) < 1:
        return

    release = f"v{revision}"
    with TemporaryDirectory() as dirname:
        cmd = ["gh", "release", "download", release, "--dir", dirname]
        cmd.extend(["-p", "*.upk"])

        run(cmd, check=True)

        for item in index_items:
            basename = item["full_path"].name
            print("Replacing: ", basename)
            downloaded_path = Path(dirname, basename)
            shutil.copy2(downloaded_path, item["full_path"])


if __name__ == "__main__":
    args = get_args()

    index_file = "index.json"
    index_data = parse_index(index_file)
    maps_data = index_data["maps"]

    static_items = list(filter(lambda i: i["path"] not in args.map_paths, maps_data))
    warn_about_local_replacements(static_items)

    if args.dry:
        print("Skipping further processing")
        sys.exit(0)

    fetch_latest_maps(static_items, index_data["revision"])

    # Now we can assume the only changes are updated maps
    updated_index = update_index_revisions(args.map_paths, index_file)
    push_index("Bumping revisions", index_file)
    push_release(args.map_paths, updated_index)