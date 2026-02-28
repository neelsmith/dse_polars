from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dse_polars") # 'name' of package from pyproject.toml
except PackageNotFoundError:
    # Package is not installed (e.g., running from a local script)
    __version__ = "unknown"

from .dse import DSE
from .texts import DSEPassages, ctsurn_contains
from .images import CitableIIIFService, urn2info_url, info_url2urn, roi, strip_roi, ptinrect, rois, urn2image_url
from .urnutils import passagecomponent_re

__all__ = ["DSE", 
           "passagecomponent_re",
           "DSEPassages",
           "ctsurn_contains",
         
                 
           "CitableIIIFService",
           "urn2info_url",
           "info_url2urn",
           "roi","strip_roi",
            "ptinrect",
            "rois",
            "urn2image_url"
        ]   