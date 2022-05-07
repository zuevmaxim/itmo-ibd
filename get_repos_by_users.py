import sys
import pandas as pd

import requests


def get_repos(username, headers):
    page_size = 100
    params = {'type': 'all', 'per_page': page_size}
    repos = []
    page = 1
    while True:
        params['page'] = page
        response = requests.get("https://api.github.com/users/%s/repos" % username, params=params, headers=headers)
        if response.status_code != 200:
            print("Failed to get repos for user %s with error %d: %s" % (username, response.status_code, response.text))
            break
        new_repos = [repo['html_url'] for repo in response.json()]
        repos += new_repos
        page += 1
        if len(new_repos) < page_size:
            break
    return repos


def get_repos_by_users(users, token=None):
    """
    Find all repositories that given users are related to.
    :param users: list of users to get repositories
    :param token: optional GitHub personal access token to enlarge requests abilities
    :return: pandas dataframe with repos
    """
    headers = {}
    if token is not None:
        headers['authorization'] = "token %s" % token

    d = {'user': [], 'repo': []}
    for user in users:
        repos = get_repos(user, headers)
        d['user'] += [user] * len(repos)
        d['repo'] += repos
    return pd.DataFrame.from_dict(d)


def get_users(file):
    with open(file, 'r') as f:
        return f.read().splitlines()


if __name__ == '__main__':
    """
    At least 2 arguments expected:
    1) path to a text file with new line separated list of GitHub user names
    2) path to the output CSV file
    
    An additional argument may be passed to enlarge the requests ability:
    3) GitHub personal access token
    """
    if len(sys.argv) < 3:
        exit(1)

    token = None
    if len(sys.argv) > 3:
        token = sys.argv[3]

    users_file = sys.argv[1]
    repos_file = sys.argv[2]

    users = get_users(users_file)

    repos = get_repos_by_users(users, token)
    repos.to_csv(repos_file, index=False)
