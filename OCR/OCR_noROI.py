import pytesseract
import cv2
import numpy as np
import json
# import lexnlp.extract.en.dates as dates
# from lexnlp.extract.en.addresses import address_features
# import lexnlp.extract.en.addresses as address
# import lexnlp.extract.en.entities.stanford_ner as stanford_ner
# import lexnlp.extract.en.entities.nltk_maxent.py as nltk 
import lexnlp.extract.en.addresses.addresses as addressFinder

def imageToText(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Resize image
    # image = cv2.resize(image, (620, 413), interpolation=cv2.INTER_CUBIC)

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

# print(imageToText("ACT-driver-license.jpeg"))
# print(imageToText("NSW-driver-license.jpg"))
print(imageToText("NT-driver-license.png"))
# print(imageToText("Queensland-driver-license.jpeg"))
# print(imageToText("SA-driver-license.jpg"))
# print(imageToText("Tasmania-driver-license.jpeg"))
# print(imageToText("Victoria-driver-license.jpg"))
# print(imageToText("WA-driver-license.jpeg"))


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


# text = imageToText("WA-driver-license.jpeg")
# print(text)
# print("----")
# print(list(dates.get_dates(text)))
# print(list(lexnlp.extract.en.addresses.address_features.get_word_features(text)))
# print(list(address_features.get_word_features(text, is_zip_code(text))))
# print(list(addresses.get_addresses(text)))
# print(list(stanford_ner.get_locations(text)))
# print("----")
# print(list(stanford_ner.get_persons(text)))
# print(list(nltk.get_geopolitical(text)))
# print(list(nltk.get_persons(text)))


# text = "The company is located at 123 Main Street, New York, NY 10001."
# print(list(addressFinder.get_addresses(text)))