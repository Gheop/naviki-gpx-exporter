#!/usr/bin/env python3
"""
Script pour télécharger automatiquement les traces GPX depuis Naviki
Authentification automatique : login HTTP direct, Selenium (Firefox) en secours

Installation requise:
  pip install selenium requests beautifulsoup4

Installation du driver Firefox (geckodriver):
  - Ubuntu/Debian: sudo apt install firefox-geckodriver
  - Arch: sudo pacman -S geckodriver
  - Ou téléchargez depuis:
    https://github.com/mozilla/geckodriver/releases

Usage:
  python naviki-gpx-exporter.py --username VotreLogin --password votremdp
  python naviki-gpx-exporter.py --token VOTRE-TOKEN-OAUTH
  python naviki-gpx-exporter.py --username VotreLogin --password votremdp
    --headless
"""

import requests
import time
import re
import pathlib
import argparse
import json
import sys
import os
import threading
from urllib.parse import parse_qs, urlparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone


def config_dir():
    """
    Dossier contenant .env, surchargeable par NAVIKI_CONFIG_DIR
    (tests, ou volume persistant sous Docker)
    """
    return pathlib.Path(
        os.environ.get("NAVIKI_CONFIG_DIR", pathlib.Path(__file__).parent)
    )


def load_env_file():
    """
    Charge les variables d'environnement depuis le fichier .env

    Returns:
        dict: Dictionnaire contenant les variables d'environnement
    """
    env_vars = {}
    env_path = config_dir() / ".env"

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Ignorer les lignes vides et les commentaires
                if line and not line.startswith("#"):
                    # Gérer les lignes de type KEY=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        value = value.strip()
                        # KEY="valeur" : guillemets retirés, comme le font
                        # la plupart des outils .env
                        if len(value) >= 2 and value[0] == value[-1] in "\"'":
                            value = value[1:-1]
                        env_vars[key.strip()] = value

    return env_vars


def save_credentials_to_env(username, password):
    """
    Sauvegarde les identifiants dans le fichier .env

    Args:
        username: Nom d'utilisateur Naviki
        password: Mot de passe Naviki
    """
    env_path = config_dir() / ".env"

    # Préserver les autres variables du fichier
    existing_content = load_env_file()
    existing_content["NAVIKI_USERNAME"] = username
    existing_content["NAVIKI_PASSWORD"] = password

    # Créé directement en 600 : un open() classique laisserait le mot de
    # passe lisible (644 selon l'umask) jusqu'au chmod
    fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("# Configuration Naviki GPX Exporter\n")
        f.write("# Ce fichier est automatiquement généré et ignoré par Git\n\n")
        f.write("# Identifiants Naviki\n")
        f.write(f"NAVIKI_USERNAME={existing_content['NAVIKI_USERNAME']}\n")
        f.write(f"NAVIKI_PASSWORD={existing_content['NAVIKI_PASSWORD']}\n")

        # Ajouter les autres variables si elles existent
        for key, value in existing_content.items():
            if key not in ["NAVIKI_USERNAME", "NAVIKI_PASSWORD"]:
                f.write(f"\n{key}={value}\n")

    # Un fichier préexistant garde ses droits avec os.open
    os.chmod(env_path, 0o600)
    print(f"✅ Identifiants sauvegardés dans {env_path}")
    print("🔒 Permissions définies à 600 " "(lecture/écriture uniquement pour vous)")


OAUTH_REDIRECT_URI = (
    "https://www.naviki.org/fr/naviki/single-pages/loading//mobile.html"
)
OAUTH_SCOPE = "way,profile,contest"
OAUTH_URL = (
    "https://www.naviki.org/oauth2/auth?lang=fr"
    f"&redirect_uri={OAUTH_REDIRECT_URI}&client_id=web"
    f"&scope={OAUTH_SCOPE}&response_type=code"
)
AJAX_DISPATCHER_URL = "https://www.naviki.org/fr/naviki/ajax-dispatcher/"


