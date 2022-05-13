import json
import sys
from collections import defaultdict

import pandas as pd


def load_dataframe(path_to_dataframe):
    return pd.read_csv(path_to_dataframe)


def save_dataframe(dataframe, path_to_save):
    dataframe.to_csv(path_to_save, index=False)


def process_hyperstyle_json_output(json_file_path):
    json_file = open(json_file_path)
    json_data = json.load(json_file)

    issues_label = "issues"
    issue_code_label = "code"
    issue_category_label = "category"
    issue_difficulty_label = "difficulty"
    count_label = "count"
    processed_data = {}
    for issue in json_data[issues_label]:
        issue_code = issue[issue_code_label]
        issue_category = issue[issue_category_label]
        issue_difficulty = issue[issue_difficulty_label]

        if issue_code in processed_data:
            value = processed_data[issue_code]
            value[count_label] += 1
            processed_data[issue_code] = value
        else:
            processed_data[issue_code] = {count_label: 1,
                                          issue_category_label: issue_category,
                                          issue_difficulty_label: issue_difficulty}
    processed_dataframe = pd.DataFrame.from_dict(processed_data, orient="index")
    processed_dataframe.reset_index(inplace=True)
    processed_dataframe.rename(columns={"index": issue_code_label}, inplace=True)
    return processed_dataframe


def merge_two_issues_dataframes(old_dataframe, new_dataframe):
    old_dataframe = old_dataframe.set_index("code")
    new_dataframe = new_dataframe.set_index("code")
    squashed_dataframe = old_dataframe.add(new_dataframe, fill_value=0)
    return squashed_dataframe.reset_index("code")


if __name__ == '__main__':
    """
    Process Json output of hyperstyle tool and make dataframe of issues (csv file).
    3 argument expected:
     - path to the json file with hyperstyle output (to json file)
     - path to save new dataframe of issues (to csv file)
     - path to an existing dataframe of issues to merge with the new one (to csv file)
    """
    if len(sys.argv) <= 2:
        exit(1)

    json_file_path = sys.argv[1]
    processed_dataframe_output_path = sys.argv[2]
    processed_dataframe = process_hyperstyle_json_output(json_file_path)

    if len(sys.argv) > 3:
        path_to_existing_dataframe = sys.argv[3]
        old_dataframe = load_dataframe(path_to_existing_dataframe)
        processed_dataframe = merge_two_issues_dataframes(old_dataframe, processed_dataframe)

    print(processed_dataframe)
    save_dataframe(processed_dataframe, processed_dataframe_output_path)
