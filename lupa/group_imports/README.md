# Lupa tool execution for grouping imports to libnames

1. Build docker image. \
   To build docker image run following command inside itmo-bd/lupa directory:

```commandline
docker build -t tigina/ibd-lupa-group-imports:1.0.0 .
```

2. Run docker image. \
   To run docker image run following command inside itmo-bd/lupa directory:

```commandline
docker run --rm \
--mount src=<absolute path to input csv with imports data>,target=/input_data.csv,type=bind \
--mount src=<absolute path to output directory>,target=/output,type=bind \
tigina/ibd-lupa-group-imports:1.0.0
```

docker run --rm \
--mount
src=/home/Dmitry.Pogrebnoy/Desktop/batch_4_python_imports/import_statements_data.csv,target=/input_data.csv,type=bind \
--mount src=/home/Dmitry.Pogrebnoy/Desktop/kaggle_libs,target=/output,type=bind \
tigina/ibd-lupa-group-imports:1.0.0