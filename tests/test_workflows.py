import json
import importlib.util
import tempfile
import unittest
import warnings
from pathlib import Path
import sys
from unittest import mock

import pandas as pd

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

warnings.simplefilter("ignore", DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"pandas\..*")
warnings.filterwarnings("ignore", message=r".*np\.find_common_type is deprecated.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=r".*find_common_type.*deprecated.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"pandas\.core\.algorithms")


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
DATA_TESTING = REPO_ROOT / "data" / "testing"
STANDARD_SAMPLE = DATA_TESTING / "opecm_paper54_tasks.csv"
HAS_WORKFLOW_DEPS = all(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("rdkit", "sklearn", "yaml")
)
HAS_GRAPH_EXEC_DEPS = all(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("torch", "torchgraphs", "pyaml", "tensorboardX", "sparse")
)
if HAS_WORKFLOW_DEPS:
    from sklearn.exceptions import UndefinedMetricWarning

    warnings.filterwarnings("ignore", category=UndefinedMetricWarning)


@unittest.skipUnless(HAS_WORKFLOW_DEPS, "workflow tests require rdkit, scikit-learn, and pyyaml")
class WorkflowTests(unittest.TestCase):
    def _build_fixture_features(self, tmpdir):
        from purs.fingerprint.build import build_pufp

        return build_pufp(
            input_csv=FIXTURES / "mobility_tiny.csv",
            name_column="sample_id",
            smiles_column="smiles",
            output_dir=tmpdir,
        )

    def _build_common_opecm_features(self, tmpdir):
        from purs.fingerprint.build import build_pufp

        return build_pufp(
            input_csv=FIXTURES / "opecm_common_tiny.csv",
            name_column="sample_id",
            smiles_column="smiles",
            output_dir=tmpdir,
        )

    def test_recognize_reports_skipped_invalid_smiles(self):
        from purs.core.recognize import recognize_units

        input_csv = FIXTURES / "invalid_smiles.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            result = recognize_units(input_csv=input_csv, output_dir=tmpdir)
            self.assertEqual(result["total_rows"], 2)
            self.assertEqual(result["sample_count"], 1)
            self.assertEqual(result["skipped_count"], 1)

            skipped_csv = Path(result["skipped_records_csv"])
            self.assertTrue(skipped_csv.exists())
            skipped_text = skipped_csv.read_text(encoding="utf-8")
            self.assertIn("rdkit_parse_failed", skipped_text)

            summary_json = Path(result["run_summary_json"])
            self.assertTrue(summary_json.exists())
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
            self.assertEqual(summary["processed_samples"], 1)
            self.assertEqual(summary["skipped_rows"], 1)

    def test_recognize_strict_mode_writes_failure_summary(self):
        from purs.core.recognize import recognize_units

        input_csv = FIXTURES / "invalid_smiles.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(ValueError, "Strict mode is enabled"):
                recognize_units(input_csv=input_csv, output_dir=tmpdir, strict=True)

            summary_json = Path(tmpdir) / "run_summary.json"
            self.assertTrue(summary_json.exists())
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "failed_due_to_skipped_rows")
            self.assertTrue(summary["strict_mode"])

    def test_recognize_deduplicates_duplicate_names(self):
        from purs.core.recognize import recognize_units

        input_csv = FIXTURES / "duplicate_names.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            recognize_units(input_csv=input_csv, output_dir=tmpdir)
            index_data = Path(tmpdir) / "index_data.csv"
            self.assertTrue(index_data.exists())
            index_df = pd.read_csv(index_data, index_col=0)
            self.assertEqual(index_df.index.tolist(), ["dup", "dup-1", "dup-2"])

    def test_fingerprint_builds_full_output_bundle(self):
        from purs.fingerprint.build import build_pufp

        input_csv = FIXTURES / "tiny_polymers.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_pufp(input_csv=input_csv, output_dir=tmpdir)
            output_dir = Path(result["output_dir"])
            for filename in [
                "ring_total_list.csv",
                "one_hot.csv",
                "number.csv",
                "adjacent_matrix.csv",
                "node_matrix.csv",
                "index_data.csv",
                "ring_df.csv",
                "type_frame.csv",
                "skipped_records.csv",
                "run_summary.json",
            ]:
                self.assertTrue((output_dir / filename).exists(), filename)

    def test_common_opecm_cases_drive_unified_pufp_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self._build_common_opecm_features(tmpdir)
            self.assertEqual(result["skipped_count"], 1)
            self.assertEqual(result["sample_count"], 7)
            summary = json.loads((Path(result["output_dir"]) / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["skipped_rows"], 1)

    def test_graph_dataset_normalizes_name_smiles_and_target_columns(self):
        from purs.graph.dataset import build_graph_input_csv

        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_graph_input_csv(
                input_csv=FIXTURES / "opecm_common_tiny.csv",
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            graph_df = pd.read_csv(result["graph_input_csv"])
            self.assertEqual(graph_df.columns.tolist(), ["Compound ID", "smiles", "PCE_max"])
            self.assertEqual(result["target_column"], "graph_target")

    def test_graph_dataset_detects_common_opecm_graph_target(self):
        from purs.graph.dataset import build_graph_input_csv

        input_csv = FIXTURES / "opecm_common_tiny.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_graph_input_csv(
                input_csv=input_csv,
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            graph_df = pd.read_csv(result["graph_input_csv"])
            self.assertEqual(result["target_column"], "graph_target")
            self.assertIn("PCE_max", graph_df.columns)

    def test_standard_scalar_feature_table_builds_expected_columns(self):
        from purs.ml.feature_fusion import build_standard_scalar_feature_table

        with tempfile.TemporaryDirectory() as tmpdir:
            output_csv = Path(tmpdir) / "scalar_features.csv"
            feature_df = build_standard_scalar_feature_table(
                input_csv=STANDARD_SAMPLE,
                output_csv=output_csv,
            )
            self.assertTrue(output_csv.exists())
            self.assertEqual(
                list(feature_df.columns),
                ["homo", "lumo", "eg", "alpha", "mu"],
            )
            self.assertIn("1", feature_df.index)

    def test_feature_fusion_combines_pufp_and_scalar_features(self):
        from purs.fingerprint.build import build_pufp
        from purs.ml.feature_fusion import build_standard_scalar_feature_table, combine_feature_tables

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            build_result = build_pufp(
                input_csv=FIXTURES / "mobility_tiny.csv",
                name_column="sample_id",
                smiles_column="smiles",
                output_dir=tmp_path / "pufp",
            )
            scalar_csv = tmp_path / "scalar_features.csv"
            build_standard_scalar_feature_table(
                input_csv=STANDARD_SAMPLE,
                output_csv=scalar_csv,
            )
            fused = combine_feature_tables(
                base_feature_csv=Path(build_result["output_dir"]) / "number.csv",
                extra_feature_tables=[scalar_csv],
                output_csv=tmp_path / "fused.csv",
            )
            self.assertEqual(len(fused), 3)
            self.assertGreater(fused.shape[1], 9)
            self.assertIn("homo", fused.columns)

    def test_graph_build_writes_manifests_and_graph_input(self):
        from purs.graph.builders import build_pugraph

        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_pugraph(
                input_csv=FIXTURES / "opecm_common_tiny.csv",
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            self.assertTrue(Path(result["graph_input_csv"]).exists())
            self.assertTrue(Path(result["dataset_manifest_json"]).exists())
            self.assertTrue(Path(result["build_manifest_json"]).exists())
            self.assertTrue(Path(result["pu_gn_exp_train_yaml"]).exists())
            self.assertTrue(Path(result["pu_mpnn_train_yaml"]).exists())

    def test_graph_build_filters_invalid_common_opecm_rows(self):
        from purs.graph.builders import build_pugraph

        input_csv = FIXTURES / "opecm_common_tiny.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_pugraph(
                input_csv=input_csv,
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            graph_df = pd.read_csv(result["graph_input_csv"])
            self.assertEqual(result["skipped_count"], 1)
            self.assertEqual(len(graph_df), 7)
            self.assertNotIn("2", graph_df["Compound ID"].tolist())

    @unittest.skipUnless(HAS_GRAPH_EXEC_DEPS, "legacy graph fallback test requires graph dependencies")
    def test_legacy_graph_adapter_falls_back_to_per_row_build(self):
        from purs.graph import legacy_purs_adapter

        input_csv = FIXTURES / "opecm_common_tiny.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_csv = Path(tmpdir) / "graph_input.csv"
            graph_df = pd.DataFrame(
                {
                    "Compound ID": ["ok-1", "bad-1", "ok-2"],
                    "smiles": ["C", "bad", "CC"],
                    "PCE_max": [1.0, 2.0, 3.0],
                }
            )
            graph_df.to_csv(temp_csv, index=False)

            call_log = []

            def fake_build(rows):
                compound_ids = [row["Compound ID"] for row in rows]
                call_log.append(compound_ids)
                if len(rows) > 1:
                    raise ValueError("bulk failed")
                if rows[0]["Compound ID"] == "bad-1":
                    raise RuntimeError("row failed")
                return {rows[0]["Compound ID"]: object()}

            with mock.patch.object(legacy_purs_adapter, "_build_graph_dist_for_rows", side_effect=fake_build):
                graph_dist = legacy_purs_adapter.build_graph_dist_from_csv(temp_csv)

            self.assertEqual(sorted(graph_dist.keys()), ["ok-1", "ok-2"])
            self.assertEqual(call_log[0], ["ok-1", "bad-1", "ok-2"])
            self.assertEqual(call_log[1:], [["ok-1"], ["bad-1"], ["ok-2"]])
            report_path = temp_csv.with_name("graph_input_legacy_graph_skipped.csv")
            self.assertTrue(report_path.exists())
            report_df = pd.read_csv(report_path)
            self.assertEqual(report_df["Compound ID"].tolist(), ["bad-1"])
            self.assertIn("row failed", report_df["error_message"].iloc[0])

    def test_legacy_mpnn_adapter_falls_back_to_per_row_precheck(self):
        from purs.graph import legacy_mpnn_adapter

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_csv = Path(tmpdir) / "release_check.csv"
            pd.DataFrame(
                {
                    "name": ["ok-1", "bad-1", "ok-2"],
                    "smiles": ["C", "bad", "CC"],
                    "target": [1.0, 2.0, 3.0],
                }
            ).to_csv(temp_csv, index=False)

            def fake_get_mpnn_input(csv_name, sdf_name):
                df = pd.read_csv(csv_name)
                names = df["name"].tolist()
                if len(names) == 1 and names[0] == "bad-1":
                    raise RuntimeError("row failed")
                if "bad-1" in names:
                    raise ValueError("bulk failed")
                return {"rows": names, "sdf": sdf_name}

            with mock.patch.object(legacy_mpnn_adapter, "legacy_get_mpnn_input", side_effect=fake_get_mpnn_input):
                result = legacy_mpnn_adapter.get_mpnn_input(temp_csv, Path(tmpdir) / "full.sdf")

            self.assertEqual(result["rows"], ["ok-1", "ok-2"])
            report_path = temp_csv.with_name("release_check_legacy_mpnn_skipped.csv")
            self.assertTrue(report_path.exists())
            report_df = pd.read_csv(report_path)
            self.assertEqual(report_df["name"].tolist(), ["bad-1"])
            self.assertIn("row failed", report_df["error_message"].iloc[0])

    def test_graph_train_returns_command_wrapper(self):
        from purs.graph.builders import build_pugraph, train_pugraph

        with tempfile.TemporaryDirectory() as tmpdir:
            build_result = build_pugraph(
                input_csv=FIXTURES / "opecm_common_tiny.csv",
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            train_result = train_pugraph(build_result["pu_gn_exp_train_yaml"])
            self.assertEqual(train_result["backend"], "pu_gn_exp")
            self.assertEqual(train_result["mode"], "command_only")
            self.assertFalse(train_result["executed"])
            self.assertIn("polymer_unit.train", " ".join(map(str, train_result["command"])))

            mpnn_result = train_pugraph(build_result["pu_mpnn_train_yaml"])
            self.assertEqual(mpnn_result["backend"], "pu_mpnn")
            self.assertFalse(mpnn_result["executed"])
            self.assertIn("purs.graph.pu_mpnn.prepare", " ".join(map(str, mpnn_result["command"])))
            self.assertTrue(mpnn_result["command"][4].endswith("graph_input.csv"))
            self.assertTrue(mpnn_result["output_pkl"].endswith("genwl3.pkl"))

    def test_graph_train_validates_missing_mpnn_fields(self):
        from purs.graph.builders import train_pugraph

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "bad_mpnn.yaml"
            config_path.write_text("backend: pu_mpnn\nmode: command_only\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must define data_csv"):
                train_pugraph(config_path)

    def test_pu_mpnn_release_check_csv_wrapper(self):
        from purs.graph.pu_mpnn.prepare import build_release_check_csv

        with tempfile.TemporaryDirectory() as tmpdir:
            dst_csv = Path(tmpdir) / "release_check.csv"
            source_csv = Path(tmpdir) / "source.csv"
            input_df = pd.DataFrame(
                {
                    "sample_id": ["1", "2"],
                    "smiles": ["C", "CC"],
                    "PCE_max": [1.0, 2.0],
                }
            )
            input_df.to_csv(source_csv, index=False)
            df = build_release_check_csv(source_csv, dst_csv, limit=2)
            self.assertTrue(dst_csv.exists())
            self.assertEqual(list(df.columns), ["name", "smiles", "target"])
            self.assertEqual(len(df), 2)
            self.assertEqual(df["target"].tolist(), input_df["PCE_max"].tolist())

    def test_ml_rf_quick_runs_on_tiny_fixture(self):
        from purs.ml.rf import run_rf

        with tempfile.TemporaryDirectory() as tmpdir:
            build_result = self._build_fixture_features(tmpdir)
            result = run_rf(
                feature_csv=Path(build_result["output_dir"]) / "number.csv",
                target_csv=FIXTURES / "mobility_tiny.csv",
                id_column="sample_id",
                target_column="target",
                cv=2,
                quick=True,
            )
            self.assertEqual(result["sample_count"], 3)
            self.assertGreater(result["feature_count"], 0)
            self.assertIn("n_estimators", result["best_params"])

    def test_ml_krr_quick_runs_on_tiny_fixture(self):
        from purs.ml.krr import run_krr

        with tempfile.TemporaryDirectory() as tmpdir:
            build_result = self._build_fixture_features(tmpdir)
            result = run_krr(
                feature_csv=Path(build_result["output_dir"]) / "number.csv",
                target_csv=FIXTURES / "mobility_tiny.csv",
                id_column="sample_id",
                target_column="target",
                cv=2,
                quick=True,
            )
            self.assertEqual(result["sample_count"], 3)
            self.assertIn("kernel", result["best_params"])

    def test_ml_svm_quick_runs_on_tiny_fixture(self):
        from purs.ml.svm import run_svm

        with tempfile.TemporaryDirectory() as tmpdir:
            build_result = self._build_fixture_features(tmpdir)
            result = run_svm(
                feature_csv=Path(build_result["output_dir"]) / "number.csv",
                target_csv=FIXTURES / "mobility_tiny.csv",
                id_column="sample_id",
                target_column="target",
                cv=2,
                quick=True,
            )
            self.assertEqual(result["sample_count"], 3)
            self.assertIn("svr__C", result["best_params"])

    def test_ml_rf_classifier_runs_on_synthetic_fixture(self):
        from purs.ml.classification import run_rf_classifier

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            feature_df = pd.DataFrame(
                {
                    "f1": [0, 0, 0, 1, 1, 1, 2, 2, 2],
                    "f2": [0, 1, 2, 0, 1, 2, 0, 1, 2],
                },
                index=[str(i) for i in range(1, 10)],
            )
            target_df = pd.DataFrame(
                {
                    "sample_id": [str(i) for i in range(1, 10)],
                    "label": ["a", "a", "a", "b", "b", "b", "c", "c", "c"],
                }
            )
            feature_csv = tmp_path / "features.csv"
            target_csv = tmp_path / "targets.csv"
            feature_df.to_csv(feature_csv)
            target_df.to_csv(target_csv, index=False)

            result = run_rf_classifier(
                feature_csv=feature_csv,
                target_csv=target_csv,
                id_column="sample_id",
                target_column="label",
                allowed_labels=["a", "b", "c"],
                test_size=1 / 3,
                cv=2,
                quick=True,
                random_state=7,
            )
            self.assertEqual(result["sample_count"], 9)
            self.assertIn("accuracy", result["test_metrics"])
            self.assertEqual(result["test_metrics"]["labels"], ["a", "b", "c"])

    def test_ml_svm_classifier_runs_on_synthetic_fixture(self):
        from purs.ml.classification import run_svm_classifier

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            feature_df = pd.DataFrame(
                {
                    "f1": [0, 0, 0, 1, 1, 1, 2, 2, 2],
                    "f2": [0, 1, 2, 0, 1, 2, 0, 1, 2],
                },
                index=[str(i) for i in range(1, 10)],
            )
            target_df = pd.DataFrame(
                {
                    "sample_id": [str(i) for i in range(1, 10)],
                    "label": ["a", "a", "a", "b", "b", "b", "c", "c", "c"],
                }
            )
            feature_csv = tmp_path / "features.csv"
            target_csv = tmp_path / "targets.csv"
            feature_df.to_csv(feature_csv)
            target_df.to_csv(target_csv, index=False)

            result = run_svm_classifier(
                feature_csv=feature_csv,
                target_csv=target_csv,
                id_column="sample_id",
                target_column="label",
                allowed_labels=["a", "b", "c"],
                test_size=1 / 3,
                cv=2,
                quick=True,
                random_state=7,
            )
            self.assertEqual(result["sample_count"], 9)
            self.assertIn("svc__C", result["best_params"])
            self.assertIn("macro_f1", result["test_metrics"])

    @unittest.skipUnless(HAS_GRAPH_EXEC_DEPS, "graph execute tests require torch, torchgraphs, pyaml, tensorboardX, and sparse")
    def test_graph_train_execute_pu_gn_exp_runs_on_demo(self):
        import yaml
        from purs.graph.builders import build_pugraph, train_pugraph

        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_pugraph(
                input_csv=FIXTURES / "opecm_common_tiny.csv",
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            config_path = Path(result["pu_gn_exp_train_yaml"])
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            cfg["mode"] = "execute"
            cfg["session"]["epochs"] = 1
            cfg["session"]["batch_size"] = 2
            config_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
            train_result = train_pugraph(config_path)
            self.assertTrue(train_result["executed"])
            self.assertIn("Target MSE", train_result["stdout"])
            self.assertIn("Target MAE", train_result["stdout"])
            self.assertNotIn("accuracy", train_result["stdout"].lower())
            run_dir = Path(cfg["output_dir"])
            self.assertTrue((run_dir / "metrics_summary.json").exists())
            self.assertTrue((run_dir / "val_predictions.csv").exists())
            self.assertTrue((run_dir / "checkpoints" / "model.e0001.pt").exists())
            self.assertTrue((run_dir / "model.latest.pt").exists())
            self.assertTrue((run_dir / "experiment.latest.yaml").exists())

    @unittest.skipUnless(HAS_GRAPH_EXEC_DEPS, "graph execute tests require torch, torchgraphs, pyaml, tensorboardX, and sparse")
    def test_graph_train_execute_pu_mpnn_runs_on_demo(self):
        import yaml
        from purs.graph.builders import build_pugraph, train_pugraph

        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_pugraph(
                input_csv=FIXTURES / "opecm_common_tiny.csv",
                output_dir=tmpdir,
                name_column="sample_id",
                smiles_column="smiles",
            )
            config_path = Path(result["pu_mpnn_train_yaml"])
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            cfg["mode"] = "execute"
            config_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
            train_result = train_pugraph(config_path)
            self.assertTrue(train_result["executed"])
            self.assertTrue(Path(train_result["output_pkl"]).exists())
            self.assertIn("saved", train_result["stdout"])


if __name__ == "__main__":
    unittest.main()
