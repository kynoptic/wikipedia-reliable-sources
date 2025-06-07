# [`/data/processed`]

## Purpose

Normalized citation and source data produced by the cleaning pipeline.

## Contents

### Files

* **[`refs_extracted.json`](./refs_extracted.json)** – Citation URLs extracted
  from wikitext
* **[`sources_canonical.csv`](./sources_canonical.csv)** – Ranked list of
  canonicalized sources

## Usage

Generated automatically by `core.clean_sources`. These files can be analyzed or
used in further processing.

## Related modules

* [`../../core/`](../../core/) – Modules that produce and consume these outputs
* [`../raw/`](../raw/) – Source data used to generate the processed files
* [`../README.md`](../README.md) – Data directory overview
