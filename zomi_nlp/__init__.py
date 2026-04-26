# zomi_nlp/__init__.py
"""Zomi NLP - Natural Language Processing for Zomi Language."""

from zomi_nlp.config import ZomiConfig
from zomi_nlp.native import ZomiParserV362, ZomiRuleBasedParser  # Expose native parser
from zomi_nlp.pipeline.orchestrator import ZomiPipeline
from zomi_nlp.utils.installation import (  # Import convenience utilities
    auto_install_recommended,
    check_installation,
    check_spacy_model,
    get_installation_advice,
    get_installation_status,
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
    "get_installation_status",
    "get_installation_advice",
    "check_spacy_model",
    "auto_install_recommended",
    "ZomiParserV362",
    "ZomiRuleBasedParser",
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
