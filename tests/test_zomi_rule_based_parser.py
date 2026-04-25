# zomi-nlp/tests/test_zomi_rule_based_parser.py
"""Tests for ZomiRuleBasedParser native backend."""

import pytest

from zomi_nlp.adapters.zomi_rule_based_parser_backend import (
    ZomiRuleBasedParserBackend,
)
from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.native import ZomiRuleBasedParser


class TestZomiRuleBasedParser:
    """Test suite for ZomiRuleBasedParser."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return ZomiRuleBasedParser()


    def test_parser_initialization(self, parser):
        """Test that parser initializes correctly."""
        assert parser is not None
        assert hasattr(parser, 'lexicon')
        assert hasattr(parser, 'suffix_table')
        assert len(parser.lexicon) > 0

    def test_basic_parse(self, parser):
        """Test basic parsing of a simple sentence."""
        result = parser.parse("Ka pai hi.")

        assert result is not None
        assert len(result) >= 4  # At least: Ka, pai, hi, .

        # Check token structure
        first_token = result[0]
        assert 'id' in first_token
        assert 'form' in first_token
        assert 'tag' in first_token

    def test_morphology_analysis(self, parser):
        """Test morphological analysis."""
        # Test noun
        lemma, tag, feats, deprel = parser.analyze_morphology("pasian")
        assert lemma == "pasian"
        assert tag == "NOUN"

        # Test pronoun
        lemma, tag, feats, deprel = parser.analyze_morphology("ka")
        assert tag == "PRON"

        # Test verb
        lemma, tag, feats, deprel = parser.analyze_morphology("pai")
        assert tag == "VERB"

        # Test punctuation
        lemma, tag, feats, deprel = parser.analyze_morphology(".")
        assert tag == "PUNCT"

    def test_parse_with_particles(self, parser):
        """Test parsing sentences with particles."""
        result = parser.parse("Ka pai ve.")

        # Find the particle
        particles = [t for t in result if t['form'] == 've']
        assert len(particles) == 1
        assert particles[0]['tag'] == 'PART'

    def test_parse_with_clitic(self, parser):
        """Test parsing with clitic handling."""
        # Your parser should handle "zohve" -> "zoh" + "ve"
        result = parser.parse("Ka zohve.")

        # Check tokens
        forms = [t['form'] for t in result]
        # The clitic might be split or kept together
        assert len(forms) >= 3  # At minimum: Ka, zohve or zoh+ve, .

    def test_dependency_heads(self, parser):
        """Test that dependency heads are assigned correctly."""
        result = parser.parse("Ka pai hi.")

        # Find the verb
        verb = next((t for t in result if t['tag'] == 'VERB'), None)
        assert verb is not None
        assert verb['head'] == 0  # Root should have head 0
        assert verb['deprel'] == 'root'

    def test_constituency_tree(self, parser):
        """Test constituency tree generation."""
        tree = parser.generate_constituency_tuple(parser.parse("Ka pai hi."))

        assert tree is not None
        assert isinstance(tree, tuple)
        assert tree[0] == 'Sbar'  # Root should be Sbar

    def test_export_conllu(self, parser, tmp_path):
        """Test CoNLL-U export functionality."""
        test_cases = [
            ("Ka pai hi.", "I go.", None),
        ]

        output_file = tmp_path / "test_output.conllu"
        parser.export_to_zomi_conllu(parser, test_cases, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "# sent_id" in content
        assert "# text" in content

    def test_multiple_sentences(self, parser):
        """Test parsing multiple sentences."""
        test_sentences = [
            "Ka pai hi.",
            "Na pai ve.",
            "Amah piang hi.",
        ]

        for sentence in test_sentences:
            result = parser.parse(sentence)
            assert len(result) > 0
            assert result[0]['id'] == 1


class TestZomiParserAliases:
    """Test that parser aliases work correctly."""

    def test_zomi_parser_alias(self):
        """Test ZomiParser alias."""
        from zomi_nlp.native import ZomiParser

        assert ZomiParser is not None
        parser = ZomiParser()
        assert parser is not None
        result = parser.parse("Ka pai hi.")
        assert len(result) > 0

    def test_zomi_parser_v362_alias(self):
        """Test ZomiParserV362 alias for backward compatibility."""
        from zomi_nlp.native import ZomiParserV362

        parser = ZomiParserV362()
        assert parser is not None
        result = parser.parse("Ka pai hi.")
        assert len(result) > 0


class TestBackendIntegration:
    """Test the backend adapter integration."""

    def test_backend_adapter_import(self):
        """Test that backend adapter can be imported."""
        backend = ZomiRuleBasedParserBackend()
        assert backend is not None
        assert backend.name() == "zomirulebasedparser"
        assert backend.is_available() is True

    def test_backend_parses_to_zomidoc(self):
        """Test that backend returns ZomiDoc."""
        backend = ZomiRuleBasedParserBackend()
        doc = ZomiDoc("Ka pai hi.")
        result = backend.parse(doc)

        assert isinstance(result, ZomiDoc)
        assert len(result.tokens) > 0


class TestPipelineWithNativeBackend:
    """Test the full pipeline with native backend."""

    def test_pipeline_auto_selects_native(self):
        """Test that pipeline can use native backend."""
        from zomi_nlp import ZomiConfig, ZomiPipeline

        config = ZomiConfig(parser_backend="native")
        nlp = ZomiPipeline(config)

        doc = nlp("Ka pai hi.")
        assert len(doc.tokens) > 0

    def test_pipeline_native_returns_tokens(self):
        """Test that native backend returns proper tokens."""
        from zomi_nlp import ZomiConfig, ZomiPipeline

        config = ZomiConfig(parser_backend="native")
        nlp = ZomiPipeline(config)

        doc = nlp("Ka pai hi.")

        # Check token structure
        for token in doc:
            assert hasattr(token, 'text')
            assert hasattr(token, 'pos_')
            # Lemma might be None for unknown words, that's fine
