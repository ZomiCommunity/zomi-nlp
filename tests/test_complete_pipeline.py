# test_complete_pipeline.py
from zomi_nlp.native.parser import ZomiRuleBasedParser


def test_complete_pipeline():
    parser = ZomiRuleBasedParser()
    result = parser.parse("Tuni hong pai mengmeng ve")

    print("ID\tFORM\tLEMMA\tTAG\tFEATS\tHEAD\tDEPREL")
    print("-" * 70)
    for token in result:
        print(f"{token['id']}\t{token['form']}\t{token['lemma']}\t{token['tag']}\t{token['feats']}\t{token['head']}\t{token['deprel']}")
