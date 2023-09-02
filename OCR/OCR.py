import pytesseract
import PIL
import cv2
import numpy as np
import re


def imageToText(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image,None, fx=3, fy=2, interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY)[1]
    image = cv2.medianBlur(image, 7)
    text = pytesseract.image_to_string(image, config = '--psm 6 --oem 3', lang='eng')
    return text

print(imageToText("WA-driver-license.jpeg"))
print("---------------------------------------")
print(imageToText("Victoria-driver-license.jpg"))
print("---------------------------------------")
print(imageToText("NSW-driver-license.jpg"))
