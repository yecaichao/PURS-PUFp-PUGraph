import unittest

import pandas as pd

from purs.data.osc_tasks import (
    PAPER54_CLASS3_LABELS,
    PAPER67_CLASS4_LABELS,
    build_paper_style_task_tables,
    dominant_carrier_label,
    paper54_mobility_class3,
    paper54_mobility_class3_id,
    paper67_mobility_class4,
    paper67_mobility_class4_id,
)


class OscTaskTests(unittest.TestCase):
    def test_dominant_carrier_label(self):
        self.assertEqual(dominant_carrier_label(2.0, 1.0), "n")
        self.assertEqual(dominant_carrier_label(1.0, 2.0), "p")
        self.assertEqual(dominant_carrier_label(1.0, 1.0), "tie")
        self.assertEqual(dominant_carrier_label(None, 1.0), "unknown")

    def test_paper54_class3_thresholds(self):
        self.assertEqual(paper54_mobility_class3(0.0), "low")
        self.assertEqual(paper54_mobility_class3(1.0), "low")
        self.assertEqual(paper54_mobility_class3(1.1), "medium")
        self.assertEqual(paper54_mobility_class3(4.0), "medium")
        self.assertEqual(paper54_mobility_class3(4.1), "high")
        self.assertEqual(paper54_mobility_class3_id(4.1), PAPER54_CLASS3_LABELS.index("high"))

    def test_paper67_class4_thresholds(self):
        self.assertEqual(paper67_mobility_class4(0.0), "0_to_1")
        self.assertEqual(paper67_mobility_class4(1.0), "0_to_1")
        self.assertEqual(paper67_mobility_class4(1.2), "1_to_4")
        self.assertEqual(paper67_mobility_class4(4.0), "1_to_4")
        self.assertEqual(paper67_mobility_class4(4.5), "4_to_10")
        self.assertEqual(paper67_mobility_class4(10.5), "gt_10")
        self.assertEqual(paper67_mobility_class4_id(10.5), PAPER67_CLASS4_LABELS.index("gt_10"))

    def test_build_paper_style_task_tables_filters_ready_rows(self):
        parent_df = pd.DataFrame(
            [
                {
                    "sample_id": "1",
                    "expected_valid": True,
                    "ue": 2.0,
                    "uh": 1.0,
                    "homo": -5.2,
                    "lumo": -3.1,
                    "paper54_carrier_type": "n",
                    "paper54_mobility_class3": "medium",
                    "paper67_ue_class4": "1_to_4",
                    "paper67_uh_class4": "0_to_1",
                    "paper54_ready": True,
                    "paper67_ready": True,
                },
                {
                    "sample_id": "2",
                    "expected_valid": True,
                    "ue": 0.5,
                    "uh": 2.0,
                    "homo": None,
                    "lumo": -3.0,
                    "paper54_carrier_type": "p",
                    "paper54_mobility_class3": "medium",
                    "paper67_ue_class4": "0_to_1",
                    "paper67_uh_class4": "1_to_4",
                    "paper54_ready": True,
                    "paper67_ready": False,
                },
            ]
        )
        tables = build_paper_style_task_tables(parent_df)
        self.assertEqual(len(tables["paper54_parent"]), 2)
        self.assertEqual(tables["paper54_tasks"]["sample_id"].tolist(), ["1", "2"])
        self.assertEqual(tables["paper67_tasks"]["sample_id"].tolist(), ["1"])


if __name__ == "__main__":
    unittest.main()
