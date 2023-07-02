from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from kraken import binarization
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from ultralytics import YOLO
from pillow_heif import register_heif_opener
from base64 import b64encode
from io import BytesIO


#######################################################################################
from app import app

register_heif_opener()

model_type = YOLO('./weights/best_type.pt')
model_result = YOLO('./weights/best_result.pt')
qcd = cv2.QRCodeDetector()

from common.pereferences import DEBUG, PORT, HOST, THREADED, TYPES, RESULTS
from common.helpers import convert_to_cv2, convert_to_pillow

@app.route('/')
@app.route('/index')
def source():
    return render_template("index.html")


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


    bw_im = binarization.nlbin(img)

    try:
        d = decode(bw_im, symbols=[ZBarSymbol.QRCODE])[0]

        decoded_info = d.data.decode(encoding='utf-8')

        draw.rectangle(((d.rect.left, d.rect.top), (d.rect.left + d.rect.width, d.rect.top + d.rect.height)),
                   outline=(0, 0, 255), width=3)

        draw.polygon(d.polygon, outline=(0, 255, 0), width=3)
        
        draw.text((d.rect.left, d.rect.top + d.rect.height), d.data.decode(),
              (255, 0, 0))


    except:
        return render_template("result.html", route = "/testing_qr", result = "Null" )

    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

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
    app.run(HOST, PORT, debug=DEBUG, threaded=THREADED)

if __name__ == '__main__':
    main()