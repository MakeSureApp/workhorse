from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from ultralytics import YOLO
from pillow_heif import register_heif_opener
from base64 import b64encode
from io import BytesIO

from qreader import QReader


from app import app
from app.detection_onnx import detect_objects_on_image
from app.supabase_api import get_n_send

register_heif_opener()

model_type = YOLO('./weights/best_type.pt')
model_result = YOLO('./weights/best_result.pt')

detector = QReader()


from common.pereferences import DEBUG, PORT, HOST, THREADED, TYPES, RESULTS, SECRET_KEY
from common.helpers import convert_to_cv2, convert_to_pillow


@app.before_request
def check_api_key():
    if request.endpoint not in ['static', 'not_need_key_endpoint', 'metrics']:
        api_key = request.headers.get('Api-Key')

        if api_key != SECRET_KEY:
            return jsonify({'error': 'Invalid API key'}), 401

@app.route('/')
@app.route('/index')
def source():
    return "The server is up and running..."


@app.route('/testing_qr')
def testing_qr():
    return render_template("qr_testing.html")

@app.route('/testing_type')
def testing_type():
    return render_template("type_testing.html")

@app.route('/testing_result')
def testing_result():
    return render_template("result_testing.html")

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

@app.route('/qr_recognition', methods = ['POST'])
def qr_recognition():
    img = Image.open(request.files['img'].stream)

    draw = ImageDraw.Draw(img)


    # bw_im = binarization.nlbin(img)

    try:
        decoded_info = detector.detect_and_decode(image=convert_to_cv2(img))[0]
    except:
        return render_template("result.html", route = "/testing_qr", result = "Null" )

    # image_io = BytesIO()
    # img.save(image_io, 'PNG')
    # dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

    return render_template("result.html", route = "/testing_qr", result = decoded_info, result_image = dataurl )


@app.route('/type_recognition', methods = ['POST'])
def type_recognition():
    test_type = ""
    img = Image.open(request.files['img'].stream)

    cv_img = convert_to_cv2(img)

    try:
        results = model_type.predict(cv_img)
        test_type = TYPES[int(results[0].boxes.cls[0])]
        annotated_frame = results[0].plot()

        print(test_type)
    except:
        return render_template("result.html", route = "/testing_type", result = "Null" )

    img = convert_to_pillow(annotated_frame)
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

    return render_template("result.html", route = "/testing_type", result = test_type, result_image = dataurl)

@app.route('/result_recognition', methods = ['POST'])
def result_recognition():
    test_type = ""
    img = Image.open(request.files['img'].stream)

    cv_img = convert_to_cv2(img)

    try:
        results = model_result.predict(cv_img)
        test_result = TYPES[int(results[0].boxes.cls[0])]
        annotated_frame = results[0].plot()

        print(test_type)
    except:
        return render_template("result.html", route = "/testing_result", result = "Null" )

    img = convert_to_pillow(annotated_frame)
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

    return render_template("result.html", route = "/testing_result", result = test_result, result_image = dataurl)


@app.route('/test_results_detection', methods = ['POST'])
def test_results_detection():
    id = ""
    package_id = ""
    test_type = ""
    result = ""
    isActivated = True
    error_code = ""

    img = request.files['img'].stream
    img = Image.open(img)
        
    try:
        decoded_info = detector.detect_and_decode(image=convert_to_cv2(img))[0]
        id, package_id = decoded_info.split('\r\n')

    except:
        return jsonify(id = None, package_id = None, test_type = None, result = None, isActivated = False, error_code = "0")

    try:
        test_type = detect_objects_on_image(img, 'best_type')[0][4]
    except:
        return jsonify(id = id, package_id = package_id, test_type = None, result = None, isActivated = False, error_code = "1")
    
    try:
        result = detect_objects_on_image(img, 'best_result')[0][4]
    except:
        return jsonify(id = id, package_id = package_id, test_type = test_type, result = None, isActivated = False, error_code = "2")


    return jsonify(id = id, package_id = package_id, test_type = test_type, result = result, isActivated = False, error_code = None)

@app.route('/notifi_reducer', methods = ['POST'])
def notifi_reducer():
    get_n_send()

def main():
    app.run(HOST, PORT, debug=DEBUG, threaded=THREADED)

if __name__ == '__main__':
    main()