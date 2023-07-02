# Server part
DEBUG = True
PORT = 5000
HOST = "0.0.0.0"

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
