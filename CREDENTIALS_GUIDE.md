# Guide de Sauvegarde Sécurisée des Identifiants

## 🔐 Présentation

Le script `naviki-gpx-exporter.py` supporte désormais la sauvegarde sécurisée de vos identifiants Naviki dans un fichier `.env` local. Ce fichier est **automatiquement ignoré par Git** et ne sera jamais envoyé sur GitHub.

## 🎯 Avantages

- ✅ **Pratique** : Plus besoin de retaper vos identifiants à chaque fois
- 🔒 **Sécurisé** : Fichier `.env` avec permissions 600 (lecture/écriture uniquement pour vous)
- 🚫 **Protégé** : Automatiquement ignoré par Git grâce au `.gitignore`
- 💾 **Local** : Les identifiants restent uniquement sur votre machine

## 🚀 Utilisation

### Première Utilisation

Lors de votre première utilisation avec vos identifiants :

```bash
python naviki-gpx-exporter.py --username MonLogin --password MonMotDePasse
```

Le script vous proposera automatiquement de sauvegarder vos identifiants :

```
💾 Voulez-vous sauvegarder ces identifiants pour les prochaines fois ?
   Ils seront stockés de manière sécurisée dans /path/to/.env
   (Ce fichier est ignoré par Git et ne sera jamais envoyé sur GitHub)
   Sauvegarder ? [O/n] :
```

Répondez **O** (ou appuyez sur Entrée) pour sauvegarder.

### Utilisations Suivantes

Une fois les identifiants sauvegardés, lancez simplement :

```bash
python naviki-gpx-exporter.py
```

Le script chargera automatiquement vos identifiants depuis `.env` ! 🎉

### Sauvegarder Sans Demander

Pour sauvegarder directement les identifiants sans confirmation interactive :

```bash
python naviki-gpx-exporter.py --username MonLogin --password MonMotDePasse --save-credentials
```

## 📁 Format du Fichier `.env`

Le fichier `.env` est créé automatiquement et contient :

```bash
# Configuration Naviki GPX Exporter
# Ce fichier est automatiquement généré et ignoré par Git

# Identifiants Naviki
NAVIKI_USERNAME=votre_username
NAVIKI_PASSWORD=votre_password
```

## 🔒 Sécurité

### Permissions du Fichier

Le fichier `.env` est créé avec les permissions `600` :
- ✅ Lecture/écriture pour vous uniquement
- ❌ Aucun accès pour les autres utilisateurs du système

### Protection Git

Le fichier `.env` est listé dans `.gitignore` :
- ❌ Ne sera **jamais** commité dans Git
- ❌ Ne sera **jamais** envoyé sur GitHub
- ✅ Reste **uniquement** sur votre machine locale

Vous pouvez vérifier avec :

```bash
git status --ignored
```

Le fichier `.env` devrait apparaître dans les fichiers ignorés.

## 🛠️ Gestion des Identifiants

### Mettre à Jour les Identifiants

Pour changer vos identifiants sauvegardés :

```bash
python naviki-gpx-exporter.py --username NouveauLogin --password NouveauMdp --save-credentials
```

### Supprimer les Identifiants Sauvegardés

Pour supprimer le fichier `.env` et les identifiants :

```bash
rm .env
```

### Vérifier les Identifiants Sauvegardés

Pour voir quels identifiants sont sauvegardés (sans afficher le mot de passe) :

```bash
grep NAVIKI_USERNAME .env
```

## ⚙️ Options de Ligne de Commande

| Option | Description |
|--------|-------------|
| `--username` / `--login` | Spécifier le nom d'utilisateur (prioritaire sur `.env`) |
| `--password` | Spécifier le mot de passe (prioritaire sur `.env`) |
| `--token` | Utiliser un token OAuth (prioritaire sur tout) |
| `--save-credentials` | Sauvegarder automatiquement sans demander |

## 💡 Cas d'Usage

### Utilisation Quotidienne

```bash
# Première fois
python naviki-gpx-exporter.py --username alice --password secret123
# [Accepter la sauvegarde]

# Toutes les fois suivantes
python naviki-gpx-exporter.py
```

### Automatisation avec Cron

Avec les identifiants sauvegardés, vous pouvez facilement automatiser les exports :

```bash
# Ajouter dans crontab -e
0 2 * * * cd /home/user/naviki-gpx-exporter && python naviki-gpx-exporter.py
```

### Utilisation avec Plusieurs Comptes

Pour gérer plusieurs comptes Naviki, utilisez différents répertoires :

```bash
# Compte 1
cd ~/naviki-account1
python naviki-gpx-exporter.py --username compte1 --password mdp1 --save-credentials

# Compte 2
cd ~/naviki-account2
python naviki-gpx-exporter.py --username compte2 --password mdp2 --save-credentials
```

### Priorité des Identifiants

L'ordre de priorité pour les identifiants est :

1. **Token OAuth** (`--token`) - priorité absolue
2. **Arguments de ligne de commande** (`--username` / `--password`)
3. **Fichier `.env`** - utilisé si aucun argument fourni

## ⚠️ Avertissements

- 🔒 Ne **jamais** commiter le fichier `.env` dans Git
- 🔒 Ne **jamais** partager votre fichier `.env`
- 🔒 Ne **jamais** copier vos identifiants dans les issues GitHub
- ✅ Le fichier `.env` est **automatiquement** dans `.gitignore`

## 🧪 Test de la Fonctionnalité

Pour tester la sauvegarde et le chargement des identifiants :

```bash
pytest tests/test_token_cache.py tests/test_argument_parsing.py
```

Ces tests vérifient :
- ✅ Sauvegarde des identifiants, en préservant les autres variables
- ✅ Chargement des identifiants (`.env`, guillemets, variables d'environnement)
- ✅ Permissions du fichier : créé directement en 600

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez que `.env` est bien dans `.gitignore` : `grep "^\.env$" .gitignore`
2. Vérifiez les permissions : `ls -la .env` (devrait afficher `-rw-------`)
3. Lancez les tests : `pytest tests/test_token_cache.py`

---

**🎉 Profitez de votre export GPX simplifié et sécurisé !**
