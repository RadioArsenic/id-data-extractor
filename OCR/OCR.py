import pytesseract
import cv2
import numpy as np
import json

class ImageConstantROI():
    class CCCD(object):
        WA_ROIS = {
            "last_name": [(19, 158, 120, 20)],
            "given_name": [(45, 176, 155, 20)],
            "address": [(19, 194, 300, 40)],
            "expiry_date": [(19, 257, 140, 30)],
            "date_of_birth": [(200, 257, 140, 30)],
        }
        Victoria_ROIS = {
            "name": [(14, 79, 350, 30)],
            "address": [(14, 128, 350, 90)],
            "expiry_date": [(14, 230, 150, 30)],
            "date_of_birth": [(217, 230, 150, 30)],
        }
        NSW_ROIS = {
            "name": [(12, 110, 250, 25)],
            "address": [(12, 175, 250, 50)],
            "expiry_date": [(465, 374, 150, 20)],
            "date_of_birth": [(280, 374, 150, 20)]
        }
        NT_ROIS = {
            "last_name": [(195, 145, 200, 25)],
            "given_name": [(195, 168, 200, 25)],
            "address": [(195, 280, 200, 50)],
            "expiry_date": [(490, 371, 90, 20)],
            "date_of_birth": [(350, 371, 90, 20)],
        }
        

def cropImageRoi(image, roi):
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])]
    return roi_cropped

def preprocessing(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.multiply(gray, 1.5)

    #blur remove noise
    #blured = cv2.medianBlur(gray,3)
    blured1 = cv2.medianBlur(gray,3)
    blured2 = cv2.medianBlur(gray,51)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255*divided/divided.max())

    # Threshold the image to convert non-black areas to white
    #_, thresholded = cv2.threshold(normed, 90, 255, cv2.THRESH_BINARY)
    th, thresholded = cv2.threshold(normed, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)

    # Create an all-white image of the same size as the original image
    result = np.ones_like(image) * 255

    # Copy the black areas from the original image to the result
    result[thresholded == 0] = image[thresholded == 0]

    # Save or display the resulting image
    cv2.imwrite('result_image.jpg', result)

    return result

def displayImage(image):
    cv2.imshow('Result Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Load the image
image = cv2.imread('NT-driver-license.png')

# Resize Image
resized_image = cv2.resize(image,(620,413), interpolation=cv2.INTER_CUBIC)
displayImage(resized_image)

for key, roi in ImageConstantROI.CCCD.NT_ROIS.items():
    data = ''
    for r in roi:
        crop_img = cropImageRoi(resized_image, r)
        displayImage(crop_img)
        crop_img = preprocessing(crop_img)
        data += pytesseract.image_to_string(crop_img, config = '--psm 6 --oem 3', lang='eng').replace('\n', ' ') + ' '
    displayImage(crop_img)
    print(f"{key} : {data.strip('')}")


# works fine:
#       ACT, has a couple of missteps where the photo is pixelated
#       SA, all the important info is there, fewer random characters
#       VIC, borders iffy but mostly alright, not many extra characters and all important is there
# iffy:
#       WA, doesn't read state, not necessary for KYC, could be an issue for verification
#       NSW, messes up the address but otherwise mostly fine
# doesn't work:
#       NT, a lot of the info is there but more of it isn't
#       QLD, we need a better sample for this one
#       TAS, we need a better sample for this one

# print(imageToText("ACT-driver-license.jpeg"))
# print(imageToText("NSW-driver-license.jpg"))
# print(imageToText("NT-driver-license.png"))
# print(imageToText("Queensland-driver-license.jpeg"))
# print(imageToText("SA-driver-license.jpg"))
# print(imageToText("Tasmania-driver-license.jpeg"))
# print(imageToText("Victoria-driver-license.jpg"))
print(imageToText("WA-driver-license.jpeg"))


# * INFO WANTED:
# Given name
# Middle name
# Family name
# DOB
# Address
# Expiry date (for verification)


# convert string to python dictionary then to json
def parsetoJSON(text):
    pass
