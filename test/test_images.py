import polars as pl
import pytest

from dse_polars.images import roi, strip_roi


@pytest.mark.parametrize(
    "imgurn,expected",
    [
        (
            "urn:cite2:demo:img.v1:abc123@10,20,30,40",
            "10,20,30,40",
        ),
        (
            "urn:cite2:demo:img.v1:abc123",
            "",
        ),
    ],
)
def test_roi_expr(imgurn: str, expected: str):
    df = pl.DataFrame({"image": [imgurn]})
    actual = df.select(roi(pl.col("image")).alias("roi")).item(0, 0)
    assert actual == expected


def test_roi_literal_input():
    actual = pl.select(
        roi("urn:cite2:demo:img.v1:abc123@1,2,3,4").alias("roi")
    ).item(0, 0)
    assert actual == "1,2,3,4"


@pytest.mark.parametrize(
    "imgurn,expected",
    [
        (
            "urn:cite2:demo:img.v1:abc123@10,20,30,40",
            "urn:cite2:demo:img.v1:abc123",
        ),
        (
            "urn:cite2:demo:img.v1:abc123",
            "urn:cite2:demo:img.v1:abc123",
        ),
    ],
)
def test_strip_roi_expr(imgurn: str, expected: str):
    df = pl.DataFrame({"image": [imgurn]})
    actual = df.select(strip_roi(pl.col("image")).alias("image")).item(0, 0)
    assert actual == expected


def test_strip_roi_literal_input():
    actual = pl.select(
        strip_roi("urn:cite2:demo:img.v1:abc123@1,2,3,4").alias("image")
    ).item(0, 0)
    assert actual == "urn:cite2:demo:img.v1:abc123"
