from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dse_polars") # 'name' of package from pyproject.toml
except PackageNotFoundError:
    # Package is not installed (e.g., running from a local script)
    __version__ = "unknown"

from .dse import DSE, drop_subref, match_passage
from .urnutils import passagecomponent_re

__all__ = ["DSE", "drop_subref", "match_passage",
           "passagecomponent_re"]