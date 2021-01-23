"""
publish.py will publish a new release.

It relies on a `gh-cli` being available on the path and
already being configured. You should also have push + release
privileges on the repo
"""

import argparse
import json
import sys
from subprocess import run
from typing import List

from util import parse_index, find_locally_existing, fetch_latest_maps, add_full_paths


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
    note = "Maps updated in release: "
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
    for map_path in updated_maps:
        cmd.append(map_path)

    run(cmd, check=True)


if __name__ == "__main__":
    args = get_args()

    index_file = "index.json"
    index_data = parse_index(index_file)
    maps_data = index_data["maps"]

    static_items = list(filter(lambda i: i["path"] not in args.map_paths, maps_data))

    locally_available = find_locally_existing(static_items)
    if locally_available:
        print("The following local files will be replaced:")
        for item in locally_available:
            print("\t" + str(item["path"]))
        user_choice = input("Is that okay? (y/N)")
        if user_choice.capitalize() != "Y":
            print("Aborting...")
            sys.exit(2)

    if args.dry:
        print("Skipping further processing")
        sys.exit(0)

    fetch_latest_maps(static_items)

    # Now we can assume the only changes are updated maps
    updated_index = update_index_revisions(args.map_paths, index_file)
    push_index("Bumping revisions", index_file)
    push_release(args.map_paths, updated_index)