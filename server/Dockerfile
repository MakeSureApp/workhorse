FROM python:3.8

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt-get install zbar-tools -y

ADD requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .

EXPOSE 5000

# CMD python ./run.py

CMD gunicorn -b 0.0.0.0:5000 app:app --log-level=debug --access-logfile=- --error-logfile=- & python bot.py


