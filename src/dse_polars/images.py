from dataclasses import dataclass
import polars as pl

@dataclass
class CitableIIIFService:
    urlbase: str
    extension: str

    def urn2image_url(self, urn: str) -> str:
        "Form a IIIF image request URL from a CITE2 URN."
        base_urn = urn
        region = "full"

        parts = urn.rsplit("@", 1)
        if len(parts) == 2:
            candidate_region = parts[1]
            region_parts = candidate_region.split(",")
            if len(region_parts) == 4 and all(part != "" for part in region_parts):
                base_urn = parts[0]
                region = candidate_region

        return self.urn2info_url(base_urn).replace(
            "/info.json", f"/{region}/full/0/default.{self.extension}"
        )

    def urn2info_url(self, urn: str) -> str:
        _, _, ns, collection, objectcomponent = urn.split(":")
        collectionid, collectionversion = collection.split(".")
        return (
            self.urlbase
            + ns
            + "/"
            + collectionid
            + "/"
            + collectionversion
            + "/"
            + objectcomponent
            + "."
            + self.extension
            + "/info.json"
        )

    def info_url2urn(self, url: str) -> str:
        strip1 = url.replace(self.urlbase, "")
        ns, coll, vers, imgid, _ = strip1.split("/")
        suffix = f".{self.extension}"
        objid = imgid.removesuffix(suffix)
        return "urn:cite2:" + ns + ":" + coll + "." + vers + ":" + objid



def rois(df: pl.DataFrame):
    "Return a python list of all ROIs in the dataframe, as strings."
    return df.select("roi").filter(pl.col("roi").is_not_null()).to_series().to_list()

def roi(imgurn: pl.Expr | str) -> pl.Expr:
    "Polars expression to extract the ROI from an image URN, or empty string if no ROI."
    expr = imgurn if isinstance(imgurn, pl.Expr) else pl.lit(imgurn)
    return expr.str.extract(r"@(.*)$", 1).fill_null("")


def strip_roi(imgurn: pl.Expr | str) -> pl.Expr:
    "Polars expression to strip the ROI from an image URN, returning the base URN."
    expr = imgurn if isinstance(imgurn, pl.Expr) else pl.lit(imgurn)
    return expr.str.replace(r"@.*", "")


def ptinrect(x: float |  pl.Expr, y: float | pl.Expr) -> pl.Expr:
    "Polars expression to check if a point (x,y) is inside a rectangle defined by columns x,y,w,h; bounds are inclusive and null rectangle values evaluate to False."
    x_expr = x if isinstance(x, pl.Expr) else pl.lit(x)
    y_expr = y if isinstance(y, pl.Expr) else pl.lit(y)
    return (
        (x_expr >= pl.col("x"))
        & (x_expr <= (pl.col("x") + pl.col("w")))
        & (y_expr >= pl.col("y"))
        & (y_expr <= (pl.col("y") + pl.col("h")))
    ).fill_null(False)