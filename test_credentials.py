#!/usr/bin/env python3
"""
Script de test pour vérifier la fonctionnalité de sauvegarde
et chargement des identifiants
"""

import sys
import pathlib
import os


def load_env_file():
    """Charge les variables d'environnement depuis le fichier .env"""
    env_vars = {}
    env_path = pathlib.Path(__file__).parent / ".env"

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

    return env_vars


def save_credentials_to_env(username, password):
    """Sauvegarde les identifiants dans le fichier .env"""
    env_path = pathlib.Path(__file__).parent / ".env"

    existing_content = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_content[key.strip()] = value.strip()

    existing_content["NAVIKI_USERNAME"] = username
    existing_content["NAVIKI_PASSWORD"] = password

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# Configuration Naviki GPX Exporter\n")
        f.write("# Ce fichier est automatiquement généré et ignoré par Git\n\n")
        f.write("# Identifiants Naviki\n")
        f.write(f"NAVIKI_USERNAME={existing_content.get('NAVIKI_USERNAME', '')}\n")
        f.write(f"NAVIKI_PASSWORD={existing_content.get('NAVIKI_PASSWORD', '')}\n")

        for key, value in existing_content.items():
            if key not in ["NAVIKI_USERNAME", "NAVIKI_PASSWORD"]:
                f.write(f"\n{key}={value}\n")

    os.chmod(env_path, 0o600)
    print(f"✅ Identifiants sauvegardés dans {env_path}")
    print("🔒 Permissions définies à 600 " "(lecture/écriture uniquement pour vous)")


def test_credentials():
    """Test la sauvegarde et le chargement des identifiants"""

    print("🧪 Test de sauvegarde et chargement des identifiants\n")

    # Test 1: Charger depuis un fichier .env vide (devrait retourner un dict vide)
    print("1️⃣  Test: Charger .env (avant sauvegarde)")
    env_vars = load_env_file()
    print(f"   Variables chargées: {env_vars}")

    # Test 2: Sauvegarder des identifiants de test
    print("\n2️⃣  Test: Sauvegarder des identifiants de test")
    test_username = "test_user"
    test_password = "test_password_123"

    try:
        save_credentials_to_env(test_username, test_password)
        print("   ✅ Sauvegarde réussie")
    except Exception as e:
        print(f"   ❌ Erreur lors de la sauvegarde: {e}")
        return False

    # Test 3: Recharger pour vérifier
    print("\n3️⃣  Test: Recharger .env pour vérifier")
    env_vars = load_env_file()

    if env_vars.get("NAVIKI_USERNAME") == test_username:
        print(f"   ✅ Username correct: {env_vars.get('NAVIKI_USERNAME')}")
    else:
        print(f"   ❌ Username incorrect: {env_vars.get('NAVIKI_USERNAME')}")
        return False

    if env_vars.get("NAVIKI_PASSWORD") == test_password:
        print(f"   ✅ Password correct: {'*' * len(test_password)}")
    else:
        print("   ❌ Password incorrect")
        return False

    # Test 4: Vérifier les permissions du fichier
    print("\n4️⃣  Test: Vérifier les permissions du fichier .env")
    env_path = pathlib.Path(__file__).parent / ".env"

    if env_path.exists():
        # Obtenir les permissions du fichier
        permissions = oct(os.stat(env_path).st_mode)[-3:]
        print(f"   Permissions: {permissions}")

        if permissions == "600":
            print(
                "   ✅ Permissions correctes (600 - lecture/écriture "
                "uniquement pour l'utilisateur)"
            )
        else:
            print(f"   ⚠️  Permissions: {permissions} (recommandé: 600)")

    # Test 5: Vérifier que .env est bien ignoré par Git
    print("\n5️⃣  Test: Vérifier que .env est dans .gitignore")
    gitignore_path = pathlib.Path(__file__).parent / ".gitignore"

    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            gitignore_content = f.read()
            if ".env" in gitignore_content:
                print("   ✅ .env est bien dans .gitignore")
            else:
                print("   ❌ .env n'est PAS dans .gitignore !")
                return False

    print("\n" + "=" * 60)
    print("✅ Tous les tests sont réussis !")
    print("=" * 60)

    print("\n📋 Instructions pour nettoyer le fichier .env de test:")
    print(f"   rm {env_path}")

    return True


if __name__ == "__main__":
    success = test_credentials()
    sys.exit(0 if success else 1)