def get_oauth_token_http(username, password):
    """
    Login OAuth sans navigateur (~0,5 s, contre ~6 s avec Firefox).

    Refait ce que fait le site : le formulaire se poste sur sa propre URL,
    le serveur redirige vers mobile.html?code=..., puis le JavaScript de
    cette page échange le code via l'action FeUser/feSession.

    Returns:
        Le token d'accès, ou None si une étape échoue (identifiants refusés,
        site modifié) : l'appelant retombe alors sur Selenium.
    """
    session = requests.Session()
    try:
        session.get(OAUTH_URL, timeout=30)
        login = session.post(
            OAUTH_URL,
            data={
                "username": username,
                "password": password,
                "scope": OAUTH_SCOPE,
                "response_type": "code",
                "redirect_uri": OAUTH_REDIRECT_URI,
                "client_id": "web",
            },
            allow_redirects=False,
            timeout=30,
        )
        location = urlparse(login.headers.get("Location", ""))
        code = parse_qs(location.query).get("code", [None])[0]
        if not code:
            return None
        exchange = session.get(
            AJAX_DISPATCHER_URL,
            params={
                "request[format]": "json",
                "request[controller]": "FeUser",
                "request[action]": "feSession",
                "request[arguments][code]": code,
            },
            timeout=30,
        )
        data = exchange.json()
    except (requests.RequestException, ValueError):
        return None

    if isinstance(data, dict) and data.get("status") and data.get("accessToken"):
        return data["accessToken"]
    return None


def get_oauth_token_with_selenium(username, password, headless=True):
    """
    Utilise Selenium pour se connecter à Naviki et récupérer le token
    depuis localStorage

    Args:
        username: Login Naviki
        password: Mot de passe
        headless: Si True, navigateur invisible (plus rapide)

    Returns:
        Token OAuth d'accès
    """
    # Import local : Selenium coûte ~140 ms à charger et ne sert plus qu'en
    # secours du login HTTP
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    print("🤖 Lancement de l'authentification automatique avec Selenium...")
    print(f"   Username: {username}")

    if headless:
        print("   Mode: Headless (invisible)")
    else:
        print("   Mode: Visible (vous verrez le navigateur)")

    # Configuration de Firefox
    options = Options()
    if headless:
        options.add_argument("--headless")

    # Réduire les logs
    options.set_preference("devtools.console.stdout.content", False)

    driver = None
    token = None

    try:
        print("\n🌐 Ouverture du navigateur Firefox...")
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(30)

        # Étape 1: Aller sur la page OAuth2
        print("\n📋 Étape 1: Chargement de la page de connexion OAuth2...")
        driver.get(OAUTH_URL)
        print("   ✓ Page chargée")

        # Étape 2: Remplir le formulaire de connexion
        print("\n🔑 Étape 2: Saisie des identifiants...")

        try:
            # Attendre que le formulaire soit chargé
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = driver.find_element(By.NAME, "password")

            # Remplir les champs
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)

            print("   ✓ Identifiants saisis")

            # Chercher et cliquer sur le bouton de soumission
            # Le bouton peut avoir différents sélecteurs possibles
            submit_button = None
            try:
                submit_button = driver.find_element(
                    By.CSS_SELECTOR, "button[type='submit']"
                )
            except Exception:
                try:
                    submit_button = driver.find_element(
                        By.CSS_SELECTOR, "input[type='submit']"
                    )
                except Exception:
                    # Soumettre le formulaire directement
                    password_field.submit()

            if submit_button:
                print("\n🚀 Étape 3: Soumission du formulaire...")
                submit_button.click()

        except TimeoutException:
            print("   ✗ Timeout: formulaire de connexion non trouvé")
            print("   Peut-être déjà connecté ou page différente?")

        # Étape 3: Attendre la redirection vers mobile.html
        # et le token dans localStorage
        print("\n⏳ Étape 4: Attente du token dans localStorage...")

        # Le token arrive ~0,4 s après la soumission : un pas d'1 s en
        # faisait perdre ~0,6 à chaque login
        poll_interval = 0.1
        max_attempts = int(20 / poll_interval)  # 20 secondes max
        token = None

        for attempt in range(max_attempts):
            time.sleep(poll_interval)

            # Essayer de récupérer le token depuis localStorage
            try:
                token = driver.execute_script("return localStorage.getItem('_n_a_at');")

                if token:
                    # Aucun caractère du token : la sortie finit souvent dans
                    # des logs (cron, Docker)
                    print("   ✓ Token récupéré")
                    break
            except Exception:
                pass

            # Vérifier si on a une erreur de connexion
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if (
                    "error" in page_text
                    or "invalid" in page_text
                    or "incorrect" in page_text
                ):
                    print(
                        "   ✗ Erreur détectée dans la page - "
                        "identifiants incorrects?"
                    )
                    break
            except Exception:
                pass

            if attempt % 50 == 0 and attempt > 0:
                print(f"   ... {attempt * poll_interval:.0f} s / 20 s")

        if not token:
            print("\n❌ Timeout: le token n'est pas apparu dans " "localStorage")
            print("Possibles causes:")
            print("   - Identifiants incorrects")
            print("   - Structure de la page Naviki a changé")
            print("   - Problème réseau")

            # Sauvegarder une capture d'écran pour debug
            screenshot_path = "/tmp/naviki_debug.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Capture d'écran sauvegardée: {screenshot_path}")
            print(f"   URL actuelle: {driver.current_url}")

            return None

        print("\n✅ Authentification réussie!")
        return token

    except WebDriverException as e:
        print(f"\n❌ Erreur Selenium: {e}")
        print("\nAssurez-vous que geckodriver est installé:")
        print("   Ubuntu/Debian: sudo apt install firefox-geckodriver")
        print("   Arch: sudo pacman -S geckodriver")
        print("   Ou: https://github.com/mozilla/geckodriver/releases")
        return None

    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback

        traceback.print_exc()
        return None

    finally:
        if driver:
            print("\n🔒 Fermeture du navigateur...")
            if token:
                # Firefox met ~1 s à se fermer : la pagination avance pendant ce temps
                global _browser_closer
                _browser_closer = threading.Thread(target=driver.quit)
                _browser_closer.start()
            else:
                driver.quit()


