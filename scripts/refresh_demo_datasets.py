from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from purs.data.osc_tasks import build_opecm_osc_parent_table, build_paper_style_task_tables


ROOT = Path(__file__).resolve().parents[1]
RAW_OPECM = ROOT / "data" / "external" / "opecm" / "1_raw_data.csv"
COMMON_DATASET = ROOT / "data" / "testing" / "common_polymer_cases.csv"
PCE_DATASET = ROOT / "data" / "testing" / "opecm_pce_cases.csv"
UE_DATASET = ROOT / "data" / "testing" / "opecm_ue_cases.csv"
UH_DATASET = ROOT / "data" / "testing" / "opecm_uh_cases.csv"
STANDARD_MASTER_DATASET = ROOT / "data" / "testing" / "opecm_paper54_tasks.csv"

CANONICAL_RAW_COLUMNS = [
    "No.",
    "SMILES",
    "InchI",
    "ue/cm2·V-1·s-1",
    "uh/cm2·V-1·s-1",
    "PCE/%",
    "epsilon/F·m-1",
    "-HOMO/eV",
    "-LUMO/eV",
    "Eg/eV",
    "alpha",
    "mu",
]


@lru_cache(maxsize=None)
def safe_is_valid_smiles(smiles: str) -> bool:
    RDLogger.DisableLog("rdApp.error")
    RDLogger.DisableLog("rdApp.warning")
    try:
        normalized = smiles.replace("/", "").replace("\\", "")
        return Chem.MolFromSmiles(normalized) is not None
    finally:
        RDLogger.EnableLog("rdApp.error")
        RDLogger.EnableLog("rdApp.warning")


def load_raw_opecm() -> pd.DataFrame:
    raw_df = pd.read_csv(RAW_OPECM).copy()
    if len(raw_df.columns) != len(CANONICAL_RAW_COLUMNS):
        raise ValueError(
            f"Expected {len(CANONICAL_RAW_COLUMNS)} OPECM columns, found {len(raw_df.columns)}"
        )
    raw_df.columns = CANONICAL_RAW_COLUMNS
    return raw_df


