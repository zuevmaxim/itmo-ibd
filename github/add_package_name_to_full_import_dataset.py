import os
import sys

import pandas as pd


def perform_adding(full_import_dataset_path: str,
                   kotlin_import_to_package_path: str,
                   python_import_to_package_path: str,
                   output_dir_path: str):
    full_import_dataset = pd.read_csv(full_import_dataset_path)

    kotlin_import_to_package = pd.read_csv(os.path.join(kotlin_import_to_package_path, 'import_to_package.csv'))
    kotlin_package_count = pd.read_csv(os.path.join(kotlin_import_to_package_path, 'total_by_package.csv'))
    kotlin_package_count = kotlin_package_count[kotlin_package_count['count'] > 10]
    kotlin_import_to_package = kotlin_import_to_package[
        kotlin_import_to_package['package'].isin(kotlin_package_count['package'])]

    python_import_to_package = pd.read_csv(os.path.join(python_import_to_package_path, 'import_to_package.csv'))
    python_package_count = pd.read_csv(os.path.join(python_import_to_package_path, 'total_by_package.csv'))
    python_package_count = python_package_count[python_package_count['count'] > 10]
    python_import_to_package = python_import_to_package[
        python_import_to_package['package'].isin(python_package_count['package'])]

    import_to_package = pd.concat([kotlin_import_to_package, python_import_to_package])
    import_to_id = {imp: id for id, imp in enumerate(import_to_package['import'].unique())}
    package_to_id = {pac: id for id, pac in enumerate(import_to_package['package'].unique())}
    import_to_package_dict = {d['import']: d['package'] for i, d in import_to_package.iterrows()}

    pd.DataFrame.from_dict({
        'import': import_to_id.keys(),
        'id': import_to_id.values(),
    }).to_csv(os.path.join(output_dir_path, f'import_to_id.csv'), index=False)

    pd.DataFrame.from_dict({
        'package': package_to_id.keys(),
        'id': package_to_id.values(),
    }).to_csv(os.path.join(output_dir_path, f'package_to_id.csv'), index=False)

    full_import_dataset['import'] = full_import_dataset['import'] \
        .apply(lambda imp: import_to_id.get(imp))
    full_import_dataset = full_import_dataset.dropna()

    full_import_dataset['package'] = \
        full_import_dataset['import'].apply(
        lambda imp: None if import_to_package_dict.get(imp) else package_to_id.get(import_to_package_dict.get(imp)))
    full_import_dataset = full_import_dataset.dropna()

    full_import_dataset.to_csv(os.path.join(output_dir_path, f'full_import_dataset_with_package.csv'), index=False)


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
