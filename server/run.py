from app import app
from common.pereferences import DEBUG, PORT, HOST, THREADED

app.run(HOST, PORT, debug=DEBUG, threaded=THREADED)