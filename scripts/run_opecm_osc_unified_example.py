from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd
import yaml

from purs.fingerprint.build import build_pufp
from purs.graph.builders import build_pugraph, train_pugraph
from purs.ml.krr import run_krr
from purs.ml.rf import run_rf
from purs.ml.svm import run_svm


ROOT = Path(__file__).resolve().parents[1]
STANDARD_SAMPLE_TABLE = ROOT / "data" / "testing" / "opecm_paper54_tasks.csv"
OUTPUT_DIR = ROOT / "output" / "opecm_osc_unified_example"
PAPER54_CLASSIFICATION_SCRIPT = ROOT / "scripts" / "run_paper54_classification_baseline.py"


def write_csv(path: Path, df: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def prepare_inputs(output_dir: Path) -> dict[str, Path]:
    standard_df = pd.read_csv(STANDARD_SAMPLE_TABLE)

    ml_input = standard_df[["sample_id", "smiles"]].copy()
    ml_target = standard_df[["sample_id", "max_mobility"]].rename(columns={"max_mobility": "target"})

    graph_ue = standard_df[["sample_id", "smiles", "ue"]].rename(columns={"ue": "graph_target"})
    graph_uh = standard_df[["sample_id", "smiles", "uh"]].rename(columns={"uh": "graph_target"})

    return {
        "standard_sample_table": STANDARD_SAMPLE_TABLE,
        "ml_input_csv": write_csv(output_dir / "inputs" / "standard_ml_input.csv", ml_input),
        "ml_target_csv": write_csv(output_dir / "inputs" / "standard_ml_target.csv", ml_target),
        "graph_ue_csv": write_csv(output_dir / "inputs" / "standard_graph_ue.csv", graph_ue),
        "graph_uh_csv": write_csv(output_dir / "inputs" / "standard_graph_uh.csv", graph_uh),
    }


def run_ml_suite(feature_csv: Path, target_csv: Path) -> dict:
    common_kwargs = {
        "feature_csv": feature_csv,
        "target_csv": target_csv,
        "id_column": "sample_id",
        "target_column": "target",
        "cv": 3,
        "quick": True,
    }
    return {
        "rf": run_rf(**common_kwargs),
        "krr": run_krr(**common_kwargs),
        "svm": run_svm(**common_kwargs),
    }


def run_paper54_classification_suite(input_csv: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(PAPER54_CLASSIFICATION_SCRIPT),
        "--input-csv",
        str(input_csv),
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return {
        "command": command,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "summary_path": str(summary_path),
        "summary": summary,
    }


def maybe_execute_graph_configs(build_result: dict, execute_graphs: bool) -> dict:
    configs = {
        "pu_gn_exp": Path(build_result["pu_gn_exp_train_yaml"]),
        "pu_mpnn": Path(build_result["pu_mpnn_train_yaml"]),
    }
    results = {}

    for name, config_path in configs.items():
        command_only = train_pugraph(config_path)
        results[f"{name}_command_only"] = command_only
        if not execute_graphs:
            continue

        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        execute_cfg = config_path.with_name(f"{config_path.stem}_execute.yaml")
        cfg["mode"] = "execute"
        if name == "pu_gn_exp":
            cfg.setdefault("session", {})
            cfg["session"]["epochs"] = 1
            cfg["session"]["batch_size"] = 8
        execute_cfg.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        results[f"{name}_execute"] = train_pugraph(execute_cfg)

    return results


def main(output_dir: Path, execute_graphs: bool = False) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = prepare_inputs(output_dir)
    classification_results = run_paper54_classification_suite(
        input_csv=STANDARD_SAMPLE_TABLE,
        output_dir=output_dir / "paper54_classification",
    )

    fingerprint_result = build_pufp(
        input_csv=inputs["ml_input_csv"],
        name_column="sample_id",
        smiles_column="smiles",
        output_dir=output_dir / "pufp",
    )
    ml_results = run_ml_suite(Path(fingerprint_result["output_dir"]) / "number.csv", inputs["ml_target_csv"])

    graph_ue_result = build_pugraph(
        input_csv=inputs["graph_ue_csv"],
        name_column="sample_id",
        smiles_column="smiles",
        output_dir=output_dir / "graph_ue",
    )
    graph_uh_result = build_pugraph(
        input_csv=inputs["graph_uh_csv"],
        name_column="sample_id",
        smiles_column="smiles",
        output_dir=output_dir / "graph_uh",
    )

    summary = {
        "inputs": {key: str(value) for key, value in inputs.items()},
        "paper54_classification": classification_results,
        "fingerprint": fingerprint_result,
        "ml": ml_results,
        "graph_ue": {
            "build": graph_ue_result,
            "train": maybe_execute_graph_configs(graph_ue_result, execute_graphs),
        },
        "graph_uh": {
            "build": graph_uh_result,
            "train": maybe_execute_graph_configs(graph_uh_result, execute_graphs),
        },
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    compact = {
        "paper54_carrier_type_best_accuracy": max(
            model_result["test_metrics"]["accuracy"]
            for feature_block in classification_results["summary"]["tasks"]["carrier_type"]["results"].values()
            for model_result in feature_block.values()
        ),
        "paper54_mobility_class3_best_accuracy": max(
            model_result["test_metrics"]["accuracy"]
            for feature_block in classification_results["summary"]["tasks"]["mobility_class3"]["results"].values()
            for model_result in feature_block.values()
        ),
        "ml_test_r2": {name: result["test_metrics"]["R2"] for name, result in ml_results.items()},
        "graph_ue_rows": graph_ue_result["sample_count"],
        "graph_uh_rows": graph_uh_result["sample_count"],
        "execute_graphs": execute_graphs,
    }
    print(f"Summary written to: {summary_path}")
    print(json.dumps(compact, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the unified OPECM-derived OSC package example from the standard master sample table."
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--execute-graphs", action="store_true")
    args = parser.parse_args()
    main(output_dir=args.output_dir, execute_graphs=args.execute_graphs)
