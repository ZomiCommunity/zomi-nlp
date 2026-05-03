#!/usr/bin/env python3
"""Quick interactive demo."""

from zomi_nlp import ZomiPipeline

def interactive_demo():
    nlp = ZomiPipeline()
    print("Zomi NLP Interactive Demo (type 'quit' to exit)")
    print("-" * 40)
    
    while True:
        text = input("\n📝 Enter Zomi text: ").strip()
        if text.lower() in ('quit', 'exit', 'q'):
            break
        
        doc = nlp(text)
        print("\nResults:")
        for token in doc:
            print(f"  {token.text:<12} → POS: {token.pos_ or 'N/A'}, Lemma: {token.lemma_ or 'N/A'}")
        print(f"\n📊 Total tokens: {len(doc)}")

if __name__ == "__main__":
    interactive_demo()