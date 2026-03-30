from __future__ import annotations

import json
from pathlib import Path

from purs.data.osc_tasks import build_opecm_osc_parent_table, build_paper_style_task_tables


ROOT = Path(__file__).resolve().parents[1]
RAW_OPECM = ROOT / "data" / "external" / "opecm" / "1_raw_data.csv"
OUT_DIR = ROOT / "data" / "testing"


def main() -> dict:
    parent_df = build_opecm_osc_parent_table(RAW_OPECM)
    tables = build_paper_style_task_tables(parent_df)

    parent_path = OUT_DIR / "opecm_osc_parent.csv"
    paper54_path = OUT_DIR / "opecm_paper54_tasks.csv"
    paper67_path = OUT_DIR / "opecm_paper67_tasks.csv"
    summary_path = OUT_DIR / "opecm_paper_tables_summary.json"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables["paper54_parent"].to_csv(parent_path, index=False)
    tables["paper54_tasks"].to_csv(paper54_path, index=False)
    tables["paper67_tasks"].to_csv(paper67_path, index=False)

    summary = {
        "parent_csv": str(parent_path),
        "paper54_tasks_csv": str(paper54_path),
        "paper67_tasks_csv": str(paper67_path),
        "counts": {
            "parent_rows": len(tables["paper54_parent"]),
            "paper54_ready_rows": len(tables["paper54_tasks"]),
            "paper67_ready_rows": len(tables["paper67_tasks"]),
            "valid_smiles_rows": int(tables["paper54_parent"]["expected_valid"].sum()),
            "n_type_rows": int((tables["paper54_tasks"]["paper54_carrier_type"] == "n").sum()),
            "p_type_rows": int((tables["paper54_tasks"]["paper54_carrier_type"] == "p").sum()),
            "tie_rows": int((tables["paper54_tasks"]["paper54_carrier_type"] == "tie").sum()),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    print(f"wrote parent table: {parent_path}")
    print(f"wrote paper54-style tasks: {paper54_path}")
    print(f"wrote paper67-style tasks: {paper67_path}")
    print(json.dumps(summary["counts"], indent=2))
    return summary


if __name__ == "__main__":
    main()
