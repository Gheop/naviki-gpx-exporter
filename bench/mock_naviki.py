"""
Faux serveur Naviki pour les benchmarks.

Latences et tailles calibrées sur l'API réelle (bench/JOURNAL.md, mesures du
2026-10-07) : liste en ~60 ms + 0,9 ms par trajet (20 par défaut, `limit`
respecté), GPX de 80 à 330 Ko en 450 ms, token posé dans localStorage 400 ms
après la soumission du formulaire, échange du code (feSession) en 370 ms.
Chaque requête dort indépendamment ; la vraie API a confirmé tenir 4 requêtes
simultanées sans hausse de latence.
"""

import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

WAY_COUNT = 431
PAGE_SIZE = 20
LIST_BASE_LATENCY_S = 0.06
LIST_PER_WAY_S = 0.0009
FESESSION_LATENCY_S = 0.37
CODE = "mock-code-0000"
MOBILE_PATH = "/fr/naviki/single-pages/loading//mobile.html"
DOWNLOAD_LATENCY_S = 0.45
OAUTH_PAGE_LATENCY_S = 0.3
TOKEN_DELAY_MS = 400
TOKEN = "mock-token-0000"


def build_ways(seed=42):
    rng = random.Random(seed)
    ways = []
    base = 1774000000  # mars 2026, les trajets remontent dans le temps
    for i in range(WAY_COUNT):
        crdate = base - i * 86400 - rng.randint(0, 3600)
        t = time.gmtime(crdate)
        # 95 % du format le plus courant, le reste couvre les autres branches
        kind = rng.random()
        if kind < 0.95:
            title = time.strftime("%d/%m/%Y, %H:%M", t)
        elif kind < 0.97:
            title = time.strftime("%d.%m.%y, %H:%M", t)
        elif kind < 0.99:
            title = "Trajet-" + time.strftime("%Y%m%d", t)
        else:
            title = f"Balade {i}"
        ways.append(
            {
                "uuid": f"00000000-0000-4000-8000-{i:012d}",
                "title": title,
                "crdate": crdate,
                # remplissage pour retrouver ~840 octets par trajet comme l'API réelle
                "geom": "x" * 700,
                "gpx_size": rng.randint(80_000, 330_000),
            }
        )
    return ways


WAYS = build_ways()
WAYS_BY_UUID = {w["uuid"]: w for w in WAYS}

GPX_HEAD = b'<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1"><trk><trkseg>\n'
GPX_POINT = b'<trkpt lat="48.85" lon="2.35"><ele>35</ele></trkpt>\n'
GPX_TAIL = b"</trkseg></trk></gpx>\n"


def gpx_body(size):
    n = max(1, (size - len(GPX_HEAD) - len(GPX_TAIL)) // len(GPX_POINT))
    return GPX_HEAD + GPX_POINT * n + GPX_TAIL


OAUTH_PAGE = b"""<!doctype html><html><body>
<form method="post">
<input name="username"><input name="password" type="password">
<input type="submit" value="Connexion">
</form></body></html>"""

MOBILE_PAGE = (
    """<!doctype html><html><body>Chargement
<script>setTimeout(function(){localStorage.setItem('_n_a_at','%s');}, %d);</script>
</body></html>"""
    % (TOKEN, TOKEN_DELAY_MS)
).encode()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    # en-têtes et corps partent en deux write : sans TCP_NODELAY, Nagle et
    # l'ACK retardé ajoutent ~40 ms par réponse, absents de l'API réelle
    disable_nagle_algorithm = True

    def log_message(self, *args):
        pass

    def _send(self, status, body, content_type, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/oauth2/auth":
            time.sleep(OAUTH_PAGE_LATENCY_S)
            return self._send(200, OAUTH_PAGE, "text/html; charset=UTF-8")
        if url.path.endswith("mobile.html"):
            return self._send(200, MOBILE_PAGE, "text/html; charset=UTF-8")
        if url.path == "/fr/naviki/ajax-dispatcher/":
            time.sleep(FESESSION_LATENCY_S)
            query = parse_qs(url.query)
            ok = query.get("request[action]") == ["feSession"] and query.get(
                "request[arguments][code]"
            ) == [CODE]
            body = {"status": ok}
            if ok:
                body.update(
                    accessToken=TOKEN, refreshToken="mock-rt", feUserId=1, username="b"
                )
            return self._send(200, json.dumps(body).encode(), "application/json")
        if url.path == "/naviki/api/v6/Way/2/findUserWaysByFilter/":
            query = parse_qs(url.query)
            offset = int(query.get("offset", ["0"])[0])
            limit = int(query.get("limit", [str(PAGE_SIZE)])[0])
            page = [
                {k: v for k, v in w.items() if k != "gpx_size"}
                for w in WAYS[offset : offset + limit]
            ]
            time.sleep(LIST_BASE_LATENCY_S + LIST_PER_WAY_S * len(page))
            if self.headers.get("Authorization") != f"Bearer {TOKEN}":
                return self._send(401, b"{}", "application/json")
            return self._send(
                200, json.dumps({"ways": page}).encode(), "application/json"
            )
        self._send(404, b"", "text/plain")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode())
        if self.path.startswith("/oauth2/auth"):
            # comme le vrai serveur : le formulaire se poste sur sa propre URL
            if form.get("password") == ["wrong"]:
                return self._send(200, OAUTH_PAGE, "text/html; charset=UTF-8")
            return self._send(
                302,
                b"",
                "text/html",
                {"Location": f"{MOBILE_PATH}?code={CODE}"},
            )
        if self.path == "/naviki/api/v6/Util/wayToFileWithUser/":
            time.sleep(DOWNLOAD_LATENCY_S)
            way = WAYS_BY_UUID.get(form.get("wayUuid", [""])[0])
            if way is None or form.get("oauth_token", [""])[0] != TOKEN:
                return self._send(200, b'{"error":1}', "application/json")
            return self._send(
                200, gpx_body(way["gpx_size"]), "application/gpx+xml; charset=UTF-8"
            )
        self._send(404, b"", "text/plain")


class MockNaviki:
    """Serveur dans un thread, utilisable comme context manager."""

    def __enter__(self):
        ThreadingHTTPServer.daemon_threads = True
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
