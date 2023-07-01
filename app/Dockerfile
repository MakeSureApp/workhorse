FROM python:3.8

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

#ADD app.py /var/server/app.py

COPY . .

EXPOSE 5000

CMD python ./app.py