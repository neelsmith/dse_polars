import polars as pl
import pytest

from dse_polars.texts import (
    DSEPassages,
    ctsurn_containedby,
    ctsurn_contains,
    md_passages,
    retrieve_leafnode_range,
    textcontents,
)


def _eval_expr(u1: str, u2: str) -> bool:
    df = pl.DataFrame({"u1": [u1], "u2": [u2]})
    return df.select(ctsurn_contains(pl.col("u1"), pl.col("u2")).alias("ok")).item(0, 0)


def test_dsepassages_init_expands_urn_parts_to_columns():
    passages = DSEPassages(
        {
            "urn": [
                "urn:cts:compnov:bible.genesis.sept_latin:1.1",
                "urn:cts:compnov:bible.genesis:2.3",
            ],
            "text": ["In principio", "Terra autem"],
        }
    )

    assert passages.df.columns == ["urn", "text", "passageref", "group", "work", "version"]
    assert passages.df["passageref"].to_list() == ["1.1", "2.3"]
    assert passages.df["group"].to_list() == ["bible", "bible"]
    assert passages.df["work"].to_list() == ["genesis", "genesis"]
    assert passages.df["version"].to_list() == ["sept_latin", None]


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


@pytest.mark.parametrize(
    "u1,u2,expected",
    [
        (
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            True,
        ),
        (
            "urn:cts:compnov:bible.genesis:1",
            "urn:cts:compnov:bible.genesis.sept_latin:1.1",
            True,
        ),
        (
            "urn:cts:compnov:bible.genesis:1",
            "urn:cts:compnov:bible.exodus:1.1",
            False,
        ),
    ],
)
def test_ctsurn_containedby_expr_semantics(u1: str, u2: str, expected: bool):
    df = pl.DataFrame({"u1": [u1], "u2": [u2]})
    actual = df.select(ctsurn_containedby(pl.col("u1"), pl.col("u2")).alias("ok")).item(0, 0)
    assert actual is expected


def test_ctsurn_containedby_matches_inverse_of_contains():
    u1 = "urn:cts:compnov:bible.genesis:1"
    u2 = "urn:cts:compnov:bible.genesis.sept_latin:1.1"

    contains_inverse = pl.select(ctsurn_contains(u2, u1).alias("ok")).item(0, 0)
    containedby = pl.select(ctsurn_containedby(u1, u2).alias("ok")).item(0, 0)

    assert containedby is contains_inverse


def test_textcontents_filters_nulls_preserves_order_and_duplicates():
    df = pl.DataFrame(
        {
            "urn": ["u1", "u2", "u3", "u4", "u5"],
            "text": ["alpha", None, "beta", "alpha", None],
        },
        schema={"urn": pl.String, "text": pl.String},
    )

    actual = textcontents(df)

    assert actual == ["alpha", "beta", "alpha"]


def test_textcontents_returns_empty_list_when_all_null():
    df = pl.DataFrame(
        {
            "urn": ["u1", "u2"],
            "text": [None, None],
        },
        schema={"urn": pl.String, "text": pl.String},
    )

    actual = textcontents(df)

    assert actual == []


def test_md_passages_formats_passage_and_text_with_default_highlighter():
    df = pl.DataFrame(
        {
            "urn": [
                "urn:cts:compnov:bible.genesis.sept_latin:1.1",
                "urn:cts:compnov:bible.genesis.sept_latin:1.2",
            ],
            "text": ["In principio", "Terra autem"],
        },
        schema={"urn": pl.String, "text": pl.String},
    )

    actual = md_passages(df)

    assert actual == ["*1.1* In principio", "*1.2* Terra autem"]


def test_md_passages_allows_custom_highlighter_and_skips_nulls():
    df = pl.DataFrame(
        {
            "urn": [
                "urn:cts:compnov:bible.genesis.sept_latin:1.1",
                "urn:cts:compnov:bible.genesis.sept_latin:1.2",
                None,
            ],
            "text": ["In principio", None, "Ignored"],
        },
        schema={"urn": pl.String, "text": pl.String},
    )

    actual = md_passages(df, highlighter="**")

    assert actual == ["**1.1** In principio"]


def test_retrieve_leafnode_range_filters_rows_between_start_and_end():
    df = pl.DataFrame(
        {
            "urn": [
                "urn:cts:compnov:bible.genesis.sept_latin:1.1",
                "urn:cts:compnov:bible.genesis.sept_latin:1.2",
                "urn:cts:compnov:bible.genesis.sept_latin:1.3",
                "urn:cts:compnov:bible.genesis.sept_latin:1.10",
                "urn:cts:compnov:bible.exodus.sept_latin:1.2",
            ],
            "text": ["a", "b", "c", "d", "x"],
        },
        schema={"urn": pl.String, "text": pl.String},
    )

    actual = retrieve_leafnode_range(df, "urn:cts:compnov:bible.genesis.sept_latin:1.2-1.10")

    assert actual["urn"].to_list() == [
        "urn:cts:compnov:bible.genesis.sept_latin:1.2",
        "urn:cts:compnov:bible.genesis.sept_latin:1.3",
        "urn:cts:compnov:bible.genesis.sept_latin:1.10",
    ]


def test_retrieve_leafnode_range_supports_abbreviated_end_value():
    df = pl.DataFrame(
        {
            "urn": [
                "urn:cts:compnov:bible.genesis.sept_latin:1.1",
                "urn:cts:compnov:bible.genesis.sept_latin:1.2",
                "urn:cts:compnov:bible.genesis.sept_latin:1.3",
                "urn:cts:compnov:bible.genesis.sept_latin:2.1",
            ],
            "text": ["a", "b", "c", "d"],
        },
        schema={"urn": pl.String, "text": pl.String},
    )

    actual = retrieve_leafnode_range(df, "urn:cts:compnov:bible.genesis.sept_latin:1.1-3")

    assert actual["urn"].to_list() == [
        "urn:cts:compnov:bible.genesis.sept_latin:1.1",
        "urn:cts:compnov:bible.genesis.sept_latin:1.2",
        "urn:cts:compnov:bible.genesis.sept_latin:1.3",
    ]
