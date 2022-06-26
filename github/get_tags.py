import sys
import pandas as pd
import requests


def get_tokens_for_project(repo, headers):
    response = requests.get('https://api.github.com/repos/{}/topics'.format(repo), headers=headers)
    if response.status_code != 200:
        print("Failed to get topics with error %d: %s" % (response.status_code, response.text))
        return ""
    return response.json()["names"]


def get_tokens(df, output_file, headers):
    df["tags"] = df["full_name"].apply(lambda x: get_tokens_for_project(x, headers))
    df = df[["full_name", "tags"]]
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    """
    At least 2 argument expected:
    1) path to the repos list
    2) output path

    An additional argument may be passed to enlarge the requests ability:
    3) GitHub personal access token
    """
    if len(sys.argv) < 3:
        exit(1)

    token = None
    if len(sys.argv) > 3:
        token = sys.argv[3]

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    headers = {}
    if token is not None:
        headers['authorization'] = "token %s" % token
    repos = pd.read_csv(input_file)
    get_tokens(repos, output_file, headers)
