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


def test_init_adds_image_part_columns():
    dse = DSE(
        {
            "passage": ["urn:cts:foo:bar:1.1", "urn:cts:foo:bar:1.2"],
            "image": ["urn:cite2:img:collection.v1:img1@10,20,30,40", "urn:cite2:img:collection.v1:img2"],
            "surface": ["urn:cite2:surf:collection.v1:s1", "urn:cite2:surf:collection.v1:s2"],
        }
    )

    assert dse.df.columns == ["passage", "image", "surface", "wholeimage", "roi", "x", "y", "w", "h"]
    assert dse.df["wholeimage"].to_list() == [
        "urn:cite2:img:collection.v1:img1",
        "urn:cite2:img:collection.v1:img2",
    ]
    assert dse.df["roi"].to_list() == ["10,20,30,40", None]
    assert dse.df["x"].to_list() == [10.0, None]
    assert dse.df["y"].to_list() == [20.0, None]
    assert dse.df["w"].to_list() == [30.0, None]
    assert dse.df["h"].to_list() == [40.0, None]


def test_init_rejects_roi_with_wrong_arity():
    with pytest.raises(ValueError, match="ROI must have four comma-separated numeric values"):
        DSE(
            {
                "passage": ["urn:cts:foo:bar:1.1"],
                "image": ["urn:cite2:img:collection.v1:img1@10,20,30"],
                "surface": ["urn:cite2:surf:collection.v1:s1"],
            }
        )


def test_init_rejects_non_numeric_roi_values():
    with pytest.raises(ValueError, match="ROI must have four comma-separated numeric values"):
        DSE(
            {
                "passage": ["urn:cts:foo:bar:1.1"],
                "image": ["urn:cite2:img:collection.v1:img1@10,abc,30,40"],
                "surface": ["urn:cite2:surf:collection.v1:s1"],
            }
        )

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
    expected = df.filter(pl.col("surface") == surface).select("image")
    _assert_same_values(actual, expected, "image")


@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_wholeimagesforsurface(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    surface = df["surface"][0]

    actual = dse.wholeimagesforsurface(surface)
    expected = (
        df.filter(pl.col("surface") == surface)
        .with_columns(pl.col("image").str.replace(r"@.*", "").alias("wholeimage"))
        .select("wholeimage")
        .unique()
    )
    _assert_same_values(actual, expected, "wholeimage")


@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_wholeimagesforpassage(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    passage = df["passage"][0]

    actual = dse.wholeimagesforpassage(passage)
    expected = (
        df.filter(pl.col("passage") == passage)
        .with_columns(pl.col("image").str.replace(r"@.*", "").alias("wholeimage"))
        .select("wholeimage")
        .unique()
    )
    _assert_same_values(actual, expected, "wholeimage")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_passagesforsurface(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    surface = df["surface"][0]

    actual = dse.passagesforsurface(surface)
    expected = df.filter(pl.col("surface") == surface).select("passage").unique()
    _assert_same_values(actual, expected, "passage")

@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_passagesforimage_accepts_wholeimage(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    image_with_roi = df["image"][0]
    normalized = image_with_roi.split("@", 1)[0]

    actual = dse.passagesforimage(normalized)
    expected = (
        df.with_columns(pl.col("image").str.replace(r"@.*", "").alias("wholeimage"))
        .filter(pl.col("wholeimage") == normalized)
        .select("passage")
    )
    _assert_same_values(actual, expected, "passage")


@pytest.mark.parametrize("path", DATA_FILES, ids=[p.name for p in DATA_FILES])
def test_passagesforimage_with_roi_returns_empty(path: Path):
    df = _load_df(path)
    dse = DSE(df)
    image_with_roi = df["image"][0]

    actual = dse.passagesforimage(image_with_roi)

    assert actual.height == 0


def test_selector_image_vs_wholeimage_behavior():
    dse = DSE(
        {
            "passage": [
                "urn:cts:foo:bar:1.1",
                "urn:cts:foo:bar:1.2",
            ],
            "image": [
                "urn:cite2:img:collection.v1:img1@1,2,3,4",
                "urn:cite2:img:collection.v1:img1@5,6,7,8",
            ],
            "surface": [
                "urn:cite2:surf:collection.v1:s1",
                "urn:cite2:surf:collection.v1:s1",
            ],
        }
    )

    images = dse.imagesforsurface("urn:cite2:surf:collection.v1:s1")["image"].to_list()
    wholeimages = dse.wholeimagesforsurface("urn:cite2:surf:collection.v1:s1")["wholeimage"].to_list()

    assert images == [
        "urn:cite2:img:collection.v1:img1@1,2,3,4",
        "urn:cite2:img:collection.v1:img1@5,6,7,8",
    ]
    assert wholeimages == ["urn:cite2:img:collection.v1:img1"]
