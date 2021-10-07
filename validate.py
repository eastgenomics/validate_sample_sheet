"""
Validate Illumina sample sheet against defined requirements.

Jethro Rainford 211007
"""
import argparse
import sys

import pandas as pd


class validators():
    """

    """
    def __init__(self) -> None:
        self.errors = {}

    def header():
        """
        Validate header against:
        """
        pass

    def sample_id():
        """
        Validate sample id against:
        """
        pass

    def sample_name():
        """
        Validate sample name against:
        """
        pass

    def sample_plate():
        """
        Validate sample plate against:
        """
        pass

    def sample_well():
        """
        Validate sample well against:
        """
        pass

    def index_plate_well():
        """
        Validate index well against:
        """
        pass

    def index():
        """
        Validate sample index against:
        """
        pass

    def index2():
        """
        Validate sample index against:
        """
        pass


def validate_sheet(sample_sheet):
    """

    """
    samplesheet_header = sample_sheet[0]
    samplesheet_df = sample_sheet[1]

    val = validators()




def read(file):
    """
    Read header in and body of samplesheet into df
    """
    with open(file) as f:
        samplesheet_header = f.readlines()
        samplesheet_header = [x.rstrip() for x in samplesheet_header[:20]]

    samplesheet_df = pd.read_csv(
        file, skiprows=21, names=[
            'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
            'Index_Plate_Well', 'index', 'index2'
        ]
    )

    print(samplesheet_df)

    sample_sheet = (samplesheet_header, samplesheet_df)

    return sample_sheet


def parse_args():
    """
    
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
    validate_sheet(sample_sheet)


if __name__ == "__main__":
    main()
