"""Tests for Zomi tokenizer."""

import pytest
from zomi_nlp.native.tokenizer import (
    ZomiTokenizer, ZomiSentenceSplitter, tokenize_zomi,
    CliticSplitter, PunctuationSplitter, ReduplicationSplitter, CompoundSplitter
)


class TestZomiTokenizer:
    """Test Zomi tokenizer."""
    
    @pytest.fixture
    def tokenizer(self):
        return ZomiTokenizer()
    
    def test_basic_tokenization(self, tokenizer):
        """Test basic whitespace tokenization."""
        tokens = tokenizer.tokenize("Ka pai hi.")
        assert tokens == ["Ka", "pai", "hi", "."]
    
    def test_clitic_splitting(self, tokenizer):
        """Test clitic splitting."""
        tokens = tokenizer.tokenize("Ka zohve.")
        assert tokens == ["Ka", "zoh", "ve", "."]
    
    def test_multiple_clitics(self, tokenizer):
        """Test words with clitics."""
        tokens = tokenizer.tokenize("Ka pai ve hi.")
        assert "ve" in tokens
        assert "hi" in tokens
    
    def test_punctuation_handling(self, tokenizer):
        """Test punctuation separation."""
        tokens = tokenizer.tokenize("Hi! How are you?")
        assert "!" in tokens
        assert "?" in tokens
    
    def test_reduplication(self, tokenizer):
        """Test reduplication handling."""
        tokens = tokenizer.tokenize("mahmah")
        # Should split into two "mahl" tokens
        assert tokens == ["mah", "mah"]
    
    def test_compound_words(self, tokenizer):
        """Test compound word splitting."""
        tokens = tokenizer.tokenize("sang-inn")
        assert tokens == ["sang", "-", "inn"]
    
    def test_empty_string(self, tokenizer):
        """Test empty string."""
        assert tokenizer.tokenize("") == []
    
    def test_preserve_case(self, tokenizer):
        """Test case preservation."""
        tokens = tokenizer.tokenize("Ka Pai Ve.")
        assert tokens[0] == "Ka"  # Preserves case


class TestZomiSentenceSplitter:
    """Test sentence splitting."""
    
    def test_split_simple(self):
        """Test simple sentence splitting."""
        sentences = ZomiSentenceSplitter.split("Ka pai hi. Na pai ve.")
        assert len(sentences) == 2
        assert sentences[0] == "Ka pai hi."
        assert sentences[1] == "Na pai ve."
    
    def test_split_with_question(self):
        """Test question splitting."""
        sentences = ZomiSentenceSplitter.split("Na pai hi? Ka pai ve.")
        assert len(sentences) == 2
        assert sentences[0] == "Na pai hi?"
    
    def test_single_sentence(self):
        """Test single sentence."""
        sentences = ZomiSentenceSplitter.split("Ka pai hi.")
        assert len(sentences) == 1


class TestTokenizeZomiFunction:
    """Test convenience function."""
    
    def test_tokenize_zomi(self):
        """Test quick tokenization function."""
        tokens = tokenize_zomi("Ka zohve hi.")
        assert tokens == ["Ka", "zoh", "ve", "hi", "."]


class TestCliticSplitter:
    """Test clitic splitting logic."""
    
    def test_clitic_splitter(self):
        """Test that clitics are split correctly."""
        tokenizer = ZomiTokenizer(split_clitics=True)
        tokens = tokenizer.tokenize("Ka zohve.")
        assert "zoh" in tokens
        assert "ve" in tokens
    
    # self.splitter = CliticSplitter()
    def setup_method(self):
        """Set up before each test."""
        self.splitter = CliticSplitter()

    def test_single_clitic(self):
        """Test single clitic splitting."""
        assert self.splitter.split("zohve") == ["zoh", "ve"]

    def test_multi_clitic_chain(self):
        """Test multiple clitic chain splitting."""
        assert self.splitter.split("zohvehi") == ["zoh", "ve", "hi"]

    def test_no_clitic(self):
        """Test words without clitics."""
        assert self.splitter.split("zomi") == ["zomi"]

    def test_case_preservation(self):
        """Test case preservation in clitic splitting."""
        assert self.splitter.split("Zohve") == ["Zoh", "ve"]


