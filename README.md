# Road Service System (Web)
A system for reporting the issues citizens find on the road, and for assigning service teams to fixing those issues. This repository contains the back-end, the APIs with which the Andriod app communicates, and the web front-end. The project is an assignment of the Object Oriented Design course offered in the Spring of 2021.

## Development
* Create a virtual environment with python 3.8.2+ using `pip` or `conda`.
* Install the dependencies using `pip install -r` or `conda install --file` both followed by `roadservice/requirements/development.txt`.
* Make sure you have `docker` installed.
* Create a file named `.env` based on the given `sample.env` in `roadservice` and in `docker/development` folders.
* Navigate your working direcotry to `docker/development` and run the docker compose file using `docker compose up -d` to create the PostgreSQL service.
* If you're running the project for the first time, be sure to `migrate` and `createsuperuser`.
* To bring down the PostgreSQL service, run `docker compose down` possibly with option `-v`.

## Installation
0. Make sure you have installed [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), [Docker Compose](https://docs.docker.com/compose/install/), and [Docker Compose V2](https://docs.docker.com/compose/cli-command/) on your production server. 
1. Clone the repository on the server.
2. Create a file named `.env` in `docker/production` based on the given `sample.env`.
3. Navigate your working directory to `docker/production`.
4. Run `docker compose up -d --build`. This will create the Django app, PostgreSQL, and Nginx services.
5. Migrate using `docker compose exec web python manage.py migrate --noinput`.
6. Collect the static files into your static root using `docker compose exec web python manage.py collectstatic --noinput --clear`.
7. Create a super user using `docker compose exec web python manage.py createsuperuser`.
8. Your web application is now running on port `1337`.
9. You may need to expose this port for clients using `sudo ufw allow 1337`.
10. Enjoy!
