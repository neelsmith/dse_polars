import polars as pl
import re

class DSEPassages:
    def __init__(self, data):
        "Enforce DSE schema for dataframe."
        base_df = pl.DataFrame(data, schema={
            "urn": pl.String,
            "text": pl.String
        })

        urn_parts = pl.col("urn").str.split_exact(":", 4)
        work_parts = urn_parts.struct.field("field_3").str.split_exact(".", 2)

        self.df = base_df.with_columns(
            urn_parts.struct.field("field_4").alias("passageref"),
            work_parts.struct.field("field_0").alias("group"),
            work_parts.struct.field("field_1").alias("work"),
            work_parts.struct.field("field_2").alias("version"),
        )


def retrieve_leafnode_range(df: pl.DataFrame, urn: str) -> pl.DataFrame:
    "Return a dataframe containing all rows whose URN falls between the first and last values of a range urn."
    if "urn" not in df.columns:
        raise ValueError("DataFrame must include an 'urn' column.")

    if "-" not in urn:
        return df.filter(pl.col("urn") == urn)

    def split_urn_parts(value: str) -> tuple[str, str]:
        base, sep, passage = value.rpartition(":")
        if not sep:
            raise ValueError(f"Invalid CTS URN: {value}")
        return base, passage

    def normalize_range_end(start_passage: str, end_passage: str) -> str:
        if "." not in start_passage or "." in end_passage:
            return end_passage

        start_parts = start_passage.split(".")
        end_parts = end_passage.split(".")
        if len(end_parts) >= len(start_parts):
            return end_passage

        borrowed = start_parts[: len(start_parts) - len(end_parts)]
        return ".".join([*borrowed, *end_parts])

    def token_key(token: str) -> tuple:
        pieces = re.findall(r"\d+|\D+", token)
        keyed: list[tuple[int, int | str]] = []
        for piece in pieces:
            if piece.isdigit():
                keyed.append((0, int(piece)))
            else:
                keyed.append((1, piece))
        return tuple(keyed)

    def passage_key(passage: str) -> tuple:
        return tuple(token_key(part) for part in passage.split("."))

    range_base, range_passage = split_urn_parts(urn)
    start_passage, end_component = range_passage.split("-", 1)
    if not start_passage or not end_component:
        raise ValueError(f"Invalid CTS range URN: {urn}")

    if end_component.startswith("urn:"):
        end_base, end_passage = split_urn_parts(end_component)
    else:
        end_base = range_base
        end_passage = normalize_range_end(start_passage, end_component)

    if end_base != range_base:
        raise ValueError("Range URN start and end must have the same work component.")

    start_key = passage_key(start_passage)
    end_key = passage_key(end_passage)

    if start_key > end_key:
        start_key, end_key = end_key, start_key

    urn_values = df.get_column("urn").to_list()
    mask = []
    for row_urn in urn_values:
        if row_urn is None:
            mask.append(False)
            continue
        try:
            row_base, row_passage = split_urn_parts(row_urn)
        except ValueError:
            mask.append(False)
            continue

        if row_base != range_base:
            mask.append(False)
            continue

        row_key = passage_key(row_passage)
        mask.append(start_key <= row_key <= end_key)

    return df.filter(pl.Series("_mask", mask))



def md_passages(df: pl.DataFrame, highlighter = "*") -> list[str]:
    "Generates a formatted string for each passage in the dataframe consisting of the final passage component of the urn, surrounded by the highlighter string, followed by a space and the text content."
    rows = (
        df.select("urn", "text")
        .filter(pl.col("urn").is_not_null() & pl.col("text").is_not_null())
        .iter_rows(named=True)
    )
    return [
        f"{highlighter}{row['urn'].rsplit(':', 1)[-1]}{highlighter} {row['text']}"
        for row in rows
    ]

def textcontents(df: pl.DataFrame) -> list[str]:
    "Return a python list of all text contents in the dataframe, as strings."
    return df.select("text").filter(pl.col("text").is_not_null()).to_series().to_list()

def ctsurn_containedby(u1: pl.Expr | str, u2: pl.Expr | str) -> pl.Expr:
    "Inverse of ctsurn_contains: true if u1 is contained by u2 as a CTS URN."
    return ctsurn_contains(u2, u1)


# urn:cts:compnov:bible.genesis.sept_latin:1.1
# urn:cts:compnov:bible.genesis.targum_latin:1.1
# urn:cts:compnov:bible.genesis.targum_latin:1
def ctsurn_contains(u1: pl.Expr | str, u2: pl.Expr | str) -> pl.Expr:
    """Polars expression: true if `u1` contains `u2` as a CTS URN.

    The match semantics follow the rules in the comment below.
    """
    urn1 = u1 if isinstance(u1, pl.Expr) else pl.lit(u1)
    urn2 = u2 if isinstance(u2, pl.Expr) else pl.lit(u2)

    parts1 = urn1.str.split_exact(":", 4)
    parts2 = urn2.str.split_exact(":", 4)

    spec1 = parts1.struct.field("field_0")
    spectype1 = parts1.struct.field("field_1")
    ns1 = parts1.struct.field("field_2")
    workcomponent1 = parts1.struct.field("field_3")
    passage1 = parts1.struct.field("field_4")

    spec2 = parts2.struct.field("field_0")
    spectype2 = parts2.struct.field("field_1")
    ns2 = parts2.struct.field("field_2")
    workcomponent2 = parts2.struct.field("field_3")
    passage2 = parts2.struct.field("field_4")

    workparts1 = workcomponent1.str.split_exact(".", 2)
    workparts2 = workcomponent2.str.split_exact(".", 2)

    wp10 = workparts1.struct.field("field_0")
    wp11 = workparts1.struct.field("field_1")
    wp12 = workparts1.struct.field("field_2")

    wp20 = workparts2.struct.field("field_0")
    wp21 = workparts2.struct.field("field_1")
    wp22 = workparts2.struct.field("field_2")

    group_eq = (spec1 == spec2) & (spectype1 == spectype2) & (ns1 == ns2)
    work_eq = (wp10 == wp20) & (wp11 == wp21)
    work3_compatible = (wp12 == wp22) | wp12.is_null() | wp22.is_null()

    passage_prefix = passage1.str.starts_with(passage2 + pl.lit(".")) & (
        passage1.str.len_chars() > (passage2.str.len_chars() + pl.lit(1))
    )
    passage_ok = (passage1 == passage2) | (passage2 == "") | passage_prefix

    return (urn1 == urn2) | (group_eq & work_eq & work3_compatible & passage_ok)

    # workparts1 and workparts2 must have either 2 or 3 elements
    #
    # Result is true if:
    # u1 == u2
    # OR 
    # [
    # group1 == group2
    # AND
    # workparts1[0] == workparts2[0]
    # AND
    # workparts1[1] == workparts2[1] 
    # AND
    # (workparts1[2] == workparts2[2] OR one of workparts1[2] or workparts2[2] is missing)
    # AND
    # passage1 == passage2 OR passage2 is empty OR 
    # passage1 starts with passage2 + "." + 1 or more characters
    # ]