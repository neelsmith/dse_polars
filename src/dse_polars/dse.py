
#from copy import replace
import polars as pl

from .urnutils import passagecomponent_re

class DSE:
    def __init__(self, data):
        "Enforce DSE schema for dataframe."
        self.df = pl.DataFrame(data, schema={
            "passage": pl.String,
            "image": pl.String,
            "surface": pl.String
        })

    
    
    def surfaces(self):
        "Find unique list of surface references."
        return self.df.select("surface").unique()

    def images(self):
        "Find unique list of image references after dropping ROI values)."
        wholeimages = self.df.with_columns(
            drop_roi().alias("image")).select("image")
        return wholeimages.unique()
    
    def texts(self):
        "Find unique list of passage references after dropping subrefs and matching to standard format."
        texturns = self.df.with_columns(
            droppassage_expr().alias("passage")
        ).select("passage")
        return texturns.unique()
    
    #S for I
    #S for P
    def surfacesforimage(self, image):
        "Find unique list of surface references for a given image."
        normalized_image = (
            pl.DataFrame({"image": [image]})
            .with_columns(drop_roi().alias("image"))
            .item(0, 0)
        )
        surfaces = self.df.filter(drop_roi() == normalized_image).select("surface")
        return surfaces.unique()

    def surfacesforpassage(self, passage):
        "Find surface references for a given passage."
        surfaces = self.df.filter(pl.col("passage") == passage).select("surface")
        return surfaces    


    #I for S
    #I for P
    
    def imagesforpassage(self, passage):
        "Find image reference for a given passage."
        images = self.df.filter(pl.col("passage") == passage).select("image")
        return images
    
    def imagesforsurface(self, surface):
        "Find unique list of image references for a given surface."
        wholeimages = self.df.filter(pl.col("surface") == surface).with_columns(
            drop_roi().alias("image")).select("image")
        return wholeimages.unique()    
    
    #P for S
    #P for I
    def passagesforsurface(self, surface):
        "Find unique list of passage references for a given surface."
        passages = self.df.filter(pl.col("surface") == surface).with_columns(
            pl.col("passage")).select("passage")
        return passages.unique()
    
    def passagesforimage(self, image):
        "Find unique list of passage references for a given image."
        normalized_image = (
            pl.DataFrame({"image": [image]})
            .with_columns(drop_roi().alias("image"))
            .item(0, 0)
        )
        passages = self.df.filter(drop_roi() == normalized_image).select("passage")
        return passages.unique()

def drop_roi():
    """Returns a Polars expression that drops subreferences from `image`."""
    return pl.col("image").str.replace(r"@.*", "")


def drop_subref():
    """Backward-compatible alias for dropping subreferences from `image`."""
    return drop_roi()


def match_passage(s: str) -> str:
    """Normalize a passage string to lowercase and trimmed form."""
    return s.strip().lower()


def droppassage_expr():
    """Returns a Polars expression to drop passage components from `passage`."""
    return pl.col("passage").str.replace(passagecomponent_re, ":")


