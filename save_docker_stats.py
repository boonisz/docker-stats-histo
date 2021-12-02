#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from subprocess import check_output
from typing import Dict

log = logging.getLogger(__name__)

HERE = Path(os.path.dirname(os.path.realpath(__file__)))
DOCKER_BIN = "/snap/bin/docker"
# DOCKER_BIN = "/usr/bin/docker"

TABLE_NAME = "dc_stats"


def parse_args():
    parser = argparse.ArgumentParser(description="Extract docker stats in a sqlite db")

    parser.add_argument(
        "sqlite",
        nargs="?",
        type=Path,
        help="Path to sqlite file",
        default=HERE / "stats.sqlite",
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    return args.sqlite, args.debug


def init_db(sqlite_fn: Path):
    """Initialize database: create sqlite and create table (if not exists)"""
    if sqlite_fn.exists():
        return

    log.info("Create sqlite file: '%s'", sqlite_fn)
    con = sqlite3.connect(str(sqlite_fn))
    cur = con.cursor()
    cur.execute(f"CREATE TABLE {TABLE_NAME} (date timestamp)")
    con.close()


def add_row(sqlite_fn: Path, stats: Dict):
    """Add new stat entry in database"""
    con = sqlite3.connect(str(sqlite_fn), detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()

    # Create column if needed
    existing_cols = [
        c[1] for c in cur.execute(f"PRAGMA table_info({TABLE_NAME});").fetchall()
    ]
    log.debug("existing_cols: %s", existing_cols)
    for k in stats:
        if k in existing_cols:
            continue
        log.debug("Create '%s' col", k)
        cur.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN '{k}' 'float';")

    # Insert row
    # ts = stats.pop("date")
    cols = "`, `".join(stats.keys())

    values = tuple(stats.values())
    v = ", ".join(["?" for v in values])
    cmd = f"INSERT INTO {TABLE_NAME} (`{cols}`) VALUES ({v});"
    log.debug("SQLITE3: %s", cmd)
    log.debug("SQLITE3: values: %s", values)
    cur.execute(cmd, values)
    cur.execute("COMMIT")
    con.close()


def format_stats(out):
    """Format docker stats"""
    json_stats = b"{" + out.replace(b"\n", b", ")[:-2] + b"}"
    stats = json.loads(json_stats)
    for k in stats:
        stats[k] = str(stats[k]).split(" ")[
            0
        ]  # keep first memory (ex: "658.4MiB / 7.724GiB" > "658.4MiB")
        stats[k] = stats[k].replace("MiB", "e3")
        stats[k] = stats[k].replace("GiB", "e6")
        stats[k] = stats[k].replace("B", "")
        stats[k] = float(stats[k]) / 1000  # values are in MiB

    stats["date"] = datetime.now()
    return stats


def main():
    sqlite_fn, debug = parse_args()
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    log.info("Export stats in %s", sqlite_fn)
    out = check_output(
        [DOCKER_BIN, "stats", "--no-stream", "--format", '"{{.Name}}": "{{.MemUsage}}"']
    )
    stats = format_stats(out)
    init_db(sqlite_fn)
    add_row(sqlite_fn, stats)


if __name__ == "__main__":
    main()
