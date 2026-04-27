# zomi-nlp/tests/test_core.py
"""Tests for core Zomi NLP components."""


from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken


class TestZomiToken:
    def test_token_creation(self):
        token = ZomiToken("zoh", 0, 3)
        assert token.text == "zoh"
        assert token.start_char == 0
        assert token.end_char == 3

    def test_token_to_dict(self):
        token = ZomiToken("zoh", 0, 3)
        token.pos_ = "VERB"
        d = token.to_dict()
        assert d["text"] == "zoh"
        assert d["pos"] == "VERB"


class TestZomiDoc:
    def test_doc_creation(self):
        doc = ZomiDoc("Ka zoh na ve.")
        assert doc.text == "Ka zoh na ve."
        assert len(doc) == 0

    def test_add_tokens(self):
        doc = ZomiDoc("Ka zoh na ve.")
        token = ZomiToken("Ka", 0, 2)
        doc.tokens.append(token)
        assert len(doc) == 1
        assert doc[0].text == "Ka"

    def test_doc_to_dict(self):
        doc = ZomiDoc("Ka zoh na ve.")
        doc.tokens.append(ZomiToken("Ka", 0, 2))
        doc.tokens.append(ZomiToken("zoh", 3, 6))
        d = doc.to_dict()
        assert d["text"] == "Ka zoh na ve."
        assert len(d["tokens"]) == 2

class TestZomiReferenceParser:
    """Test the ZomiReferenceParser directly."""

    def test_parser_parses_text(self):
        """Test that ZomiReferenceParser can parse text."""
        from zomi_nlp.native import ZomiReferenceParser

        parser = ZomiReferenceParser()
        result = parser.parse("Ka zoh na ve.")
        assert result is not None
        assert len(result) > 0

    def test_zomi_reference_parser_import(self):
        """Test that ZomiReferenceParser can be imported."""
        from zomi_nlp.native import ZomiReferenceParser
        parser = ZomiReferenceParser()
        assert parser is not None

    def test_zomi_reference_parser_backend_in_orchestrator(self):
        """Test that ZomiReferenceParser backend is registered."""
        from zomi_nlp import ZomiPipeline, ZomiConfig # noqa: I001

        config = ZomiConfig(parser_backend="native")
        nlp = ZomiPipeline(config)

        # Check that native backend was selected
        status = nlp.get_status()
        assert status['parser']['active'] == 'native'
        assert status['parser']['available'] is True
