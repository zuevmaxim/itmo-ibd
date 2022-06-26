# Github Topic Suggester
[![License](https://img.shields.io/badge/License-MIT%202.0-blue.svg)](https://github.com/zuevmaxim/itmo-ibd/blob/master/LICENSE)

A tool for suggesting topics related to the project on Github based on packages used in the project.

The tool uses [Lupa](https://github.com/JetBrains-Research/Lupa) analyzer for extract information about the packages used in the project and 
supports only Python and Kotlin project for now.

# Demo
This is a demo of the Github Topic Suggester.

The user enters the owner and name of the repository on Github and clicks "Suggest". 
After a few minutes of waiting, he gets the recommended topics for his project!

Take a look on it!

[//]: # (Insert demo video)

You can run the demo yourself using the instructions [here](https://github.com/zuevmaxim/itmo-ibd/tree/master/app).

# Pipeline suggesting topics
The pipeline for processing a new project and suggesting topics for it is as follows.
 1. Clone repository from Github
 2. Apply [Lupa](https://github.com/JetBrains-Research/Lupa) analyser
for extracting package imports from the project
 3. Made some processing
 4. Predict relative topics
 5. Save suggested topics to file

You can find more information about the pipeline [here](https://github.com/zuevmaxim/itmo-ibd/tree/master/pipeline).

# Used technologies
 * Docker - runs [Lupa](https://github.com/JetBrains-Research/Lupa) and pipeline
 * Spark - data processing and pipeline processing
 * XGBoost - builds topic predictor
 * Flask - builds demonstration app 
 * Celery - runs the docker container with pipeline on a separate worker

# Team
 * Dmitry Pogrebnoy
 * Maria Tigina
 * Maxim Zuev
 * Ksenia Razheva