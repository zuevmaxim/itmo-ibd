FROM python:3.9.13-bullseye

RUN apt-get update -y && \
RUN apt-get install -y ca-certificates curl gnupg lsb-release curl && \
RUN mkdir -p /etc/apt/keyrings && \
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
RUN apt-get update -y && \
RUN apt-get install -y docker-ce docker-ce-cli && \
RUN apt-get install -y default-jdk && \
RUN pip install pyspark docker pandas sklearn xgboost

COPY ./data/pipeline/final_tags.csv /final_tags.csv
COPY ./data/pipeline/final_columns.csv /final_columns.csv

COPY ./data/full_import_dataset/lupa_import_to_package/output/kotlin/import_to_package.csv /kotlin_import_to_package.csv
COPY ./data/full_import_dataset/lupa_import_to_package/output/python/import_to_package.csv /python_import_to_package.csv

COPY ./pipeline/new_project_pipeline.py /new_project_pipeline.py
COPY ./pipeline/new_project_pipeline.py /new_project_pipeline.py

RUN mkdir /models
COPY ./classification/models/* /models/
COPY ./classification/results/results.csv /results.csv

CMD rm -rf /data_tmp/* && python new_project_pipeline.py $GIT_CLONE_LINK $DATA_TMP