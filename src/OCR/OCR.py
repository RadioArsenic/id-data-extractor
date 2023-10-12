import cv2
import numpy as np
import pytesseract
import json

class ImageConstantROI():
    class CCCD(object):
        WA_ROIS = {
            "name": [(45, 180, 155, 20), (19, 160, 120, 20)],
            "address": [(17, 199, 300, 40)],
            "expiry_date": [(17, 270, 140, 26)],
            "date_of_birth": [(200, 270, 140, 26)],
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
            "name": [(195, 168, 200, 25), (195, 145, 200, 25)],
            "address": [(195, 280, 200, 50)],
            "expiry_date": [(490, 371, 90, 20)],
            "date_of_birth": [(350, 371, 90, 20)],
        }
        ACT_ROIS = {
            "name": [(16, 100, 250, 30)],
            "address": [(16, 126, 250, 60)],
            "expiry_date": [(252, 246, 130, 30)],
            "date_of_birth": [(115, 212, 140, 30)],
        }
        SA_ROIS = {
            "name": [(37, 209, 250, 25)],
            "address": [(16, 234, 250, 50)],
            "expiry_date": [(335, 100, 105, 30)],
            "date_of_birth": [(181, 100, 105, 30)],
        }
        Queensland_ROIS = {
            "name": [(15, 86, 200, 25), (15, 62, 200, 25)],
            "expiry_date": [(347, 198, 75, 25)],
            "date_of_birth": [(215, 122, 120, 22)],
        }
        ACT_ROIS = {
            "name": [(11, 97, 250, 30)],
            "address": [(11, 126, 250, 60)],
            "expiry_date": [(253, 245, 130, 30)],
            "date_of_birth": [(115, 213, 140, 30)],
        }
        

def cropImageRoi(image, roi):
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])]
    return roi_cropped

def cropImage(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply edge detection to find the contour of the ID card
    edges = cv2.Canny(gray, threshold1=30, threshold2=100)

    # Find the contours in the image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour (assuming it's the ID card)
    largest_contour = max(contours, key=cv2.contourArea)

    # Create a mask for the ID card using the largest contour
    mask = np.zeros_like(image)
    cv2.drawContours(mask, [largest_contour], 0, (255, 255, 255), thickness=cv2.FILLED)

    # Apply the mask to the original image to extract the ID card
    result = cv2.bitwise_and(image, mask)

    # Save the cropped ID card as a new image
    cv2.imwrite('cropped_id_card.jpg', result)

    return result

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

def extract_information(image_path):
    information = {}

    # Load the image
    image = cv2.imread(image_path)

    # Resize Image
    resized_image = cv2.resize(image,(620,413), interpolation=cv2.INTER_CUBIC)
    displayImage(resized_image)

    for key, roi in ImageConstantROI.CCCD.WA_ROIS.items():
        data = ''
        for r in roi:
            crop_img = cropImageRoi(resized_image, r)
            #displayImage(crop_img)
            crop_img = preprocessing(crop_img)
            data += pytesseract.image_to_string(crop_img, config = '--psm 6 --oem 3', lang='eng').replace('\n', ' ').strip() + ' '
        displayImage(crop_img)
        information[key] = data.strip()
        #print(f"{key} : {data.strip()}")

    return information

print(extract_information("./test_images/WA-driver-license.jpeg"))

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
#print(imageToText("WA-driver-license.jpeg"))


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
