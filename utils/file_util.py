import os


def get_filenames_in_folder(folder_path):
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
