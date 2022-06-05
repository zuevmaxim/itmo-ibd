"""
This script allows the user to clone repositories listed in dataset from GitHub.
It accepts
    * path to CSV file --  dataset downloaded from https://seart-ghs.si.usi.ch/
    * path to the output directory, where repositories are cloned
    * allowed extensions to filter, f.e. to save only .kt files
    * index to start from
"""
import logging
import os
import subprocess
import sys

import pandas as pd


def create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def load_repos(csv_path: str, repos_path: str):
    create_dir(repos_path)

    df_repos = pd.read_csv(csv_path)
    os.environ['GIT_TERMINAL_PROMPT'] = '0'
    for i, repo in df_repos.iterrows():
        user = repo['user']
        repo_owner, repo_name = repo['repo'].split('/')[-2:]
        repo_dir_name = f'{user}#{repo_owner}#{repo_name}'
        repo_dir = os.path.join(repos_path, repo_dir_name)
        create_dir(repo_dir)

        p = subprocess.Popen(
            ['git', 'clone', repo['repo'], repo_dir, '--depth', '1'])
        return_code = p.wait()
        if return_code != 0:
            logging.info(f'Error while cloning {repo_dir_name}, skipping..')


if __name__ == '__main__':
    """
    Download repos.
    """
    if len(sys.argv) != 3:
        exit(1)

    csv_path = sys.argv[1]
    repos_path = sys.argv[2]
    load_repos(csv_path, repos_path)
    print("Now repos are loaded!")
