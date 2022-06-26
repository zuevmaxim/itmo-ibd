import csv
import logging
import os
import subprocess
import sys
import uuid
from collections import defaultdict

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from xgboost import XGBClassifier

import docker


def create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def predict_tags(spark, data):
    PATH_TO_TAG_MODELS = "/models"
    PATH_TO_TAG_INFO = "/results.csv"

    results_dataset = spark.read.csv(PATH_TO_TAG_INFO, header=True)
    tag_to_threshold = dict(zip(results_dataset["tag"], results_dataset["trashhold2"]))
    tags = []
    for f in os.listdir(PATH_TO_TAG_MODELS):
        print(f"processing tag {f}")
        tag_name, _ = f.split('.')
        tag = tag_name[4:]
        clf = XGBClassifier()
        clf.load_model(os.path.join(PATH_TO_TAG_MODELS, f))
        threshold = tag_to_threshold[tag_name]
        y_pred_proba = clf.predict_proba([data])
        print(f"pred={y_pred_proba[0]} threshold={threshold}")

        if y_pred_proba[0] > threshold:
            tags.append(tag)

    return tags


def predict_tags_for_new_project(git_clone_link, absolute_path_to_data):
    spark = (SparkSession
             .builder
             .appName("Process new project pipline")
             .getOrCreate())

    DATA_TMP_FOLDER = "/data_tmp"
    FOLDER_TO_CLONE_REPO = f"{uuid.uuid4().hex}"
    PATH_TO_CLONE_REPO = os.path.join(DATA_TMP_FOLDER, FOLDER_TO_CLONE_REPO)
    GIT_CLONE_LINK = git_clone_link
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

    # Apply mapping import to package
    PATH_TO_KOTLIN_IMPORT_TO_PACKAGE_DATASET = "/kotlin_import_to_package.csv"
    PATH_TO_PYTHON_IMPORT_TO_PACKAGE_DATASET = "/python_import_to_package.csv"

    kotlin_import_to_package_dataset = spark.read.csv(PATH_TO_KOTLIN_IMPORT_TO_PACKAGE_DATASET, header=True)
    python_import_to_package_dataset = spark.read.csv(PATH_TO_PYTHON_IMPORT_TO_PACKAGE_DATASET, header=True)

    kotlin_imports_dataset = kotlin_imports_dataset \
        .join(kotlin_import_to_package_dataset,
              kotlin_imports_dataset("import") == kotlin_import_to_package_dataset("import"),
              "inner")

    python_imports_dataset = python_imports_dataset \
        .join(kotlin_import_to_package_dataset,
              python_imports_dataset("import") == python_import_to_package_dataset("import"),
              "inner")

    udf_rename_kotlin_package = F.udf(lambda package: f'package#kotlin#{package}', returnType=StringType())
    kotlin_imports_dataset = kotlin_imports_dataset \
        .select("project_name", udf_rename_kotlin_package("package").alias("package"))

    udf_rename_python_package = F.udf(lambda package: f'package#python#{package}', returnType=StringType())
    python_imports_dataset = python_imports_dataset \
        .select("project_name", udf_rename_python_package("package").alias("package"))

    # Imports dataset is ready
    full_imports_dataset = python_imports_dataset.union(kotlin_imports_dataset).cache()
    print("Head of full import dataset")
    full_imports_dataset.show()

    # Make final dataset
    intermediate_dataframe = (full_imports_dataset.select("*")
                              .groupby(['project_name', 'package'])
                              .agg(F.count("*").alias("count_different_import")))

    udf_rename_extension = F.udf(lambda extension: f"ext#{extension}", returnType=StringType())

    extensions_metrics_dataset = extensions_metrics_dataset.select(
        "project_name", udf_rename_extension("extension").alias("extension")
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

    predicted_tags = predict_tags(spark, final_data_for_prediction)

    OUTPUT_FILE_NAME = "predicted_tag.csv"

    # predicted_tags = [tags_dataset[i] for i in random.sample(range(0, len(tags_dataset)), 5)]
    with open(os.path.join(DATA_TMP_FOLDER, OUTPUT_FILE_NAME), 'w') as f:
        write = csv.writer(f)
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
