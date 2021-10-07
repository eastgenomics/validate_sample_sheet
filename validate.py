"""
Validate Illumina sample sheet against defined requirements.

Jethro Rainford 211007
"""
import argparse
from pprint import PrettyPrinter
import string
import sys

import pandas as pd

PPRINT = PrettyPrinter(indent=4).pprint


class validators():
    """

    """
    def __init__(self, samplesheet) -> None:
        self.errors = {
            'header': [],
            'Sample_ID': [],
            'Sample_Name': [],
            'Sample_Plate': [],
            'Sample_Well': [],
            'Index_Plate_Well': [],
            'index': [],
            'index2': []
        }
        self.samplesheet_header = samplesheet[0]
        self.samplesheet_body = samplesheet[1]


    def header(self) -> None:
        """
        Validate header against:
        """
        header_errors = []

        for l in self.samplesheet_header:
            print(l)


        for num, line in enumerate(self.samplesheet_header):
            # check each line of header for specific matches
            print(num)
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
                # check experiment nasme set
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

            if line.startswith('Adapter'):
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

            if num == len(self.samplesheet_header) - 1:
                # final line should column names
                if not line.startswith('Sample_ID,Sample_Name'):
                    header_errors.append((
                        f'Error in line {num + 1}: invalid column names given. '
                        'Sample_ID and Sample_Name must be the first 2 columns'
                    ))

        if header_errors:
            self.errors['header'].extend(header_errors)


    def check_name_or_id(self, column) -> None:
        """
        Checks both Sample_Name and Sample_ID columns for valid names
        """
        valid_chars = string.ascii_letters + string.digits + '_' + '-'

        column_vals = self.samplesheet_body[column].tolist()

        # check for any none alphanumeric or -/_ characters
        invalid_chars = set([
            val for val in column_vals if not all(c in valid_chars for c in val)
        ])

        if invalid_chars:
            for i in invalid_chars:
                self.errors[column].append(
                    f'Invalid characters in sample: {i}'
                )

        # check for duplicate samples
        duplicates = set([x for x in column_vals if column_vals.count(x) > 1])

        if duplicates:
            for dup in duplicates:
                self.errors[column].append(f'Duplicate sample present: {dup}')

        if column == 'Sample_ID':
            for val in column_vals:
                if len(val) > 100:
                    self.errors[column].append(
                        f'Invalid sample ID (> 100 characters): {val}'
                    )


    def sample_id(self) -> None:
        """
        Validate sample id against:
        """
        # checks for duplicates and invalid characters
        self.check_name_or_id('Sample_ID')


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
        index1 = [x for x in columns if x == 'index' or x == 'Index']
        index2 = [x for x in columns if x == 'index2' or x == 'Index2']

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

        invalid_chars = [
            x for x in indices if not all(c in 'ATCG' for c in x)
        ]

        duplicates = duplicates = set([
            x for x in indices if indices.count(x) > 1
        ])

        if '2' not in index_column:
            # set key for adding messages to errors dict
            index_key = 'index'
        else:
            index_key = 'index2'

        if invalid_chars:
            for i in invalid_chars:
                self.errors[index_key].append(
                    f'Invalid characters found in index: {i}'
                )

        if duplicates:
            for i in duplicates:
                self.errors[index_key].append(
                    f'Duplicate indices found in {index_key}: {i}'
                )


def validate_sheet(sample_sheet) -> dict:
    """
    Call all functions to validate sample sheet, validate.errors dict will
    be populated with errors if found
    """
    validate = validators(sample_sheet)

    validate.header()
    validate.sample_id()
    validate.sample_name()
    validate.indices()

    return validate.errors


def read(file) -> tuple:
    """
    Read header and body of samplesheet into df, returned in a tuple
    """
    with open(file) as f:
        # read in header of file, column names should always start with Sample_
        samplesheet_header = []
        for line in f.readlines():
            if not line.startswith('Sample_'):
                samplesheet_header.append(line.rstrip())
            else:
                # read in column names and stop
                samplesheet_header.append(line.rstrip())
                break

    samplesheet_df = pd.read_csv(
        file, skiprows=21, names=[
            'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
            'Index_Plate_Well', 'index', 'index2'
        ]
    )

    return (samplesheet_header, samplesheet_df)


def parse_args():
    """
    Parse cmd line arguments
    """
    parser = argparse.ArgumentParser(
        description="Validate Illumina sample sheet against defined requirements"
    )

    parser.add_argument(
        '--samplesheet', required=True,
        help="sample sheet to validate"
    )
    parser.add_argument(
        '--name', required=False,
        help='regex pattern(s) against whicheah to validate sample name'
    )

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    sample_sheet = read(args.samplesheet)
    errors = validate_sheet(sample_sheet)


    if not all(x == [] for x in errors.values()):
        # found some errors => print
        for key, val in errors.items():
            if val:
                print(f'\n\nErrors found in {key}:\n')
                [print(f'\t{x}') for x in val]


if __name__ == "__main__":
    main()
