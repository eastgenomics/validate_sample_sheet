"""
Set of tests for testing correct functioning of validate.py.

Uses example test samplesheet in same directory to check for errors.
Errors introduced and covered by tests:
- [Header] missing from first line
- [Data] missing from last line of header
- Investigator name missing
- Experiment name missing
- Correct header count set (number of header lines)
- Check for invalid adapters ('xx' added to 1st adapter, 'zz' added to 2nd)
- Check for invalid indices ('xx added to 1st index for 1st sample, 'zz' to
    2nd index of 1st sample)
- Check for duplicate indices (last index of index1 and index2 duplicated to
    line above)
- Check for invalid characters in sample ID (added a space to id of sample 1)
- Check for invalid characters in sample name (added tilde to name of sample 1)
- Check for missing sample ID / name (deleted both from line 30)
- Check using regex sample id is conforms to specified pattern (regex below,
    added '_' in place of first '-')
- Check for duplicate sample ID and sample name (duplicated last 2 of both)

"""
import os
from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.append(os.path.abspath('../'))

from validate.validate import validate_sheet, validators, read_sheet


# test sample sheet with known errors
test_sample_sheet = f'{Path(__file__).parent.resolve()}/testSampleSheet.csv'

# example regex pattern for given test samplesheet
regex_pattern = "[0-9]{7}-[A-Z0-9]*-[A-Za-z0-9-()]*-MYE-[MF]-EGG2"

# run validation to generate data to test on
sample_sheet = read_sheet(test_sample_sheet)
validate = validators(sample_sheet, regex_pattern)
errors = validate_sheet(test_sample_sheet, regex_pattern)

for key, error in errors.items():
    # if running directly, show error messages for testing
    print(key, error)


def test_self_header_count():
    """
    Check header count is correct, used to know length of header to print
    correct row number. Adds 1 on initialising class
    """
    assert validate.header_count == 22


def test_bad_header_line():
    """
    Test first line is [Header]
    """
    assert (
        "Error in line 1 of header: value should be [Header]"
    ) in errors['header']


def test_bad_data_line():
    """
    Check last line of header is [Data]
    """
    assert (
        "Error in line 20: the first cell should contain [Data]"
    ) in errors['header']


def test_no_invesitgator():
    """
    Check missing investiagtor correctly picked up
    """
    assert "Error in line 3: no investigator name given" in errors['header']


def test_no_experiment():
    """
    Check missing experiment name
    """
    assert "Error in line 4: no experiment name given" in errors['header']


def test_adapter():
    """
    Check for invalid characters in adapter
    """
    assert (
        "Error in line 17: invalid adapter sequence "
        "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAxx"
    ) in errors['header']


def test_adapter2():
    """
    Check for invalid characters in adapter2
    """
    assert (
        "Error in line 18: invalid adapter sequence "
        "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTzz"
    ) in errors['header']


def test_index():
    """
    Check testing for invalid characters in indices
    """
    assert (
        "Invalid characters found in index: ACTAGTGCTTxx at row 22"
    ) in errors["index"]


def test_index2():
    """
    Check testing for invalid characters in indices
    """
    assert (
        "Invalid characters found in index: ACTCTGTTCTzz at row 22"
    ) in errors["index2"]


def test_duplicate_index():
    """
    Check for duplciates in index column
    """
    assert "Duplicate indices found in index: CACGAGTATG" in errors["index"]


def test_duplicate_index2():
    """
    Check for duplciates in index2 column
    """
    assert "Duplicate indices found in index2: CGCTAAGGCT" in errors["index2"]


def test_id_invalid_characters():
    """
    Check for invalid characters in sample id
    """
    assert (
        "Invalid characters in sample: 2107995 21256Z0077-BM-AML-MYE-M-EGG2 "
        "in row 24"
    ) in errors['Sample_ID']


def test_name_invalid_characters():
    """
    Check for invalid characters in sample name
    """
    assert (
        "Invalid characters in sample: 2107909~21251Z0094-BM-MPD-MYE-F-EGG2 "
        "in row 23"
    ) in errors['Sample_Name']


def test_id_regex_check():
    """
    Check given regex correctly picks up invalid named samples
    """
    assert (
        "Sample ID 2107909_21251Z0094-BM-MPD-MYE-F-EGG2 is invalid, please "
        "ensure it conforms to the expected format for the given sample assay"
    ) in errors["Sample_ID"]


def test_missing_id():
    """
    Check for catching missing sample id
    """
    assert (
        "Sample_ID in row 30 is missing / invalid: (nan)"
    ) in errors["Sample_ID"]


def test_missing_name():
    """
    Check for catching missing sample name
    """
    assert (
        "Sample_Name in row 30 is missing / invalid: (nan)"
    ) in errors["Sample_Name"]


def test_duplicate_id():
    """
    Check for duplicated sample ids
    """
    assert (
        "Duplicate Sample ID present: 2107383-21236Z0079-BM-MPD-MYE-F-EGG2"
    ) in errors["Sample_ID"]


def test_duplicate_name():
    """
    Check for duplcicated sample names
    """
    assert (
        "Duplicate Sample Name present: 2107383-21236Z0079-BM-MPD-MYE-F-EGG2"
    ) in errors["Sample_Name"]
