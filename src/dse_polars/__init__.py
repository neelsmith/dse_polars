from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dse_polars") # 'name' of package from pyproject.toml
except PackageNotFoundError:
    # Package is not installed (e.g., running from a local script)
    __version__ = "unknown"

#

#__all__ = ["Urn", "CtsUrn", "Cite2Urn"]