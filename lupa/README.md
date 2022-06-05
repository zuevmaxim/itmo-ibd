# Lupa tool execution

1. Build docker image. \
To build docker image run following command inside itmo-bd/lupa directory:
```commandline
docker build -t tigina/ibd-lupa:1.0.0 .
```
2. Run docker image. \
To run docker image run following command inside itmo-bd/lupa directory:
```commandline
docker run --rm \
--mount src=<absolute path to directory with sources>,target=/data,type=bind \
--mount src=<absolute path to output directory>,target=/output,type=bind \
tigina/ibd-lupa:1.0.0
```