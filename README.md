# validate sample sheet [![GitHub release][release-image]][release-url] [![made-with-python][python-image]][python-url]

Validates Illumina SampleSheets for use with bcl2fastq / bclconvert.

Currently validated fields include:

- <b>Header</b>
    - Check first line is `[Header]`.
    - Check last line is `[Data]`.
    - Check adapters contain only `ATCG`.
    - Check read(s) are valid integers.
    - Check investigator and experiment name set.

</br>

- <b>Sample_ID</b>
    - Check for presence of any non-alphanumeric characters, underscores or dashes.
    - Check for duplicates in sheet.
    - (optional) use given regex patterns to validate sample ID against. Useful for where strict sample ID naming required that may break downstream analysis.

</br>

- <b>Sample_Name</b>
    - Check for presence of any non-alphanumeric characters, underscores or dashes.
    - Check for duplicates in sheet.  


## Requirements

The following Python packages are required:

- `pandas (>v1.0.0)`


## Usage

The only required input to be passed is the path to a sample sheet:
```
# sample sheet with no errors
$ python validate/validate.py --samplesheet Samplesheet.csv

Checking samplesheet for issues

SUCCESS: Samplesheet has passed validation.



# sample sheet with errors

$ python validate/validate.py --samplesheet SampleSheet.csv

Checking samplesheet for issues

Errors found in Sample_ID:

        Invalid characters in sample: 2106557 21211Z0021-BM-MPD-MYE-F-EGG2 in row 45
        Sample_ID in row 51 is missing / invalid: (nan)


Errors found in index:

        Invalid characters found in index: TGTTCCTAGAff at row 22
```

Regex patterns for checking sample IDs are valid against a required specification may be passed
either as strings at the cmd line (`--name_patterns pattern1 pattern2`) or in a file 
(`--name_patterns_file sample_patterns.txt`).

n.b. if passing patterns at the cmd line these must be quoted to stop shell expansion.

```
$ python validate/validate.py --samplesheet SampleSheet.csv 
--name_patterns "[0-9]{7}-[A-Z0-9]*-[A-Za-z0-9-\(\)]*-MYE-[MF]-EGG2"

Errors found in index:

        Invalid characters found in index: TGTTCCTAGAff at row 22


Errors found in Sample_ID:

        Invalid characters in sample: 2106557 21211Z0021-BM-MPD-MYE-F-EGG2 in row 45
        Sample_ID in row 51 is missing / invalid: (nan)
        Sample ID 2106557 21211Z0021-BM-MPD-MYE-F-EGG2 is invalid, please ensure it conforms to the expected format for the given sample assay
        Sample ID 2106298_20-21202Z0083_20-PB-MPD-MYE-M-EGG2 is invalid, please ensure it conforms to the expected format for the given sample assay
        Sample ID 2106298_PH-21202Z0083_PH-PB-MPD-MYE-M-EGG2 is invalid, please ensure it conforms to the expected format for the given sample assay
```




[release-image]: https://img.shields.io/github/v/release/eastgenomics/validate_sample_sheet
[release-url]: https://github.com/eastgenomics/athena/validate_sample_sheet
[python-image]: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
[python-url]: https://www.python.org/
