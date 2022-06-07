import os
import shutil
import sys

set_of_supported_extension = {".kt", ".kts", ".py", ".java"}


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


def delete_repos(repos_dir):
    repos_to_delete = []
    for repo in os.listdir(repos_dir):
        repo_dir = os.path.join(repos_dir, repo)
        if os.path.isdir(repo_dir):
            delete_repo = True
            for root, _, files in os.walk(os.path.join(repos_dir, repo)):
                if not delete_repo:
                    break
                for file in files:
                    file_name, ext = os.path.splitext(file)
                    if ext in set_of_supported_extension:
                        delete_repo = False
                        break
            if delete_repo:
                repos_to_delete.append(repo_dir)

    for repo_dir in repos_to_delete:
        print(f"Delete repo {repo_dir}")
        try:
            shutil.rmtree(repo_dir)
        except Exception as e:
            print(f"Failed to delete: {e}")


if __name__ == '__main__':
    """
    Clean repos of unsupported files.
    1 argument expected - path to the folder with repos to be cleaned 
    """
    if len(sys.argv) != 2:
        exit(1)

    repos_dir = sys.argv[1]
    delete_repos(repos_dir)
    print("Now repos are clean!")
