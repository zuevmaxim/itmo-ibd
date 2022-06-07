import sys

import pandas as pd


def filter_repos(repos_csv_path: str, filtered_repos_csv_path: str):

    df_repos = pd.read_csv(repos_csv_path, sep='\t')
    print(f'{df_repos.shape[0]} repos loaded')

    df_repos = df_repos[df_repos["language"].isin(["Kotlin", "Python"])]
    print(f'{df_repos.shape[0]} repos left after filtering')

    df_repos['repo'] = df_repos['full_name'].apply(lambda full_name: f'https://github.com/{full_name}')

    df_repos.to_csv(filtered_repos_csv_path, index=False)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        exit(1)

    repos_csv_path = sys.argv[1]
    filtered_repos_csv_path = sys.argv[2]
    filter_repos(repos_csv_path, filtered_repos_csv_path)
    print("Now repos are filtered!")
