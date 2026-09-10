"""Create the machine-readable GCOR public-release files from the source workbook.

The script deliberately preserves source-row order and never removes, deduplicates,
or imputes records. It is intended to be rerun after an approved source update.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "GCOR_public_source_v1.0.xlsx"
OUTPUT = ROOT / "data" / "GCOR_v1.0.csv"
REPORT = ROOT / "docs" / "release_checks.json"
CHECKSUMS = ROOT / "SHA256SUMS.txt"

SOURCE_COLUMNS = [
    "Site",
    "Crop",
    "CH4_CO2eq_kg_per_ha",
    "N2O_CO2eq_kg_per_ha",
    "Yield_kgha",
    "Nitrogen_kg N/ha",
    "Pho_kg P₂O₅/ha",
    "Pot_kg K₂O/ha",
    "CH4_measurement_method",
    "N2O_measurement_method",
    "Title",
]

MOJIBAKE_TITLE_REPAIRS = {
    "\u8292\u9227\ue0fd\u20ac\u6e28": "–w",
    "\u8292\u9227\ue0fd\u20ac\u6e03": "–c",
    "\u8292\u9227\ue0fd\u20ac\u6e07": "–f",
    "\u8292\u9227\ue0fd\u20ac\u6e08": "–g",
    "\u8292\u9227\ue0fd\u5289": "’",
    "\u8292\u9227\ue0fd\u20ac\u6e1e": "–r",
    "\u8292\u9227\ue0fd\u20ac\u6e1b": "–p",
    "\u8292\u9227\ue0e6\u6e28": "‘w",
    "\u8292\u9227\ue0fd\u20ac?": "–",
    "\u9225\u6418": "–w",
    "\u8292\u9227\ue0fd\u20ac\u6e18": "–n",
    "\u8292\u9227\ue0fd\u20ac\u6e1f": "–s",
    "\u8119\u5364": "ñ",
    "\u8292\u9227\ue0fd\u20ac\u6dda": "–I",
    "–With both": "– With both",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_source_title(value: object) -> object:
    """Repair confirmed encoding artifacts without correcting source wording."""
    if pd.isna(value):
        return value
    title = str(value)
    for damaged, repaired in MOJIBAKE_TITLE_REPAIRS.items():
        title = title.replace(damaged, repaired)
    return re.sub(r"\s+", " ", title.replace("_x000D_", " ")).strip()


def main() -> None:
    source = pd.read_excel(SOURCE, dtype=object)
    if source.columns.tolist() != SOURCE_COLUMNS:
        raise ValueError("Unexpected source-workbook columns; release was not created.")
    if source.empty or source.isna().all(axis=1).any():
        raise ValueError("Source contains an empty record; release was not created.")
    source["Title"] = source["Title"].map(normalize_source_title)

    # An identifier is assigned once, in source order, for stable cross-file citation.
    study_keys = pd.factorize(source["Title"], sort=False)[0] + 1
    nitrogen_numeric = pd.to_numeric(source["Nitrogen_kg N/ha"], errors="coerce")
    release = pd.DataFrame(
        {
            "observation_id": [f"GCOR_{n:06d}" for n in range(1, len(source) + 1)],
            "source_row": range(2, len(source) + 2),
            "study_id": [f"GCOR_STUDY_{n:04d}" for n in study_keys],
            "site_label": source["Site"],
            "crop_label": source["Crop"],
            "ch4_co2eq_kg_ha": source["CH4_CO2eq_kg_per_ha"],
            "n2o_co2eq_kg_ha": source["N2O_CO2eq_kg_per_ha"],
            "yield_kg_ha": source["Yield_kgha"],
            "nitrogen_kg_n_ha_reported": source["Nitrogen_kg N/ha"],
            "nitrogen_kg_n_ha_numeric": nitrogen_numeric,
            "phosphorus_kg_p2o5_ha": source["Pho_kg P₂O₅/ha"],
            "potassium_kg_k2o_ha": source["Pot_kg K₂O/ha"],
            "ch4_measurement_method": source["CH4_measurement_method"],
            "n2o_measurement_method": source["N2O_measurement_method"],
            "source_title": source["Title"],
        }
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    release.to_csv(OUTPUT, index=False, encoding="utf-8-sig", lineterminator="\n")

    report = {
        "release_version": "1.0.0",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
        "canonical_file": OUTPUT.relative_to(ROOT).as_posix(),
        "source_rows": int(len(source)),
        "release_rows": int(len(release)),
        "source_columns": int(len(source.columns)),
        "release_columns": int(len(release.columns)),
        "blank_source_rows": int(source.isna().all(axis=1).sum()),
        "exact_duplicate_source_rows_retained": int(source.duplicated().sum()),
        "unique_source_titles": int(source["Title"].nunique()),
        "unique_site_labels": int(source["Site"].nunique()),
        "nitrogen_reported_nonmissing": int(source["Nitrogen_kg N/ha"].notna().sum()),
        "nitrogen_numeric_nonmissing": int(nitrogen_numeric.notna().sum()),
        "nitrogen_non_numeric_reported": int(
            (source["Nitrogen_kg N/ha"].notna() & nitrogen_numeric.isna()).sum()
        ),
        "source_sha256": sha256(SOURCE),
        "canonical_sha256": sha256(OUTPUT),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    CHECKSUMS.write_text(
        f"{report['canonical_sha256']}  data/GCOR_v1.0.csv\n"
        f"{report['source_sha256']}  data/raw/GCOR_public_source_v1.0.xlsx\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
