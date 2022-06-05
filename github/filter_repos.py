import os
import sys

set_of_supported_extension = {".kt", ".kts", ".js", ".py", ".java"}


def clean_repos(repos_dir):
    for root, _, files in os.walk(repos_dir):
        for file in files:
            splitted_file = os.path.splitext(file)
            if len(splitted_file) < 2:
                os.remove(os.path.join(root, file))
            else:
                file_extension = os.path.splitext(file)[1]
                if file_extension not in set_of_supported_extension:
                    os.remove(os.path.join(root, file))


if __name__ == '__main__':
    """
    Clean repos of unsupported files.
    1 argument expected - path to the folder with repos to be cleaned 
    """
    if len(sys.argv) != 2:
        exit(1)

    repos_dir = sys.argv[1]
    clean_repos(repos_dir)
    print("Now repos are clean!")
