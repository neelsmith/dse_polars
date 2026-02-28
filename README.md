# dse_polars
Work with DSE triples in a polars dataframe

## `ctsurn_contains` usage

`ctsurn_contains` returns a Polars expression, so you can use it directly in `filter`/`select`.

```python
import polars as pl
from dse_polars.texts import ctsurn_contains

df = pl.DataFrame(
	{
		"urn": [
			"urn:cts:compnov:bible.genesis.sept_latin:1.1",
			"urn:cts:compnov:bible.genesis.sept_latin:2.1",
			"urn:cts:compnov:bible.exodus.sept_latin:1.1",
		]
	}
)

query = "urn:cts:compnov:bible.genesis:1"

matches = df.filter(ctsurn_contains(pl.col("urn"), query))
print(matches)

# quick boolean check with literals
is_contained = pl.select(
	ctsurn_contains(
		"urn:cts:compnov:bible.genesis.sept_latin:1.1",
		"urn:cts:compnov:bible.genesis:1",
	).alias("ok")
).item(0, 0)
print(is_contained)  # True
```

## `ptinrect` usage

`ptinrect` returns a Polars expression, so you can use it directly in `filter`/`select`.

```python
import polars as pl
from dse_polars.images import ptinrect

rects = pl.DataFrame(
	{
		"label": ["A", "B"],
		"x": [10.0, 100.0],
		"y": [20.0, 200.0],
		"w": [30.0, 20.0],
		"h": [40.0, 20.0],
	}
)

# filter rectangles containing a literal point (25, 35)
hits = rects.filter(ptinrect(25.0, 35.0))
print(hits)

# use point columns too
points = pl.DataFrame({"px": [25.0, 130.0], "py": [35.0, 210.0]})
checks = rects.with_columns(points).select(
	pl.col("label"),
	ptinrect(pl.col("px"), pl.col("py")).alias("contains_point"),
)
print(checks)
```

## `textcontents` usage

`textcontents` returns a Python list of values in the `text` column, excluding nulls.

```python
import polars as pl
from dse_polars.texts import textcontents

df = pl.DataFrame(
	{
		"urn": ["u1", "u2", "u3", "u4"],
		"text": ["alpha", None, "beta", "alpha"],
	}
)

contents = textcontents(df)
print(contents)  # ['alpha', 'beta', 'alpha']
```
