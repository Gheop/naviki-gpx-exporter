#!/usr/bin/env python3
"""
Profil des latences réelles de Naviki, pour calibrer le serveur mock.

Charge volontairement faible : un login, la pagination complète de la liste,
puis quelques téléchargements GPX. Écrit le résultat en JSON sur stdout.

Usage : python bench/profile_real.py [--downloads 5]
"""

import argparse
import importlib.util
import json
import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "exporter", ROOT / "naviki-gpx-exporter.py"
)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

API = "https://www.naviki.org/naviki/api/v6"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--downloads", type=int, default=5)
    parser.add_argument("--types", default="routedAll,recordedMy,recordedOthers")
    args = parser.parse_args()

    env = exporter.load_env_file()
    t0 = time.perf_counter()
    token = exporter.get_oauth_token_with_selenium(
        env["NAVIKI_USERNAME"], env["NAVIKI_PASSWORD"], headless=True
    )
    login_s = time.perf_counter() - t0
    if not token:
        raise SystemExit("login échoué")

    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})

    pages = []
    ways = []
    offset = 0
    while True:
        t = time.perf_counter()
        r = s.get(
            f"{API}/Way/2/findUserWaysByFilter/?filter={args.types}"
            f"&sort=crdateDesc&offset={offset}&fullDataSet=0"
        )
        dt = time.perf_counter() - t
        batch = r.json()["ways"]
        pages.append({"s": dt, "n": len(batch), "bytes": len(r.content)})
        if not batch:
            break
        ways.extend(batch)
        offset += len(batch)

    downloads = []
    for way in ways[: args.downloads]:
        t = time.perf_counter()
        dl = s.post(
            f"{API}/Util/wayToFileWithUser/",
            data={"wayUuid": way["uuid"], "oauth_token": token, "format": "gpx"},
            headers={"Authorization": None},
        )
        downloads.append({"s": time.perf_counter() - t, "bytes": len(dl.content)})

    print(
        json.dumps(
            {
                "login_s": login_s,
                "ways_total": len(ways),
                "pages": pages,
                "downloads": downloads,
                "sample_way_keys": sorted(ways[0].keys()) if ways else [],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
