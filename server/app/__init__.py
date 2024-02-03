from flask import Flask
import secrets
from common.pereferences import DBHOST, DBUSER, DBPASSWORD, DBNAME, DBPORT
import mysql.connector

from prometheus_flask_exporter import PrometheusMetrics



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

metrics = PrometheusMetrics(app)

db_config = {
    'host': DBHOST,
    'port': DBPORT,
    'user': DBUSER,
    'password': DBPASSWORD,
    'database': DBNAME
}

db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

from app import views