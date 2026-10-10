"""A custom ML autoresearch harness: an empirical propose→run→evaluate→improve loop."""
from .researcher import Researcher
from .experiment import run_candidate
__all__ = ["Researcher", "run_candidate"]
__version__ = "0.1.0"
