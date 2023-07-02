import cv2
import numpy as np
from PIL import Image

def convert_to_cv2(img):
    open_cv_image = np.array(img) 
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    
    return open_cv_image

def convert_to_pillow(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img)

    return im_pil