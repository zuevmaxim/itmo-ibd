# Container for tag prediction for the new project

1. Build docker image. \
   To build docker image run following command inside itmo-bd directory:

```commandline
docker build -t pogrebnoy/ibd-tag-prediction:1.0.0 -f ./pipeline/docker/Dockerfile .
```

2. Run docker image. \
   To run docker image run following command:

```commandline
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v <folder fo storing data>:/data_tmp -e DATA_TMP=<folder fo storing data> -e GIT_CLONE_LINK=<git clone link for github repo> pogrebnoy/ibd-tag-prediction:1.0.0
```

Be aware, that <folder fo storing data> should be the same in two places in command!

For example:

```commandline
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v /home/Dmitry.Pogrebnoy/Desktop/data_tmp:/data_tmp -e DATA_TMP=/home/Dmitry.Pogrebnoy/Desktop/data_tmp -e GIT_CLONE_LINK=https://github.com/zuevmaxim/itmo-ibd.git pogrebnoy/ibd-tag-prediction:1.0.0
```
