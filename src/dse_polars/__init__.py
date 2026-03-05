from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dse_polars") # 'name' of package from pyproject.toml
except PackageNotFoundError:
    # Package is not installed (e.g., running from a local script)
    __version__ = "unknown"

from .dse import DSE
from .texts import DSEPassages, ctsurn_contains, retrieve_leafnode_range, textcontents
from .images import CitableIIIFService, roi, strip_roi, ptinrect, rois
from .urnutils import passagecomponent_re

__all__ = [
    "DSE",
    "passagecomponent_re",
    "DSEPassages",
    "ctsurn_contains",
    "retrieve_leafnode_range",
    "textcontents",
    "CitableIIIFService",
    "roi",
    "strip_roi",
    "ptinrect",
    "rois",
]