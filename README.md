# table-differ

Creates a diff of two tabular data files (CSV, Excel, etc.) based on a specified key column.
It identifies added, removed, and common rows between the two files and can output the results in Excel format.

```bash
usage: table-differ.py [-h] --key KEY [--exclude [EXCLUDE ...]] [--added-xlsx ADDED_XLSX] [--removed-xlsx REMOVED_XLSX] [--common-xlsx COMMON_XLSX] old_file new_file

positional arguments:
  old_file              Path to old file
  new_file              Path to new file

options:
  -h, --help            show this help message and exit
  --key KEY             Key column name
  --exclude [EXCLUDE ...]
                        Columns to exclude from comparison/output
  --added-xlsx ADDED_XLSX
                        Path to write the added rows as an Excel file
  --removed-xlsx REMOVED_XLSX
                        Path to write the removed rows as an Excel file
  --common-xlsx COMMON_XLSX
                        Path to write the common rows as an Excel file
```
