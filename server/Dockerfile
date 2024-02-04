FROM python:3.8

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt-get install zbar-tools -y

ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY . .

EXPOSE 5000

# CMD python ./run.py

CMD ["gunicorn" , "0.0.0.0:5000", "run:app"]
