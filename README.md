# Global Crop Observation Repository (GCOR)

GCOR is a public, machine-readable compilation of field-based crop observations used to support crop-model parameterization and validation in *Agricultural burdens emerge as crop climates depart from historical extremes*.

Version 1.0.0 contains 10,791 observation records associated with 933 source-publication titles and 42 retained location labels. Each row represents an observation or experimental-treatment record. The dataset contains crop yield, CH4 and N2O emissions expressed as CO2-equivalent values, fertilizer inputs, measurement methods where recorded, and the source-publication title.

## Download and use

Use [`data/GCOR_v1.0.csv`](data/GCOR_v1.0.csv) for analysis. It is UTF-8 encoded with a byte-order mark (BOM) for direct opening in spreadsheet software, uses one header row, and has one observation per row.

The `crop_label` field preserves the original record label, including capitalization differences, cultivars, crop types, rotations, and non-cereal crops reported in source studies. Use it for source-label grouping and citation; create analytical crop categories separately when needed.

## Files

| Path | Purpose |
| --- | --- |
| `data/GCOR_v1.0.csv` | Canonical analysis-ready CSV release. |
| `scripts/build_release.py` | Rebuild script for the canonical CSV and checksums. |
| `SHA256SUMS.txt` | SHA-256 integrity hashes for the data files. |

## Important interpretation notes

- `ch4_co2eq_kg_ha` and `n2o_co2eq_kg_ha` are area-scaled CO2-equivalent emission values. Interpret seasonal or annual coverage using the associated source publication.
- `nitrogen_kg_n_ha_reported` preserves the source entry, which may be numeric, a range, a treatment description, or another source expression. `nitrogen_kg_n_ha_numeric` contains values parsed as a single number; the reported field retains the original expression.
- The public CSV preserves every source row in source order, including exact duplicates, missing values, source labels, and unusual values. Analytical quality control and exclusion criteria should be documented by the analyst.

## Citation

Please cite this dataset release as specified in [`CITATION.cff`](CITATION.cff). Please also cite the associated article once it is published. Where appropriate, cite the original publication named in `source_title`.

## License and source-material notice

GCOR is licensed under [CC BY 4.0](LICENSE). Please provide attribution in accordance with the license and cite this dataset release as described in [`CITATION.cff`](CITATION.cff). Users remain responsible for complying with rights and terms that apply to underlying publications and for citing them where appropriate.
