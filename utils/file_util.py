# external imports:
import os
import pandas as pd
import csv


def custom_read_csv(file_name, error_file):
    # Open the CSV file
    with open(file_name, "r") as file, open(error_file, "w") as error_log:
        # Read the first line (header) to determine the number of expected fields
        reader = csv.reader(file)
        header = next(reader)  # Read the header
        expected_num_fields = len(header)

        # Log the header information
        print(f"Header has {expected_num_fields} fields: {header}")
        error_log.write(f"Header has {expected_num_fields} fields: {header}\n")

        # List to collect valid rows
        valid_rows = []

        # Check each row in the CSV file
        for line_num, row in enumerate(
            reader, start=2
        ):  # Start from line 2 (after the header)
            if len(row) == expected_num_fields:
                valid_rows.append(row)
            else:
                # Log the invalid row
                print(f"Line {line_num} has {len(row)} fields: {row}")
                error_log.write(f"Line {line_num} has {len(row)} fields: {row}\n")

    # Convert valid rows into a DataFrame
    df = pd.DataFrame(valid_rows, columns=header)
    return df


def get_filenames_in_folder(folder_path: str):
    """
    Retrieves all the filenames in the specified folder.

    Parameters:
        folder_path (str): The path to the folder from which to retrieve filenames.

    Returns:
        list: A list of filenames in the folder.
    """
    # List to store the filenames
    filenames = []

    # Iterate through all files in the specified folder
    for file_name in os.listdir(folder_path):
        # Check if it's a file (not a directory)
        if os.path.isfile(os.path.join(folder_path, file_name)):
            filenames.append(file_name)

    return filenames
