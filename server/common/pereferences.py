import os
from dotenv import load_dotenv

load_dotenv()

# Server part
DEBUG = False
PORT = 5000
HOST = "0.0.0.0"
SECRET_KEY = os.getenv('SECRET_KEY')
THREADED = True

# Recognition part
TYPES = {
    0: 'HIV',
    1: 'Hepatitis',
    2: 'Syphilis'
}

RESULTS = {
    0: 'Negative',
    1: 'Positive',
    2: 'Failure'
}