def clean_numeric_column(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip()
    cleaned = cleaned.str.replace(r"(?<=\d)\.$", "", regex=True)
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce")


def build_target_dataset(raw_df: pd.DataFrame, target_column: str, dataset_path: Path, target_name: str, target_unit: str) -> pd.DataFrame:
    dataset = pd.DataFrame(
        {
            "case_id": [f"CASE_{int(no):03d}" for no in raw_df["No."]],
            "source_dataset": "OPECM",
            "source_record_id": raw_df["No."].astype(int),
            "sample_id": raw_df["No."].astype(int).astype(str),
            "smiles": raw_df["SMILES"].astype(str),
            "regression_target": raw_df[target_column].astype(float),
            "graph_target": raw_df[target_column].astype(float),
            "target_name": target_name,
            "target_unit": target_unit,
            "target_source_column": target_column,
        }
    )
    dataset["expected_valid"] = dataset["smiles"].map(safe_is_valid_smiles)
    dataset["notes"] = dataset["expected_valid"].map(lambda flag: "valid" if flag else "invalid_smiles")
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(dataset_path, index=False)
    return dataset


def build_common_dataset() -> pd.DataFrame:
    raw_df = load_raw_opecm()
    raw_df["Eg/eV"] = clean_numeric_column(raw_df["Eg/eV"])
    return build_target_dataset(
        raw_df=raw_df,
        target_column="Eg/eV",
        dataset_path=COMMON_DATASET,
        target_name="Eg",
        target_unit="eV",
    )


def build_pce_dataset() -> pd.DataFrame:
    raw_df = load_raw_opecm()
    raw_df["PCE/%"] = clean_numeric_column(raw_df["PCE/%"])
    raw_df = raw_df[raw_df["PCE/%"].notna()].copy()
    return build_target_dataset(
        raw_df=raw_df,
        target_column="PCE/%",
        dataset_path=PCE_DATASET,
        target_name="PCE",
        target_unit="%",
    )


def build_ue_dataset() -> pd.DataFrame:
    raw_df = load_raw_opecm()
    raw_df["ue/cm2·V-1·s-1"] = clean_numeric_column(raw_df["ue/cm2·V-1·s-1"])
    raw_df = raw_df[raw_df["ue/cm2·V-1·s-1"].notna()].copy()
    return build_target_dataset(
        raw_df=raw_df,
        target_column="ue/cm2·V-1·s-1",
        dataset_path=UE_DATASET,
        target_name="ue",
        target_unit="cm2/V/s",
    )


def build_uh_dataset() -> pd.DataFrame:
    raw_df = load_raw_opecm()
    raw_df["uh/cm2·V-1·s-1"] = clean_numeric_column(raw_df["uh/cm2·V-1·s-1"])
    raw_df = raw_df[raw_df["uh/cm2·V-1·s-1"].notna()].copy()
    return build_target_dataset(
        raw_df=raw_df,
        target_column="uh/cm2·V-1·s-1",
        dataset_path=UH_DATASET,
        target_name="uh",
        target_unit="cm2/V/s",
    )


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def build_standard_master_dataset() -> pd.DataFrame:
    parent_df = build_opecm_osc_parent_table(RAW_OPECM)
    tables = build_paper_style_task_tables(parent_df)
    standard_df = tables["paper54_tasks"].copy()
    write_csv(STANDARD_MASTER_DATASET, standard_df)
    return standard_df


def refresh_examples_and_fixtures(
    common_dataset: pd.DataFrame,
    pce_dataset: pd.DataFrame,
    ue_dataset: pd.DataFrame,
    standard_dataset: pd.DataFrame,
) -> None:
    valid_df = common_dataset[common_dataset["expected_valid"]].reset_index(drop=True)
    invalid_df = common_dataset[~common_dataset["expected_valid"]].reset_index(drop=True)
    valid_pce_df = pce_dataset[pce_dataset["expected_valid"]].reset_index(drop=True)
    valid_ue_df = ue_dataset[ue_dataset["expected_valid"]].reset_index(drop=True)
    valid_standard_df = standard_dataset[standard_dataset["expected_valid"]].reset_index(drop=True)

    write_csv(
        ROOT / "examples" / "basic_recognition" / "input.csv",
        valid_df.head(4)[["sample_id", "smiles"]].rename(columns={"sample_id": "name"}),
    )
    write_csv(
        ROOT / "examples" / "opecm_demo" / "input.csv",
        common_dataset[["sample_id", "smiles"]],
    )
    ml_input = valid_pce_df.head(8)[["sample_id", "smiles"]]
    ml_target = valid_pce_df.head(8)[["sample_id", "regression_target"]].rename(columns={"regression_target": "target"})
    write_csv(ROOT / "examples" / "pufp_opv_demo" / "input.csv", ml_input)
    write_csv(ROOT / "examples" / "pufp_opv_demo" / "target.csv", ml_target)

    mobility_input = valid_standard_df.head(8)[["sample_id", "smiles"]]
    mobility_target = valid_standard_df.head(8)[["sample_id", "max_mobility"]].rename(columns={"max_mobility": "target"})
    write_csv(ROOT / "examples" / "pufp_mobility_demo" / "input.csv", mobility_input)
    write_csv(ROOT / "examples" / "pufp_mobility_demo" / "target.csv", mobility_target)

    graph_input = valid_standard_df.head(8)[["sample_id", "smiles", "ue"]].rename(
        columns={"sample_id": "Compound ID", "ue": "PCE_max"}
    )
    write_csv(ROOT / "examples" / "pugraph_demo" / "input.csv", graph_input)

    write_csv(
        ROOT / "tests" / "fixtures" / "tiny_polymers.csv",
        valid_df.head(2)[["sample_id", "smiles"]].rename(columns={"sample_id": "name"}),
    )
    duplicate_fixture = valid_df.head(3)[["smiles"]].copy()
    duplicate_fixture.insert(0, "name", ["dup", "dup", "dup"])
    write_csv(ROOT / "tests" / "fixtures" / "duplicate_names.csv", duplicate_fixture)

    invalid_fixture = pd.concat(
        [
            valid_df.head(1)[["sample_id", "smiles"]].rename(columns={"sample_id": "name"}),
            invalid_df.head(1)[["sample_id", "smiles"]].rename(columns={"sample_id": "name"}),
        ],
        ignore_index=True,
    )
    write_csv(ROOT / "tests" / "fixtures" / "invalid_smiles.csv", invalid_fixture)

    write_csv(
        ROOT / "tests" / "fixtures" / "opv_tiny.csv",
        valid_pce_df.head(3)[["sample_id", "smiles", "regression_target"]].rename(columns={"regression_target": "target"}),
    )
    write_csv(
        ROOT / "tests" / "fixtures" / "mobility_tiny.csv",
        valid_ue_df.head(3)[["sample_id", "smiles", "regression_target"]].rename(columns={"regression_target": "target"}),
    )


def main() -> None:
    common_dataset = build_common_dataset()
    pce_dataset = build_pce_dataset()
    ue_dataset = build_ue_dataset()
    uh_dataset = build_uh_dataset()
    standard_dataset = build_standard_master_dataset()
    refresh_examples_and_fixtures(common_dataset, pce_dataset, ue_dataset, standard_dataset)
    print(f"wrote common dataset: {COMMON_DATASET}")
    print(f"common total rows: {len(common_dataset)}")
    print(f"common valid rows: {int(common_dataset['expected_valid'].sum())}")
    print(f"common invalid rows: {int((~common_dataset['expected_valid']).sum())}")
    print(f"wrote pce dataset: {PCE_DATASET}")
    print(f"pce total rows: {len(pce_dataset)}")
    print(f"pce valid rows: {int(pce_dataset['expected_valid'].sum())}")
    print(f"pce invalid rows: {int((~pce_dataset['expected_valid']).sum())}")
    print(f"wrote ue dataset: {UE_DATASET}")
    print(f"ue total rows: {len(ue_dataset)}")
    print(f"ue valid rows: {int(ue_dataset['expected_valid'].sum())}")
    print(f"ue invalid rows: {int((~ue_dataset['expected_valid']).sum())}")
    print(f"wrote uh dataset: {UH_DATASET}")
    print(f"uh total rows: {len(uh_dataset)}")
    print(f"uh valid rows: {int(uh_dataset['expected_valid'].sum())}")
    print(f"uh invalid rows: {int((~uh_dataset['expected_valid']).sum())}")
    print(f"wrote standard master dataset: {STANDARD_MASTER_DATASET}")
    print(f"standard master rows: {len(standard_dataset)}")


if __name__ == "__main__":
    main()
