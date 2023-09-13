from PIL import Image
import onnxruntime as ort
import numpy as np

yolo_classes = {
    'best_type': ["HIV", "Hepatitis", "Syphilis"],
    'best_result': ["Negative", "Positive", "Failure"]
}


def detect_objects_on_image(buf,  model):
    input, img_width, img_height = prepare_input(buf)
    output = run_model(input, model)
    return process_output(output,img_width,img_height, model)

def prepare_input(img):
    img_width, img_height = img.size
    img = img.resize((640, 640))
    img = img.convert("RGB")
    input = np.array(img)
    input = input.transpose(2, 0, 1)
    input = input.reshape(1, 3, 640, 640) / 255.0
    return input.astype(np.float32), img_width, img_height

def run_model(input, model):
    model = ort.InferenceSession(f"./weights/{model}.onnx")
    outputs = model.run(["output0"], {"images":input})
    return outputs[0]

def iou(box1,box2):
    return intersection(box1,box2)/union(box1,box2)

def union(box1,box2):
    box1_x1,box1_y1,box1_x2,box1_y2 = box1[:4]
    box2_x1,box2_y1,box2_x2,box2_y2 = box2[:4]
    box1_area = (box1_x2-box1_x1)*(box1_y2-box1_y1)
    box2_area = (box2_x2-box2_x1)*(box2_y2-box2_y1)
    return box1_area + box2_area - intersection(box1,box2)

def intersection(box1,box2):
    box1_x1,box1_y1,box1_x2,box1_y2 = box1[:4]
    box2_x1,box2_y1,box2_x2,box2_y2 = box2[:4]
    x1 = max(box1_x1,box2_x1)
    y1 = max(box1_y1,box2_y1)
    x2 = min(box1_x2,box2_x2)
    y2 = min(box1_y2,box2_y2)
    return (x2-x1)*(y2-y1)

def process_output(output, img_width, img_height, model):
    output = output[0].astype(float)
    output = output.transpose()


    boxes = []
    for row in output:
        prob = row[4:].max()
        if prob < 0.5:
            continue
        class_id = row[4:].argmax()
        label = yolo_classes[model][class_id]

        xc, yc, w, h = row[:4]
        x1 = (xc - w/2) / 640 * img_width
        y1 = (yc - h/2) / 640 * img_height
        x2 = (xc + w/2) / 640 * img_width
        y2 = (yc + h/2) / 640 * img_height
        boxes.append([x1, y1, x2, y2, label, prob])

    boxes.sort(key=lambda x: x[5], reverse=True)
    result = []
    while len(boxes) > 0:
        result.append(boxes[0])
        boxes = [box for box in boxes if iou(box, boxes[0]) < 0.6]
    return result
