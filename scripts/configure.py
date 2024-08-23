import os
from utils import print_err


def set_env_variable(variable_key, variable_value):
    """
    Sets an environment variable to a specified value.

    Parameters:
    - variable_key (str): The name of the environment variable.
    - variable_value (str): The value to set the environment variable to.
    """
    try:
        os.system("SETX {0} {1} /M".format(variable_key, variable_value))
        print(f"Environment variable {variable_key} set to {variable_value}")
    except Exception as e:
        print_err(f"Error setting environment variable {variable_key} to {variable_value}: {e}")


if __name__ == "__main__":
    """
    Sets the ALICEVISION_ROOT environment variable to the path of the 'aliceVision' directory
    located in the project's root directory.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    alicevision_path = os.path.join(project_root, 'aliceVision')
    set_env_variable('ALICEVISION_ROOT', alicevision_path)
