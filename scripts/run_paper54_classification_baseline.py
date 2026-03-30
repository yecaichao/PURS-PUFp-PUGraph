from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from purs.fingerprint.build import build_pufp
from purs.ml.feature_fusion import (
    build_opecm_descriptor_feature_table,
    build_opecm_raw_feature_table,
    combine_feature_tables,
)
from purs.ml.classification import (
    run_knn_classifier,
    run_mlp_classifier,
    run_rf_classifier,
    run_svm_classifier,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "testing" / "opecm_paper54_tasks.csv"
DEFAULT_RAW = REPO_ROOT / "data" / "external" / "opecm" / "1_raw_data.csv"
DEFAULT_DESCRIPTORS = REPO_ROOT / "data" / "processed" / "opecm" / "3_Descriptors.csv"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "paper54_classification_baseline"

TASK_CONFIGS = {
    "carrier_type": {
        "target_column": "paper54_carrier_type",
        "allowed_labels": ["n", "p"],
        "description": "Binary dominant-carrier classification; tie rows are excluded.",
    },
    "mobility_class3": {
        "target_column": "paper54_mobility_class3",
        "allowed_labels": ["low", "medium", "high"],
        "description": "Three-bin mobility classification using paper54 thresholds.",
    },
}


def run_model_suite(feature_csv: Path, target_csv: Path, target_column: str, allowed_labels: list[str], quick: bool, cv: int, random_state: int):
    common_kwargs = {
        "feature_csv": feature_csv,
        "target_csv": target_csv,
        "id_column": "sample_id",
        "target_column": target_column,
        "allowed_labels": allowed_labels,
        "cv": cv,
        "random_state": random_state,
        "quick": quick,
    }
    return {
        "rf": run_rf_classifier(**common_kwargs),
        "knn": run_knn_classifier(**common_kwargs),
        "svm": run_svm_classifier(**common_kwargs),
        "mlp": run_mlp_classifier(**common_kwargs),
    }


def build_task_target_csv(input_csv: Path, output_csv: Path, target_column: str, allowed_labels: list[str]) -> Path:
    df = pd.read_csv(input_csv)
    filtered = df[df[target_column].isin(allowed_labels)][["sample_id", "smiles", target_column]].copy()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output_csv, index=False)
    return output_csv


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        values = [str(row[column]) for column in df.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def write_summary_tables(summary: dict, output_dir: Path) -> dict[str, str]:
    generated = {}
    for task_name, task_block in summary["tasks"].items():
        rows = []
        for feature_name, feature_block in task_block["results"].items():
            for model_name, model_result in feature_block.items():
                test_metrics = model_result["test_metrics"]
                rows.append(
                    {
                        "task": task_name,
                        "feature_set": feature_name,
                        "model": model_name,
                        "sample_count": model_result["sample_count"],
                        "feature_count": model_result["feature_count"],
                        "accuracy": test_metrics["accuracy"],
                        "balanced_accuracy": test_metrics["balanced_accuracy"],
                        "macro_f1": test_metrics["macro_f1"],
                    }
                )
        task_df = pd.DataFrame(rows).sort_values(
            by=["accuracy", "balanced_accuracy", "macro_f1"],
            ascending=[False, False, False],
        )
        csv_path = output_dir / f"{task_name}_model_comparison.csv"
        md_path = output_dir / f"{task_name}_model_comparison.md"
        task_df.to_csv(csv_path, index=False)
        md_path.write_text(dataframe_to_markdown(task_df), encoding="utf-8")
        generated[f"{task_name}_csv"] = str(csv_path)
        generated[f"{task_name}_md"] = str(md_path)
    return generated


def main(
    input_csv: Path,
    raw_csv: Path,
    descriptor_csv: Path,
    output_dir: Path,
    task: str = "both",
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
    descriptor_feature_csv = output_dir / "descriptor_features.csv"
    build_opecm_raw_feature_table(raw_csv=raw_csv, output_csv=raw_feature_csv)
    build_opecm_descriptor_feature_table(descriptor_csv=descriptor_csv, output_csv=descriptor_feature_csv)

    pufp_plus_raw_csv = output_dir / "pufp_plus_raw.csv"
    pufp_plus_descriptors_csv = output_dir / "pufp_plus_descriptors.csv"
    raw_plus_descriptors_csv = output_dir / "raw_plus_descriptors.csv"
    pufp_plus_raw_plus_descriptors_csv = output_dir / "pufp_plus_raw_plus_descriptors.csv"

    combine_feature_tables(
        base_feature_csv=pufp_feature_csv,
        extra_feature_tables=[raw_feature_csv],
        output_csv=pufp_plus_raw_csv,
    )
    combine_feature_tables(
        base_feature_csv=pufp_feature_csv,
        extra_feature_tables=[descriptor_feature_csv],
        output_csv=pufp_plus_descriptors_csv,
    )
    combine_feature_tables(
        base_feature_csv=raw_feature_csv,
        extra_feature_tables=[descriptor_feature_csv],
        output_csv=raw_plus_descriptors_csv,
    )
    combine_feature_tables(
        base_feature_csv=pufp_feature_csv,
        extra_feature_tables=[raw_feature_csv, descriptor_feature_csv],
        output_csv=pufp_plus_raw_plus_descriptors_csv,
    )

    feature_sets = {
        "pufp": pufp_feature_csv,
        "raw_features": raw_feature_csv,
        "descriptor_features": descriptor_feature_csv,
        "pufp_plus_raw": pufp_plus_raw_csv,
        "pufp_plus_descriptors": pufp_plus_descriptors_csv,
        "raw_plus_descriptors": raw_plus_descriptors_csv,
        "pufp_plus_raw_plus_descriptors": pufp_plus_raw_plus_descriptors_csv,
    }

    selected_tasks = TASK_CONFIGS.keys() if task == "both" else [task]
    summary = {
        "input_csv": str(input_csv),
        "raw_csv": str(raw_csv),
        "descriptor_csv": str(descriptor_csv),
        "build_result": build_result,
        "feature_sets": {name: str(path) for name, path in feature_sets.items()},
        "tasks": {},
    }

    for task_name in selected_tasks:
        task_cfg = TASK_CONFIGS[task_name]
        task_target_csv = build_task_target_csv(
            input_csv=input_csv,
            output_csv=output_dir / "targets" / f"{task_name}.csv",
            target_column=task_cfg["target_column"],
            allowed_labels=task_cfg["allowed_labels"],
        )
        results = {}
        for feature_name, feature_csv in feature_sets.items():
            results[feature_name] = run_model_suite(
                feature_csv=feature_csv,
                target_csv=task_target_csv,
                target_column=task_cfg["target_column"],
                allowed_labels=task_cfg["allowed_labels"],
                quick=quick,
                cv=cv,
                random_state=random_state,
            )
        summary["tasks"][task_name] = {
            "description": task_cfg["description"],
            "target_csv": str(task_target_csv),
            "allowed_labels": task_cfg["allowed_labels"],
            "results": results,
        }

    summary["summary_tables"] = write_summary_tables(summary, output_dir)
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    compact = {}
    for task_name, task_block in summary["tasks"].items():
        compact[task_name] = {
            feature_name: {
                model_name: model_result["test_metrics"]["accuracy"]
                for model_name, model_result in feature_block.items()
            }
            for feature_name, feature_block in task_block["results"].items()
        }

    print(f"Summary written to: {summary_path}")
    print(json.dumps(compact, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run paper54-style PUFp classification baselines on OPECM OSC tasks.")
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--raw-csv", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--descriptor-csv", type=Path, default=DEFAULT_DESCRIPTORS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--task", choices=["carrier_type", "mobility_class3", "both"], default="both")
    parser.add_argument("--cv", type=int, default=3)
    parser.add_argument("--random-state", type=int, default=111)
    parser.add_argument("--full", action="store_true", help="Run the wider non-quick hyperparameter search.")
    args = parser.parse_args()
    main(
        input_csv=args.input_csv,
        raw_csv=args.raw_csv,
        descriptor_csv=args.descriptor_csv,
        output_dir=args.output_dir,
        task=args.task,
        quick=not args.full,
        cv=args.cv,
        random_state=args.random_state,
    )
