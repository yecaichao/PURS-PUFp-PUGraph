from __future__ import annotations

import argparse
import json
from pathlib import Path

from purs.fingerprint.build import build_pufp
from purs.ml.feature_fusion import (
    build_opecm_descriptor_feature_table,
    build_opecm_raw_feature_table,
    combine_feature_tables,
)
from purs.ml.krr import run_krr
from purs.ml.rf import run_rf
from purs.ml.svm import run_svm


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "testing" / "opecm_ue_cases.csv"
DEFAULT_RAW = REPO_ROOT / "data" / "external" / "opecm" / "1_raw_data.csv"
DEFAULT_DESCRIPTORS = REPO_ROOT / "data" / "processed" / "opecm" / "3_Descriptors.csv"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "feature_fusion_baseline"


def run_model_suite(feature_csv: Path, target_csv: Path, quick: bool, cv: int, random_state: int):
    common_kwargs = {
        "feature_csv": feature_csv,
        "target_csv": target_csv,
        "id_column": "sample_id",
        "target_column": "regression_target",
        "cv": cv,
        "random_state": random_state,
        "quick": quick,
    }
    return {
        "rf": run_rf(**common_kwargs),
        "krr": run_krr(**common_kwargs),
        "svm": run_svm(**common_kwargs),
    }


def main(
    input_csv: Path,
    raw_csv: Path,
    descriptor_csv: Path,
    output_dir: Path,
    quick: bool = True,
    cv: int = 3,
    random_state: int = 111,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    pufp_dir = output_dir / "pufp"
    build_result = build_pufp(
        input_csv=input_csv,
        name_column="sample_id",
        smiles_column="smiles",
        output_dir=pufp_dir,
    )
    pufp_feature_csv = pufp_dir / "number.csv"

    raw_feature_csv = output_dir / "raw_features.csv"
    build_opecm_raw_feature_table(raw_csv=raw_csv, output_csv=raw_feature_csv)

    descriptor_feature_csv = output_dir / "descriptor_features.csv"
    build_opecm_descriptor_feature_table(
        descriptor_csv=descriptor_csv,
        output_csv=descriptor_feature_csv,
    )

    pufp_plus_raw_csv = output_dir / "pufp_plus_raw.csv"
    combine_feature_tables(
        base_feature_csv=pufp_feature_csv,
        extra_feature_tables=[raw_feature_csv],
        output_csv=pufp_plus_raw_csv,
    )

    pufp_plus_descriptors_csv = output_dir / "pufp_plus_descriptors.csv"
    combine_feature_tables(
        base_feature_csv=pufp_feature_csv,
        extra_feature_tables=[descriptor_feature_csv],
        output_csv=pufp_plus_descriptors_csv,
    )

    raw_plus_descriptors_csv = output_dir / "raw_plus_descriptors.csv"
    combine_feature_tables(
        base_feature_csv=raw_feature_csv,
        extra_feature_tables=[descriptor_feature_csv],
        output_csv=raw_plus_descriptors_csv,
    )

    pufp_plus_raw_plus_descriptors_csv = output_dir / "pufp_plus_raw_plus_descriptors.csv"
    combine_feature_tables(
        base_feature_csv=pufp_feature_csv,
        extra_feature_tables=[raw_feature_csv, descriptor_feature_csv],
        output_csv=pufp_plus_raw_plus_descriptors_csv,
    )

    summary = {
        "input_csv": str(input_csv),
        "raw_csv": str(raw_csv),
        "descriptor_csv": str(descriptor_csv),
        "build_result": build_result,
        "feature_sets": {
            "pufp": {
                "feature_csv": str(pufp_feature_csv),
                "results": run_model_suite(pufp_feature_csv, input_csv, quick, cv, random_state),
            },
            "raw_features": {
                "feature_csv": str(raw_feature_csv),
                "results": run_model_suite(raw_feature_csv, input_csv, quick, cv, random_state),
            },
            "descriptor_features": {
                "feature_csv": str(descriptor_feature_csv),
                "results": run_model_suite(descriptor_feature_csv, input_csv, quick, cv, random_state),
            },
            "pufp_plus_raw": {
                "feature_csv": str(pufp_plus_raw_csv),
                "results": run_model_suite(pufp_plus_raw_csv, input_csv, quick, cv, random_state),
            },
            "pufp_plus_descriptors": {
                "feature_csv": str(pufp_plus_descriptors_csv),
                "results": run_model_suite(pufp_plus_descriptors_csv, input_csv, quick, cv, random_state),
            },
            "raw_plus_descriptors": {
                "feature_csv": str(raw_plus_descriptors_csv),
                "results": run_model_suite(raw_plus_descriptors_csv, input_csv, quick, cv, random_state),
            },
            "pufp_plus_raw_plus_descriptors": {
                "feature_csv": str(pufp_plus_raw_plus_descriptors_csv),
                "results": run_model_suite(pufp_plus_raw_plus_descriptors_csv, input_csv, quick, cv, random_state),
            },
        },
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    compact = {}
    for feature_name, feature_block in summary["feature_sets"].items():
        compact[feature_name] = {
            model_name: model_result["test_metrics"]["R2"]
            for model_name, model_result in feature_block["results"].items()
        }

    print(f"Summary written to: {summary_path}")
    print(json.dumps(compact, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare PUFp, raw OPECM features, descriptor features, and fused feature sets."
    )
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--raw-csv", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--descriptor-csv", type=Path, default=DEFAULT_DESCRIPTORS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cv", type=int, default=3)
    parser.add_argument("--random-state", type=int, default=111)
    parser.add_argument("--full", action="store_true", help="Run the wider non-quick hyperparameter search.")
    args = parser.parse_args()
    main(
        input_csv=args.input_csv,
        raw_csv=args.raw_csv,
        descriptor_csv=args.descriptor_csv,
        output_dir=args.output_dir,
        quick=not args.full,
        cv=args.cv,
        random_state=args.random_state,
    )
