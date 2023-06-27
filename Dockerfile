FROM python:3.8

# RUN pip install pipenv

# COPY Pipfile* /tmp/

# RUN cd /tmp

# RUN pipenv lock --keep-outdated --requirements

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]