# Fermeture de Firefox lancée après un login réussi, attendue en fin de programme
_browser_closer = None


def wait_browser_closed():
    """Attend la fin de la fermeture de Firefox, si elle est en cours."""
    if _browser_closer is not None:
        _browser_closer.join()


# Variables lues dans l'environnement, prioritaires sur le .env : elles évitent
# de passer le mot de passe en argument, visible dans ps et l'historique
CREDENTIAL_VARS = ("NAVIKI_USERNAME", "NAVIKI_PASSWORD", "NAVIKI_TOKEN")


def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description=(
            "Télécharge les traces GPX depuis Naviki avec "
            "authentification automatique"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s --username MonLogin --password monmdp
  %(prog)s --token 14dcc0f4-d964-396c-a19e-3cc42e36d372
  %(prog)s --username MonLogin --password monmdp --output ~/mes_traces
  %(prog)s --username MonLogin --password monmdp --headless
  %(prog)s  # Utilise les identifiants sauvegardés dans .env

Note: Les identifiants peuvent être sauvegardés dans le fichier .env
      après une première authentification réussie.
        """,
    )

    # Valeurs par défaut : .env, puis variables d'environnement
    env_vars = load_env_file()
    env_vars.update(
        {name: os.environ[name] for name in CREDENTIAL_VARS if os.environ.get(name)}
    )

    auth_group = parser.add_mutually_exclusive_group(required=False)
    auth_group.add_argument(
        "--username",
        "--login",
        dest="username",
        help="Login/Username Naviki (pas un email)",
    )
    auth_group.add_argument(
        "--token",
        help="Token OAuth (si vous l'avez déjà)",
    )

    parser.add_argument(
        "--password",
        default=env_vars.get("NAVIKI_PASSWORD"),
        help="Mot de passe Naviki (requis si --username est utilisé)",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="./traces",
        help="Dossier de destination des fichiers GPX (défaut: ./traces)",
    )

    parser.add_argument(
        "--types",
        default="routedAll,recordedMy,recordedOthers",
        help="Types de routes à exporter (défaut: tous)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Mode headless (navigateur invisible, plus rapide)",
    )

    parser.add_argument(
        "--visible",
        action="store_true",
        help=("Mode visible (voir le navigateur pendant " "l'authentification)"),
    )

    parser.add_argument(
        "--save-credentials",
        action="store_true",
        help="Sauvegarder les identifiants dans .env pour les prochaines fois",
    )

    args = parser.parse_args()

    # Valeurs par défaut appliquées après coup, pour savoir ce qui vient de la
    # ligne de commande : un NAVIKI_TOKEN enregistré ne doit pas remplacer en
    # silence un --username donné explicitement (et inversement)
    auth_from_cli = args.username is not None or args.token is not None
    if not auth_from_cli:
        args.username = env_vars.get("NAVIKI_USERNAME")
        args.token = env_vars.get("NAVIKI_TOKEN")

    # Vérifier qu'on a soit un token, soit username + password
    if not args.token and not args.username:
        parser.error(
            "Vous devez fournir soit --token, soit --username/--password, "
            "ou définir NAVIKI_USERNAME/NAVIKI_PASSWORD (environnement ou .env)"
        )

    # Validation: si username est fourni, password est requis
    if args.username and not args.password:
        parser.error("--password est requis quand --username est utilisé")

    # Par défaut headless sauf si --visible est spécifié
    if not args.visible and not args.headless:
        args.headless = True

    # Afficher si les identifiants proviennent de l'environnement ou de .env
    if not auth_from_cli and (args.username or args.token):
        print("🔑 Utilisation des identifiants de l'environnement ou de .env")

    return args


# Multiple patterns to handle different date formats
patterns = [
    # Format: 16/10/2025, 07:20 (slashes, 4-digit year with time)
    # MOST COMMON
    (
        r"(?P<day>\d\d)/(?P<month>\d\d)/(?P<year>\d{4}), "
        r"(?P<hour>\d\d):(?P<minute>\d\d)"
    ),
    # Format: 16.10.25, 07:20 (points, 2-digit year with time)
    (
        r"(?P<day>\d\d)\.(?P<month>\d\d)\.(?P<year>\d\d), "
        r"(?P<hour>\d\d):(?P<minute>\d\d)"
    ),
    # Format: 16-10-2025, 07:20 (dashes, 4-digit year with time)
    (
        r"(?P<day>\d\d)-(?P<month>\d\d)-(?P<year>\d{4}), "
        r"(?P<hour>\d\d):(?P<minute>\d\d)"
    ),
    # Format: 20250422 or Text-20250422 (compact date without time)
    # negative lookahead to avoid partial matches
    r"(?P<year>\d{4})(?P<month>\d\d)(?P<day>\d\d)(?![\d])",
]


def is_real_date(year, month, day):
    """Vrai si la date existe au calendrier, sur une année plausible pour Naviki."""
    try:
        return 2000 <= datetime(int(year), int(month), int(day)).year <= 2099
    except ValueError:
        return False


def date_from_title(title):
    """
    Date d'un titre Naviki : dict year, month, day (+ hour, minute si présents),
    ou None si aucun motif ne donne une vraie date.

    Un bloc de 8 chiffres se lit AAAAMMJJ, ou JJMMAAAA quand AAAAMMJJ n'est pas
    une date : « Gouter30012024 » est le 30/01/2024, pas le 24/20/3001.
    """
    for pattern in patterns:
        m = re.search(pattern, title)
        if m is None:
            continue
        parts = m.groupdict()
        if len(parts["year"]) == 2:
            parts["year"] = "20" + parts["year"]
        if is_real_date(parts["year"], parts["month"], parts["day"]):
            return parts
        digits = m.group(0)
        if len(digits) == 8 and is_real_date(digits[4:], digits[2:4], digits[:2]):
            return {"year": digits[4:], "month": digits[2:4], "day": digits[:2]}
    return None


def legacy_date_from_title(title):
    """
    Lecture des dates d'avant 1fbecdf : premier motif trouvé, même si la date
    n'existe pas (« Gouter30012024 » donnait 3001-20-24). Ne sert qu'à
    retrouver les fichiers enregistrés sous ces noms.
    """
    for pattern in patterns:
        m = re.search(pattern, title)
        if m:
            parts = m.groupdict()
            if len(parts["year"]) == 2:
                parts["year"] = "20" + parts["year"]
            return parts
    return None


def rename_legacy_file(way, output_dir, save_path):
    """
    Renomme vers save_path le fichier d'un trajet enregistré sous son ancien
    nom erroné, pour éviter de le retélécharger en double.

    Returns:
        True si un fichier a été renommé.
    """
    legacy_parts = legacy_date_from_title(way["title"])
    # Un ancien nom ne diffère du bon que s'il porte une date impossible :
    # il ne peut donc pas être le fichier correct d'un autre trajet
    if legacy_parts is None or is_real_date(
        legacy_parts["year"], legacy_parts["month"], legacy_parts["day"]
    ):
        return False
    legacy_path = output_dir / gpx_filename(way, legacy_parts)
    if legacy_path == save_path or not legacy_path.exists():
        return False
    os.replace(legacy_path, save_path)
    print(f"🔁 Renommé: {legacy_path.name} → {save_path.name}")
    return True


def gpx_filename(way, parts):
    """
    Nom du fichier GPX d'un trajet. C'est la clé de déduplication de
    l'archive : un changement ici fait retélécharger les trajets concernés.

    Args:
        way: trajet renvoyé par l'API (title, crdate)
        parts: date lue dans le titre (cf. date_from_title), ou None pour
            se rabattre sur crdate

    Returns:
        Le nom du fichier, ou None si aucune date n'est disponible.
    """
    if parts is None:
        if "crdate" not in way:
            return None
        # crdate est un timestamp UTC
        dt = datetime.fromtimestamp(way["crdate"], tz=timezone.utc)
        # Titre nettoyé en suffixe s'il apporte quelque chose
        title = way["title"]
        safe_title = re.sub(r"[^\w\-]", "_", title)[:30]
        if len(safe_title) > 3 and safe_title != title:
            return f"{dt.strftime('%Y-%m-%d_%H-%M')}_UTC_{safe_title}.gpx"
        return dt.strftime("%Y-%m-%d_%H-%M") + "_UTC_Naviki.gpx"

    year, month, day = parts["year"], parts["month"], parts["day"]
    hour, minute = parts.get("hour"), parts.get("minute")
    if hour and minute:
        return f"{year}-{month}-{day}_{hour}-{minute}_Naviki.gpx"
    # Pas d'heure dans le titre (ex. format compact 20241124) : l'heure vient
    # de crdate
    if "crdate" in way:
        dt = datetime.fromtimestamp(way["crdate"], tz=timezone.utc)
        return f"{year}-{month}-{day}_{dt.strftime('%H-%M')}_UTC_Naviki.gpx"
    return f"{year}-{month}-{day}_Naviki.gpx"


# (connexion, lecture) en secondes : sans timeout, requests attend
# indéfiniment une réponse qui ne vient pas. Le GPX le plus lent mesuré
# prend 0,6 s.
HTTP_TIMEOUT = (10, 60)

# Téléchargements simultanés : ~4x plus rapide sur un export complet,
# sans charger davantage le serveur Naviki
DOWNLOAD_WORKERS = 4

# L'API renvoie 20 trajets par défaut ; 500 ramène un compte typique en
# 2 requêtes au lieu de 23. La boucle s'arrête sur la première page vide,
# donc un plafond plus bas côté serveur reste géré.
WAYS_PAGE_SIZE = 500


def log(message):
    """print() en une seule écriture, pour ne pas mêler les lignes des threads"""
    sys.stdout.write(f"{message}\n")


def download_gpx(session, oauth_token, uuid, save_path):
    """Télécharge un GPX dans save_path ; renvoie True si le fichier est écrit."""
    form_data = {
        "wayUuid": uuid,
        "oauth_token": oauth_token,
        "format": "gpx",
    }
    dl_headers = {"Authorization": None}  # token is passed in form data

    try:
        dl = session.post(
            "https://www.naviki.org/naviki/api/v6/Util/" "wayToFileWithUser/",
            data=form_data,
            headers=dl_headers,
            timeout=HTTP_TIMEOUT,
        )

        if not dl.text.startswith("<?xml"):
            log(f"❌ Échec du téléchargement GPX (réponse invalide): {save_path.name}")
            return False

        # Écriture puis renommage atomique : un arrêt en cours d'écriture ne
        # laisse qu'un .part, jamais un GPX tronqué que l'incrémental sauterait
        part_path = save_path.with_name(save_path.name + ".part")
        with open(part_path, "wb") as f:
            f.write(dl.text.encode())
        os.replace(part_path, save_path)
        log(f"✅ Sauvegardé: {save_path}")
        return True

    except Exception as e:
        log(f"❌ Erreur lors du téléchargement de {save_path.name}: {e}")
        return False


# Cache du dernier token OAuth, pour ne relancer Firefox qu'à son expiration
TOKEN_CACHE_NAME = ".naviki-token.json"


def load_cached_token(username):
    """Renvoie le token en cache pour ce compte, ou None."""
    try:
        cached = json.loads((config_dir() / TOKEN_CACHE_NAME).read_text("utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(cached, dict) or cached.get("username") != username:
        return None
    return cached.get("token") or None


def save_cached_token(username, token):
    """Écrit le token en cache, lisible par l'utilisateur seul."""
    path = config_dir() / TOKEN_CACHE_NAME
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"username": username, "token": token}, f)
        # un fichier préexistant garde ses droits avec os.open
        os.chmod(path, 0o600)
    except OSError as e:
        print(f"⚠️  Token non mis en cache: {e}")


