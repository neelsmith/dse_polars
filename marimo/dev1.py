# /// script
# dependencies = [
#     "marimo",
#     "polars==1.38.1",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Polars basics with DSE data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Essential imports
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Create a DSE object

    Create a DSE object from a dataframe with required schema (columns `image`, `passage` and `surface`):
    """)
    return


@app.cell
def _(DSE, lxxdf):
    lxx = DSE(lxxdf)
    return (lxx,)


@app.cell
def _(DSE, targumdf):
    targum = DSE(targumdf)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Inventory of contents
    Get URN-aware inventory of unique surfaces, images and texts:
    """)
    return


@app.cell
def _(lxx):
    lxx.texts()
    return


@app.cell
def _(lxx):
    lxx.images()
    return


@app.cell
def _(lxx):
    lxx.surfaces()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The 6 basic relations

    Text, image, surface each relate to the other two.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Relations from surface
    """)
    return


@app.cell
def _():
    surf = "urn:cite2:complut:pages.bne:vol1_e_1r"
    return (surf,)


@app.cell
def _(lxx, surf):
    lxx.imagesforsurface(surf)
    return


@app.cell
def _(lxx, surf):
    lxx.passagesforsurface(surf)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Relations from image
    """)
    return


@app.cell
def _():
    img = "urn:cite2:citebne:complutensian.v1:v1p67"
    return (img,)


@app.cell
def _(img, lxx):
    lxx.surfacesforimage(img)
    return


@app.cell
def _(img, lxx):
    lxx.passagesforimage(img)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Relations from text passage
    """)
    return


@app.cell
def _():
    psg = "urn:cts:compnov:bible.genesis.sept_latin:21.8"
    return (psg,)


@app.cell
def _(lxx, psg):
    lxx.surfacesforpassage(psg)
    return


@app.cell
def _(lxx, psg):
    lxx.imagesforpassage(psg)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.Html("<br/><br/><br/><br/><br/><br/><br/><br/><br/><hr/>")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Load data
    """)
    return


@app.cell
def _(lxxfile, pl):
    lxxdf =  pl.read_csv( lxxfile, separator="|")
    return (lxxdf,)


@app.cell
def _(pl, targumfile):
    targumdf = pl.read_csv(targumfile, separator="|")
    return (targumdf,)


@app.cell
def _(mo):
    datadir = mo.notebook_dir().parent / "test" / "data"
    return (datadir,)


@app.cell
def _(datadir):
    targumfile = str(datadir / "targum_latin_genesis_dse.cex")
    return (targumfile,)


@app.cell
def _(datadir):
    lxxfile = str(datadir / "septuagint_latin_genesis_dse.cex")
    return (lxxfile,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Imports
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    import sys
    repo = mo.notebook_dir().parent
    src_dir = str(repo / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from dse_polars import DSE

    return (DSE,)


if __name__ == "__main__":
    app.run()
