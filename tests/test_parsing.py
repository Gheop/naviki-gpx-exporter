"""
Tests de la lecture des dates dans les titres Naviki
"""

import pytest

import naviki_exporter  # noqa: E402  (chargé par conftest.py)


class TestDateFromTitle:
    """Tests de date_from_title, la fonction réellement utilisée par main()"""

    @pytest.mark.parametrize(
        "title, expected",
        [
            ("16/10/2025, 07:20", ("2025", "10", "16", "07", "20")),
            ("16.10.25, 07:20", ("2025", "10", "16", "07", "20")),
            ("16-10-2025, 07:20", ("2025", "10", "16", "07", "20")),
            ("Prep - 20241124", ("2024", "11", "24", None, None)),
        ],
    )
    def test_known_formats(self, title, expected):
        parts = naviki_exporter.date_from_title(title)
        got = tuple(parts.get(k) for k in ("year", "month", "day", "hour", "minute"))
        assert got == expected

    def test_ddmmyyyy_block_is_not_read_as_year_3001(self):
        """« Gouter30012024 » donnait le fichier 3001-20-24_..."""
        parts = naviki_exporter.date_from_title("Gouter30012024")
        assert (parts["year"], parts["month"], parts["day"]) == ("2024", "01", "30")

    @pytest.mark.parametrize(
        "title", ["Vervant", "Code 99999999", "32/13/2025, 07:20", "Tour 12345678"]
    )
    def test_no_real_date_gives_none(self, title):
        """Sans vraie date, main() retombe sur crdate"""
        assert naviki_exporter.date_from_title(title) is None

    def test_invalid_slash_date_falls_back_to_compact(self):
        """Un motif qui ne donne pas une vraie date laisse sa chance aux suivants"""
        parts = naviki_exporter.date_from_title("31/02/2025, 07:20 - 20250301")
        assert (parts["year"], parts["month"], parts["day"]) == ("2025", "03", "01")
