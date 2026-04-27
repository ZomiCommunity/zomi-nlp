"""Tests for native tokenizer adapter."""

import pytest

from zomi_nlp.adapters.zomi_native_adapter import ZomiTokenizerAdapter


class TestZomiTokenizerAdapter:
    """Test native tokenizer adapter."""

    @pytest.fixture
    def adapter(self):
        return ZomiTokenizerAdapter()

    def test_tokenize_basic(self, adapter):
        """Test basic tokenization."""
        tokens = adapter.tokenize("Ka pai hi.")
        assert len(tokens) == 4
        assert tokens[0].text == "Ka"
        assert tokens[1].text == "pai"
        assert tokens[2].text == "hi"
        assert tokens[3].text == "."

    def test_tokenize_with_clitics(self, adapter):
        """Test clitic handling."""
        tokens = adapter.tokenize("Ka zohve.")
        # "zohve" should split into "zoh" and "ve"
        token_texts = [t.text for t in tokens]
        assert "zoh" in token_texts
        assert "ve" in token_texts

    def test_token_spans(self, adapter):
        """Test token spans."""
        text = "Ka pai hi."
        tokens = adapter.tokenize(text)

        # First token
        assert tokens[0].start_char == 0
        assert tokens[0].end_char == 2  # "Ka"

        # Last token (period)
        assert tokens[-1].start_char == 9
        assert tokens[-1].end_char == 10

    def test_clitic_detection(self, adapter):
        """Test clitic detection."""
        tokens = adapter.tokenize("Ka zohve hi.")

        # Find clitic tokens
        clitic_tokens = [t for t in tokens if t.is_clitic]
        assert len(clitic_tokens) >= 1
        for token in clitic_tokens:
            assert token.clitic_type is not None

    def test_empty_string(self, adapter):
        """Test empty string."""
        tokens = adapter.tokenize("")
        assert tokens == []
