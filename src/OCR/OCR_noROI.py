import pytesseract
import cv2
import numpy as np
import json
import re
import lexnlp.extract.en.dates as dates


def imageToText(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Resize image
    image = cv2.resize(image, (620, 413), interpolation=cv2.INTER_CUBIC)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.multiply(gray, 1.5)

    # blur remove noise
    # blured = cv2.medianBlur(gray,3)
    blured1 = cv2.medianBlur(gray, 3)
    blured2 = cv2.medianBlur(gray, 51)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255 * divided / divided.max())

    # Threshold the image to convert non-black areas to white
    # _, thresholded = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    th, thresholded = cv2.threshold(normed, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)

    # Create an all-white image of the same size as the original image
    result = np.ones_like(image) * 255

    # Copy the black areas from the original image to the result
    result[thresholded == 0] = image[thresholded == 0]

    # Save or display the resulting image
    cv2.imwrite("result_image.jpg", result)

    # Display the result (optional)
    # cv2.imshow("Result Image", result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Extract text from image
    text = pytesseract.image_to_string(result, config="--psm 6 --oem 3", lang="eng")

    # Clean output
    print(text, "\n ~~~~~~~~~")
    text = re.sub("[^ \na-zA-Z\d'\/-]*", "", text)
    text = re.sub("\n", " ", text)

    return text


# works fine:
#       ACT, has a couple of missteps where the photo is pixelated
#       SA, all the important info is there, fewer random characters
#       VIC, borders iffy but mostly alright, not many extra characters and all important is there      good for dates
# iffy:
#       WA, doesn't read state, not necessary for KYC, could be an issue for verification
#       NSW, messes up the address but otherwise mostly fine
# doesn't work:
#       NT, a lot of the info is there but more of it isn't
#       QLD, we need a better sample for this one
#       TAS, we need a better sample for this one

# print(imageToText("ACT-driver-license.jpeg"))             dates are good, it should read the address but doesn't (maybe thinks multiple and overwrites?)              look into
# print(imageToText("NSW-driver-license.jpg"))              dates are back to back and have couple random characters, address is jumbled in OCR
# print(imageToText("NT-driver-license.png"))               dates are removed in OCR, address is jumbled in OCR
# print(imageToText("Queensland-driver-license.jpeg"))      dates are jumped in OCR, doesn't have an address on license
# print(imageToText("SA-driver-license.jpg"))               dates are good, address has a couple random characters so doesn't pick up
# print(imageToText("Tasmania-driver-license.jpeg"))        everything is jumbled
# print(
#     imageToText("Victoria-driver-license.jpg")
# )  # dates are back to back, address has a couple random characters so doesn't pick up
# print(imageToText("WA-driver-license.jpeg"))              #dates are back to back, address is jumbled in OCR


# * INFO WANTED:
# Given name
# Middle name
# Family name
# DOB
# Address
# Expiry date (for verification)


# convert string to python dictionary then to json
# returns json if fine, otherwise gives error
def parsetoJSON(text):
    pass


# print(list(dates.get_dates(text)))
def address_detection(text):
    regexp = r"\d{1,4}(?:\s+[A-Za-z]+){3,}\s+\d{4,5}"
    address = re.findall(regexp, text)
    print(address)
    return address
