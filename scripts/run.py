from CLI import print_err, check_admin_permission, intro_to_string, cli
import os

if __name__ == "__main__":
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
