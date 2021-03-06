"""
Validate Illumina sample sheet against defined requirements.

Currently checks header, sample IDs/names and indices for valid values.
Can also accept a list/file of regex patterns to check sample IDs against to
ensure sample naming conforms to requirements.
See readme for full details on what is checked.

Jethro Rainford 211007
"""
import argparse
import re
import string
import sys

import pandas as pd


class validators():
    """
    Functions to validate each part of sample sheet.
    self.errors is dict used to store any errors found to return / print
    """
    def __init__(self, samplesheet, regex_patterns=None) -> None:
        # self.errors is dict to add errors from each section to
        self.errors = {
            'header': [],
            'Sample_ID': [],
            'Sample_Name': [],
            'index': [],
            'index2': []
        }
        self.samplesheet_body = samplesheet[0]
        self.samplesheet_header = samplesheet[1]
        self.header_count = samplesheet[2] + 1
        self.regex_patterns = regex_patterns

        if isinstance(self.regex_patterns, str):
            # pattern is string and not list, probably passed just one
            self.regex_patterns = [self.regex_patterns]


    def header(self) -> None:
        """
        Validate header against:
        - first line being [Header]
        - having Investigator and Experiment names set
        - Valid value for reads
        - Last line of header is [Data]
        - Column names begin with Sample_ID Sample_Name, all others are
            variable
        """
        header_errors = []

        # regex to match adapter lines as they can be Adapter, Adapter1,
        # AdapterRead1 etc.
        adapter_regex = re.compile("^adapter(read)?[1,2]?", re.IGNORECASE)

        for num, line in enumerate(self.samplesheet_header):
            # check each line of header for specific matches
            if num == 0:
                if not line.startswith('[Header]'):
                    # first line should always be [Header]
                    header_errors.append(
                        f'Error in line {num + 1} of header: value should be [Header]'
                    )

            if line.startswith('Investigator'):
                # check invesitgator name set
                if not line.split(',')[1]:
                    header_errors.append(
                        f'Error in line {num + 1}: no investigator name given'
                    )

            if line.startswith('Experiment'):
                # check experiment name set
                if not line.split(',')[1]:
                    header_errors.append(
                        f'Error in line {num + 1}: no experiment name given'
                    )

            if line.startswith('[Reads]'):
                # check the next line is a valid integer
                if not self.samplesheet_header[num + 1].strip(',').isnumeric():
                    header_errors.append((
                        f'Error in value for [Reads] given on line {num + 1}: '
                        f'{self.samplesheet_header[num + 1].strip(",")}'
                    ))

            if re.search(adapter_regex, line):
                # check given adaptor sequence(s) are valid
                if not all(c in 'ATCGatcg-' for c in line.split(',')[1]):
                    header_errors.append((
                        f'Error in line {num + 1}: invalid adapter sequence '
                        f'{line.split(",")[1]}'
                    ))

            if num == len(self.samplesheet_header) - 2:
                # line before column names should always be [Data]
                if not line.startswith('[Data]'):
                    header_errors.append(
                        f'Error in line {num + 1}: the first cell should contain [Data]'
                    )

        if header_errors:
            self.errors['header'].extend(header_errors)


    def check_name_or_id(self, column) -> None:
        """
        Checks both Sample_Name and Sample_ID columns for valid names
        """
        valid_chars = string.ascii_letters + string.digits + '_' + '-'

        if column == 'Sample_Name':
            if column not in self.samplesheet_body.columns:
                # Sample_Name not required => may not be present
                print(f'{column} not in columns, skipping check')
                return

            if all(self.samplesheet_body[column].isnull()):
                # column name specified but no values entered, not required
                # so print message and continue witout validation errors
                print((
                    'Sample_Name column present but no sample names given, '
                    'continuing...'
                ))
                return

        column_vals = self.samplesheet_body[column].tolist()

        for row, name in enumerate(column_vals):
            if isinstance(name, float):
                # float -> nan value -> empty cell
                self.errors[column].append((
                    f'{column} in row {self.header_count + row} is missing / '
                    f'invalid: ({name})'
                ))
                continue

            if not all(c in valid_chars for c in name):
                # check for any none alphanumeric or -/_ characters
                self.errors[column].append((
                    f'Invalid characters in sample: {name} in row '
                    f'{self.header_count + row}'
                ))

            # check name/id is not too long
            if len(name) > 100:
                self.errors[column].append((
                    f'{column} invalid (> 100 characters) in row '
                    f'{self.header_count + row}: {name} '
                ))


    def check_duplicate_ids(self):
        """
        Check for duplicate sample_ids, they are allowed if either they are on
        different lanes OR the same lane with different indices
        """
        sample_ids = self.samplesheet_body['Sample_ID'].tolist()

        # check for duplicate samples
        duplicates = list(set(
            [x for x in sample_ids if sample_ids.count(x) > 1]
        ))

        if duplicates:
            # found duplicates, check if in different lanes and/or have
            # different indices
            for dup in duplicates:
                # get rows containing duplicate sample IDs
                dup_rows = self.samplesheet_body[
                    self.samplesheet_body['Sample_ID'] == dup
                ]

                # dropping everything except for lane (if present) and index
                # then checking if rows are unique
                check_columns = ['Sample_ID', 'lane', 'Lane', 'index', 'Index']

                for df_col in dup_rows.columns:
                    if df_col not in check_columns:
                        # remove all unneeded columns
                        dup_rows = dup_rows.drop(columns=[df_col])

                total_rows = len(dup_rows.index)

                dup_rows = dup_rows.drop_duplicates(ignore_index=True)

                unique_rows = len(dup_rows.index)

                if total_rows > unique_rows:
                    # if we're here that means we have more than one sample id
                    # with the same lane and / or index which is probably wrong
                    self.errors['Sample_ID'].append(
                        f'Duplicate sample ID found in same lane and / or with '
                        f'same indices: {dup}'
                    )


    def sample_id(self) -> None:
        """
        Validate sample id with check_name_or_id() and uses regex checks
        if regex patterns defined
        """
        # checks for invalid characters
        self.check_name_or_id('Sample_ID')

        # checks for duplicate IDs
        self.check_duplicate_ids()

        # if given, use regex patterns to validate sample ids against
        if self.regex_patterns:
            sample_ids = self.samplesheet_body['Sample_ID'].tolist()

            # compile all regex upfront to make searching faster
            regex_patterns = [re.compile(x) for x in self.regex_patterns]

            for idx, sample in enumerate(sample_ids):
                # for each sample, try each regex to find a match
                if isinstance(sample, float):
                    # float value => empty,
                    # already caught in check_name_or_id() so continue here
                    continue

                for pattern in regex_patterns:
                    match = re.search(pattern, sample)
                    if match:
                        # found match => stop checking current sample
                        break
                if not match:
                    # no matches found in given patterns
                    self.errors['Sample_ID'].append((
                        f'Sample ID {sample} is invalid, please ensure it '
                        'conforms to the expected format for the given sample '
                        'assay'
                    ))


    def sample_name(self) -> None:
        """
        Validate sample name against:
        """
        # checks for duplicates and invalid characters
        self.check_name_or_id('Sample_Name')


    def indices(self) -> None:
        """
        Validate index and index2 columns
        """
        columns = self.samplesheet_body.columns.tolist()

        # find index columns
        index1 = [
            x for x in columns if x.strip('\n') == 'index' or
            x.strip('\n') == 'Index'
        ]
        index2 = [
            x for x in columns if x.strip('\n') == 'index2' or
            x.strip('\n') == 'Index2'
        ]

        if index1:
            self.check_index(index1[0])
        else:
            # should always have at least one set of indices
            self.errors['index'].append(
                'Sample sheet appears to have no index column (index / Index)'
            )

        if index2:
            # not always used, therefore check first
            self.check_index(index2[0])


    def check_index(self, index_column) -> None:
        """
        Validate sample index against for having non ATCG characters and
        duplicates being present in index column
        """
        indices = self.samplesheet_body[index_column].tolist()

        if '2' not in index_column:
            # set key for adding messages to errors dict
            index_key = 'index'
        else:
            index_key = 'index2'

        for row, index in enumerate(indices):
            if not all(c in 'ATCG' for c in index):
                # check for invalid characters
                self.errors[index_key].append((
                    f'Invalid characters found in index: {index} at row '
                    f'{self.header_count + row}'
                ))

        duplicates = duplicates = set([
            x for x in indices if indices.count(x) > 1
        ])

        if duplicates:
            for i in duplicates:
                self.errors[index_key].append(
                    f'Duplicate indices found in {index_key}: {i}'
                )


