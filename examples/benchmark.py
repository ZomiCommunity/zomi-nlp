#!/usr/bin/env python3
"""Benchmark Zomi NLP performance."""

import time
from zomi_nlp import ZomiPipeline

def benchmark():
    nlp = ZomiPipeline()
    
    # Test text
    text = "Pasian in vantung leh leitung a piangsak hi. " * 100
    
    print("Benchmarking Zomi NLP...")
    print(f"Text length: {len(text)} characters")
    
    # Warm up
    for _ in range(3):
        _ = nlp(text)
    
    # Benchmark
    start = time.perf_counter()
    doc = nlp(text)
    end = time.perf_counter()
    
    print(f"\n✅ Processed {len(doc.tokens)} tokens in {end-start:.4f}s")
    print(f"📊 Speed: {len(doc.tokens) / (end-start):.0f} tokens/second")

if __name__ == "__main__":
    benchmark()