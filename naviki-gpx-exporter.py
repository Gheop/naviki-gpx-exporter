#!/usr/bin/env python3
"""
Script pour télécharger automatiquement les traces GPX depuis Naviki
Utilise Selenium pour une authentification 100% automatique

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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
import time
import re
import pathlib
import argparse
import sys
import os
from datetime import datetime, timezone


def load_env_file():
    """
    Charge les variables d'environnement depuis le fichier .env

    Returns:
        dict: Dictionnaire contenant les variables d'environnement
    """
    env_vars = {}
    env_path = pathlib.Path(__file__).parent / ".env"

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Ignorer les lignes vides et les commentaires
                if line and not line.startswith("#"):
                    # Gérer les lignes de type KEY=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

    return env_vars


def save_credentials_to_env(username, password):
    """
    Sauvegarde les identifiants dans le fichier .env

    Args:
        username: Nom d'utilisateur Naviki
        password: Mot de passe Naviki
    """
    env_path = pathlib.Path(__file__).parent / ".env"

    # Lire le contenu existant pour préserver les autres variables
    existing_content = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_content[key.strip()] = value.strip()

    # Mettre à jour les identifiants
    existing_content["NAVIKI_USERNAME"] = username
    existing_content["NAVIKI_PASSWORD"] = password

    # Écrire le fichier .env
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# Configuration Naviki GPX Exporter\n")
        f.write("# Ce fichier est automatiquement généré et ignoré par Git\n\n")
        f.write("# Identifiants Naviki\n")
        f.write(f"NAVIKI_USERNAME={existing_content.get('NAVIKI_USERNAME', '')}\n")
        f.write(f"NAVIKI_PASSWORD={existing_content.get('NAVIKI_PASSWORD', '')}\n")

        # Ajouter les autres variables si elles existent
        for key, value in existing_content.items():
            if key not in ["NAVIKI_USERNAME", "NAVIKI_PASSWORD"]:
                f.write(f"\n{key}={value}\n")

    # Définir les permissions en lecture/écriture uniquement pour l'utilisateur
    os.chmod(env_path, 0o600)
    print(f"✅ Identifiants sauvegardés dans {env_path}")
    print("🔒 Permissions définies à 600 " "(lecture/écriture uniquement pour vous)")


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

    try:
        print("\n🌐 Ouverture du navigateur Firefox...")
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(30)

        # Étape 1: Aller sur la page OAuth2
        print("\n📋 Étape 1: Chargement de la page de connexion OAuth2...")
        oauth_url = (
            "https://www.naviki.org/oauth2/auth?lang=fr"
            "&redirect_uri=https://www.naviki.org/fr/naviki/"
            "single-pages/loading//mobile.html&client_id=web"
            "&scope=way,profile,contest&response_type=code"
        )

        driver.get(oauth_url)
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

        max_attempts = 20  # 20 secondes max
        token = None

        for attempt in range(max_attempts):
            time.sleep(1)

            # Essayer de récupérer le token depuis localStorage
            try:
                token = driver.execute_script("return localStorage.getItem('_n_a_at');")

                if token:
                    print(f"   ✓ Token récupéré: {token[:20]}...")
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

            if attempt % 5 == 0 and attempt > 0:
                print(f"   ... tentative {attempt}/{max_attempts}")

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
            driver.quit()


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

    # Charger les variables d'environnement depuis .env
    env_vars = load_env_file()

    auth_group = parser.add_mutually_exclusive_group(required=False)
    auth_group.add_argument(
        "--username",
        "--login",
        dest="username",
        default=env_vars.get("NAVIKI_USERNAME"),
        help="Login/Username Naviki (pas un email)",
    )
    auth_group.add_argument(
        "--token",
        default=env_vars.get("NAVIKI_TOKEN"),
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

    # Vérifier qu'on a soit un token, soit username + password
    if not args.token and not args.username:
        parser.error(
            "Vous devez fournir soit --token, soit --username/--password, "
            "ou avoir des identifiants sauvegardés dans .env"
        )

    # Validation: si username est fourni, password est requis
    if args.username and not args.password:
        parser.error("--password est requis quand --username est utilisé")

    # Par défaut headless sauf si --visible est spécifié
    if not args.visible and not args.headless:
        args.headless = True

    # Afficher si les identifiants proviennent de .env
    if env_vars.get("NAVIKI_USERNAME") and not any(
        arg in sys.argv for arg in ["--username", "--login", "--token"]
    ):
        print("🔑 Utilisation des identifiants depuis .env")

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


def main():
    # Parse arguments
    args = parse_arguments()

    # Obtenir le token OAuth
    credentials_used_from_args = False
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
            print(
                f"      python {sys.argv[0]} --token VOTRE-TOKEN "
                f"--output {args.output}"
            )
            sys.exit(1)

        # Proposer de sauvegarder les identifiants après authentification réussie
        # Ne demander que si on n'est pas en mode test (stdin est disponible)
        if credentials_used_from_args and not args.save_credentials:
            env_path = pathlib.Path(__file__).parent / ".env"
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

    while more_to_download:
        r = s.get(
            "https://www.naviki.org/naviki/api/v6/Way/2/"
            f"findUserWaysByFilter/?filter={route_types}"
            f"&sort=crdateDesc&offset={offset}&fullDataSet=0"
            f"&_={timestamp}"
        )

        if r.status_code != 200:
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

            # Try each pattern
            m = None
            for pattern in patterns:
                m = re.search(pattern, title)
                if m:
                    break

            if m is None:
                # Fallback: use crdate timestamp with timezone awareness
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

                if "crdate" in way:
                    # Use timezone-aware datetime
                    # (crdate is UTC timestamp)
                    dt = datetime.fromtimestamp(way["crdate"], tz=timezone.utc)
                    # Use sanitized title as prefix if it's short
                    # and has no special chars
                    safe_title = re.sub(r"[^\w\-]", "_", title)[:30]
                    if len(safe_title) > 3 and safe_title != title:
                        new_title = (
                            f"{dt.strftime('%Y-%m-%d_%H-%M')}_UTC_" f"{safe_title}.gpx"
                        )
                    else:
                        new_title = dt.strftime("%Y-%m-%d_%H-%M") + "_UTC_Naviki.gpx"
                else:
                    print("❌ Impossible d'extraire la date, " "itinéraire ignoré")
                    error_count += 1
                    continue
            else:
                # Extract date components
                year = m.group("year")
                # Handle 2-digit or 4-digit year
                if len(year) == 2:
                    year = "20" + year

                month = m.group("month")
                day = m.group("day")

                # Check if pattern includes time
                # (check if groups exist in the match)
                try:
                    hour = m.group("hour")
                    minute = m.group("minute")
                    if hour and minute:
                        new_title = (
                            f"{year}-{month}-{day}_{hour}-{minute}" "_Naviki.gpx"
                        )
                    else:
                        raise IndexError  # Fall through to crdate
                except (IndexError, AttributeError):
                    # No time in the pattern
                    # (e.g., compact format 20241124)
                    # Use crdate for time
                    if "crdate" in way:
                        dt = datetime.fromtimestamp(way["crdate"], tz=timezone.utc)
                        time_str = dt.strftime("%H-%M")
                        new_title = f"{year}-{month}-{day}_{time_str}_UTC_" "Naviki.gpx"
                    else:
                        new_title = f"{year}-{month}-{day}_Naviki.gpx"

            # Check if file already exists
            save_path = output_dir.joinpath(new_title)
            if save_path.exists():
                print(f"⏭️  Déjà présent, ignoré: {new_title}")
                skipped_count += 1
                continue

            # Download GPX
            form_data = {
                "wayUuid": uuid,
                "oauth_token": oauth_token,
                "format": "gpx",
            }
            dl_headers = {"Authorization": None}  # token is passed in form data

            try:
                dl = s.post(
                    "https://www.naviki.org/naviki/api/v6/Util/" "wayToFileWithUser/",
                    data=form_data,
                    headers=dl_headers,
                )

                if not dl.text.startswith("<?xml"):
                    print("❌ Échec du téléchargement GPX " "(réponse invalide)")
                    error_count += 1
                    continue

                with open(save_path, "wb") as f:
                    f.write(dl.text.encode())
                print(f"✅ Sauvegardé: {save_path}")
                success_count += 1

            except Exception as e:
                print(f"❌ Erreur lors du téléchargement: {e}")
                error_count += 1
                continue

    print(f"\n{'='*50}")
    print("Téléchargement terminé!")
    print(f"✅ Téléchargés: {success_count}")
    print(f"⏭️  Ignorés (déjà présents): {skipped_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📊 Total traité: " f"{success_count + skipped_count + error_count}")
    print(f"📁 Fichiers sauvegardés dans: {output_dir}")


if __name__ == "__main__":
    main()
