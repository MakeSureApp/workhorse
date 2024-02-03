from flask import Flask
import secrets
from common.pereferences import DBHOST, DBUSER, DBPASSWORD, DBNAME
import mysql.connector

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

db_config = {
    'host': DBHOST,
    'user': DBUSER,
    'password': DBPASSWORD,
    'database': DBNAME
}

db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

from app import views