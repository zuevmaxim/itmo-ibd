import os
import sys
from collections import defaultdict

import pandas as pd


def count_file_extensions(repos_dir, output_dir):
    data_dict = defaultdict(defaultdict)
    for dirname in os.listdir(repos_dir):
        cont_extensions = defaultdict(int)
        for root, _, files in os.walk(os.path.join(repos_dir, dirname)):
            for filename in files:
                extension = os.path.splitext(filename)[1]
                cont_extensions[extension] += 1
        data_dict[dirname] = cont_extensions
    result = []
    for dirname, dirvalue in data_dict.items():
        for extension, count in dirvalue.items():
            result.append((dirname, extension, count))

    dataframe = pd.DataFrame(result, columns=["project_name", "ext", "count"])
    dataframe.to_csv(os.path.join(output_dir, "extension_count_data.csv"))


if __name__ == '__main__':
    """
    Count files extension count in repos
    2 argument expected - path to the folder with repos and path to save result
    """
    if len(sys.argv) != 3:
        exit(1)

    repos_dir = sys.argv[1]
    output_dir = sys.argv[2]
    count_file_extensions(repos_dir, output_dir)
