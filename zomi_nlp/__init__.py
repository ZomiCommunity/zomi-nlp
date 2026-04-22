"""Zomi NLP - Natural Language Processing for Zomi Language."""

from zomi_nlp.config import ZomiConfig
from zomi_nlp.pipeline.orchestrator import ZomiPipeline

# Import convenience utilities
from zomi_nlp.utils.installation import (
    auto_install_recommended,
    check_installation,
    install_spacy_model,
    install_stanza_model,
)
from zomi_nlp.version import __version__

__all__ = [
    "ZomiPipeline",
    "ZomiConfig",
    "__version__",
    "install_spacy_model",
    "install_stanza_model",
    "check_installation",
    "auto_install_recommended"
]


def load(model: str = "auto", **kwargs):
    """Load a Zomi NLP pipeline."""
    config = ZomiConfig(model_name=model, **kwargs)
    return ZomiPipeline(config)


# Optional: Auto-check on import (disabled by default)
# Uncomment if you want users to see status when importing
# if not check_installation(verbose=False)[0]:
#     import warnings
#     warnings.warn(
#         "Zomi NLP: No backend installed. "
#         "Run 'from zomi_nlp import auto_install_recommended; auto_install_recommended()'",
#         UserWarning
#     )
