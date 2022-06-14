# Lupa tool execution for extracting imports

1. Build docker image. \
   To build docker image run following command inside itmo-bd/lupa/extract_imports directory:
```commandline
docker build -t tigina/ibd-lupa-extract-imports:1.0.0 .
```
2. Run docker image. \
   To run docker image run following command inside itmo-bd/lupa/extract_imports directory:
```commandline
docker run --rm \
--mount src=<absolute path to directory with sources>,target=/data,type=bind \
--mount src=<absolute path to output directory with python imports>,target=/output_python,type=bind \
--mount src=<absolute path to output directory with kotlin imports>,target=/output_kotlin,type=bind \
tigina/ibd-lupa-extract-imports:1.0.0
```