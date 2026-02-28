# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## 0.3.0 - 2026-02-28

### Changed

- clarified selector behavior for image values: `imagesfor*` methods return full `image` values (including ROI), while `wholeimagesfor*` methods return ROI-stripped `wholeimage` values.
- added `wholeimagesforsurface` and `wholeimagesforpassage` selector methods.

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