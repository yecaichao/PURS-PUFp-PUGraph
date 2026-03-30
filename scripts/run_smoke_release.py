from __future__ import annotations

import json
import os
import stat
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "smoke_release"


def _retry_remove_readonly(func, path, excinfo) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def reset_output_dir(output_dir: Path) -> None:
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        return

    last_error = None
    for _ in range(3):
        try:
            shutil.rmtree(output_dir, onerror=_retry_remove_readonly)
            break
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.5)
    else:
        raise RuntimeError(
            f"Could not clear previous smoke output directory: {output_dir}. "
            "Close any open files in that folder and retry."
        ) from last_error

    output_dir.mkdir(parents=True, exist_ok=True)


def run_step(name: str, args: list[str], expect_success: bool = True) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    command = [sys.executable, "-m", "purs.cli", *args]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    success = completed.returncode == 0
    if expect_success and not success:
        raise RuntimeError(
            f"Smoke step '{name}' failed with code {completed.returncode}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    if not expect_success and success:
        raise RuntimeError(f"Smoke step '{name}' was expected to fail but succeeded.")
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "expected_success": expect_success,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def write_execute_config(src_config: Path, dst_config: Path, updates: dict) -> Path:
    cfg = yaml.safe_load(src_config.read_text(encoding="utf-8")) or {}
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(cfg.get(key), dict):
            cfg[key].update(value)
        else:
            cfg[key] = value
    dst_config.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return dst_config


def main() -> None:
    reset_output_dir(OUTPUT_DIR)

    results = []
    results.append(
        run_step(
            "fingerprint",
            [
                "fingerprint",
                "--input-csv",
                "repro/supplementary_examples/pufp_opv_demo/input.csv",
                "--name-column",
                "sample_id",
                "--smiles-column",
                "smiles",
                "--output-dir",
                "output/smoke_release/pufp",
            ],
        )
    )
    results.append(
        run_step(
            "ml_rf",
            [
                "ml",
                "rf",
                "--feature-csv",
                "output/smoke_release/pufp/number.csv",
                "--target-csv",
                "repro/supplementary_examples/pufp_opv_demo/target.csv",
                "--id-column",
                "sample_id",
                "--target-column",
                "target",
                "--cv",
                "2",
                "--quick",
                "--output-plot",
                "output/smoke_release/ml_rf.png",
            ],
        )
    )
    results.append(
        run_step(
            "graph_build",
            [
                "graph",
                "build",
                "--input-csv",
                "repro/supplementary_examples/pugraph_demo/input.csv",
                "--output-dir",
                "output/smoke_release/graph",
            ],
        )
    )
    results.append(
        run_step(
            "graph_train_pu_gn_exp",
            [
                "graph",
                "train",
                "--config",
                "output/smoke_release/graph/pu_gn_exp_train.yaml",
            ],
        )
    )
    gn_execute_config = write_execute_config(
        OUTPUT_DIR / "graph" / "pu_gn_exp_train.yaml",
        OUTPUT_DIR / "graph" / "pu_gn_exp_execute.yaml",
        {"mode": "execute", "session": {"epochs": 1, "batch_size": 2}},
    )
    results.append(
        run_step(
            "graph_train_pu_gn_exp_execute",
            [
                "graph",
                "train",
                "--config",
                str(gn_execute_config),
            ],
        )
    )
    results.append(
        run_step(
            "graph_train_pu_mpnn",
            [
                "graph",
                "train",
                "--config",
                "output/smoke_release/graph/pu_mpnn_train.yaml",
            ],
        )
    )
    mpnn_execute_config = write_execute_config(
        OUTPUT_DIR / "graph" / "pu_mpnn_train.yaml",
        OUTPUT_DIR / "graph" / "pu_mpnn_execute.yaml",
        {"mode": "execute"},
    )
    results.append(
        run_step(
            "graph_train_pu_mpnn_execute",
            [
                "graph",
                "train",
                "--config",
                str(mpnn_execute_config),
            ],
        )
    )
    results.append(
        run_step(
            "strict_invalid_input",
            [
                "recognize",
                "--input-csv",
                "tests/fixtures/invalid_smiles.csv",
                "--output-dir",
                "output/smoke_release/strict_invalid",
                "--strict",
            ],
            expect_success=False,
        )
    )

    summary = {
        "status": "ok",
        "steps": [
            {
                "name": item["name"],
                "returncode": item["returncode"],
                "expected_success": item["expected_success"],
            }
            for item in results
        ],
    }
    summary_path = OUTPUT_DIR / "smoke_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Smoke test completed successfully. Summary: {summary_path}")


if __name__ == "__main__":
    main()
