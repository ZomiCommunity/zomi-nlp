"""Tests for Zomi native POS tagger."""

import pytest

from zomi_nlp.native.tagger import ZomiPOSTagger, ZomiTaggerBackend, tag_zomi
from zomi_nlp.native.tokenizer import ZomiTokenizer


class TestZomiPOSTagger:
    """Test Zomi POS tagger."""

    @pytest.fixture
    def tagger(self):
        return ZomiPOSTagger()

    @pytest.fixture
    def tokenizer(self):
        return ZomiTokenizer()

    def test_tag_known_noun(self, tagger):
        """Test tagging known noun."""
        tag, feats = tagger._tag_single("pasian")
        assert tag == "NOUN"
        assert "Proper=Yes" in feats

    def test_tag_known_pronoun(self, tagger):
        """Test tagging known pronoun."""
        tag, feats = tagger._tag_single("ka")
        assert tag == "PRON"

    def test_tag_known_verb(self, tagger):
        """Test tagging known verb."""
        tag, feats = tagger._tag_single("pai")
        assert tag == "VERB"

    def test_tag_particle(self, tagger):
        """Test tagging particle."""
        tag, feats = tagger._tag_single("ve")
        assert tag == "PART"

    def test_tag_unknown_word(self, tagger):
        """Test tagging unknown word (default to NOUN)."""
        tag, feats = tagger._tag_single("unknownword")
        assert tag == "NOUN"

    def test_tag_number(self, tagger):
        """Test tagging number."""
        tag, feats = tagger._tag_single("123")
        assert tag == "NUM"

    def test_tag_punctuation(self, tagger):
        """Test tagging punctuation."""
        tag, feats = tagger._tag_single(".")
        assert tag == "PUNCT"

    def test_tag_multiple_tokens(self, tagger, tokenizer):
        """Test tagging multiple tokens."""
        tokens = tokenizer.tokenize("Ka pai ve.")
        results = tagger.tag(tokens)

        assert len(results) == 4
        tags = [r[1] for r in results]
        assert "PRON" in tags
        assert "VERB" in tags
        assert "PART" in tags
        assert "PUNCT" in tags

    def test_context_aware(self, tagger, tokenizer):
        """Test context-aware tagging."""
        tokens = tokenizer.tokenize("Ka pai ve.")
        results = tagger.tag_with_context(tokens)

        # 'ka' before verb should be PRON
        for token, tag, feats in results:
            if token == "ka":
                assert tag == "PRON"

    def test_pen_topic_marker(self, tagger, tokenizer):
        """Test 'pen' as topic marker."""
        tokens = tokenizer.tokenize("Eite pen")
        results = tagger.tag_with_context(tokens)

        for token, tag, feats in results:
            if token == "pen":
                assert tag == "PART"
                assert feats == "Topic=Yes"


class TestZomiTaggerBackend:
    """Test tagger backend adapter."""

    def test_backend_tagging(self):
        """Test backend adapter."""
        from zomi_nlp.core.doc import ZomiDoc
        from zomi_nlp.core.token import ZomiToken

        backend = ZomiTaggerBackend()

        # Create doc with tokens
        doc = ZomiDoc("Ka pai ve.")
        doc.tokens = [
            ZomiToken(text="Ka", start_char=0, end_char=2, idx=0),
            ZomiToken(text="pai", start_char=3, end_char=6, idx=1),
            ZomiToken(text="ve", start_char=7, end_char=9, idx=2),
            ZomiToken(text=".", start_char=9, end_char=10, idx=3),
        ]

        result = backend.tag(doc)

        # Check tags were assigned
        assert result.tokens[0].pos_ == "PRON"
        assert result.tokens[1].pos_ == "VERB"
        assert result.tokens[2].pos_ == "PART"


class TestTagZomiFunction:
    """Test convenience function."""

    def test_tag_zomi(self):
        """Test tag_zomi convenience function."""
        results = tag_zomi("Ka pai ve.")

        assert len(results) >= 3
        tags = [tag for _, tag, _ in results]
        assert "PRON" in tags
        assert "VERB" in tags
