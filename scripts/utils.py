import os
import time


def print_err(error):
    """
    Prints a string in error format with red color.

    Parameters:
    - error (str): Error description.
    """
    print(f"\033[31m[ERROR]\033[0m {str(error)}")


def mkdir(dir_str):
    """
    Create a directory if it doesn't exist.

    Parameters:
    - dir_str (str): Directory path.

    Raises:
    - OSError: If the directory creation fails.
    """
    try:
        if not os.path.exists(dir_str):
            os.makedirs(dir_str)
    except OSError as e:
        print_err(f"Failed to create directory {dir_str}: {e}")


def number_to_shortcut(number):
    """
    Converts a number to its shorthand notation ensuring all values are expressed in terms of 'k' or 'm'.

    Parameters:
    - number (int or float): The number to convert.

    Returns:
    - str: The number in shorthand notation.
    """
    if number >= 1_000_000_000:
        return f'{number / 1_000_000:.0f}m'
    elif number >= 1_000_000:
        return f'{number / 1_000:.0f}k'
    elif number >= 1_000:
        return f'{number / 1_000:.0f}k'
    else:
        return str(number)


def measure_run_time(func, *args, **kwargs):
    """
    Measures the time taken to execute a function and returns the elapsed time along with the function's result.

    Parameters:
    - func (callable): The function to execute.
    - *args: Positional arguments to pass to the function.
    - **kwargs: Keyword arguments to pass to the function.

    Returns:
    - tuple: A tuple containing the elapsed time as a string in 'HH:MM:SS.ss' format and the result of the function.
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()

    # Calculate elapsed time
    hours, rem = divmod(end_time - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    elapsed_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

    return elapsed_time, result if result is not None else None


def clear_file(file_path):
    """
    Clears the contents of a file by opening it in write mode, which truncates the file.

    Parameters:
    - file_path (str): Path to the file to clear.

    Raises:
    - OSError: If there is an issue accessing or modifying the file.
    """
    try:
        open(file_path, 'w').close()
    except OSError as e:
        print_err(f"Failed to clear file {file_path}: {e}")


def append_file(file_path, text):
    """
    Appends a string to a file. If the file does not exist, it will be created.

    Parameters:
    - file_path (str): Path to the file where the text will be appended.
    - text (str): The text to append to the file.

    Raises:
    - OSError: If there is an issue accessing or modifying the file.
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(text + '\n')
    except OSError as e:
        print_err(f"Failed to append to file {file_path}: {e}")


def count_faces_in_obj(file_path):
    """
    Counts the number of faces in an OBJ file.

    The function reads an OBJ file and counts the lines that start with 'f ', which denotes a face in the OBJ format.

    Parameters:
    - file_path (str): Path to the OBJ file.

    Returns:
    - int: The number of faces in the OBJ file. Returns 1,000,000 if the file is not found or an error occurs.

    Raises:
    - FileNotFoundError: If the specified file does not exist.
    - Exception: For other unexpected errors while reading the file.

    Notes:
    - If an error occurs (e.g., the file is not found or another issue is encountered), the function logs an error message
      and returns 1,000,000 as a fallback value. This behavior allows the calling function to handle such cases without
      immediately terminating execution.
    """
    try:
        with open(file_path, 'r') as file:
            face_count = sum(1 for line in file if line.startswith('f '))
        return face_count
    except FileNotFoundError as e:
        print_err(f"File not found: {e}")
    except Exception as e:
        print_err(f"An error occurred: {e}")
    return 1_000_000


def check_admin_permission():
    """
    Checks if the current script is running with administrative privileges.

    Returns:
    - bool: True if the script has administrative privileges, False otherwise.

    This function attempts to create and then remove a directory in the root of the C: drive to test if the
    current process has administrative permissions. If it succeeds, the script is running with admin rights.
    If it fails with a `PermissionError`, it indicates that the script does not have sufficient permissions.

    Note:
    - This function is intended for use on Windows systems where the ability to write to the C: drive root
      is restricted to administrators.
    - Use this function to check if elevated privileges are available before performing operations
      that require admin rights.
    """
    try:
        # Check for administrative privileges by attempting to create a folder in C:\
        if not os.path.isdir("C:\\TestAdminPermission"):
            os.makedirs("C:\\TestAdminPermission")
        os.rmdir("C:\\TestAdminPermission")
        return True
    except PermissionError:
        return False

