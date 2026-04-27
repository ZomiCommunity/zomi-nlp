# tests/test_morphological_analyser.py

from zomi_nlp.native import analyze_morphology


def test_morphological_analyser():
    """Test the Zomi morphological analyzer with various words."""
    result = analyze_morphology("pasian")
    assert result["word"] == "pasian"
    assert result["root"] == "pasian"
    assert result["pos"] == "NOUN"
    assert isinstance(result["features"], dict)
    # Features for "pasian": Number=Sing, Proper=Yes
    assert result["features"].get("Number") == "Sing"
    assert result["features"].get("Proper") == "Yes"
    assert result["morphemes"][0][0] == "pasian"
    assert result["morphemes"][0][1] == "root"


def test_morphological_analyser_with_prefixes_and_suffixes():
    """Test morphological analysis with prefixes and suffixes."""
    result = analyze_morphology("kaom")
    assert result["word"] == "kaom"
    assert result["root"] == "om"
    assert result["pos"] == "VERB"
    assert isinstance(result["features"], dict)
    # "ka" prefix adds Person=1, Number=Sing
    assert result["features"].get("Person") == "1"
    assert result["features"].get("Number") == "Sing"
    # "om" root may have no special features
    assert result["morphemes"][0][0] == "ka"
    assert result["morphemes"][0][1] == "prefix"
    assert result["morphemes"][1][0] == "om"
    assert result["morphemes"][1][1] == "root"


def test_morphological_analyser_with_reduplication():
    """Test morphological analysis of reduplicated words."""
    result = analyze_morphology("kapiangsakve")
    assert result["word"] == "kapiangsakve"
    assert result["root"] == "piangsak"
    assert result["pos"] == "VERB"
    assert isinstance(result["features"], dict)
    
    # Expected features from root + prefix + suffix
    # Root "piangsak" should have: Voice=Cau, VerbForm=Fin
    assert result["features"].get("Voice") == "Cau"
    assert result["features"].get("VerbForm") == "Fin"
    # Prefix "ka" adds: Person=1, Number=Sing
    assert result["features"].get("Person") == "1"
    assert result["features"].get("Number") == "Sing"
    # Suffix "ve" adds: Mood=Ind, Polite=Yes
    assert result["features"].get("Mood") == "Ind"
    assert result["features"].get("Polite") == "Yes"
    
    # Check morphemes in order
    assert result["morphemes"][0][0] == "ka"
    assert result["morphemes"][0][1] == "prefix"
    assert result["morphemes"][1][0] == "piangsak"
    assert result["morphemes"][1][1] == "root"
    assert result["morphemes"][2][0] == "ve"
    assert result["morphemes"][2][1] == "suffix"


def test_morphological_analyser_features_to_string():
    """Test converting features dict to string."""
    from zomi_nlp.native.morphology import ZomiMorphologicalAnalyzer
    analyzer = ZomiMorphologicalAnalyzer()
    
    features = {"Person": "1", "Number": "Sing"}
    result = analyzer.features_to_string(features)
    # Order may vary, so check components
    assert "Person=1" in result
    assert "Number=Sing" in result
    assert "|" in result
    
    features = {}
    assert analyzer.features_to_string(features) == "_"