import argparse
from typing import List, Optional

import pandas as pd


def compare_excel(old_file: str, new_file: str, key: str, exclude: List[str]) -> None:
    old_df = pd.read_excel(old_file)
    new_df = pd.read_excel(new_file)

    old_df = old_df.drop(columns=exclude, errors="ignore")
    new_df = new_df.drop(columns=exclude, errors="ignore")

    if old_df is None or new_df is None:
        return

    if key not in old_df.columns or key not in new_df.columns:
        raise ValueError(f"Key column '{key}' not found in both files")

    column_order = new_df.columns.tolist()

    old_df = old_df.set_index(key)
    new_df = new_df.set_index(key)

    old_keys = set(old_df.index)
    new_keys = set(new_df.index)

    removed_keys = old_keys - new_keys
    added_keys = new_keys - old_keys
    common_keys = old_keys & new_keys

    removed = old_df.loc[list(removed_keys)]
    added = new_df.loc[list(added_keys)]
    common = new_df.loc[list(common_keys)]

    def format_output(df: pd.DataFrame) -> pd.DataFrame:
        df = df.reset_index()
        df = df.reindex(columns=column_order)
        return df

    print("\n=== Removed rows ===")
    print(format_output(removed).to_string(index=False))

    print("\n=== Added rows ===")
    print(format_output(added).to_string(index=False))

    print("\n=== Common rows ===")
    print(format_output(common).to_string(index=False))


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("old_file")
    parser.add_argument("new_file")
    parser.add_argument("--key", required=True)
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Columns to exclude from comparison/output"
    )

    args = parser.parse_args(argv)

    compare_excel(
        args.old_file,
        args.new_file,
        args.key,
        args.exclude
    )


if __name__ == "__main__":
    main()