def login_or_exit(args):
    """Login HTTP, puis Selenium en secours ; quitte si aucun token n'est obtenu."""
    oauth_token = None
    # --visible : l'utilisateur veut voir le navigateur, on passe par Firefox
    if not args.visible:
        print("🔑 Connexion directe à Naviki...")
        oauth_token = get_oauth_token_http(args.username, args.password)
        if oauth_token:
            print("✅ Authentification réussie, sans navigateur")
        else:
            print("⚠️  Connexion directe impossible, nouvel essai avec Firefox")

    if not oauth_token:
        oauth_token = get_oauth_token_with_selenium(
            args.username, args.password, headless=args.headless
        )

    if not oauth_token:
        print("\n❌ Impossible de récupérer le token")
        print("\n📋 Solution alternative:")
        print("   1. Connectez-vous manuellement sur naviki.org")
        print("   2. Ouvrez la console (F12)")
        print("   3. Tapez: localStorage.getItem('_n_a_at')")
        print("   4. Copiez le token et relancez avec:")
        print(f"      python {sys.argv[0]} --token VOTRE-TOKEN --output {args.output}")
        sys.exit(1)

    # sys.exit peut être simulé (tests) : ne jamais mettre None en cache
    if oauth_token:
        save_cached_token(args.username, oauth_token)
    return oauth_token


