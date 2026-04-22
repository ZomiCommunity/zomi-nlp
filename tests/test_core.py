import pytest
from zomi_nlp.core.token import ZomiToken
from zomi_nlp.core.doc import ZomiDoc


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