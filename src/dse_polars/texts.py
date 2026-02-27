import polars as pl

class DSEPassages:
    def __init__(self, data):
        "Enforce DSE schema for dataframe."
        self.df = pl.DataFrame(data, schema={
            "urn": pl.String,
            "text": pl.String
        })


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