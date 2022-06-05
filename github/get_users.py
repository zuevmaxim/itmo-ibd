import sys
import requests


def get_users(request_line, output_file, headers):
    page_size = 100
    params = {'per_page': page_size,
              'q': "{} type:user".format(request_line)}
    page = 1
    with open(output_file, 'a') as f:
        while True:
            params['page'] = page
            response = requests.get('https://api.github.com/search/users', params=params, headers=headers)
            if response.status_code != 200:
                print("Failed to make search with error %d: %s" % (response.status_code, response.text))
                break

            results = response.json()['items']
            users = [result['login'] for result in results]
            if len(users) > 0:
                f.writelines([user + "\n" for user in users])
            if len(results) == 0:
                break
            page += 1


if __name__ == '__main__':
    """
    At least 1 argument expected:
    1) path to the output file

    An additional argument may be passed to enlarge the requests ability:
    2) GitHub personal access token
    """
    if len(sys.argv) < 2:
        exit(1)

    token = None
    if len(sys.argv) > 2:
        token = sys.argv[2]

    output_file = sys.argv[1]

    headers = {}
    if token is not None:
        headers['authorization'] = "token %s" % token
    request_line = "itmo"
    get_users(request_line, output_file, headers)