def main():
    # Parse arguments
    args = parse_arguments()

    # Obtenir le token OAuth
    credentials_used_from_args = False
    token_from_cache = False
    if args.token:
        oauth_token = args.token
        if oauth_token.startswith("Bearer "):
            oauth_token = oauth_token[7:]
        print("✅ Utilisation du token fourni")
    else:
        # Vérifier si les identifiants proviennent des arguments de ligne de commande
        credentials_used_from_args = any(
            arg in sys.argv for arg in ["--username", "--login", "--password"]
        )

        oauth_token = load_cached_token(args.username)
        token_from_cache = oauth_token is not None
        if token_from_cache:
            print("✅ Token en cache réutilisé, connexion Firefox évitée")
        else:
            oauth_token = login_or_exit(args)

        # Proposer de sauvegarder les identifiants après authentification réussie
        # Ne demander que si on n'est pas en mode test (stdin est disponible)
        if credentials_used_from_args and not args.save_credentials:
            env_path = config_dir() / ".env"
            # Ne proposer que si le fichier n'existe pas déjà avec ces identifiants
            env_vars = load_env_file()
            should_ask = (
                not env_vars.get("NAVIKI_USERNAME")
                or env_vars.get("NAVIKI_USERNAME") != args.username
            )

            # Vérifier si stdin est disponible (pas en mode test)
            if should_ask and sys.stdin.isatty():
                print(
                    "\n💾 Voulez-vous sauvegarder ces identifiants "
                    "pour les prochaines fois ?"
                )
                print(f"   Ils seront stockés de manière sécurisée " f"dans {env_path}")
                print(
                    "   (Ce fichier est ignoré par Git et ne sera "
                    "jamais envoyé sur GitHub)"
                )
                response = input("   Sauvegarder ? [O/n] : ").strip().lower()

                if response in ["o", "oui", "y", "yes", ""]:
                    save_credentials_to_env(args.username, args.password)
                    print("\n   La prochaine fois, vous pourrez lancer simplement:")
                    print(f"   python {sys.argv[0]}")
                else:
                    print("   Identifiants non sauvegardés.")
        elif args.save_credentials:
            save_credentials_to_env(args.username, args.password)

    # Configuration
    route_types = args.types
    output_dir = pathlib.Path(args.output)

    # Créer le dossier de sortie si nécessaire
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"📁 Destination: {output_dir}")
    print(f"🔍 Types de routes: {route_types}")
    print(f"{'='*50}\n")
    print("Début du téléchargement...\n")

    timestamp = str(int(time.time()))

    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {oauth_token}"})
    s.headers.update({"Accept": "application/json"})

    more_to_download = True
    offset = 0
    success_count = 0
    error_count = 0
    skipped_count = 0
    api_error = False

    # Les téléchargements partent pendant que la pagination continue
    pool = ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS)
    downloads = []
    in_flight = set()
    deferred = []

    try:
        while more_to_download:
            try:
                r = s.get(
                    "https://www.naviki.org/naviki/api/v6/Way/2/"
                    f"findUserWaysByFilter/?filter={route_types}"
                    f"&sort=crdateDesc&offset={offset}&limit={WAYS_PAGE_SIZE}"
                    "&fullDataSet=0"
                    f"&_={timestamp}",
                    timeout=HTTP_TIMEOUT,
                )
            except requests.RequestException as e:
                api_error = True
                print(f"❌ Erreur réseau sur la liste des trajets: {e}")
                break

            if r.status_code == 401 and token_from_cache:
                print("🔄 Token en cache expiré, reconnexion...")
                token_from_cache = False
                oauth_token = login_or_exit(args)
                s.headers.update({"Authorization": f"Bearer {oauth_token}"})
                continue

            if r.status_code != 200:
                api_error = True
                print(f"❌ Erreur API: {r.status_code}")
                if r.status_code == 401:
                    print("⚠️  Token invalide ou expiré. " "Veuillez vous reconnecter.")
                break

            j = r.json()
            more_to_download = len(j["ways"]) > 0
            offset += len(j["ways"])

            for way in j["ways"]:
                uuid = way["uuid"]
                title = way["title"]
                print(f"\nTraitement: {title}")
                print(f"UUID: {uuid}")

                parts = date_from_title(title)

                if parts is None:
                    # Check if title looks like a place name
                    # (contains letters/spaces)
                    if any(c.isalpha() for c in title) and not any(
                        c.isdigit() for c in title[:4]
                    ):
                        print(
                            f"ℹ️  Titre personnalisé détecté "
                            f"('{title[:30]}...'), utilisation de crdate"
                        )
                    else:
                        print(
                            f"⚠️  Format de date non standard dans "
                            f"'{title}', utilisation de crdate"
                        )

                new_title = gpx_filename(way, parts)
                if new_title is None:
                    print("❌ Impossible d'extraire la date, " "itinéraire ignoré")
                    error_count += 1
                    continue

                # Check if file already exists
                save_path = output_dir.joinpath(new_title)
                if not save_path.exists():
                    rename_legacy_file(way, output_dir, save_path)
                if save_path.exists():
                    print(f"⏭️  Déjà présent, ignoré: {new_title}")
                    skipped_count += 1
                    continue

                # Un fichier du même nom en cours de téléchargement serait écrasé :
                # on le traite après le pool, comme le ferait le mode séquentiel
                if save_path in in_flight:
                    deferred.append((uuid, save_path))
                    continue

                in_flight.add(save_path)
                downloads.append(
                    pool.submit(download_gpx, s, oauth_token, uuid, save_path)
                )

        pool.shutdown(wait=True)
    except KeyboardInterrupt:
        # Sans annulation, les threads du pool videraient toute la file
        # avant que le processus ne s'arrête (~50 s sur un export complet)
        pool.shutdown(wait=False, cancel_futures=True)
        print("\n⛔ Interrompu : téléchargements en attente annulés")
        sys.exit(130)
    results = [f.result() for f in downloads]
    for uuid, save_path in deferred:
        if save_path.exists():
            print(f"⏭️  Déjà présent, ignoré: {save_path.name}")
            skipped_count += 1
        else:
            results.append(download_gpx(s, oauth_token, uuid, save_path))
    success_count += results.count(True)
    error_count += results.count(False)

    print(f"\n{'='*50}")
    print("Téléchargement terminé!")
    print(f"✅ Téléchargés: {success_count}")
    print(f"⏭️  Ignorés (déjà présents): {skipped_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📊 Total traité: " f"{success_count + skipped_count + error_count}")
    print(f"📁 Fichiers sauvegardés dans: {output_dir}")
    wait_browser_closed()

    # Code non nul pour qu'un cron ou un script appelant voie l'échec
    if api_error or error_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
