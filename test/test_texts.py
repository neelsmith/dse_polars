import polars as pl
import pytest

from dse_polars.texts import ctsurn_contains


def _eval_expr(u1: str, u2: str) -> bool:
    df = pl.DataFrame({"u1": [u1], "u2": [u2]})
    return df.select(ctsurn_contains(pl.col("u1"), pl.col("u2")).alias("ok")).item(0, 0)


@pytest.mark.parametrize(
    "u1,u2,expected",
    [
        (
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            True,
        ),
        (
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            "urn:cts:compnov:bible.genesis.sept_latin:1",
            True,
        ),
        (
            "urn:cts:compnov:bible.genesis.sept_latin:1",
            "urn:cts:compnov:bible.genesis:1",
            True,
        ),
        (
            "urn:cts:compnov:bible.genesis:1",
            "urn:cts:compnov:bible.genesis.sept_latin:1",
            True,
        ),
        (
            "urn:cts:compnov:bible.genesis.sept_latin:1",
            "urn:cts:compnov:bible.genesis.targum_latin:1",
            False,
        ),
        (
            "urn:cts:compnov:bible.genesis:1.1",
            "urn:cts:compnov:bible.exodus:1.1",
            False,
        ),
        (
            "urn:cts:compnov:bible.genesis:10.1",
            "urn:cts:compnov:bible.genesis:1",
            False,
        ),
        (
            "urn:cts:compnov:bible.genesis:1",
            "urn:cts:compnov:bible.genesis:",
            True,
        ),
    ],
)
def test_ctsurn_contains_expr_semantics(u1: str, u2: str, expected: bool):
    assert _eval_expr(u1, u2) is expected


def test_ctsurn_contains_mixed_expr_and_literal_inputs():
    df = pl.DataFrame(
        {
            "urn": [
                "urn:cts:compnov:bible.genesis.sept_latin:1.1",
                "urn:cts:compnov:bible.exodus.sept_latin:1.1",
            ]
        }
    )

    result = df.select(
        ctsurn_contains(pl.col("urn"), "urn:cts:compnov:bible.genesis:1").alias("ok")
    )

    assert result["ok"].to_list() == [True, False]


def test_ctsurn_contains_literal_inputs_in_select():
    actual = pl.select(
        ctsurn_contains(
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            "urn:cts:compnov:bible.genesis:1",
        ).alias("ok")
    ).item(0, 0)

    assert actual is True
