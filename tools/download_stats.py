"""Append today's GitHub release download counts to a CSV.

GitHub only reports a running total per release file, with no dates, so this
records a snapshot (one row per file per day). Daily downloads are the
difference between consecutive days.

    python tools/download_stats.py downloads.csv
    python tools/download_stats.py downloads.csv --repo openNMR/opennmr.github.io

Running it twice on the same day replaces that day's rows rather than
duplicating them. Uses GITHUB_TOKEN if set (higher rate limit), but the
repo is public so it works without one.
"""
import argparse
import csv
import datetime as dt
import json
import os
import urllib.request

FIELDS = ["date", "tag", "published", "asset", "downloads"]


def fetch_releases(repo, token=None):
    """All releases of `repo`, following pagination."""
    releases, page = [], 1
    while True:
        url = f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                   "User-Agent": "opennmr-download-stats"})
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.load(r)
        releases += batch
        if len(batch) < 100:
            return releases
        page += 1


def snapshot_rows(releases, date):
    """One row per release file, in a stable order."""
    rows = []
    for rel in releases:
        if rel.get("draft"):
            continue
        for a in rel.get("assets", []):
            rows.append({"date": date, "tag": rel["tag_name"],
                         "published": (rel.get("published_at") or "")[:10],
                         "asset": a["name"], "downloads": int(a["download_count"])})
    rows.sort(key=lambda r: (r["published"], r["tag"], r["asset"]))
    return rows


def update_csv(path, new_rows, date):
    """Rewrite `path` with any earlier rows for `date` replaced by `new_rows`."""
    old = []
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, newline="", encoding="utf-8") as f:
            old = [r for r in csv.DictReader(f) if r["date"] != date]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(old + new_rows)
    return len(old) + len(new_rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv")
    ap.add_argument("--repo", default="openNMR/opennmr.github.io")
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    a = ap.parse_args(argv)
    rows = snapshot_rows(fetch_releases(a.repo, os.environ.get("GITHUB_TOKEN")), a.date)
    update_csv(a.csv, rows, a.date)
    total = sum(r["downloads"] for r in rows)
    print(f"{a.date}: {len(rows)} files, {total} downloads in total")


if __name__ == "__main__":
    main()
