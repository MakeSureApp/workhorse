import os
from dotenv import load_dotenv

load_dotenv()

# Server part
DEBUG = False
PORT = 5000
HOST = "0.0.0.0"
SECRET_KEY = os.getenv('SECRET_KEY')
THREADED = True

# DB part
DBHOST = "149.154.71.67"
DBPORT = 3306
DBUSER = "main_admin"
DBPASSWORD = 'Accessors231'
DBNAME = 'my_api_keys_db'


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
