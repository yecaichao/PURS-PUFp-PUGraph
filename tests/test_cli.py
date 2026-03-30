import unittest
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from purs.cli import build_parser


class CliParserTests(unittest.TestCase):
    def test_cli_parser_builds(self):
        parser = build_parser()
        self.assertIsNotNone(parser)

    def test_cli_parser_allows_help_without_optional_dependencies(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "ml",
                "rf",
                "--feature-csv",
                "features.csv",
                "--target-csv",
                "targets.csv",
                "--id-column",
                "sample_id",
                "--target-column",
                "target",
            ]
        )
        self.assertEqual(args.model_name, "rf")
        self.assertTrue(callable(args.handler))


if __name__ == "__main__":
    unittest.main()