def validate_sheet(sample_sheet, regex_patterns=None) -> dict:
    """
    Call all functions to validate sample sheet, validate.errors dict will
    be populated with errors if found
    Args:
        - sample_sheet (tuple): contains df of samplesheet data (df), sample
            sheet header (list) and header_count (int)
        - regex_patterns (list): (optional) list of regex patterns to validate
            Sample_ID against for valid sample naming
    Returns:
        - errors (dict): dictionary of errors found in samplesheet, if none
            found will be a dict of keys with empty values
    """
    sample_sheet = read_sheet(sample_sheet)
    validate = validators(sample_sheet, regex_patterns)

    validate.header()
    validate.sample_id()
    validate.sample_name()
    validate.indices()

    return validate.errors


def read_sheet(file) -> tuple:
    """
    Read header and body of samplesheet into df, returned in a tuple

    Args:
        - file (str): name of samplesheet file to validate
    Returns:
        - sample_sheet (tuple): contains df of samplesheet data (df), sample
            sheet header (list) and header_count (int)
    """
    with open(file) as f:
        # read in header of file, column names should always start with Sample_
        samplesheet_header = []
        for count, line in enumerate(f.readlines()):
            if 'Sample_ID' not in line:
                samplesheet_header.append(line.rstrip())
            else:
                # Sample_ID present => line is column names
                samplesheet_header.append(line.rstrip())
                column_names = line.split(',')
                break

        # used to return what row issues are on when looping over data body
        header_count = count + 1

    samplesheet_df = pd.read_csv(
        file, skiprows=header_count, names=column_names
    )

    return (samplesheet_df, samplesheet_header, header_count)


