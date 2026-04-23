"""Shared Stanza resources to prevent duplicate downloads."""

import logging
from typing import Any, Optional

import stanza

# Suppress stanza's verbose logging
logging.getLogger('stanza').setLevel(logging.WARNING)


class StanzaShared:
    """Singleton manager for shared Stanza pipelines."""

    _instance: Optional['StanzaShared'] = None
    _pipelines: dict[str, Any] = {}
    _downloaded: set = set()  # Track downloaded languages

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_pipeline(self, lang: str = "en", processors: str = "tokenize") -> Any:
        """Get or create a shared pipeline for specific processors."""
        key = f"{lang}_{processors}"

        if key not in self._pipelines:
            # Download once for this processor combination
            if lang not in self._downloaded:
                print(f"📦 Downloading Stanza models for {lang}...")
                stanza.download(lang)
                self._downloaded.add(lang)

            # Create pipeline with reduced verbosity
            print(f"🔧 Loading Stanza pipeline: {processors}")
            self._pipelines[key] = stanza.Pipeline(
                lang,
                processors=processors,
                use_gpu=False,
                verbose=False  # Reduce logging
            )

        return self._pipelines[key]

# Global singleton instance
_stanza_shared = StanzaShared()
