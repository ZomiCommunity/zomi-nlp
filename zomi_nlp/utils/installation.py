"""Installation helpers for Zomi NLP dependencies"""

import subprocess
import sys
from typing import Dict, Tuple
from importlib import import_module


def install_spacy_model(model_name: str = "en_core_web_sm") -> bool:
    """
    Helper to install spaCy model.
    
    Args:
        model_name: Name of spaCy model to install (default: en_core_web_sm)
    
    Returns:
        bool: True if installation successful, False otherwise
    
    Example:
        >>> from zomi_nlp.utils import install_spacy_model
        >>> install_spacy_model("en_core_web_sm")
    """
    print(f"📦 Installing spaCy model '{model_name}'...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", model_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        print(f"✅ Successfully installed {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {model_name}")
        print(f"   Try manual install: python -m spacy download {model_name}")
        return False
    except FileNotFoundError:
        print("❌ spaCy not found. Install it first: pip install spacy")
        return False


def install_stanza_model(lang: str = "en") -> bool:
    """
    Helper to install stanza model.
    
    Args:
        lang: Language code (default: en)
    
    Returns:
        bool: True if installation successful, False otherwise
    
    Example:
        >>> from zomi_nlp.utils import install_stanza_model
        >>> install_stanza_model("en")
    """
    print(f"📦 Installing stanza model for '{lang}'...")
    try:
        import stanza
        stanza.download(lang, quiet=True)
        print(f"✅ Successfully installed {lang} model")
        return True
    except ImportError:
        print("❌ stanza not found. Install it first: pip install stanza")
        return False
    except Exception as e:
        print(f"❌ Failed to install stanza model: {e}")
        return False


def check_installation(verbose: bool = True) -> Dict[str, Dict]:
    """
    Check what's installed and print recommendations.
    
    Args:
        verbose: If True, print detailed output to console
    
    Returns:
        Dict with installation status for each component
    
    Example:
        >>> from zomi_nlp.utils import check_installation
        >>> status = check_installation()
        >>> if status["spacy"]["installed"]:
        ...     print("spaCy is ready!")
    """
    status = {
        "spacy": {"installed": False, "model_available": False, "error": None},
        "stanza": {"installed": False, "model_available": False, "error": None},
        "zomi_nlp": {"version": None, "ready": False}
    }
    
    # Check zomi_nlp version
    try:
        from zomi_nlp.version import __version__
        status["zomi_nlp"]["version"] = __version__
    except ImportError:
        status["zomi_nlp"]["version"] = "unknown"
    
    # Check spaCy
    try:
        import spacy
        status["spacy"]["installed"] = True
        try:
            nlp = spacy.load("en_core_web_sm")
            status["spacy"]["model_available"] = True
        except OSError:
            status["spacy"]["error"] = "Model 'en_core_web_sm' not found"
        except Exception as e:
            status["spacy"]["error"] = str(e)
    except ImportError:
        status["spacy"]["error"] = "spaCy not installed"
    
    # Check Stanza
    try:
        import stanza
        status["stanza"]["installed"] = True
        status["stanza"]["model_available"] = True  # Stanza downloads on demand
    except ImportError:
        status["stanza"]["error"] = "stanza not installed"
    
    # Determine overall readiness
    status["zomi_nlp"]["ready"] = (
        status["spacy"]["model_available"] or 
        status["stanza"]["installed"]
    )
    
    # Print verbose output
    if verbose:
        print("\n" + "=" * 50)
        print("Zomi NLP Installation Check")
        print("=" * 50)
        print(f"📦 Zomi NLP version: {status['zomi_nlp']['version']}")
        print()
        
        # spaCy status
        if status["spacy"]["installed"]:
            if status["spacy"]["model_available"]:
                print("✅ spaCy: Installed with model")
            else:
                print("⚠️  spaCy: Installed but model missing")
                print(f"   → {status['spacy']['error']}")
                print("   → Run: from zomi_nlp.utils import install_spacy_model")
                print("         install_spacy_model()")
        else:
            print("❌ spaCy: Not installed")
            print("   → Run: pip install spacy")
        
        # Stanza status
        if status["stanza"]["installed"]:
            print("✅ stanza: Installed")
        else:
            print("❌ stanza: Not installed")
            print("   → Run: pip install stanza")
        
        print()
        print("💡 Recommendations:")
        if not status["zomi_nlp"]["ready"]:
            print("   • Install at least one backend:")
            print("     pip install 'zomi-nlp[full]'")
        elif not status["spacy"]["model_available"]:
            print("   • Download spaCy model for better performance")
        
        print("=" * 50 + "\n")
    
    return status


def get_installation_status() -> Tuple[bool, str]:
    """
    Quick check if Zomi NLP is ready to use.
    
    Returns:
        Tuple of (is_ready, message)
    
    Example:
        >>> from zomi_nlp.utils import get_installation_status
        >>> ready, msg = get_installation_status()
        >>> if not ready:
        ...     print(msg)
    """
    status = check_installation(verbose=False)
    
    if status["spacy"]["model_available"]:
        return True, "Ready with spaCy"
    elif status["stanza"]["installed"]:
        return True, "Ready with stanza"
    elif status["spacy"]["installed"]:
        return False, "spaCy installed but missing model. Run: install_spacy_model()"
    else:
        return False, "No backend installed. Run: pip install 'zomi-nlp[full]'"


def auto_install_recommended(interactive: bool = True) -> bool:
    """
    Automatically install recommended dependencies.
    
    Args:
        interactive: If True, ask for confirmation before installing
    
    Returns:
        bool: True if installation successful
    
    Example:
        >>> from zomi_nlp.utils import auto_install_recommended
        >>> auto_install_recommended()
    """
    status = check_installation(verbose=False)
    
    if status["zomi_nlp"]["ready"]:
        print("✅ Zomi NLP is already ready to use!")
        return True
    
    if interactive:
        print("\n📦 Zomi NLP needs some dependencies to work fully.")
        response = input("Install recommended packages? (y/n): ")
        if response.lower() != 'y':
            print("Skipping installation. Some features may not work.")
            return False
    
    success = True
    
    # Install spaCy if missing
    if not status["spacy"]["installed"]:
        print("\n📦 Installing spaCy...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "spacy"],
                stdout=subprocess.DEVNULL
            )
            print("✅ spaCy installed")
        except:
            print("❌ Failed to install spaCy")
            success = False
    
    # Install spaCy model
    if status["spacy"]["installed"] and not status["spacy"]["model_available"]:
        success = install_spacy_model() and success
    
    # Install stanza if missing
    if not status["stanza"]["installed"]:
        print("\n📦 Installing stanza...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "stanza"],
                stdout=subprocess.DEVNULL
            )
            print("✅ stanza installed")
        except:
            print("❌ Failed to install stanza")
            success = False
    
    if success:
        print("\n✅ Installation complete! Zomi NLP is ready.")
    else:
        print("\n⚠️  Some components failed to install. Run 'check_installation()' for details.")
    
    return success