def read_name_patterns(config_file):
    """
    Read regex patterns used for validating sample IDs from file

    Args:
        - config_file (str): filename of config file containing regex patterns
    Returns:
        regex_patterns (list): list of patterns read from file
    """
    with open(config_file) as f:
        regex_patterns = [x.rstrip() for x in f.readlines()]

    return regex_patterns


def parse_args():
    """
    Parse cmd line arguments
    """
    parser = argparse.ArgumentParser(
        description=(
            "Validate Illumina sample sheet against defined requirements. "
            "Requires passing a samplesheet, and optionally a list or file of "
            "regex patterns to validate sample IDs against. "
            "See readme for details."
        )
    )

    parser.add_argument(
        '--samplesheet', required=True,
        help="sample sheet to validate"
    )
    parser.add_argument(
        '--name_patterns', nargs='*', action="store", required=False,
        help='regex pattern(s) against which to validate sample names'
    )
    parser.add_argument(
        '--name_patterns_file', required=False,
        help='file of regex pattern(s) against which to validate sameple names'
    )

    args = parser.parse_args()

    return args


def main():
    # turns off chained assignment warning - not req. as
    # intentionally writing back to df
    # pd.options.mode.chained_assignment = None

    args = parse_args()

    regex_patterns = None

    if args.name_patterns_file:
        # regex patterns given in file, read to list
        regex_patterns = read_name_patterns(args.name_patterns_file)

    if args.name_patterns:
        # regex patterns passed in cmd line arg
        regex_patterns = args.name_patterns

    print(f'\nChecking samplesheet for issues\n')

    # run validation
    errors = validate_sheet(args.samplesheet, regex_patterns)

    if not all(x == [] for x in errors.values()):
        # found some errors => print
        for key, val in errors.items():
            if val:
                print(f'\n\nErrors found in {key}:\n')
                [print(f'\t{x}') for x in val]
    else:
        print(f'\nSUCCESS: Samplesheet has passed validation.\n')


if __name__ == "__main__":
    main()
