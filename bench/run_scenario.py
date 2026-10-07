#!/usr/bin/env python3
"""
Lance main() d'une version donnée de l'exporteur contre le serveur mock.

Les URL naviki.org sont codées en dur dans le script : on réécrit l'hôte au
niveau de requests et de webdriver.Firefox plutôt que de modifier le code
mesuré.

Usage : run_scenario.py <exporteur.py> <base_url_mock> -- <arguments du script>
"""

import importlib.abc
import importlib.util
import sys

import requests

REAL_HOST = "https://www.naviki.org"


class _PatchAfterImport(importlib.abc.MetaPathFinder):
    """Applique patch(module) juste après le premier import de `name`."""

    def __init__(self, name, patch):
        self.name, self.patch = name, patch

    def find_spec(self, fullname, path, target=None):
        if fullname != self.name:
            return None
        sys.meta_path.remove(self)
        spec = importlib.util.find_spec(fullname)
        exec_module = spec.loader.exec_module

        def exec_and_patch(module):
            exec_module(module)
            self.patch(module)

        spec.loader.exec_module = exec_and_patch
        return spec


def redirect_firefox_when_imported(base_url):
    """
    Redirige Firefox vers le mock sans importer Selenium nous-mêmes : son
    chargement (~140 ms) doit rester à la charge du script mesuré.
    """

    def patch(webdriver):
        original_get = webdriver.Firefox.get

        def get(self, url):
            return original_get(self, url.replace(REAL_HOST, base_url))

        webdriver.Firefox.get = get

    sys.meta_path.insert(0, _PatchAfterImport("selenium.webdriver", patch))


def main():
    exporter_path, base_url = sys.argv[1], sys.argv[2]
    script_args = sys.argv[sys.argv.index("--") + 1 :]

    original_request = requests.Session.request

    def request(self, method, url, *args, **kwargs):
        return original_request(
            self, method, url.replace(REAL_HOST, base_url), *args, **kwargs
        )

    requests.Session.request = request

    redirect_firefox_when_imported(base_url)

    spec = importlib.util.spec_from_file_location("exporter", exporter_path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    # load_env_file lit le .env à côté du script : la copie de bench n'en a pas
    sys.argv = [exporter_path] + script_args
    exporter.main()


if __name__ == "__main__":
    main()
