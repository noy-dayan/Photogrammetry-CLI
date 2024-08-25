from CLI import print_err, check_admin_permission, intro_to_string, cli
import os


if __name__ == "__main__":
    """
    Main script for the command-line interface (CLI) application.

    This script handles the user input, executes the corresponding commands, and manages the overall flow of the CLI.
    It utilizes various utility functions and classes to provide an interactive interface for the user.

    Modules:
    - CLI: Contains helper functions such as `print_err`, `check_admin_permission`, `intro_to_string`, and `cli`.

    Execution:
    - The script starts by calling `intro_to_string()` to display an introductory message.
    - It then enters an infinite loop where it continuously prompts the user for input using the `input` function.
    - The user's input is passed to the `cli` function to be processed.
      - If `cli` returns 0, the program exits.
      - If an exception occurs during the execution of `cli`, it is caught and passed to `print_err` to display an error message.
    - The script handles `KeyboardInterrupt` exceptions (e.g., when the user presses Ctrl+C) to allow for graceful exit.

    Special Notes:
    - The script uses `os.system("")` to ensure that ANSI escape codes are enabled on Windows, allowing for colored output in the terminal.

    Usage:
    - Run this script directly in a Python environment to start the CLI.
    - Type commands as prompted to interact with the application.
    - To exit the CLI, use commands such as `-e`, `-stop`, `-quit`, `-exit`, or press Ctrl+C.
    """

    os.system("")

    """
    if not check_admin_permission():
        print_err("This script requires administrative permission to run. Please start the script with administrative "
                  "privileges.")
        exit(1)
    """

    intro_to_string()
    while True:
        try:
            user_cmd = input("\033[35m>\033[0m ")
            try:
                if cli(user_cmd) == 0:
                    exit(0)
            except Exception as e:
                print_err(e)
        except KeyboardInterrupt as e:
            exit(0)
