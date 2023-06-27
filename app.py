from flask import Flask, request, jsonify
from PIL import Image
import numpy as np

from common.pereferences import DEBUG, PORT

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)