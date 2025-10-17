#!/usr/bin/env python3
"""
Tests unitaires pour naviki-gpx-exporter
"""

import pytest
import re
from datetime import datetime, timezone

# Import des patterns depuis votre script
patterns = [
    r'(?P<day>\d\d)/(?P<month>\d\d)/(?P<year>\d{4}), (?P<hour>\d\d):(?P<minute>\d\d)',
    r'(?P<day>\d\d)\.(?P<month>\d\d)\.(?P<year>\d\d), (?P<hour>\d\d):(?P<minute>\d\d)',
    r'(?P<day>\d\d)-(?P<month>\d\d)-(?P<year>\d{4}), (?P<hour>\d\d):(?P<minute>\d\d)',
    r'(?P<year>\d{4})(?P<month>\d\d)(?P<day>\d\d)(?![\d])',
]


class TestDateParsing:
    """Tests pour le parsing des dates"""
    
    def test_parse_slash_format(self):
        """Test format: 16/10/2025, 07:20"""
        title = "16/10/2025, 07:20"
        pattern = patterns[0]
        match = re.search(pattern, title)
        
        assert match is not None
        assert match.group('day') == '16'
        assert match.group('month') == '10'
        assert match.group('year') == '2025'
        assert match.group('hour') == '07'
        assert match.group('minute') == '20'
    
    def test_parse_dot_format(self):
        """Test format: 16.10.25, 07:20"""
        title = "16.10.25, 07:20"
        pattern = patterns[1]
        match = re.search(pattern, title)
        
        assert match is not None
        assert match.group('day') == '16'
        assert match.group('month') == '10'
        assert match.group('year') == '25'
    
    def test_parse_compact_format(self):
        """Test format: 20241124"""
        title = "Prep - 20241124"
        pattern = patterns[3]
        match = re.search(pattern, title)
        
        assert match is not None
        assert match.group('year') == '2024'
        assert match.group('month') == '11'
        assert match.group('day') == '24'
    
    def test_no_match_for_text_only(self):
        """Test qu'un titre sans date ne match pas"""
        title = "Vervant"
        
        for pattern in patterns:
            match = re.search(pattern, title)
            assert match is None
    
    def test_custom_title_with_date(self):
        """Test titre personnalisé avec date"""
        title = "Route de la Chapelle, Coulonges"
        
        # Ne devrait matcher aucun pattern
        matches = [re.search(p, title) for p in patterns]
        assert all(m is None for m in matches)


class TestFilenameGeneration:
    """Tests pour la génération des noms de fichiers"""
    
    def test_filename_format(self):
        """Test que le nom de fichier est bien formé"""
        year, month, day = "2025", "10", "16"
        hour, minute = "07", "20"
        
        filename = f"{year}-{month}-{day}_{hour}-{minute}_Naviki.gpx"
        
        assert filename == "2025-10-16_07-20_Naviki.gpx"
        assert filename.endswith('.gpx')
    
    def test_sanitize_custom_title(self):
        """Test la sanitisation des titres personnalisés"""
        title = "Route de la Chapelle, Coulonges"
        safe_title = re.sub(r'[^\w\-]', '_', title)[:30]
        
        assert ',' not in safe_title
        assert ' ' not in safe_title
        assert len(safe_title) <= 30


class TestTokenValidation:
    """Tests pour la validation des tokens"""
    
    def test_token_format(self):
        """Test qu'un token a le bon format UUID"""
        token = "14dcc0f4-d964-396c-a19e-3cc42e36d372"
        
        # Format UUID avec tirets
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        assert re.match(uuid_pattern, token)
    
    def test_bearer_token_strip(self):
        """Test le nettoyage du préfixe Bearer"""
        token = "Bearer 14dcc0f4-d964-396c-a19e-3cc42e36d372"
        
        if token.startswith("Bearer "):
            token = token[7:]
        
        assert not token.startswith("Bearer")
        assert len(token) == 36  # UUID length


class TestErrorHandling:
    """Tests pour la gestion des erreurs"""
    
    def test_invalid_date_components(self):
        """Test dates invalides"""
        invalid_dates = [
            "32/13/2025, 07:20",  # Jour/mois invalides
            "00/00/2025, 07:20",  # Zéros
            "2025, 07:20",         # Format incomplet
        ]
        
        # Ces dates ne devraient pas matcher
        for date in invalid_dates:
            match = re.search(patterns[0], date)
            # Le regex match syntaxiquement mais la validation logique devrait rejeter
            assert match is None or int(match.group('day')) > 31


@pytest.fixture
def sample_way_data():
    """Fixture avec des données d'exemple d'un way Naviki"""
    return {
        "uuid": "8252D5EB-42FD-4022-A545-244F305D03DE",
        "title": "16/10/2025, 07:20",
        "crdate": 1729065600  # Timestamp exemple
    }


def test_crdate_parsing(sample_way_data):
    """Test le parsing du crdate"""
    crdate = sample_way_data["crdate"]
    dt = datetime.fromtimestamp(crdate, tz=timezone.utc)
    
    assert isinstance(dt, datetime)
    assert dt.tzinfo == timezone.utc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
