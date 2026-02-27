import polars as pl
import pytest

from dse_polars.images import CitableIIIFService, info_url2urn, roi, strip_roi, urn2info_url


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
