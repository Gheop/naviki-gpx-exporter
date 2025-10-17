# 🚀 Quick Start Docker - Naviki GPX Exporter

Guide de démarrage rapide en 5 minutes pour utiliser l'exporter avec Docker.

## ⚡ Méthode ultra-rapide (1 commande)

```bash
# Linux/macOS
docker run --rm -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username VotreUsername --password 'VotrePassword' --output /output

# Windows (PowerShell)
docker run --rm -v ${PWD}/output:/output `
  ghcr.io/gheop/naviki-gpx-exporter:latest `
  --username VotreUsername --password "VotrePassword" --output /output

# Windows (CMD)
docker run --rm -v %cd%/output:/output ^
  ghcr.io/gheop/naviki-gpx-exporter:latest ^
  --username VotreUsername --password "VotrePassword" --output /output
```

Vos fichiers GPX seront dans le dossier `output/` !

## 📝 Méthode avec script helper (recommandée)

### 1. Télécharger le script

```bash
# Télécharger uniquement le script helper
curl -O https://raw.githubusercontent.com/Gheop/naviki-gpx-exporter/main/docker-run.sh
chmod +x docker-run.sh

# OU cloner le repo complet
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter
chmod +x docker-run.sh
```

### 2. Lancer l'export

```bash
# Avec username/password
./docker-run.sh -u VotreUsername -p 'VotrePassword'

# Avec token OAuth
./docker-run.sh -t votre-token-oauth

# Dossier personnalisé
./docker-run.sh -u VotreUsername -p 'VotrePassword' -o ~/mes-traces
```

## 🎯 Méthode avec Makefile (la plus simple)

### 1. Cloner et configurer

```bash
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter

# Copier et éditer le fichier de config
cp .env.example .env
nano .env  # Mettez vos identifiants
```

### 2. Lancer

```bash
make build  # Builder l'image (une seule fois)
make run    # Lancer l'export
```

C'est tout ! 🎉

## 🔐 Méthode sécurisée (sans mot de passe en clair)

### Utiliser un token OAuth

```bash
# 1. Obtenir un token
./docker-run.sh -u VotreUsername -p 'VotrePassword' -o /tmp
# Le token sera affiché dans les logs

# 2. Réutiliser le token (plus sûr)
./docker-run.sh -t abc123-def456-ghi789 -o ~/backup

# 3. Ou via variable d'environnement
export NAVIKI_TOKEN="abc123-def456-ghi789"
./docker-run.sh -o ~/backup
```

### Avec un fichier .env (pour automatisation)

```bash
# Créer .env (jamais commité dans git)
cat > .env << 'EOF'
NAVIKI_USERNAME=MonUsername
NAVIKI_PASSWORD=MonPassword
EOF

# Protéger le fichier
chmod 600 .env

# Utiliser avec docker-compose
docker-compose run --rm naviki-exporter \
  --username "$NAVIKI_USERNAME" \
  --password "$NAVIKI_PASSWORD" \
  --output /output
```

## 📅 Backup automatique quotidien

### Cron job (Linux/macOS)

```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne (tous les jours à 2h du matin)
0 2 * * * docker run --rm -v /home/user/naviki-backup:/output ghcr.io/gheop/naviki-gpx-exporter:latest --token YOUR_TOKEN --output /output >> /var/log/naviki.log 2>&1
```

### Scheduled Task (Windows)

```powershell
# Créer un script backup.ps1
@"
docker run --rm -v C:\Users\user\naviki-backup:/output `
  ghcr.io/gheop/naviki-gpx-exporter:latest `
  --token YOUR_TOKEN --output /output
"@ | Out-File -FilePath C:\Scripts\naviki-backup.ps1

# Planifier avec Task Scheduler
# Action: powershell.exe -File C:\Scripts\naviki-backup.ps1
# Déclencheur: Quotidien à 2h00
```

## 🐛 Résolution de problèmes rapide

### "Cannot connect to Docker daemon"

```bash
# Vérifier que Docker est lancé
docker --version
docker ps

# Si erreur, démarrer Docker
# Linux: sudo systemctl start docker
# macOS/Windows: Démarrer Docker Desktop
```

### "Permission denied" sur les fichiers exportés

```bash
# Solution 1: Changer le propriétaire après
sudo chown -R $USER:$USER output/

# Solution 2: Lancer avec votre UID
docker run --rm --user $(id -u):$(id -g) \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username VotreUsername --password 'VotrePassword' --output /output
```

### Image pas à jour

```bash
# Télécharger la dernière version
docker pull ghcr.io/gheop/naviki-gpx-exporter:latest

# Ou avec le script
./docker-run.sh --pull -u VotreUsername -p 'VotrePassword'
```

### Voir les logs en cas d'erreur

```bash
# Les logs s'affichent directement dans le terminal
# Pour plus de détails, lancer en mode visible
./docker-run.sh -u VotreUsername -p 'VotrePassword' --visible
```

## 📊 Commandes utiles

```bash
# Voir l'espace disque utilisé par Docker
docker system df

# Nettoyer les images inutilisées
docker system prune -a

# Voir les images disponibles
docker images | grep naviki

# Voir le nombre de fichiers exportés
ls -1 output/*.gpx | wc -l

# Voir l'espace total des fichiers GPX
du -sh output/
```

## 🎓 Prochaines étapes

Une fois que vous maîtrisez le Quick Start :

1. **Automatisation** : Configurez un cron job pour des backups réguliers
2. **Organisation** : Utilisez des dossiers par année/mois
3. **Synchronisation** : Intégrez avec Nextcloud, Syncthing, etc.
4. **Analyse** : Utilisez les GPX avec d'autres outils (GPXSee, QGIS, etc.)

## 💡 Astuces

### Export incrémental quotidien

```bash
# Les fichiers déjà présents sont automatiquement ignorés
# Pas besoin de suppression, juste relancer l'export
./docker-run.sh -u VotreUsername -p 'VotrePassword' -o ~/naviki-backup
```

### Organisation par date

```bash
# Créer un dossier avec la date du jour
mkdir -p ~/naviki-backup/$(date +%Y-%m)
./docker-run.sh -u VotreUsername -p 'VotrePassword' -o ~/naviki-backup/$(date +%Y-%m)
```

### Backup sur NAS Synology

```bash
# Via SSH sur le NAS
ssh admin@nas.local
docker run --rm -v /volume1/backups/naviki:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --token YOUR_TOKEN --output /output
```

## 🆘 Support

- **Issues** : https://github.com/Gheop/naviki-gpx-exporter/issues
- **Discussions** : https://github.com/Gheop/naviki-gpx-exporter/discussions
- **Documentation complète** : [README.md](README.md)

---

**⏱️ Temps moyen** : ~2-5 minutes pour 100 routes  
**💾 Espace requis** : ~50-500KB par fichier GPX  
**🔒 Sécurité** : Vos identifiants restent sur votre machine