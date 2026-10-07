# Journal d'optimisation

Mesures sur le mock (`bench/mock_naviki.py`), runs alternés baseline/candidat,
décision sur l'écart apparié run par run avec IC bootstrap 95 % de la médiane.
Machine : Fedora 44, noyau 7.2.8, Python 3.14.7, gouverneur `powersave`
(non modifiable sans root). Résultats bruts dans `bench/results/`.

| # | Hypothèse | Fichiers | Résultat | Δ métrique | Δ RAM | Verdict |
|---|-----------|----------|----------|-----------|-------|---------|
| 1 | Le polling du token dort 1 s avant la 1re lecture alors que le token arrive 0,4 s après la soumission : un pas de 100 ms doit rendre ~0,6 s par login | `naviki-gpx-exporter.py` | 20 paires, scénario incrémental (login à chaque run à ce stade). Gain conforme à l'hypothèse | −8,1 % temps mur, IC [−13,2 ; −5,0] | −7 % | Retenu |
| 2 | Les 431 POST séquentiels font 96 % de l'export complet ; 4 workers doivent diviser ce temps par ~4 | `naviki-gpx-exporter.py`, `tests/test_parallel_downloads.py` | 196,9 s → 49,2 s. Mesure arrêtée à 4 paires (dont 1 warmup) sur décision explicite : écart de 4x pour une dispersion < 0,1 %. Validation réelle : 53,7 s login compris, 0 erreur, 431 GPX identiques à l'archive hors horodatage d'export | −75,0 % temps mur | non relevé sur le mock ; 614 Mo de RSS max en réel, Firefox compris | Retenu |
| 3 | Le login Firefox (~6 s sur 7,6 s) est refait à chaque run alors que le token reste valide : un cache par compte doit le supprimer | `naviki-gpx-exporter.py`, `tests/test_token_cache.py`, `.gitignore` | 20 paires. 7,75 s → 2,16 s, p95 8,86 s → 2,23 s. Réel : 9,38 s → 2,17 s (5 runs alternés) | −72,3 % temps mur, IC [−72,5 ; −71,5] ; CPU −96 % | 513 → 37 Mo (−93 %) | Retenu |
| 4 | `driver.quit()` bloque ~0,9 s ; le lancer dans un thread après un login réussi le recouvre avec la pagination | `naviki-gpx-exporter.py`, `tests/test_selenium_auth.py` | 20 paires, scénario `login` (cache supprimé avant chaque run). Ne sert plus qu'aux runs qui doivent se connecter | −11,7 % temps mur, IC [−16,9 ; −7,0] ; CPU IC contient 0 | IC [−5,6 ; +0,3] | Retenu |
| 5 | La liste coûte 23 requêtes de 20 trajets (~1,8 s) ; le paramètre `limit`, trouvé en sondant l'API, ramène 431 trajets en 2 requêtes | `naviki-gpx-exporter.py`, `bench/mock_naviki.py` | 20 paires, scénario incrémental. Réel : pagination 2,54 s → 0,54 s, liste identique et dans le même ordre pour `limit` = 100, 200, 500 et 1000 | −64,7 % temps mur, IC [−64,9 ; −64,6] ; CPU −9 % | +3,3 % (37,7 → 38,9 Mo, page JSON plus grosse) | Retenu |
| 6 | Le site échange un `code` OAuth via l'action `FeUser/feSession` du dispatcher AJAX : refaire ce flux en HTTP supprime Firefox du login (~6 s → ~0,5 s), Selenium restant en secours et pour `--visible` | `naviki-gpx-exporter.py`, `tests/test_http_login.py`, `tests/conftest.py` | 20 paires, scénario `login`. Réel : run avec login 1,38 s, aucun Firefox lancé. Les itérations 1 et 4 ne servent plus qu'au repli | −64,0 % temps mur, IC [−65,7 ; −62,3] ; CPU −96 % | 566 → 39 Mo (−93 %) | Retenu |
| 7 | Importer Selenium coûte ~140 ms sur ~165 ms d'imports, à chaque run, alors qu'il ne sert plus qu'en secours | `naviki-gpx-exporter.py`, tests Selenium (cibles des `patch`) | 20 paires, scénario incrémental. Le banc importait lui-même Selenium et aurait masqué le gain : la redirection vers le mock se pose maintenant au moment de l'import | −11,8 % temps mur, IC [−12,1 ; −11,5] ; CPU −43 % | 39 → 32 Mo (−17 %) | Retenu |

## Pistes examinées, non tentées

| Piste | Constat | Raison |
|-------|---------|--------|
| Décodage `dl.text` puis `.encode()` des GPX | Naviki déclare `charset=UTF-8` : pas de détection d'encodage, 1 ms par fichier sur 480 ms | Gain sous le bruit |
| Compression des GPX | La liste est servie en gzip, les GPX non, malgré `Accept-Encoding: gzip` | Côté serveur, hors de portée |
| Arrêt de la pagination au premier fichier déjà présent | Supprimerait ~1,8 s en incrémental | Change le comportement : un trou plus ancien dans l'archive ne serait plus rattrapé |
| Renouvellement par refresh token (action `FeUser/refreshToken`) | Trouvé dans le JS du site ; l'appel répond `status: false` et le nouveau token est refusé (401) | Inutile depuis le login HTTP (0,5 s) |
| Pagination parallèle | Prévue pour réduire les 23 requêtes séquentielles | Rendue inutile par `limit` (2 requêtes) |
| Arrêter la liste quand une page compte moins de `limit` trajets | Économiserait la requête qui confirme la page vide, ~60 ms | Si Naviki abaisse son plafond (ex. 200), le script s'arrêterait après une page et raterait des trajets sans le signaler |
| Demander en parallèle la page suivante | ~60 ms | Pagination concurrente pour un gain de 60 ms : complexité non justifiée |

## Incidents de mesure

- Le premier mock ajoutait ~40 ms par réponse (Nagle + ACK retardé : en-têtes et corps en deux `write`). Corrigé par `disable_nagle_algorithm`, sinon la pagination était surévaluée de 50 %.
- Un processus `badge_sim` à 400 % CPU rendait le login bimodal (7,5 s ou 10,5 s, CV 17 %). Arrêté par l'utilisateur. Le CV est resté entre 8 et 20 % à cause du démarrage de Firefox et d'une charge de fond, d'où la décision sur IC apparié plutôt que sur le seul écart-type.
- 3 tests échouaient dès qu'un `.env` local existait, et la suite lançait un vrai Firefox (31 s) parce que chaque fichier rechargeait le module et que les `patch()` visaient une autre copie. Corrigé hors périmètre perf (commits `74e4257`, `6f2f040`) : la suite passe en 1,1 s, dans n'importe quel ordre.
