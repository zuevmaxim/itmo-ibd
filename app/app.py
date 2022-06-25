import csv
import os.path
import sys
import uuid

import celery
import docker
import requests
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

PIPELINE_DOCKER_IMAGE_NAME = "pogrebnoy/ibd-tag-prediction:1.0.0"
DATA_TMP_PATH_INSIDE_DOCKER = "/data_tmp"
RESULT_FILE_NAME = "predicted_tag.csv"

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = celery.Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


# with Flask-WTF, each web form is represented by a class
# "GitCloneLinkForm" can change; "(FlaskForm)" cannot
class GitCloneLinkForm(FlaskForm):
    owner_name = StringField('Github repo owner', validators=[DataRequired()])
    repo_name = StringField('Github repo name', validators=[DataRequired()])
    submit = SubmitField('Suggest tags')


@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = GitCloneLinkForm()
    message = ""
    if form.validate_on_submit():
        owner_name = form.owner_name.data
        repo_name = form.repo_name.data
        response = requests.get(f'https://api.github.com/repos/{owner_name}/{repo_name}', timeout=5)
        if response.status_code == 200:
            # redirect the browser to another route and template
            return redirect(url_for('repo_tags', owner_name=owner_name, repo_name=repo_name))
        else:
            message = "Repository owner or repository name os incorrect!"
    return render_template('index.html', form=form, message=message)


@app.route('/repo_tags/<owner_name>/<repo_name>}')
def repo_tags(owner_name, repo_name):
    original_repo_tags = []
    original_repo_topics_request = requests.get(f"https://api.github.com/repos/{owner_name}/{repo_name}/topics",
                                                timeout=5)
    if original_repo_topics_request.status_code == 200:
        original_repo_tags.extend(original_repo_topics_request.json()["names"])

    data_tmp_dir = os.path.join(app.config["data_tmp_dir"], uuid.uuid4().hex)
    task = suggest_topics.delay(data_tmp_dir, owner_name, repo_name)
    task.wait()

    try:
        with open(os.path.join(data_tmp_dir, RESULT_FILE_NAME), "r") as f:
            reader = csv.reader(f)
            predicted_repo_tags = list(reader)
            # flatten list
            predicted_repo_tags = [tag for tag_signle_list in predicted_repo_tags for tag in tag_signle_list]
            return render_template('repo_tags.html', repo_name=repo_name,
                                   predicted_repo_tags=predicted_repo_tags,
                                   original_repo_tags=original_repo_tags)
    except EnvironmentError as e:
        return render_template('404.html'), 404


@celery.task()
def suggest_topics(data_tmp_dir, owner_name, repo_name):
    # Run pipeline docker container
    docker_client = docker.from_env()
    docker_volumes = {
        f'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'ro'},
        f'{data_tmp_dir}': {'bind': f'{DATA_TMP_PATH_INSIDE_DOCKER}', 'mode': 'rw'},
    }
    docker_environment = [
        f"DATA_TMP={data_tmp_dir}",
        f"GIT_CLONE_LINK=https://github.com/{owner_name}/{repo_name}.git"
    ]
    docker_client.containers.run(PIPELINE_DOCKER_IMAGE_NAME,
                                 auto_remove=True,
                                 stderr=True,
                                 stdout=True,
                                 volumes=docker_volumes,
                                 environment=docker_environment)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    """
        1 argument expected - path to data tmp dir. CAREFULL! This folder cleaned at the beginning!!!
    """

    if len(sys.argv) < 2:
        exit(1)

    app.config['data_tmp_dir'] = sys.argv[1]

    app.run()
