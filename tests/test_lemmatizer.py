"""Tests for Zomi native lemmatizer."""

import pytest

from zomi_nlp.native.lemmatizer import (
    ZomiLemmatizer,
    ZomiLemmatizerBackend,
    lemmatize_with_info_zomi,
    lemmatize_zomi,
)
from zomi_nlp.native.tokenizer import ZomiTokenizer


class TestZomiLemmatizer:
    """Test Zomi lemmatizer."""

    @pytest.fixture
    def lemmatizer(self):
        return ZomiLemmatizer()

    @pytest.fixture
    def tokenizer(self):
        return ZomiTokenizer()

    def test_lexicon_lookup(self, lemmatizer):
        """Test lexicon-based lemmatization."""
        lemma = lemmatizer._get_lemma("pasian")
        assert lemma == "pasian"

    def test_clitic_splitting(self, lemmatizer):
        """Test clitic splitting."""
        lemma = lemmatizer._get_lemma("zohve")
        # Should strip 've', return 'zoh'
        assert lemma == "zoh"

    def test_irregular_form(self, lemmatizer):
        """Test irregular form handling."""
        lemma = lemmatizer._get_lemma("hikei")
        assert lemma == "hi"

    def test_plural_handling(self, lemmatizer):
        """Test plural noun lemmatization."""
        lemma = lemmatizer._get_lemma("sangnaupangte")
        assert lemma == "sangnaupang"

    def test_multiple_tokens(self, lemmatizer, tokenizer):
        """Test lemmatizing multiple tokens."""
        tokens = tokenizer.tokenize("Ka pai ve.")
        lemmas = lemmatizer.lemmatize(tokens)

        assert len(lemmas) == 4
        assert lemmas[0] == "ka"
        assert lemmas[1] == "pai"
        assert lemmas[2] == "ve"
        assert lemmas[3] == "."

    def test_lemmatize_with_info(self, lemmatizer):
        """Test lemmatization with method info."""
        results = lemmatizer.lemmatize_with_info(["zohve", "pasian"])

        assert len(results) == 2
        assert results[0][1] == "zoh"  # lemma
        assert results[1][2] == "lexicon"  # method

    def test_unknown_word(self, lemmatizer):
        """Test unknown word (returns itself)."""
        lemma = lemmatizer._get_lemma("unknownword123")
        assert lemma == "unknownword123"

    def test_reduplication(self, lemmatizer):
        """Test reduplication handling."""
        lemma = lemmatizer._get_lemma("mahmah")
        assert lemma == "mah"


class TestZomiLemmatizerBackend:
    """Test lemmatizer backend adapter."""

    def test_backend_lemmatization(self):
        """Test backend adapter."""
        from zomi_nlp.core.doc import ZomiDoc
        from zomi_nlp.core.token import ZomiToken

        backend = ZomiLemmatizerBackend()

        # Create doc with tokens
        doc = ZomiDoc("Ka pai ve.")
        doc.tokens = [
            ZomiToken(text="Ka", start_char=0, end_char=2, idx=0),
            ZomiToken(text="pai", start_char=3, end_char=6, idx=1),
            ZomiToken(text="ve", start_char=7, end_char=9, idx=2),
            ZomiToken(text=".", start_char=9, end_char=10, idx=3),
        ]

        result = backend.lemmatize(doc)

        # Check lemmas were assigned
        assert result.tokens[0].lemma_ == "ka"
        assert result.tokens[1].lemma_ == "pai"
        assert result.tokens[2].lemma_ == "ve"


class TestLemmatizeZomiFunction:
    """Test convenience functions."""

    def test_lemmatize_zomi(self):
        """Test lemmatize_zomi convenience function."""
        lemmas = lemmatize_zomi("Ka zohve hi.")
        assert "zoh" in lemmas
        assert "ve" in lemmas

    def test_lemmatize_with_info_zomi(self):
        """Test lemmatize_with_info_zomi."""
        results = lemmatize_with_info_zomi("Ka pai hi.")
        assert len(results) >= 3
        # Should have lemma info
        assert results[1][1] == "pai"  # lemma
