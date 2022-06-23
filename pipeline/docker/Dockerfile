FROM python:3.9.13-bullseye

RUN apt-get update -y && \
    apt-get install -y ca-certificates curl gnupg lsb-release curl && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update -y && \
    apt-get install -y docker-ce docker-ce-cli && \
    apt-get install -y default-jdk && \
    pip install pyspark docker pandas

COPY ./data/pipeline/final_tags.csv /final_tags.csv
COPY ./data/pipeline/final_columns.csv /final_columns.csv
COPY ./data/full_import_dataset/lupa_import_grouping/output/import_by_package.csv /import_by_package.csv
COPY ./pipeline/new_project_pipeline.py /new_project_pipeline.py

CMD rm -rf /data_tmp/* && python new_project_pipeline.py $GIT_CLONE_LINK $DATA_TMP