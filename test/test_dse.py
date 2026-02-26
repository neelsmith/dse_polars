from pathlib import Path

import polars as pl
import pytest

from dse_polars.dse import DSE
from dse_polars.urnutils import passagecomponent_re


DATA_DIR = Path(__file__).parent / "data"
DATA_FILES = [
    DATA_DIR / "septuagint_latin_genesis_dse.cex",
    DATA_DIR / "targum_latin_genesis_dse.cex",
]


def _load_df(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, separator="|")

def _assert_same_values(actual: pl.DataFrame, expected: pl.DataFrame, column: str) -> None:
    assert set(actual[column].to_list()) == set(expected[column].to_list())

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_surfaces(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    actual = dse.surfaces()
    expected = df.select("surface").unique()
    _assert_same_values(actual, expected, "surface")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_images_drops_roi(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    actual = dse.images()
    expected = (
        df.with_columns(pl.col("image").str.replace(r"@.*", "").alias("image"))
        .select("image")
        .unique()
    )
    _assert_same_values(actual, expected, "image")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_texts_drops_passage_component(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    actual = dse.texts()
    expected = (
        df.with_columns(pl.col("passage").str.replace(passagecomponent_re, ":").alias("passage"))
        .select("passage")
        .unique()
    )
    _assert_same_values(actual, expected, "passage")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_surfacesforimage_accepts_roi_image(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    image_with_roi = df["image"][0]
    normalized = image_with_roi.split("@", 1)[0]

    actual = dse.surfacesforimage(image_with_roi)
    expected = (
        df.with_columns(pl.col("image").str.replace(r"@.*", "").alias("image"))
        .filter(pl.col("image") == normalized)
        .select("surface")
        .unique()
    )
    _assert_same_values(actual, expected, "surface")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_surfacesforpassage(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    passage = df["passage"][0]

    actual = dse.surfacesforpassage(passage)
    expected = df.filter(pl.col("passage") == passage).select("surface")
    _assert_same_values(actual, expected, "surface")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_imagesforpassage(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    passage = df["passage"][0]

    actual = dse.imagesforpassage(passage)
    expected = df.filter(pl.col("passage") == passage).select("image")
    _assert_same_values(actual, expected, "image")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_imagesforsurface(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    surface = df["surface"][0]

    actual = dse.imagesforsurface(surface)
    expected = (
        df.filter(pl.col("surface") == surface)
        .with_columns(pl.col("image").str.replace(r"@.*", "").alias("image"))
        .select("image")
        .unique()
    )
    _assert_same_values(actual, expected, "image")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_passagesforsurface(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    surface = df["surface"][0]

    actual = dse.passagesforsurface(surface)
    expected = df.filter(pl.col("surface") == surface).select("passage").unique()
    _assert_same_values(actual, expected, "passage")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_passagesforimage_accepts_roi_image(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    image_with_roi = df["image"][0]
    normalized = image_with_roi.split("@", 1)[0]

    actual = dse.passagesforimage(image_with_roi)
    expected = (
        df.with_columns(pl.col("image").str.replace(r"@.*", "").alias("image"))
        .filter(pl.col("image") == normalized)
        .select("passage")
        .unique()
    )
    _assert_same_values(actual, expected, "passage")
