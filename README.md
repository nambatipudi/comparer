# File Comparison Utility

This Python script is designed to compare two files and output the differences in a format that can be used in CI/CD pipelines like GitHub Actions. The script supports various file types, including text files, CSV, Excel, JSON, PDF, and logs, and can retrieve files from local storage, AWS S3, or Azure Blob Storage.

## Features

- **Supported File Types**:
  - Text files (`.txt`, `.log`)
  - CSV files (`.csv`)
  - Excel files (`.xls`, `.xlsx`)
  - JSON files (`.json`)
  - PDF files (`.pdf`)

- **File Source Support**:
  - Local file system
  - AWS S3 (using `boto3`)
  - Azure Blob Storage (using `azure-storage-blob`)

- **Output**:
  - Line-by-line differences for text-based files (txt, log, pdf).
  - Row-by-row and column-by-column differences for CSV and Excel files.
  - JSON attribute differences for JSON files.
  - Output is compatible with GitHub Actions for CI/CD integration.

## Prerequisites

- **Python 3.x**
- AWS and/or Azure credentials if accessing files from cloud storage.

### Install Required Packages

To install the required Python packages, run:

```bash
pip install -r requirements.txt
```

The required packages are:
```text
pandas==2.1.1
PyPDF2==3.0.1
boto3==1.28.75
azure-storage-blob==12.17.0
```

## Usage

### Running the Script

To compare two files, run the script with the paths to the files you want to compare. You can specify local paths, S3 paths (`s3://bucket/key`), or Azure Blob Storage paths (`azure://connection_string/container_name/blob_name`).

```bash
python compare_files.py
```

Example:
```bash
python compare_files.py local/file1.csv s3://mybucket/file2.csv
```

### GitHub Actions Integration

To integrate the script into a GitHub Actions workflow, you can use the following example in your `.github/workflows/compare_files.yml`:

```yaml
name: File Comparison

on:
  push:
    branches:
      - main

jobs:
  compare_files:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run File Comparison
        run: |
          python compare_files.py path/to/file1 path/to/file2

      - name: Display differences
        if: success() && steps.compare_files.outputs.diff
        run: echo "Differences: ${{ steps.compare_files.outputs.diff }}"
```

### Command-Line Arguments

The script supports the following file types and automatically detects the file format based on the file extension:

- `.txt`, `.log`: Line-by-line text comparison
- `.csv`: Row and column comparison
- `.xls`, `.xlsx`: Sheet, row, and column comparison
- `.json`: Attribute-based comparison
- `.pdf`: Line-by-line text extraction and comparison

### Example Commands

#### Compare Two CSV Files:
```bash
python compare_files.py local/file1.csv local/file2.csv
```

#### Compare Two JSON Files:
```bash
python compare_files.py s3://bucket/file1.json azure://connection_string/container/file2.json
```

#### Compare Two PDF Files:
```bash
python compare_files.py local/file1.pdf local/file2.pdf
```

## Output

The script will output the differences in a unified diff format (similar to `git diff`), and the differences will also be captured in GitHub Actions output logs.

### Example Output:
```
--- file1.csv
+++ file2.csv
@@ -1,3 +1,3 @@
 Name, Age, Location
-Alice, 30, New York
+Alice, 31, New York
 Bob, 22, San Francisco
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

If you want to contribute to this project, feel free to submit issues or pull requests.
