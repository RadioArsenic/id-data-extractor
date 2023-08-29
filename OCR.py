import pytesseract
import PIL
import cv2
import numpy as np
import re


def imageToText(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image,None, fx=10, fy=10, interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 136, 255, cv2.THRESH_BINARY)[1]
    image = cv2.medianBlur(image, 3)
    text = pytesseract.image_to_string(image, config = '--psm 6 --oem 3', lang='eng')
    return text

print(imageToText("driver-license-sample.jpeg"))
