#!/usr/bin/env python3
"""
Convert episode JSON files from data/graph_data/ into a single CSV.

File naming convention:
  episode_data_new_ips_<N>.json   → network N, episodes as-is
  episode_data_new_ips_<N>b.json  → network N, episodes renumbered 101-200
                                     (second half when split across two files)

Output columns: network, episode, outcome
"""

import csv
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "graph_data"
OUTPUT_CSV = Path(__file__).parent / "episodes.csv"

# (network, file, episode_offset)
FILE_PLAN = [
    (1, "episode_data_new_ips_1.json",  0),
    (2, "episode_data_new_ips_2.json",  0),
    (2, "episode_data_new_ips_2b.json", 100),
    (3, "episode_data_new_ips_3.json",  0),
    (4, "episode_data_new_ips_4.json",  0),
    (5, "episode_data_new_ips_5.json",  0),
    (5, "episode_data_new_ips_5b.json", 100),
]

def outcome(end_reason: str) -> str:
    return "win" if end_reason == "AgentStatus.Success" else "fail"

def main():
    rows = []
    for network, filename, offset in FILE_PLAN:
        path = DATA_DIR / filename
        if not path.exists():
            print(f"WARNING: {path} not found, skipping.", file=sys.stderr)
            continue
        with open(path) as f:
            data = json.load(f)
        for ep in data:
            rows.append({
                "network": network,
                "episode": ep["episode"] + offset,
                "outcome": outcome(ep["end_reason"]),
            })
        print(f"Loaded {len(data):>3} episodes from {filename} (network {network}, offset {offset})")

    rows.sort(key=lambda r: (r["network"], r["episode"]))

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["network", "episode", "outcome"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
