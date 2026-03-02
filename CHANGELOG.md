# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## 0.4.0 - 2026-03-02

### Added

- `rectsforsurface` method
- `ctsurn_containedby` function
- `md_passages` function


## 0.3.3 - 2026-03-02

### Changed

- adjusted packaging for marimo HTML-WASM compatibility:
	- `Requires-Python` now `>=3.12,<3.14`
	- `polars` dependency floor now `>=1.18.0`
- added release/publish guidance to README for pure Python wheel builds and upload workflow

## 0.3.2 - 2026-03-01

### Fixed

- correctly published `textcontents` as package-level function

## 0.3.1 - 2026-03-01

### Fixed

- in `DSE` class, inventory methods `surfaces`, `images` and `texts` now preserve order


## 0.3.0 - 2026-02-28


### Added 

- `DSE.wholeimagesforsurface(surface)` method to return unique ROI-stripped image URNs for a surface.
- `DSE.wholeimagesforpassage(passage)` method to return unique ROI-stripped image URNs for a passage.
- `urn2image_url(urn, srvc)` function to generate IIIF image request URLs from CITE2 URNs.
- `rois(df)` function to collect non-null ROI strings from a dataframe.
- `ptinrect(x, y)` function to test whether a point is inside ROI rectangle columns (`x`, `y`, `w`, `h`).
- `textcontents(df)` function to collect non-null text content strings from a dataframe.


### Changed

- clarified selector behavior for image values: `imagesfor*` methods return full `image` values (including ROI), while `wholeimagesfor*` methods return ROI-stripped `wholeimage` values.


### Breaking changes

- removed `drop_roi`

## 0.2.0 - 2026-02-27

### Added

- `DSEPassages` class and `ctsur_contains` functions
- `CitableIIIFService` class and `urn2info_url`, `info_url2urn`, `roi` and `strip_roi` functions


## 0.1.0 - 2026-02-26

Initial release.

### Adds

- `DSE` class wrapping a polars dataframe with required schema.
- methods to find complete inventory of recorded texts, images and physical surfaces.
- methods relating texts, images and surfaces to each other in all possible combinations.