# Performance

Optimisation du 2026-10-07, de `702b414` à `ebe1e96`. Détail des itérations : `bench/JOURNAL.md`.

## 1. Bilan

Métrique principale : temps mur, médiane et p95. Garde-fous : RSS max et CPU total.

| Scénario | Avant | Après | Δ |
|----------|-------|-------|---|
| Synchro quotidienne, 431 traces déjà présentes (mock, 20 runs) | 7,75 s, p95 8,86 s | 2,16 s, p95 2,23 s | −72 % |
| Synchro quotidienne, vraie API (5 runs alternés) | 9,38 s | 2,17 s | −77 % |
| Export complet, 431 GPX (mock) | 196,9 s | 49,2 s | −75 % |
| Export complet, vraie API (1 run, login compris) | ~215 s (estimé : 6 s + 1,9 s + 431 × 0,48 s) | 53,7 s | −75 % |
| Run qui doit se connecter, cache absent ou expiré (mock) | 7,33 s | 6,48 s | −12 % |
| RSS max, synchro quotidienne | 513 Mo | 37 Mo | −93 % |
| CPU, synchro quotidienne | 8,9 s | 0,37 s | −96 % |

Les 431 GPX produits par la nouvelle version sont identiques octet pour octet à l'archive existante, hors horodatage d'export que Naviki écrit dans `<metadata><time>`.

## 2. Ce qui a payé

1. **Téléchargements parallèles (4 workers)** : −75 % sur l'export complet. Les POST sont des attentes réseau de ~0,45 s, quatre se recouvrent sans charge CPU supplémentaire. Deux trajets qui donnent le même nom de fichier sont traités comme avant (le second est ignoré, ou retenté si le premier a échoué).
2. **Cache du token OAuth** : −72 % sur la synchro quotidienne. Firefox ne démarre plus tant que le token est accepté ; un 401 déclenche un login et met le cache à jour. Fichier `.naviki-token.json`, mode 600, lié au nom d'utilisateur.
3. **Fermeture de Firefox en arrière-plan** : −12 % sur un run avec login. `driver.quit()` (~0,9 s) se recouvre avec la pagination.
4. **Polling du token toutes les 100 ms** : −8 % sur un run avec login. L'ancien pas d'1 s perdait ~0,6 s.

## 3. Ce qui n'a pas payé

Aucune itération reverti. Pistes écartées avant d'écrire du code, sur profil :

- Décoder puis réencoder les GPX (`dl.text.encode()`) : 1 ms sur 480 ms, Naviki déclare l'encodage.
- Compresser les GPX : le serveur ne les compresse pas, même en gzip demandé.
- Arrêter la pagination au premier fichier déjà présent : ~1,8 s de gain, mais une trace plus ancienne manquante ne serait plus récupérée. Changement fonctionnel, à décider séparément.

## 4. Plafond atteint

- **Synchro quotidienne (2,16 s)** : 23 pages de 20 trajets lues l'une après l'autre (~85 ms chacune, 2,0 s) plus ~0,15 s de démarrage Python. Piste suivante : lire les pages par lots de 4 en parallèle jusqu'à la première page vide, ~0,5 s attendues. Ou un paramètre de taille de page côté API, s'il existe.
- **Export complet (49 s)** : 431 × 0,45 s / 4. Plus de workers chargerait davantage le serveur de Naviki ; 4 est la limite choisie.
- **Run avec login (6,5 s)** : démarrage de Firefox, 3,4 s. Seul un login sans navigateur le supprimerait : le localStorage contient un refresh token (`_n_a_rt`), utilisable si l'on identifie l'endpoint OAuth de renouvellement de Naviki.

## 5. Reproduire

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt

# synchro quotidienne, 20 runs alternés, comparaison appariée
.venv/bin/python bench/bench.py --scenario incremental --runs 20 702b414 HEAD

# run avec login (cache supprimé avant chaque run)
.venv/bin/python bench/bench.py --scenario login --runs 20 HEAD~1 HEAD

# export complet (~4 min par paire avec l'ancienne version)
.venv/bin/python bench/bench.py --scenario full --runs 10 702b414 HEAD

# latences réelles de Naviki (identifiants dans .env, charge faible)
.venv/bin/python bench/profile_real.py --downloads 5
.venv/bin/python bench/profile_login.py
```

`bench.py` accepte toute révision git ou `WORKTREE`, copie le script dans un dossier isolé sans `.env`, démarre le mock et écrit le rapport en JSON (`--json`). La clé `delta_vs_<révision>` donne la médiane des écarts appariés et son IC 95 %.

## 6. Surveiller

À ajouter en CI, sur le mock, donc sans réseau ni identifiants :

| Benchmark | Commande | Seuil d'alerte |
|-----------|----------|----------------|
| Synchro quotidienne | `bench.py --scenario incremental --runs 10 origin/main HEAD` | IC 95 % du temps mur entièrement au-dessus de +10 % |
| Export complet | `bench.py --scenario full --runs 3 origin/main HEAD` | médiane > +10 % (dispersion < 0,1 %, 3 runs suffisent) ; `outputs_identical` doit rester vrai |

Le scénario `incremental` a besoin de Firefox et de geckodriver sur le runner ; `full` n'a besoin que de Python. Les runners partagés sont bruités : n'alerter que sur l'IC apparié, jamais sur une médiane isolée.
