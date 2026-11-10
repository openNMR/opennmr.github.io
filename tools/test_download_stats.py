"""Tests for download_stats.py (no network). Run: python -m unittest discover tools"""
import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import download_stats as ds

RELEASES = [
    {"tag_name": "v0.9.11", "published_at": "2026-11-09T10:00:00Z", "draft": False,
     "assets": [{"name": "openNMR-0.9.11-windows-setup.exe", "download_count": 2},
                {"name": "SHA256SUMS", "download_count": 1}]},
    {"tag_name": "v0.9.12", "published_at": None, "draft": True,
     "assets": [{"name": "openNMR-0.9.12-windows-setup.exe", "download_count": 0}]},
    {"tag_name": "v0.8.3", "published_at": "2026-10-25T10:00:00Z", "draft": False,
     "assets": [{"name": "openNMR-0.8.3-windows-setup.exe", "download_count": 3}]},
]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TestDownloadStats(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "downloads.csv")

    def test_rows_skip_drafts_and_sort_oldest_first(self):
        rows = ds.snapshot_rows(RELEASES, "2026-11-10")
        self.assertEqual([r["tag"] for r in rows], ["v0.8.3", "v0.9.11", "v0.9.11"])
        self.assertEqual(sum(r["downloads"] for r in rows), 6)

    def test_new_file_gets_header(self):
        ds.update_csv(self.path, ds.snapshot_rows(RELEASES, "2026-11-10"), "2026-11-10")
        rows = read(self.path)
        self.assertEqual(list(rows[0].keys()), ds.FIELDS)
        self.assertEqual(len(rows), 3)

    def test_same_day_replaces_other_days_kept(self):
        ds.update_csv(self.path, ds.snapshot_rows(RELEASES, "2026-11-10"), "2026-11-10")
        RELEASES[0]["assets"][0]["download_count"] = 5
        try:
            for _ in range(2):  # re-run the same day twice
                ds.update_csv(self.path, ds.snapshot_rows(RELEASES, "2026-11-11"), "2026-11-11")
        finally:
            RELEASES[0]["assets"][0]["download_count"] = 2
        rows = read(self.path)
        self.assertEqual(len(rows), 6)
        win = {r["date"]: r["downloads"] for r in rows if r["asset"].endswith("0.9.11-windows-setup.exe")}
        self.assertEqual(win, {"2026-11-10": "2", "2026-11-11": "5"})


if __name__ == "__main__":
    unittest.main()
