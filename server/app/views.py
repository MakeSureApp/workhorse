from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
#from ultralytics import YOLO
from pillow_heif import register_heif_opener
from base64 import b64encode
from io import BytesIO
import uuid
import tempfile
import threading
import json
import requests

#from qreader import QReader

from app import app
#from app.detection_onnx import detect_objects_on_image
from app.supabase_api import get_n_send

register_heif_opener()

# model_type = YOLO('./weights/best_type.pt')
# model_result = YOLO('./weights/best_result.pt')

#detector = QReader()


from common.pereferences import DEBUG, PORT, HOST, THREADED, TYPES, RESULTS, SECRET_KEY, BOT_TOKEN, CHAT_ID
from common.helpers import convert_to_cv2, convert_to_pillow

CHAT_ID_FILE = 'chat_ids.txt'

def get_all_chat_ids():
    with open(CHAT_ID_FILE, 'r') as file:
        chat_ids = file.read().splitlines()
    return chat_ids

@app.before_request
def check_api_key():
    if request.endpoint not in ["/index","index",'static', "test_results_detection", "/test_results_detection",'checker', 'metrics', '/metrics', 'prometheus_metrics']:
        print('Имя эндпоинта:', request.endpoint)

        
# @app.route('/checker', methods=['POST'])
# def checker():
#     data = request.json

#     key_name = data.get('name')
#     key_value = data.get('key')

#     if key_name is None or key_value is None:
#         return "Missing 'name' or 'key' in the request data", 400

#     query = "SELECT api_key FROM api_credentials  WHERE service_name = %s"
#     cursor.execute(query, (key_name,))
#     result = cursor.fetchone()

#     if result is not None and result[0] == key_value:
#         # Если ключ совпадает, возвращаем "OK"
#         return "OK"
#     elif result is not None:
#         # Если ключ не совпадает, возвращаем значение ключа из базы данных
#         return result[0]
#     else:
#         return "NOT KEY NAME"

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
        #decoded_info = detector.detect_and_decode(image=convert_to_cv2(img))[0]
        print("lol")
    except:
        return render_template("result.html", route = "/testing_qr", result = "Null" )

    # image_io = BytesIO()
    # img.save(image_io, 'PNG')
    # dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

    return render_template("result.html", route = "/testing_qr", result = decoded_info, result_image = dataurl )


# @app.route('/type_recognition', methods = ['POST'])
# def type_recognition():
#     test_type = ""
#     img = Image.open(request.files['img'].stream)

#     cv_img = convert_to_cv2(img)

#     try:
#         results = model_type.predict(cv_img)
#         test_type = TYPES[int(results[0].boxes.cls[0])]
#         annotated_frame = results[0].plot()

#         print(test_type)
#     except:
#         return render_template("result.html", route = "/testing_type", result = "Null" )

#     img = convert_to_pillow(annotated_frame)
#     image_io = BytesIO()
#     img.save(image_io, 'PNG')
#     dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

#     return render_template("result.html", route = "/testing_type", result = test_type, result_image = dataurl)

# @app.route('/result_recognition', methods = ['POST'])
# def result_recognition():
#     test_type = ""
#     img = Image.open(request.files['img'].stream)

#     cv_img = convert_to_cv2(img)

#     try:
#         results = model_result.predict(cv_img)
#         test_result = TYPES[int(results[0].boxes.cls[0])]
#         annotated_frame = results[0].plot()

#         print(test_type)
#     except:
#         return render_template("result.html", route = "/testing_result", result = "Null" )

#     img = convert_to_pillow(annotated_frame)
#     image_io = BytesIO()
#     img.save(image_io, 'PNG')
#     dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

#     return render_template("result.html", route = "/testing_result", result = test_result, result_image = dataurl)


# Словарь для хранения событий ожидания
waiting_events = {}
waiting_results = {}

@app.route('/test_results_detection', methods=['POST'])
def test_results_detection():
    # Уникальный идентификатор для хранения состояния
    unique_id = str(uuid.uuid4())

    # Получаем изображение
    img = request.files['img'].stream
    img = Image.open(img)

    # Сохраняем изображение во временный файл
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        img.save(tmp_file, format="JPEG")
        tmp_file_path = tmp_file.name

    chat_ids = get_all_chat_ids()
    for chat_id in chat_ids:
        # Отправляем фото в Telegram и сохраняем состояние ожидания
        send_photo_to_telegram(tmp_file_path, unique_id, chat_id)

    # Создаем событие ожидания (по желанию, если нужно контролировать состояние)
    event = threading.Event()
    waiting_events[unique_id] = event

    # Здесь не блокируем поток. Просто возвращаем идентификатор сессии.
    return jsonify({"session_id": unique_id})

def send_photo_to_telegram(file_path, unique_id, chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    # Открываем временный файл и отправляем в Telegram
    with open(file_path, 'rb') as file:
        files = {'photo': file}
        payload = {
            'chat_id': chat_id,
            'caption': '',
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'Positive', 'callback_data': f'positive_{unique_id}'},
                     {'text': 'Negative', 'callback_data': f'negative_{unique_id}'},
                     {'text': 'Error', 'callback_data': f'error_{unique_id}'}]
                ]
            })
        }
        response = requests.post(url, files=files, data=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    callback_query = update.get('callback_query')

    if callback_query:
        user_id = callback_query['from']['id']
        callback_data = callback_query['data']
        
        # Извлекаем уникальный идентификатор из callback_data
        response_type = callback_data.split('_')[0]
        unique_id = callback_data.split('_')[1]

        # Сохраняем ответ в словаре
        waiting_results[unique_id] = response_type

        # Уведомляем, что результат получен (если нужно, можно добавить логику для уведомления)
        if unique_id in waiting_events:
            waiting_events[unique_id].set()

        # Отправляем сообщение пользователю
        send_message_to_telegram(user_id, f"You clicked: {response_type}")

    return jsonify({'status': 'ok'})

def send_message_to_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, data=payload)

@app.route('/notifi_reducer', methods=['POST'])
def notifi_reducer():
    get_n_send()

def main():
    app.run(HOST, PORT, debug=DEBUG, threaded=THREADED)

if __name__ == '__main__':
    main()