"""
Tests de gpx_filename : le nom de fichier est la clé de déduplication de
l'archive, chaque branche doit rester stable
"""

import pytest

import naviki_exporter  # noqa: E402  (chargé par conftest.py)

CRDATE = 1729065600  # 2024-10-16 08:00 UTC


@pytest.mark.parametrize(
    "way, expected",
    [
        # date et heure dans le titre
        (
            {"title": "16/10/2025, 07:20", "crdate": CRDATE},
            "2025-10-16_07-20_Naviki.gpx",
        ),
        ({"title": "16.10.25, 07:20"}, "2025-10-16_07-20_Naviki.gpx"),
        # date sans heure : l'heure vient de crdate
        (
            {"title": "Prep - 20241124", "crdate": CRDATE},
            "2024-11-24_08-00_UTC_Naviki.gpx",
        ),
        # date sans heure ni crdate
        ({"title": "Prep - 20241124"}, "2024-11-24_Naviki.gpx"),
        # pas de date : crdate, avec le titre nettoyé en suffixe (\w est Unicode)
        (
            {"title": "Balade à Paris", "crdate": CRDATE},
            "2024-10-16_08-00_UTC_Balade_à_Paris.gpx",
        ),
        # titre trop court ou déjà propre : suffixe générique
        ({"title": "Tour", "crdate": CRDATE}, "2024-10-16_08-00_UTC_Naviki.gpx"),
        ({"title": "abc", "crdate": CRDATE}, "2024-10-16_08-00_UTC_Naviki.gpx"),
        # séparateurs de chemin neutralisés
        (
            {"title": "../../etc/passwd", "crdate": CRDATE},
            "2024-10-16_08-00_UTC_______etc_passwd.gpx",
        ),
    ],
)
def test_gpx_filename(way, expected):
    parts = naviki_exporter.date_from_title(way["title"])
    assert naviki_exporter.gpx_filename(way, parts) == expected


def test_no_date_and_no_crdate_gives_none():
    assert naviki_exporter.gpx_filename({"title": "Vervant"}, None) is None


def test_long_title_suffix_is_cut_to_30_characters():
    way = {"title": "Une très longue balade du dimanche matin", "crdate": CRDATE}
    name = naviki_exporter.gpx_filename(way, None)
    assert name == "2024-10-16_08-00_UTC_Une_très_longue_balade_du_dima.gpx"
