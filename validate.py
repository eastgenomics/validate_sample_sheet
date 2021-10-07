"""
Validate Illumina sample sheet against defined requirements.

Jethro Rainford 211007
"""
import argparse
import string
import sys

import pandas as pd


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

        column_names = (
            'Sample_ID,Sample_Name,Sample_Plate,Sample_Well,'
            'Index_Plate_Well,index,index2'
        )

        for num, line in enumerate(self.samplesheet_header):
            # check each line of header for specific matches
            if num == 0:
                if not line == '[Header],,,,,,':
                    header_errors.append(
                        f'Error in line {num + 1} of header: {line}'
                    )

            if num == 2:
                if not line.split(',')[1]:
                    header_errors.append(
                        f'Error in line {num + 1}: no investigator name given'
                    )

            if num == 3:
                if not line.split(',')[1]:
                    header_errors.append(
                        f'Error in line {num + 1}: no experiment name given'
                    )

            if num == 16 or num == 17:
                if not all(c in 'ATCG' for c in line):
                    header_errors.append(
                        f'Error in line {num + 1}: invalid adapter sequence {line}'
                    )

            if num == 19:
                if not line == '[Data],,,,,,':
                    header_errors.append(
                        f'Error in line {num + 1}: the first cell should contain [Data]'
                    )

            if num == 20:
                if column_names not in line:
                    header_errors.append(
                        f'Error in line {num + 1}: invalid column names given'
                    )

            if header_errors:
                self.errors['header'].extend(header_errors)



    def sample_id(self) -> None:
        """
        Validate sample id against:
        """
        valid_chars = string.ascii_letters + string.digits + '_' + '-'

        invalid_id = []

        # check if any ids have any none alphanumeric or -/_ characters
        self.samplesheet_body["Sample_ID"].apply(
            lambda id: invalid_id.append(id) if not all(
                c in valid_chars for c in id
            ) else None
        )

        self.errors['Sample_ID'].extend(invalid_id)


    def sample_name(self) -> None:
        """
        Validate sample name against:
        """
        pass

    def sample_plate(self) -> None:
        """
        Validate sample plate against:
        """
        pass

    def sample_well() -> None:
        """
        Validate sample well against:
        """
        pass

    def index_plate_well() -> None:
        """
        Validate index well against:
        """
        pass

    def index() -> None:
        """
        Validate sample index against:
        """
        pass

    def index2() -> None:
        """
        Validate sample index against:
        """
        pass


def validate_sheet(sample_sheet):
    """

    """
    validate = validators(sample_sheet)

    validate.header()
    validate.sample_id()





def read(file):
    """
    Read header in and body of samplesheet into df
    """
    with open(file) as f:
        samplesheet_header = f.readlines()
        samplesheet_header = [x.rstrip() for x in samplesheet_header[:21]]

    # for i in samplesheet_header:
    #     print(i)

    # sys.exit()

    samplesheet_df = pd.read_csv(
        file, skiprows=21, names=[
            'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
            'Index_Plate_Well', 'index', 'index2'
        ]
    )

    # print(samplesheet_df)

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
