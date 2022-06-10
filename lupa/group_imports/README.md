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