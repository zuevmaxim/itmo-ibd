import csv
import logging
import os
import random
import subprocess
import sys
import uuid
from collections import defaultdict

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

import docker


def create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def predict_tags_for_new_project(git_clone_link, absolute_path_to_data):
    spark = (SparkSession
             .builder
             .appName("Process new project pipline")
             .getOrCreate())
    DATA_TMP_FOLDER = "/data_tmp"
    FOLDER_TO_CLONE_REPO = f"{uuid.uuid4().hex}"
    PATH_TO_CLONE_REPO = os.path.join(DATA_TMP_FOLDER, FOLDER_TO_CLONE_REPO)
    GIT_CLONE_LINK = git_clone_link
    PROJECT_OWNER = GIT_CLONE_LINK.split("/")[-2]
    PROJECT_NAME = GIT_CLONE_LINK.split("/")[-1].split(".git")[0]
    PROJECT_PATH = os.path.join(PATH_TO_CLONE_REPO, PROJECT_NAME)

    create_dir(PATH_TO_CLONE_REPO)
    create_dir(PROJECT_PATH)

    # First of all clone repo
    p = subprocess.Popen(['git', 'clone', GIT_CLONE_LINK, PROJECT_PATH, '--depth', '1'])
    return_code = p.wait()
    if return_code != 0:
        logging.info(f'Error while cloning {GIT_CLONE_LINK}!')
        exit(1)

    # Build file extensions count dataset
    cont_extensions = defaultdict(int)
    for root, _, files in os.walk(PROJECT_PATH):
        for filename in files:
            extension = os.path.splitext(filename)[1]
            cont_extensions[extension] += 1
    extensions_metrics = []
    for extension, count in cont_extensions.items():
        extensions_metrics.append((f"{PROJECT_NAME}", extension, count))

    extensions_metrics_dataset = spark.createDataFrame(extensions_metrics).toDF(
        *["project_name", "extension", "count"]).cache()

    def rename_extension(package_name):
        return f"extension#{package_name}"

    udf_rename_extension = F.udf(rename_extension, returnType=StringType())
    # Extension count dataset is ready
    extensions_metrics_dataset = extensions_metrics_dataset.select("project_name",
                                                                   udf_rename_extension("extension").alias("extension"),
                                                                   "count")

    LUPA_DOCKER_IMAGE_NAME = "pogrebnoy/ibd-lupa-extract-imports:1.0.0"

    FOLDER_FOR_LUPA_KOTLIN_OUTPUT = f"{uuid.uuid4().hex}"
    FOLDER_FOR_LUPA_PYTHON_OUTPUT = f"{uuid.uuid4().hex}"
    PATH_TO_LUPA_KOTLIN_OUTPUT = os.path.join(DATA_TMP_FOLDER, FOLDER_FOR_LUPA_KOTLIN_OUTPUT)
    PATH_TO_LUPA_PYTHON_OUTPUT = os.path.join(DATA_TMP_FOLDER, FOLDER_FOR_LUPA_PYTHON_OUTPUT)

    create_dir(PATH_TO_LUPA_KOTLIN_OUTPUT)
    create_dir(PATH_TO_LUPA_PYTHON_OUTPUT)

    # Create docker volumes config for running Lupa
    docker_volumes = {
        f'{os.path.join(absolute_path_to_data, FOLDER_TO_CLONE_REPO)}': {'bind': '/data', 'mode': 'ro'},
        f'{os.path.join(absolute_path_to_data, FOLDER_FOR_LUPA_PYTHON_OUTPUT)}': {'bind': '/output_python',
                                                                                  'mode': 'rw'},
        f'{os.path.join(absolute_path_to_data, FOLDER_FOR_LUPA_KOTLIN_OUTPUT)}': {'bind': '/output_kotlin',
                                                                                  'mode': 'rw'}
    }

    print("Lupa docker volumes")
    print(docker_volumes)

    # Run Lupa in docker container
    docker_client = docker.from_env()
    print("Start Lupa")
    docker_client.containers.run(LUPA_DOCKER_IMAGE_NAME,
                                 auto_remove=True,
                                 # user=f"{os.getuid()}", # Fails lupa with Exception in thread "main" java.lang.RuntimeException: Could not create parent directory for lock file /Lupa/?/.gradle/wrapper/dists/gradle-6.8.3-bin/7ykxq50lst7lb7wx1nijpicxn/gradle-6.8.3-bin.zip.lck
                                 stderr=True,
                                 stdout=True,
                                 volumes=docker_volumes)
    print("Finish Lupa")

    # Take python imports dataset
    python_imports_dataset = spark.read.csv(os.path.join(PATH_TO_LUPA_PYTHON_OUTPUT, "import_statements_data.csv"),
                                            header=True).cache()
    print("Head of python import dataset")
    python_imports_dataset.show()

    # Take kotlin imports dataset
    kotlin_imports_dataset = spark.read.csv(os.path.join(PATH_TO_LUPA_KOTLIN_OUTPUT, "import_directives_data.csv"),
                                            header=True).cache()
    print("Head of kotlin import dataset")
    kotlin_imports_dataset.show()

    # Imports dataset is ready
    imports_dataset = python_imports_dataset.union(kotlin_imports_dataset).cache()
    print("Head of full import dataset")
    imports_dataset.show()

    # Apply mapping import to package
    PATH_TO_IMPORT_TO_PACKAGE_DATASET = "/import_by_package.csv"

    import_to_package_dataset = spark.read.csv(PATH_TO_IMPORT_TO_PACKAGE_DATASET, header=True).toPandas()
    import_to_package_dict = dict(zip(import_to_package_dataset["import"], import_to_package_dataset["package"]))

    def get_package_by_import(lib_import):
        if lib_import in import_to_package_dict:
            return import_to_package_dict[lib_import]
        else:
            return lib_import

    map_import_to_package = F.udf(get_package_by_import, returnType=StringType())

    full_import_dataset = imports_dataset.select(
        "*", map_import_to_package("import").alias("package")
    ).cache()

    # Make final dataset
    intermediate_dataframe = (full_import_dataset.select("*")
                              .groupby(['project_name', 'package'])
                              .agg(F.count("*").alias("count_different_import")))

    def rename_package(package_name):
        return f"package#{package_name}"

    udf_rename_package = F.udf(rename_package, returnType=StringType())

    # Datasets with import and package is ready
    intermediate_dataframe = intermediate_dataframe.select(
        "project_name", udf_rename_package("package").alias("package")
    ).cache()

    # Pivot all built dataset
    pivot_package_dataframe = intermediate_dataframe.groupby("project_name").pivot("package").agg(F.count("*"))
    pivot_ext_count_dataset = extensions_metrics_dataset.groupby("project_name").pivot("extension").agg(
        F.first("count"))

    # Join pivot datasets
    final_dataset = pivot_package_dataframe.join(pivot_ext_count_dataset, ["project_name"])
    final_dataset_dict = final_dataset.collect()[0].asDict(True)

    PATH_TO_COLUMN_DATASET = "/final_columns.csv"

    columns_dataset = spark.read.csv(PATH_TO_COLUMN_DATASET, header=True).toPandas()["column_name"].to_list()
    final_data_for_prediction = []
    for item in columns_dataset:
        if item in final_dataset_dict:
            final_data_for_prediction.append(final_dataset_dict.get(item))
        else:
            final_data_for_prediction.append(0)

    # !!! Push final_data_for_prediction to predictor
    print(final_data_for_prediction)

    # bla bla bla

    PATH_TO_TAG_DATASET = "/final_tags.csv"
    OUTPUT_FILE_NAME = "predicted_tag.csv"

    tags_dataset = spark.read.csv(PATH_TO_TAG_DATASET, header=True).toPandas()["tag_name"].to_list()
    predicted_tags = [tags_dataset[i] for i in random.sample(range(0, len(tags_dataset)), 5)]
    with open(os.path.join(DATA_TMP_FOLDER, OUTPUT_FILE_NAME), 'w') as f:
        write = csv.writer(f)
        write.writerow(["predicted_tag"])
        write.writerows([[tag] for tag in predicted_tags])

    print("Predicted tags:")
    print(predicted_tags)
    print(f"Tags saved to {os.path.join(absolute_path_to_data, OUTPUT_FILE_NAME)}")


if __name__ == '__main__':
    """
    2 argument expected - git clone link in form - https://github.com/OWNER/REPO_NAME.git
    """
    if len(sys.argv) < 3:
        exit(1)

    git_clone_link = sys.argv[1]
    absolute_path_to_data = sys.argv[2]
    predict_tags_for_new_project(git_clone_link, absolute_path_to_data)
