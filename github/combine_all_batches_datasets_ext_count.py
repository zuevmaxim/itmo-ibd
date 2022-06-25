import sys

import pandas as pd


def perform_combine(batch_import_dir, full_output_dir):
    # Prepare dataset
    datasets = list()
    for i in range(0, 5):
        tmp_dataframe = pd.read_csv(f"{batch_import_dir}/extension_count_data_batch_{i}.csv", index_col=0)
        datasets.append(tmp_dataframe)
    dataset = pd.concat(datasets)
    dataset.to_csv(f"{full_output_dir}/full_ext_count_dataset.csv", index=False)


if __name__ == '__main__':
    """
    Combine all batch of ext count datasets
    2 argument expected:
     1 - path to dir with ext count of five batches. 
         Files should be as `extension_count_data_btach_{batch_num}.csv`
     2 - path to output dir. 
    """
    if len(sys.argv) != 3:
        exit(1)

    batch_import_dir = sys.argv[1]
    full_output_dir = sys.argv[2]
    perform_combine(batch_import_dir, full_output_dir)
