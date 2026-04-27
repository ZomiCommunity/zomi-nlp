"""Tests for Zomi dependency parser."""

import pytest

from zomi_nlp.native.dependency_parser import ZomiDependencyParser, parse_dependencies


class TestZomiDependencyParser:
    """Test dependency parser."""

    @pytest.fixture
    def parser(self):
        return ZomiDependencyParser()

    def test_basic_svo(self, parser):
        """Test basic Subject-Verb-Object pattern."""
        tokens = ["Ka", "pai", "hi", "."]
        pos_tags = ["PRON", "VERB", "PART", "PUNCT"]

        result = parser.parse(tokens, pos_tags)

        # Find root (should be "pai")
        root = [t for t in result if t["deprel"] == "root"][0]
        assert root["form"] == "pai"

        # Subject should point to root
        subject = [t for t in result if t["form"] == "Ka"][0]
        assert subject["head"] == root["id"]
        assert subject["deprel"] == "nsubj"

    def test_with_particle(self, parser):
        """Test sentence with final particle."""
        tokens = ["Ka", "pai", "ve", "."]
        pos_tags = ["PRON", "VERB", "PART", "PUNCT"]

        result = parser.parse(tokens, pos_tags)

        # Particle should attach to root
        particle = [t for t in result if t["form"] == "ve"][0]
        root = [t for t in result if t["deprel"] == "root"][0]
        assert particle["head"] == root["id"]
        assert particle["deprel"] == "discourse"

    def test_with_case_marker(self, parser):
        """Test ergative case marker."""
        tokens = ["Pasian", "in", "piangsak", "sa", "hi", "."]
        pos_tags = ["NOUN", "ADP", "VERB", "AUX", "PART", "PUNCT"]

        result = parser.parse(tokens, pos_tags)

        # Case marker should attach to preceding noun
        case = [t for t in result if t["form"] == "in"][0]
        noun = [t for t in result if t["form"] == "Pasian"][0]
        assert case["head"] == noun["id"]
        assert case["deprel"] == "case"

    def test_to_conllu(self, parser):
        """Test CoNLL-U export."""
        tokens = ["Ka", "pai", "hi", "."]
        pos_tags = ["PRON", "VERB", "PART", "PUNCT"]

        result = parser.parse(tokens, pos_tags)
        conllu = parser.to_conllu(result)

        assert "Ka" in conllu
        assert "pai" in conllu
        assert "nsubj" in conllu
        assert "root" in conllu

    def test_convenience_function(self):
        """Test parse_dependencies convenience function."""
        tokens = ["Ka", "pai", "hi", "."]
        pos_tags = ["PRON", "VERB", "PART", "PUNCT"]

        result = parse_dependencies(tokens, pos_tags)
        assert len(result) == 4
        assert result[1]["deprel"] == "root"  # "pai" should be root
