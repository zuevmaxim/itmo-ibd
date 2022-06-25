import os
import sys

import pandas as pd


def get_imports_to_packages(df_full: pd.DataFrame, import_to_package_path: str, min_count: int = 10) -> pd.DataFrame:
    import_to_package = pd.read_csv(os.path.join(import_to_package_path, 'import_to_package.csv'))
    import_to_package = import_to_package.groupby(['import', 'package']).first().reset_index()

    package_count = pd.read_csv(os.path.join(import_to_package_path, 'total_by_package.csv'))
    package_count = package_count[package_count['count'] >= min_count]
    import_to_package = import_to_package[import_to_package['package'].isin(package_count['package'])]

    import_dataset_with_package = df_full.merge(import_to_package, how='inner', on='import')

    return import_dataset_with_package


def perform_adding(full_import_dataset_path: str,
                   kotlin_import_to_package_path: str,
                   python_import_to_package_path: str,
                   output_dir_path: str):
    full_import_dataset = pd.read_csv(full_import_dataset_path)

    kotlin_import_with_package = get_imports_to_packages(
        full_import_dataset[full_import_dataset['is_kotlin_import'] == 1], kotlin_import_to_package_path)

    python_import_with_package = get_imports_to_packages(
        full_import_dataset[full_import_dataset['is_python_import'] == 1], python_import_to_package_path)

    import_to_package = pd.concat([kotlin_import_with_package, python_import_with_package])

    import_to_package.to_csv(os.path.join(output_dir_path, f'full_import_dataset_with_package.csv'), index=False)


if __name__ == '__main__':
    """
    Add column with package name of import in full_import_dataset.csv
    3 argument expected:
     1 - path to full import dataset, like full_import_dataset.csv
     2 - path to kotlin import to package mapping directory with dataset (like import_to_package.csv) and package counts (total_by_package.csv)
     3 - path to python import to package mapping directory with dataset (like import_to_package.csv) and package counts (total_by_package.csv)
     4 - path to output dir

     path to the folder with repos and path to save result
    """
    if len(sys.argv) != 5:
        exit(1)

    full_import_dataset_path = sys.argv[1]
    kotlin_import_to_package_path = sys.argv[2]
    python_import_to_package_path = sys.argv[3]
    output_dir_path = sys.argv[4]
    perform_adding(full_import_dataset_path, kotlin_import_to_package_path,
                   python_import_to_package_path, output_dir_path)
