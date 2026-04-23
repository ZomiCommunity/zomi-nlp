"""Helper utilities for Zomi NLP."""

import contextlib
import subprocess
import sys
from importlib.util import find_spec
from typing import Optional


def download_model(model_name: str, backend: str = "auto") -> bool:
    """Download a model for a specific backend.

    Args:
        model_name: Name of the model to download
        backend: "spacy", "stanza", or "auto"

    Returns:
        bool: True if successful

    Example:
        >>> from zomi_nlp.utils import download_model
        >>> download_model("en_core_web_sm", backend="spacy")
    """
    if backend == "spacy" or (backend == "auto" and _is_spacy_available()):
        return _download_spacy_model(model_name)
    elif backend == "stanza" or (backend == "auto" and _is_stanza_available()):
        return _download_stanza_model(model_name)
    else:
        print(f"❌ Backend '{backend}' not available")
        return False


def _is_spacy_available() -> bool:
    return find_spec("spacy") is not None

def _is_stanza_available() -> bool:
    return find_spec("stanza") is not None

def _download_spacy_model(model_name: str) -> bool:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", model_name],
            stdout=subprocess.DEVNULL
        )
        print(f"✅ Downloaded {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download {model_name}: {e}")
        return False


def _download_stanza_model(lang: str) -> bool:
    try:
        import stanza
        stanza.download(lang)
        print(f"✅ Downloaded stanza model for {lang}")
        return True
    except ImportError as e:
        print(f"❌ Failed to download stanza model for {lang}: {e}")
        return False


def get_model_info(model_name: str) -> Optional[dict]:
    """Get information about a model.

    Args:
        model_name: Name of the model

    Returns:
        Dictionary with model info or None if not found
    """
    # Check spaCy models
    try:
        import spacy
        try:
            nlp = spacy.load(model_name)
            return {
                "backend": "spacy",
                "name": model_name,
                "lang": nlp.lang,
                "pipeline": nlp.pipeline_names, # type: ignore[attr-defined]
                "vectors": nlp.vocab.vectors_length if nlp.vocab.vectors_length else None
            }
        except OSError as e:
            print(f"❌ Error loading spaCy model '{model_name}': {e}")
    except ImportError as e:
        print(f"❌ spaCy not available: {e}")

    return None


def list_available_models() -> list[str]:
    """List all available models for Zomi NLP.

    Returns:
        List of model names

    Example:
        >>> from zomi_nlp.utils import list_available_models
        >>> models = list_available_models()
        >>> print(models)
    """
    models = []

    # Check spaCy models
    try:
        # This is simplified - real implementation would check installed models
        models.append("en_core_web_sm")
        models.append("en_core_web_md")
        models.append("en_core_web_lg")
    except Exception:
        pass

    # Check stanza models
    with contextlib.suppress(BaseException):
        models.append("stanza_en")
    return models
