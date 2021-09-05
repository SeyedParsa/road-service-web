FROM python:3.8.2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./requirements ./requirements
RUN pip install -r ./requirements/production.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "roadservice.wsgi:application", "--bind", "0.0.0.0:8000"]
