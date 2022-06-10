# syntax=docker/dockerfile:1

FROM openjdk:11-jdk as LUPA

RUN apt-get update -y

RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install build-essential -y
RUN apt-get install python3-dev -y
RUN apt-get install libpq-dev -y
RUN apt-get install postgresql -y
RUN apt-get install git -y

RUN git clone -b quick-fixes-import-to-package-mapping https://github.com/tiginamaria/Lupa.git

WORKDIR /Lupa
RUN pip3 install -r scripts/requirements.txt

WORKDIR /Lupa/scripts
ENV PYTHONPATH=$PYTHONPATH:/Lupa/scripts

RUN pip3 install psycopg2
CMD python3 analysis/dependencies/import_directives_analysis.py --input=/input_data.csv --output=/output