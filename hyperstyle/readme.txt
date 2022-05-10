For build docker image:
cd <path to directory with Dockerfile>
docker build -t pogrebnoy/ibd-hyperstyle:1.0.0 .

OR

You can pull built image from docker hub:
docker pull pogrebnoy/ibd-hyperstyle:1.0.0

For run container:
docker run --rm \
--mount src=<absolute path to directory with sources>,target=/data,type=bind \
--mount src=<absolute path to output directory>,target=/output,type=bind \
pogrebnoy/ibd-hyperstyle:1.0.0

Example:
docker run --rm \
--mount src=/home/Dmitry.Pogrebnoy/Desktop/python_files,target=/data,type=bind \
--mount src=/home/Dmitry.Pogrebnoy/Desktop,target=/output,type=bind \
pogrebnoy/ibd-hyperstyle:1.0.0

Json file with output will be located in <absolute path to output directory> with name result.json