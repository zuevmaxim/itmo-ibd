import sys

import pandas as pd


def perform_combine(python_batch_import_dir: str, kotlin_batch_import_dir: str,
                    full_import_dataset_dir: str, full_import_dataset_for_lupa_dir: str):
    # Prepare dataset for kotlin imports
    kotlin_imports_datasets = list()
    for i in range(0, 5):
        tmp_dataframe = pd.read_csv(f"{python_batch_import_dir}/import_directives_data_batch_{i}.csv")
        kotlin_imports_datasets.append(tmp_dataframe)
    kotlin_import_dataset = pd.concat(kotlin_imports_datasets)
    kotlin_import_dataset.to_csv(f"{full_import_dataset_for_lupa_dir}/kotlin_import_dataset_for_lupa.csv", index=False)
    # Add language import flags
    kotlin_import_dataset["is_kotlin_import"] = 1
    kotlin_import_dataset["is_python_import"] = 0

    # Prepare dataset for python imports
    python_imports_datasets = list()
    for i in range(0, 5):
        tmp_dataframe = pd.read_csv(f"{kotlin_batch_import_dir}/import_statements_data_batch_{i}.csv")
        python_imports_datasets.append(tmp_dataframe)
    python_import_dataset = pd.concat(python_imports_datasets)
    python_import_dataset.to_csv(f"{full_import_dataset_for_lupa_dir}/python_import_dataset_for_lupa.csv", index=False)

    # Add language import flags
    python_import_dataset["is_kotlin_import"] = 0
    python_import_dataset["is_python_import"] = 1

    # Combine python and kotlin import dataframe - this is the base dataframe for joining other features
    full_dataset = pd.concat([kotlin_import_dataset, python_import_dataset])
    full_dataset.to_csv(f"{full_import_dataset_dir}/full_import_dataset.csv", index=False)


if __name__ == '__main__':
    """
    Combine all batch import datasets
    4 argument expected:
     1 - path to dir with python import output of five batches. 
         Files should be as `import_statements_data_batch_{batch_num}.csv`
     2 - path to dir with kotlin import output of five batches. 
         Files should be as `import_directives_data_batch_{batch_num}.csv`
     3 - path to output dir for save full import dataset 
     4 - path to output dir for save full import dataset for Lupa
     
     path to the folder with repos and path to save result
    """
    if len(sys.argv) != 5:
        exit(1)

    python_batch_import_dir = sys.argv[1]
    kotlin_batch_import_dir = sys.argv[2]
    full_import_dataset_dir = sys.argv[3]
    full_import_dataset_for_lupa_dir = sys.argv[4]
    perform_combine(python_batch_import_dir, kotlin_batch_import_dir, full_import_dataset_dir,
                    full_import_dataset_for_lupa_dir)
