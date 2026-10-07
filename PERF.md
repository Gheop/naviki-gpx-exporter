# Performance

Optimisation du 2026-10-07, de `702b414` à `4bd19ec`. Détail des 7 itérations : `bench/JOURNAL.md`.

## 1. Bilan

Métrique principale : temps mur, médiane et p95. Garde-fous : RSS max et CPU total.

| Scénario | Avant | Après | Δ |
|----------|-------|-------|---|
| Synchro quotidienne, 431 traces déjà présentes, vraie API | 9,38 s | 0,83 s | −91 % |
| Run qui doit se connecter (1er run, token expiré), vraie API | 9,38 s | 1,38 s | −85 % |
| Export complet, 431 GPX, vraie API | ~215 s (estimé : 6 s + 1,9 s + 431 × 0,48 s) | 53,7 s mesuré avant les itérations 5 à 7, ~50 s attendus | −75 % |
| Synchro quotidienne, mock (20 runs) | 7,75 s, p95 8,86 s | 0,62 s, p95 0,63 s | −92 % |
| RSS max, synchro quotidienne (mock) | 513 Mo | 32 Mo | −94 % |
| CPU, synchro quotidienne (mock) | 8,9 s | 0,11 s | −99 % |

Les 431 GPX produits par la nouvelle version sont identiques octet pour octet à l'archive existante, hors horodatage d'export que Naviki écrit dans `<metadata><time>`. La liste obtenue avec `limit=500` est identique, dans le même ordre, à celle de la pagination par 20.

## 2. Ce qui a payé

Par ordre de gain sur le scénario qu'il vise :

1. **Téléchargements parallèles (4 workers)** : −75 % sur l'export complet. Les POST sont des attentes réseau de ~0,45 s, quatre se recouvrent ; le vrai serveur tient cette concurrence sans hausse de latence. Deux trajets qui donnent le même nom de fichier sont traités comme avant.
2. **Cache du token OAuth** : −72 % sur la synchro quotidienne. Aucun login tant que Naviki accepte le token ; un 401 déclenche un login et met le cache à jour. Fichier `.naviki-token.json`, mode 600, lié au nom d'utilisateur.
3. **`limit=500` sur la liste** : −65 %. Le paramètre, absent de toute documentation, a été trouvé en sondant l'API : 2 requêtes au lieu de 23.
4. **Login HTTP direct** : −64 % sur un run qui doit se connecter. Le script refait le flux du site (formulaire OAuth, redirection avec `code`, échange via `FeUser/feSession`) sans navigateur. Firefox reste en secours et pour `--visible`.
5. **Fermeture de Firefox en arrière-plan** : −12 % sur un run avec login Firefox. Ne joue plus que sur le repli.
6. **Import local de Selenium** : −12 % sur la synchro quotidienne, CPU −43 %. ~140 ms d'import évités quand Firefox ne sert pas.
7. **Polling du token toutes les 100 ms** : −8 % sur un run avec login Firefox. Ne joue plus que sur le repli.

## 3. Ce qui n'a pas payé

Aucune itération reverti. Pistes écartées, sur profil ou sur risque :

- Renouveler le token par refresh token (`FeUser/refreshToken`, trouvé dans le JS du site) : l'appel répond `status: false` et le nouveau token est refusé. Inutile depuis que le login coûte 0,5 s.
- Paralléliser la pagination : rendu inutile par `limit`.
- Arrêter la liste dès qu'une page compte moins de `limit` trajets (~60 ms) : si Naviki abaisse un jour son plafond, le script raterait des trajets sans le signaler.
- Demander la page suivante en parallèle (~60 ms) : pagination concurrente pour un gain trop faible.
- Arrêter la pagination au premier fichier déjà présent : une trace plus ancienne manquante ne serait plus récupérée. Changement fonctionnel.
- Décoder puis réencoder les GPX : 1 ms sur 480 ms. Compresser les GPX : le serveur ne le fait pas.

## 4. Plafond atteint

- **Synchro quotidienne (0,62 s sur le mock, 0,83 s en réel)** : la requête qui ramène les 431 trajets coûte ~0,45 s côté serveur, la requête de fin de liste ~0,06 s, le démarrage Python ~0,1 s. Il ne reste plus de travail évitable côté client sans changer le comportement.
- **Export complet (~50 s)** : 431 × 0,45 s / 4. Aller plus loin demande plus de workers, donc plus de charge sur Naviki ; 4 est la limite choisie.
- **Dépendance** : le login HTTP et `limit` reposent sur des comportements non documentés de Naviki. Le login retombe sur Firefox si le flux change ; `limit` reste sûr tant que la boucle s'arrête sur la première page vide.

## 5. Reproduire

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt

# synchro quotidienne, 20 runs alternés, comparaison appariée
.venv/bin/python bench/bench.py --scenario incremental --runs 20 702b414 HEAD

# run qui doit se connecter (cache supprimé avant chaque run)
.venv/bin/python bench/bench.py --scenario login --runs 20 HEAD~1 HEAD

# export complet (~4 min par paire avec l'ancienne version)
.venv/bin/python bench/bench.py --scenario full --runs 10 702b414 HEAD

# latences réelles de Naviki (identifiants dans .env, charge faible)
.venv/bin/python bench/profile_real.py --downloads 5
.venv/bin/python bench/profile_login.py
```

`bench.py` accepte toute révision git ou `WORKTREE`, copie le script dans un dossier isolé sans `.env`, démarre le mock et écrit le rapport en JSON (`--json`). La clé `delta_vs_<révision>` donne la médiane des écarts appariés et son IC 95 %. Le mock (`bench/mock_naviki.py`) reproduit le formulaire OAuth, l'échange `feSession`, le paramètre `limit` et les latences mesurées.

## 6. Surveiller

À ajouter en CI, sur le mock, donc sans réseau ni identifiants. Depuis le login HTTP, aucun de ces scénarios ne lance Firefox.

| Benchmark | Commande | Seuil d'alerte |
|-----------|----------|----------------|
| Synchro quotidienne | `bench.py --scenario incremental --runs 10 origin/main HEAD` | IC 95 % du temps mur entièrement au-dessus de +10 % |
| Run avec login | `bench.py --scenario login --runs 10 origin/main HEAD` | idem ; un saut à ~4 s signale un retour sur Firefox |
| Export complet | `bench.py --scenario full --runs 3 origin/main HEAD` | médiane > +10 % (dispersion < 0,1 %) ; `outputs_identical` doit rester vrai |

Côté production, surveiller la ligne « Connexion directe impossible » dans la sortie : elle signale que Naviki a changé son flux de login et que le script est retombé sur Firefox.
