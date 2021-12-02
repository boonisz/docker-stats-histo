#!/usr/bin/env python3

import argparse
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px

log = logging.getLogger(__name__)

HERE = Path(os.path.dirname(os.path.realpath(__file__)))

TABLE_NAME = "dc_stats"
INTERVALS = [1]  # on cron interval is 10min


def parse_args():
    parser = argparse.ArgumentParser(description="Extract docker stats in a sqlite db")

    parser.add_argument(
        "sqlite",
        nargs="?",
        type=Path,
        help="Path to sqlite file",
        default=HERE / "stats.sqlite",
    )
    parser.add_argument(
        "html",
        nargs="?",
        type=Path,
        help="Path to html output report",
        default=HERE / "stats.html",
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    return args.sqlite, args.html, args.debug


def generate_html_report(sqlite_fn: Path, html_fn: Path):
    # Create your connection.
    log.info(f"Read sqlite {sqlite_fn}")
    cnx = sqlite3.connect(sqlite_fn)

    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", cnx)
    df = df.set_index("date")
    log.info(f"Find {len(df)} items")

    # df["granu"] = 1

    dfs = pd.DataFrame()
    for i in INTERVALS:
        dfi = df[::i].copy()

        # dfi["granu"] = i
        dfs = dfs.append(dfi)

    log.info(f"Get {len(dfs)} items after sub-sampling")
    fig = px.area(dfs)
    fig.for_each_trace(lambda trace: trace.update(fillcolor=trace.line.color))
    fig["layout"].pop("updatemenus")  # optional, drop animation buttons
    fig.update_layout(transition={"duration": 1e12})
    now = datetime.now()
    fig.update_layout(
        title="Utilisation de RAM pour les docker-compose de l'eunuque (pour voir une stat, mettre la sourie sur "
        f"le haut des courbes, vers les points), généré le {now.strftime('%d/%m/%Y %H:%M:%S')}",
        xaxis_title="Temps",
        yaxis_title="RAM",
    )
    fig.write_html(html_fn, include_plotlyjs="cdn")
    log.info(f"Report generate in {html_fn}")


def main():
    sqlite_fn, html_fn, debug = parse_args()
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    generate_html_report(sqlite_fn, html_fn)


if __name__ == "__main__":
    main()
