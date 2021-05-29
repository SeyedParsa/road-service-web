# Road Service System (Web)
A system for reporting the issues citizens find on the road, and for assigning service teams to fixing those issues. This repository contains the back-end, the APIs with which the Andriod app communicates, and the web front-end. The project is an assignment of the Object Oriented Design course offered in the Spring of 2021.

## Development
* Create a virtual environment with python 3.8.2+ using `pip` or `conda`.
* Install the dependencies using `pip install -r` or `conda install --file` both followed by `roadservice/requirements.txt`.
* Make sure you have `docker` installed.
* Create a `.env` file based on the given `sample.env` in `roadservice` and in `docker` folders.
* Run the docker compose file at `docker` folder using `docker compose up -d` to create the PostgreSQL container.
* If you're running the project for the first time, be sure to `migrate` and `createsuperuser`.

