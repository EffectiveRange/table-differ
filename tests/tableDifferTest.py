import importlib.util
import os
import subprocess
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import openpyxl


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    script_path = command[0]
    script_module_name = os.path.splitext(os.path.basename(script_path))[0]
    spec = importlib.util.spec_from_file_location(script_module_name, script_path)
    script_module = importlib.util.module_from_spec(spec)
    sys.modules[script_module_name] = script_module
    spec.loader.exec_module(script_module)

    with patch.object(sys, 'argv', command):
        with patch('sys.stdout', new=StringIO()) as fake_out, patch('sys.stderr', new=StringIO()) as fake_err:
            try:
                script_module.main()
                return_code = 0
            except SystemExit as error:
                return_code = error.code
            stdout = fake_out.getvalue()
            stderr = fake_err.getvalue()

    result = subprocess.CompletedProcess(args=command, returncode=return_code, stdout=stdout, stderr=stderr)

    print("Return code:", result.returncode)
    if result.stdout:
        print("Output:", result.stdout.rstrip("\n"))
    if result.stderr:
        print("Error:", result.stderr.rstrip("\n"))
    print()

    return result


def normalize_output(output_text):
    sections = output_text.strip("\n").split("\n\n")
    normalized_sections = []

    for section in sections:
        lines = section.splitlines()
        if not lines:
            continue

        header = lines[0]
        if len(lines) <= 2:
            normalized_sections.append("\n".join(lines))
            continue

        table_header = lines[1]
        table_rows = sorted(lines[2:])
        normalized_sections.append("\n".join([header, table_header, *table_rows]))

    return "\n\n".join(normalized_sections) + "\n"


class TableDifferCliTest(unittest.TestCase):
    def test_output_matches_expected(self):
        repo_root = Path(__file__).resolve().parent.parent
        script = repo_root / "bin" / "table-differ.py"
        expected_output_file = repo_root / "tests" / "expected" / "output.txt"

        added_xlsx = repo_root / "tests" / "generated" / "added.xlsx"
        removed_xlsx = repo_root / "tests" / "generated" / "removed.xlsx"
        common_xlsx = repo_root / "tests" / "generated" / "common.xlsx"

        command = [
            str(script),
            f"{repo_root}/tests/test_data/pcb-mrcm-v0.5.0-bom.xlsx",
            f"{repo_root}/tests/test_data/pcb-mrcm-v1.0.4-bom.xlsx",
            "--key",
            "mpn",
            "--exclude",
            "supplier_link",
            "--added-xlsx",
            str(added_xlsx),
            "--removed-xlsx",
            str(removed_xlsx),
            "--common-xlsx",
            str(common_xlsx)
        ]

        result = run_command(command)

        self.assertEqual(result.returncode, 0, result.stderr)

        expected_output = expected_output_file.read_text(encoding="utf-8")
        self.assertEqual(
            normalize_output(result.stdout),
            normalize_output(expected_output),
        )

        def read_xlsx(path):
            wb = openpyxl.load_workbook(path)
            ws = wb.active
            return [[cell.value for cell in row] for row in ws.iter_rows()]

        def sort_xlsx_rows(rows):
            if not rows:
                return rows
            header, data = rows[0], rows[1:]
            data_sorted = sorted(data)
            return [header] + data_sorted

        expected_added_xlsx = repo_root / "tests" / "expected" / "added.xlsx"
        expected_removed_xlsx = repo_root / "tests" / "expected" / "removed.xlsx"
        expected_common_xlsx = repo_root / "tests" / "expected" / "common.xlsx"

        expected_added = sort_xlsx_rows(read_xlsx(expected_added_xlsx))
        expected_removed = sort_xlsx_rows(read_xlsx(expected_removed_xlsx))
        expected_common = sort_xlsx_rows(read_xlsx(expected_common_xlsx))
        actual_added = sort_xlsx_rows(read_xlsx(added_xlsx))
        actual_removed = sort_xlsx_rows(read_xlsx(removed_xlsx))
        actual_common = sort_xlsx_rows(read_xlsx(common_xlsx))

        self.assertEqual(actual_added, expected_added, f"added.xlsx content mismatch: {actual_added}")
        self.assertEqual(actual_removed, expected_removed, f"removed.xlsx content mismatch: {actual_removed}")
        self.assertEqual(actual_common, expected_common, f"common.xlsx content mismatch: {actual_common}")


if __name__ == "__main__":
    unittest.main()
