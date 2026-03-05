
#from copy import replace
import polars as pl
import itertools
from cite_exchange import CexBlock

from .urnutils import passagecomponent_re

class DSE:
    def __init__(self, data):
        "Enforce DSE schema for dataframe."
        base_df = pl.DataFrame(data, schema={
            "passage": pl.String,
            "image": pl.String,
            "surface": pl.String
        })

        parts = pl.col("image").str.split_exact("@", 1)
        passage_parts = pl.col("passage").str.split_exact(":", 4)
        passage_work_parts = passage_parts.struct.field("field_3").str.split_exact(".", 2)
        roi_parts = pl.col("roi").str.split_exact(",", 3)
        try:
            self.df = base_df.with_columns(
                parts.struct.field("field_0").alias("wholeimage"),
                parts.struct.field("field_1").alias("roi"),
                passage_parts.struct.field("field_4").alias("passageref"),
                passage_work_parts.struct.field("field_0").alias("group"),
                passage_work_parts.struct.field("field_1").alias("work"),
                passage_work_parts.struct.field("field_2").alias("version"),
            ).with_columns(
                pl.when(pl.col("roi").is_not_null())
                .then(roi_parts.struct.field("field_0").cast(pl.Float64, strict=True))
                .otherwise(None)
                .alias("x"),
                pl.when(pl.col("roi").is_not_null())
                .then(roi_parts.struct.field("field_1").cast(pl.Float64, strict=True))
                .otherwise(None)
                .alias("y"),
                pl.when(pl.col("roi").is_not_null())
                .then(roi_parts.struct.field("field_2").cast(pl.Float64, strict=True))
                .otherwise(None)
                .alias("w"),
                pl.when(pl.col("roi").is_not_null())
                .then(roi_parts.struct.field("field_3").cast(pl.Float64, strict=True))
                .otherwise(None)
                .alias("h")
            )
        except pl.exceptions.PolarsError as exc:
            raise ValueError(
                "Invalid ROI in image value: ROI must have four comma-separated numeric values (x,y,w,h)."
            ) from exc

        invalid_roi_rows = self.df.filter(
            pl.col("roi").is_not_null()
            & (
                pl.col("x").is_null()
                | pl.col("y").is_null()
                | pl.col("w").is_null()
                | pl.col("h").is_null()
            )
        )
        if invalid_roi_rows.height > 0:
            raise ValueError(
                "Invalid ROI in image value: ROI must have four comma-separated numeric values (x,y,w,h)."
            )

    @classmethod
    def from_cex_file(cls, cexfile: str):
        with open(cexfile, encoding="utf-8") as f:
            cex_text = f.read()
        return cls.from_cex_text(cex_text)

    @staticmethod
    def get_dse_urns(cex_text: str):
        "Extract DSE URNs from CEX data."
        modelurn = "urn:cite2:cite:datamodels.v1:dsemodel"
        modelblocks = CexBlock.from_text(cex_text, label = "datamodels")
        nested = [dm.data for dm in modelblocks]
        flattened = list(itertools.chain.from_iterable(nested) )
        dsecollections = [row for row in flattened if modelurn in row]
        dseurns = [row.split("|")[0] for row in dsecollections]
        return dseurns
    

    @classmethod
    def from_cex_text(cls, cex_text: str):
        "Create DSE from CEX data."
        dseurns = cls.get_dse_urns(cex_text)

        allrelationblocks = CexBlock.from_text(cex_text, label = "citerelationset")
        dseblocks = [blk.data[3:] for blk in allrelationblocks if blk.data[0].replace('urn|','') in dseurns]
        flattened = list(itertools.chain.from_iterable(dseblocks))
        rows = [row for row in flattened if row.strip()]

        if not rows:
            return cls({"passage": [], "image": [], "surface": []})

        parsed_rows = []
        for row in rows:
            columns = row.split("|")
            if len(columns) != 3:
                raise ValueError(
                    "Invalid DSE relation row in CEX: expected 3 pipe-delimited fields (passage|image|surface)."
                )
            parsed_rows.append(columns)

        dse_df = pl.DataFrame(parsed_rows, schema=["passage", "image", "surface"], orient="row")
        return cls(dse_df)
    


        


    # Inventory functions:
    def surfaces(self):
        "Find unique list of surface references."
        return self.df.select("surface").unique(maintain_order=True)

    def images(self):
        "Find unique list of image references after dropping ROI values)."
        wholeimages = self.df.select(pl.col("wholeimage").alias("image"))
        return wholeimages.unique(maintain_order=True)
    
    def texts(self):
        "Find unique list of passage references after dropping subrefs and matching to standard format."
        texturns = self.df.with_columns(
            droppassage_expr().alias("passage")
        ).select("passage")
        return texturns.unique(maintain_order=True)
    

    #
    # DSE selection functions:
    #
    
    

    #S for I
    #S for P
    def surfacesforimage(self, image):
        "Find unique list of surface references for a given image."
        normalized_image = image.split("@", 1)[0]
        surfaces = self.df.filter(pl.col("wholeimage") == normalized_image).select("surface")
        return surfaces.unique(maintain_order=True)

    def surfacesforpassage(self, passage):
        "Find surface references for a given passage."
        surfaces = self.df.filter(pl.col("passage") == passage).select("surface")
        return surfaces    


    #I for S
    #I for P  
    def imagesforpassage(self, passage):
        "Find image references for a given passage."
        images = self.df.filter(pl.col("passage") == passage).select("image")
        return images
    
    def imagesforsurface(self, surface):
        "Find image references for a given surface."
        images = self.df.filter(pl.col("surface") == surface).select("image")
        return images
    
    # Whole I for S
    # Whole I for P
    def wholeimagesforsurface(self, surface):
        "Find unique list of whole image references for a given surface."
        wholeimages = self.df.filter(pl.col("surface") == surface).select("wholeimage")
        return wholeimages.unique(maintain_order=True)
    def wholeimagesforpassage(self, passage):
        "Find unique list of whole image references for a given passage."
        wholeimages = self.df.filter(pl.col("passage") == passage).select("wholeimage")
        return wholeimages.unique(maintain_order=True)
    
    def rectsforsurface(self, surface):
        "Find unique list of rectangles for a given surface."
        rects = self.df.filter(pl.col("surface") == surface).select(
            pl.struct(["x", "y", "w", "h"]).alias("rect")
        )
        return rects.unique(maintain_order=True)
    
    #P for S
    #P for I
    def passagesforsurface(self, surface):
        "Find unique list of passage references for a given surface."
        passages = self.df.filter(pl.col("surface") == surface).with_columns(
            pl.col("passage")).select("passage")
        return passages.unique(maintain_order=True)
    
    def passagesforimage(self, image):
        "Find unique list of passage references for a given image."
        passages = self.df.filter(pl.col("wholeimage") == image).select("passage")
        return passages


def droppassage_expr():
    """Returns a Polars expression to drop passage components from `passage`."""
    return pl.col("passage").str.replace(passagecomponent_re, ":")


