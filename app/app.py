from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import cv2
from kraken import binarization

from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol

from ultralytics import YOLO


# import whatimage
from prometheus_flask_exporter import PrometheusMetrics
from pillow_heif import register_heif_opener

register_heif_opener()

types = {
    0: 'HIV',
    1: 'Hepatitis',
    2: 'Syphilis'
}

results = {
    0: 'Negative',
    1: 'Positive',
    2: 'Failure'
}

model_type = YOLO('./weights/best_type.pt')
model_result = YOLO('./weights/best_result.pt')
qcd = cv2.QRCodeDetector()


# from common.pereferences import DEBUG, PORT

app = Flask(__name__)
metrics = PrometheusMetrics(app)

endpoints = ("test_img_sending", "test_results_parse")

#helpers
def convert_to_cv2(img):
    open_cv_image = np.array(img) 
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    
    return open_cv_image


@app.route('/')
def source():
    return 'Server is loaded...'


@app.route('/test_img_sending', methods = ['POST'])
def test_img_sending():
    img = Image.open(request.files['img'].stream)
    cv_img = convert_to_cv2(img)

    return f"loaded image with shape: {cv_img.shape}"


@app.route('/test_results_parse', methods = ['POST'])
def test_results_parse():
    img = Image.open(request.files['img'].stream)
    cv_img = convert_to_cv2(img)


    return jsonify(id = 0, package_id = 0, result = True, isActivated = True)


@app.route('/test_results_detection', methods = ['POST'])
def test_results_detection():
    id = ""
    package_id = ""
    test_type = ""
    result = ""
    isActivated = True
    error_code = ""

    # Get image
    img = request.files['img'].stream
    img = Image.open(img)
    
    bw_im = binarization.nlbin(img)
    
    try:
        decoded_info = decode(bw_im, symbols=[ZBarSymbol.QRCODE])[0].data.decode(encoding='utf-8')
        id, package_id = decoded_info.split('\r\n')

    except:
        return jsonify(id = None, package_id = None, test_type = None, result = None, isActivated = False, error_code = "0")

    cv_img = convert_to_cv2(img)

    try:
        test_type = types[int(model_type.predict(cv_img)[0].boxes.cls[0])]

    except:
        return jsonify(id = id, package_id = package_id, test_type = None, result = None, isActivated = False, error_code = "1")
    
    try:
        result = results[int(model_result.predict(cv_img)[0].boxes.cls[0])]
    except:
        return jsonify(id = id, package_id = package_id, test_type = test_type, result = None, isActivated = False, error_code = "2")


    return jsonify(id = id, package_id = package_id, test_type = test_type, result = result, isActivated = False, error_code = None)

def main():
    app.run("0.0.0.0", 5000, debug=False, threaded=True)

if __name__ == '__main__':
    main()