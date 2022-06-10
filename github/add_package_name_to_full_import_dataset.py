import sys

import pandas as pd


def perform_adding(full_import_dataset_path, import_by_package_dataset_path, output_dir_path):
    full_import_dataset = pd.read_csv(full_import_dataset_path, index_col=0)

    import_to_package_dataset = pd.read_csv(import_by_package_dataset_path)
    import_to_package_dict = dict(zip(import_to_package_dataset["import"], import_to_package_dataset["package"]))

    def get_package_by_import(lib_import):
        if lib_import in import_to_package_dict:
            return import_to_package_dict[lib_import]
        else:
            return None

    full_import_dataset["package"] = full_import_dataset["import"].map(get_package_by_import)

    full_import_dataset.to_csv(f"{output_dir_path}/full_import_dataset_with_libname.csv")


if __name__ == '__main__':
    """
    Add column with package name of import in full_import_dataset.csv
    3 argument expected:
     1 - path to full import dataset, like full_import_dataset.csv
     2 - path to import to package mapping dataset, like import_by_package.csv
     3 - path to output dir

     path to the folder with repos and path to save result
    """
    if len(sys.argv) != 4:
        exit(1)

    full_import_dataset_path = sys.argv[1]
    import_by_package_dataset_path = sys.argv[2]
    output_dir_path = sys.argv[3]
    perform_adding(full_import_dataset_path, import_by_package_dataset_path, output_dir_path)
