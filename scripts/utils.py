import os


def print_err(error):
    """
    Prints string in error format.

    Parameters:
    - error (str): Error description.
    """
    print(f"\033[31m[ERROR]\033[0m {str(error)}")


def mkdir(dir_str):
    """
    Create a directory if it doesn't exist.

    Parameters:
    - dir_str (str): Directory path.
    """
    try:
        if not os.path.exists(dir_str):
            os.makedirs(dir_str)
    except:
        pass  # Ignore errors if the directory already exists
