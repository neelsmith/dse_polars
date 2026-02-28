import polars as pl
import pytest

from dse_polars.images import (
    CitableIIIFService,
    info_url2urn,
    ptinrect,
    rois,
    roi,
    strip_roi,
    urn2image_url,
    urn2info_url,
)


@pytest.fixture
def iiif_service() -> CitableIIIFService:
    return CitableIIIFService(
        urlbase="https://images.example.org/iiif/",
        extension="jpg",
    )


def test_citable_iiif_service_dataclass_fields(iiif_service: CitableIIIFService):
    assert iiif_service.urlbase == "https://images.example.org/iiif/"
    assert iiif_service.extension == "jpg"


def test_urn2info_url(iiif_service: CitableIIIFService):
    urn = "urn:cite2:hmt:vaimg.2017a:VA012RN_0013"
    actual = urn2info_url(urn, iiif_service)
    expected = (
        "https://images.example.org/iiif/hmt/vaimg/2017a/"
        "VA012RN_0013.jpg/info.json"
    )
    assert actual == expected


def test_urn2image_url_without_roi(iiif_service: CitableIIIFService):
    urn = "urn:cite2:hmt:vaimg.2017a:VA012RN_0013"
    actual = urn2image_url(urn, iiif_service)
    expected = (
        "https://images.example.org/iiif/hmt/vaimg/2017a/"
        "VA012RN_0013.jpg/full/full/0/default.jpg"
    )
    assert actual == expected


def test_urn2image_url_with_roi_uses_region(iiif_service: CitableIIIFService):
    urn = "urn:cite2:hmt:vaimg.2017a:VA012RN_0013@10,20,30,40"
    actual = urn2image_url(urn, iiif_service)
    expected = (
        "https://images.example.org/iiif/hmt/vaimg/2017a/"
        "VA012RN_0013.jpg/10,20,30,40/full/0/default.jpg"
    )
    assert actual == expected


def test_urn2image_url_malformed_roi_falls_back_to_full(iiif_service: CitableIIIFService):
    urn = "urn:cite2:hmt:vaimg.2017a:VA012RN_0013@10,20,30"
    actual = urn2image_url(urn, iiif_service)
    expected = (
        "https://images.example.org/iiif/hmt/vaimg/2017a/"
        "VA012RN_0013@10,20,30.jpg/full/full/0/default.jpg"
    )
    assert actual == expected


def test_info_url2urn(iiif_service: CitableIIIFService):
    url = "https://images.example.org/iiif/hmt/vaimg/2017a/VA012RN_0013.jpg/info.json"
    actual = info_url2urn(url, iiif_service)
    assert actual == "urn:cite2:hmt:vaimg.2017a:VA012RN_0013"


def test_urn_info_url_round_trip(iiif_service: CitableIIIFService):
    urn = "urn:cite2:hmt:vaimg.2017a:VA012RN_0013"
    url = urn2info_url(urn, iiif_service)
    assert info_url2urn(url, iiif_service) == urn


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


def test_ptinrect_literal_point_inclusive_bounds():
    df = pl.DataFrame({"x": [10.0], "y": [20.0], "w": [30.0], "h": [40.0]})
    actual = df.select(
        ptinrect(10.0, 20.0).alias("at_top_left"),
        ptinrect(40.0, 60.0).alias("at_bottom_right"),
        ptinrect(25.0, 35.0).alias("inside"),
    )

    assert actual.item(0, 0) is True
    assert actual.item(0, 1) is True
    assert actual.item(0, 2) is True


def test_ptinrect_literal_point_outside():
    df = pl.DataFrame({"x": [10.0], "y": [20.0], "w": [30.0], "h": [40.0]})
    actual = df.select(
        ptinrect(9.9, 20.0).alias("left"),
        ptinrect(40.1, 20.0).alias("right"),
        ptinrect(10.0, 19.9).alias("above"),
        ptinrect(10.0, 60.1).alias("below"),
    )

    assert actual.item(0, 0) is False
    assert actual.item(0, 1) is False
    assert actual.item(0, 2) is False
    assert actual.item(0, 3) is False


def test_ptinrect_expr_inputs():
    df = pl.DataFrame(
        {
            "x": [0.0, 5.0],
            "y": [0.0, 5.0],
            "w": [10.0, 2.0],
            "h": [10.0, 2.0],
            "px": [7.0, 8.5],
            "py": [7.0, 6.0],
        }
    )
    actual = df.select(ptinrect(pl.col("px"), pl.col("py")).alias("ok"))["ok"].to_list()
    assert actual == [True, False]


def test_ptinrect_null_rectangle_values_return_false():
    df = pl.DataFrame(
        {
            "x": [None],
            "y": [20.0],
            "w": [30.0],
            "h": [40.0],
        },
        schema={"x": pl.Float64, "y": pl.Float64, "w": pl.Float64, "h": pl.Float64},
    )
    actual = df.select(ptinrect(25.0, 35.0).alias("ok")).item(0, 0)
    assert actual is False


def test_rois_filters_null_values_and_preserves_order():
    df = pl.DataFrame(
        {
            "roi": [
                "10,20,30,40",
                None,
                "5,6,7,8",
                "10,20,30,40",
                None,
            ]
        },
        schema={"roi": pl.String},
    )
    actual = rois(df)
    assert actual == ["10,20,30,40", "5,6,7,8", "10,20,30,40"]


def test_rois_returns_empty_list_when_all_null():
    df = pl.DataFrame({"roi": [None, None]}, schema={"roi": pl.String})
    actual = rois(df)
    assert actual == []
