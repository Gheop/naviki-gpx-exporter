#!/usr/bin/env python3
"""
Lance main() d'une version donnée de l'exporteur contre le serveur mock.

Les URL naviki.org sont codées en dur dans le script : on réécrit l'hôte au
niveau de requests et de webdriver.Firefox plutôt que de modifier le code
mesuré.

Usage : run_scenario.py <exporteur.py> <base_url_mock> -- <arguments du script>
"""

import importlib.util
import sys

import requests
from selenium import webdriver

REAL_HOST = "https://www.naviki.org"


def main():
    exporter_path, base_url = sys.argv[1], sys.argv[2]
    script_args = sys.argv[sys.argv.index("--") + 1 :]

    original_request = requests.Session.request

    def request(self, method, url, *args, **kwargs):
        return original_request(
            self, method, url.replace(REAL_HOST, base_url), *args, **kwargs
        )

    requests.Session.request = request

    original_get = webdriver.Firefox.get

    def get(self, url):
        return original_get(self, url.replace(REAL_HOST, base_url))

    webdriver.Firefox.get = get

    spec = importlib.util.spec_from_file_location("exporter", exporter_path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    # load_env_file lit le .env à côté du script : la copie de bench n'en a pas
    sys.argv = [exporter_path] + script_args
    exporter.main()


if __name__ == "__main__":
    main()
