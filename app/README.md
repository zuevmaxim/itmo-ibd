# Topic suggestion demo

This is an example of a web application to demonstrate the work of a pipeline for predicting topics on libraries imports
for repositories from Github.

The demo is written in Flash and uses Celery to execute a docker container with a pipeline in a separate worker.

## Example

## How to run

1. Install redis package to your venv

```bash
pip install redis
```

2. Run docker container with redis

```bash
docker run -d -p 6379:6379 redis
```

3. Run Celery worker by command from directory `/itmo-ibd/app` and using your `venv`

```bash
celery --app app.celery worker --loglevel=info
```

4. Finally run Flask demo app from `/itmo-ibd/app` using your `venv`

```bash
python app.py <path to folder for tmp data>
```