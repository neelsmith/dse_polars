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
