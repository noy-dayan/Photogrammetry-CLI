from scripts.CLI import *

if __name__ == "__main__":
    if not check_admin_permission():
        print(
            "Error: This script requires administrative permission to run. Please start the script with "
            "administrative privileges.")
        exit(1)

    intro_to_string()
    while True:
        user_cmd = input("> ")
        try:
            if cli(user_cmd) == 0:
                exit(0)
        except Exception as e:
            print(f"[ERROR] {e}")