class TestPunctuationSplitter:
    """Test punctuation splitting logic."""
    
    def setup_method(self):
        """Set up before each test."""
        self.splitter = PunctuationSplitter()
    
    def test_punctuation_splitter(self):
        """Test that punctuation is split correctly."""
        assert self.splitter.split("hi!") == ["hi", "!"]

    def test_end_punctuation(self):
        assert self.splitter.split("hi.") == ["hi", "."]

    def test_start_punctuation(self):
        assert self.splitter.split("(hi") == ["(", "hi"]

    def test_mid_punctuation(self):
        assert self.splitter.split("hi,mah") == ["hi", ",", "mah"]

    def test_multiple_punct(self):
        assert self.splitter.split("wow!!") == ["wow", "!", "!"]

    def test_unicode_punct(self):
        assert self.splitter.split("“hi”") == ["“", "hi", "”"]

class TestReduplicationSplitter:
    """Test reduplication splitting logic."""
    
    def setup_method(self):
        """Set up before each test."""
        self.splitter = ReduplicationSplitter()
    
    def test_reduplication_splitter(self):
        """Test that reduplication is split correctly."""
        assert self.splitter.split("mahmah") == ["mah", "mah"]
        assert self.splitter.split("sangsang") == ["sang", "sang"]

    def test_no_reduplication(self):
        """Test words without reduplication."""
        assert self.splitter.split("zomi") == ["zomi"]

    def test_case_preservation(self):
        """Test case preservation in reduplication splitting."""
        assert self.splitter.split("MahMah") == ["Mah", "Mah"]
    
    def test_reduplication_valid_zomi(self):
        assert self.splitter.split("mahmah") == ["mah", "mah"]

    def test_non_reduplication(self):
        assert self.splitter.split("zomi") == ["zomi"]

    def test_english_like_not_split(self):
        assert self.splitter.split("haha") == ["haha"]
        assert self.splitter.split("mama") == ["mama"]

class TestCompoundSplitter:
    """Test compound word splitting logic."""
    
    def setup_method(self):
        """Set up before each test."""
        self.splitter = CompoundSplitter()
    
    def test_compound_splitter(self):
        """Test that compound words are split correctly."""
        assert self.splitter.split("sang-inn") == ["sang", "-", "inn"]

    def test_no_compound(self):
        """Test words without compounds."""
        assert self.splitter.split("zomi") == ["zomi"]

    def test_case_preservation(self):
        """Test case preservation in compound splitting."""
        assert self.splitter.split("Sang-Inn") == ["Sang", "-", "Inn"]
    
    def test_simple_compound1(self):
        assert self.splitter.split("a-b") == ["a", "-", "b"]

    def test_simple_compound2(self):
        assert self.splitter.split("sang-inn") == ["sang", "-", "inn"]

    def test_multi_compound(self):
        assert self.splitter.split("a-b-c") == ["a", "-", "b", "-", "c"]


class TestTokenizeWithSpans:
    """Test that tokenization with spans returns correct offsets."""
    
    def setup_method(self):
        """Set up before each test."""
        self.tokenizer = ZomiTokenizer(split_clitics=True)
    
    def test_span_alignment(self):
        text = "Zohve hi."
        tokens = self.tokenizer.tokenize_with_spans(text)

        assert tokens[0] == ("Zoh", 0, 3)
        assert tokens[1] == ("ve", 3, 5)
        assert tokens[2] == ("hi", 6, 8)
        assert tokens[3] == (".", 8, 9)

    def test_repeated_tokens(self):
        text = "mahmah mah"
        tokens = self.tokenizer.tokenize_with_spans(text)

        # First reduplication
        assert tokens[0] == ("mah", 0, 3)
        assert tokens[1] == ("mah", 3, 6)

        # Second standalone
        assert tokens[2] == ("mah", 7, 10)
