"""Tests for Zomi NER."""

import pytest

from zomi_nlp.native.ner import ZomiNER, extract_entities_zomi


class TestZomiNER:
    """Test Zomi NER."""

    @pytest.fixture
    def ner(self):
        return ZomiNER()

    def test_extract_person(self, ner):
        """Test person name extraction."""
        entities = ner.extract("Pasian in leitung a piangsak hi.")
        print(entities)
        person_entities = [e for e in entities if e.type == "PERSON"]
        print(person_entities)
        assert len(person_entities) >= 1
        assert person_entities[0].text == "Pasian"

    def test_extract_location(self, ner):
        """Test location extraction."""
        entities = ner.extract("Jerusalem ah pai ve.")

        location_entities = [e for e in entities if e.type == "LOCATION"]
        assert len(location_entities) >= 1
        assert "Jerusalem" in [e.text for e in location_entities]

    def test_extract_date(self, ner):
        """Test date extraction."""
        entities = ner.extract("Tuni ka pai ve.")
        print(entities)

        date_entities = [e for e in entities if e.type == "DATE"]
        print(date_entities)
        assert len(date_entities) >= 1

    def test_extract_numeric(self, ner):
        """Test numeric extraction."""
        entities = ner.extract("Kum khat sung")

        numeric_entities = [e for e in entities if e.type == "NUMERIC"]
        assert len(numeric_entities) >= 1

    def test_extract_with_titles(self, ner):
        """Test person with title extraction."""
        entities = ner.extract("Pipa Paulam in a piangsak hi.")

        person_entities = [e for e in entities if e.type == "PERSON"]
        assert len(person_entities) >= 1

    def test_merge_overlapping(self, ner):
        """Test merging overlapping entities."""
        entities = ner.extract("Tedim ah pai ve.")

        # Should have location entity
        location_entities = [e for e in entities if e.type in ["GPE", "LOCATION"]]
        assert len(location_entities) >= 1


class TestExtractEntitiesZomi:
    """Test convenience function."""

    def test_extract_entities_zomi(self):
        """Test quick extraction function."""
        results = extract_entities_zomi("Pasian in leitung a piangsak hi.")

        assert len(results) >= 1
        assert results[0]["text"] == "Pasian"
        assert results[0]["type"] == "PERSON"
