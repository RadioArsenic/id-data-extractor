import pytesseract
import cv2
import numpy as np
import json
import re
import lexnlp.extract.en.dates as dates
import imghdr
import os


def image_to_text(image_path):
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
def parse_to_json(text):
    pass


# print(list(dates.get_dates(text)))
def address_detection(text):
    regexp = r"\d{1,4}(?:\s+[A-Za-z]+){3,}\s+\d{4,5}"
    address = re.findall(regexp, text)
    print(address)
    return address


def date_builder(day, month, year):
    """formats the date"""
    return f"{day}-{month}-{year}"


def month_conversion(month):
    """converts the month from letter to number format"""
    month = month.upper()
    month_dict = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
        "SEPT": "09",
    }
    return month_dict.get(month, "00")


def date_detection(text):
    """a function to detect dates in a variety of forms and transform
    them into the typical dd-mm-yyyy format"""
    # an array to hold all discovered dates
    dates = []

    # regex patterns
    pattern16 = r"\b\d{16}\b"  # 16 numbers
    pattern8 = r"\b\d{8}\b"  # 8 numbers

    pattern3L = r"\d{2}[A-Za-z]{3}\d{4}"  # 10JUN1990
    pattern4L = r"\d{2}[A-Za-z]{4}\d{4}"  # 10SEPT1990
    
    patternLDash = r"[0-9]{2}-[A-Za-z]{3}-[0-9]{4}"  # 10-JUN-1990
    patternLSlash = r"[0-9]{2}/[A-Za-z]{3}/[0-9]{4}"  # 10/JUN/1990
    patternLDot = r"[0-9]{2}.[A-Za-z]{3}.[0-9]{4}"  # 10.JUN.1990
    patternLSpace = r'\d{2} [A-Za-z]{3} \d{4}' # 10 JUN 1990

    patternDDash = r"[0-9]{2}-[0-9]{2}-[0-9]{4}"  # 10-06-1990
    patternDSlash = r"[0-9]{2}/[0-9]{2}/[0-9]{4}"  # 10/06/1990
    patternDDot = r"[0-9]{2}.[0-9]{2}.[0-9]{4}"  # 10.06.1990
    patternDSpace = r'\d{2} \d{2} \d{4}' # 10 06 1990

    pattern4Dash = r"[0-9]{2}-[A-Za-z]{4}-[0-9]{4}"  # 10-SEPT-1990
    pattern4Slash = r"[0-9]{2}/[A-Za-z]{4}/[0-9]{4}"  # 10/SEPT/1990
    pattern4Dot = r"[0-9]{2}.[A-Za-z]{4}.[0-9]{4}"  # 10.SEPT.1990
    pattern4Space = r'\d{2} [A-Za-z]{4} \d{4}' # 10 SEPT 1990

    # 16 numbers
    matches_16 = re.findall(pattern16, text)
    for i in matches_16:
        j = i[8:]
        dates.append(date_builder(i[:2], i[2:4], i[4:8]))
        dates.append(date_builder(j[:2], j[2:4], j[4:8]))

    # 8 numbers
    matches_8 = re.findall(pattern8, text)
    for i in matches_8:
        dates.append(date_builder(i[:2], i[2:4], i[4:]))

    # ddMMMyyyy
    matches_3m = re.findall(pattern3L, text)
    for i in matches_3m:
        month = month_conversion(i[2:5])
        dates.append(date_builder(i[:2], month, i[5:]))
    
    # ddMMMMyyyy
    matches_3m = re.findall(pattern4L, text)
    for i in matches_3m:
        month = month_conversion(i[2:6])
        dates.append(date_builder(i[:2], month, i[6:]))

    # dd-MMMM-yyyy dd/MMMM/yyyy dd.MMMM.yyyy dd MMMM yyyy
    matches_3dash = re.findall(pattern4Dash, text)
    matches_3dash.extend(re.findall(pattern4Slash, text))
    matches_3dash.extend(re.findall(pattern4Dot, text))
    matches_3dash.extend(re.findall(pattern4Space, text))
    for i in matches_3dash:
        month = month_conversion(i[3:7])
        dates.append(date_builder(i[:2], month, i[8:]))

    # dd-MMM-yyyy dd/MMM/yyyy dd.MMM.yyyy dd MMM yyyy
    matches_3dash = re.findall(patternLDash, text)
    matches_3dash.extend(re.findall(patternLSlash, text))
    matches_3dash.extend(re.findall(patternLDot, text))
    matches_3dash.extend(re.findall(patternLSpace, text))
    for i in matches_3dash:
        month = month_conversion(i[3:6])
        dates.append(date_builder(i[:2], month, i[7:]))

    # dd-mm-yyyy dd/mm/yyyy dd.mm.yyyy dd mm yyyy
    matches_2dash = re.findall(patternDDash, text)
    matches_2dash.extend(re.findall(patternDSlash, text))
    matches_2dash.extend(re.findall(patternDDot, text))
    matches_2dash.extend(re.findall(patternDSpace, text))
    for i in matches_2dash:
        dates.append(date_builder(i[:2], i[3:5], i[6:]))

    return dates


def validate_dates(dates):
    """ensures that all dates are valid. returns 0 if
    invalid date is present. if all dates are valid, returns
    the oldest date (date of birth)"""
    birthdate = ""
    year_check = 2101
    for i in dates:
        day = int(i[:2])
        month = int(i[3:5])
        year = int(i[6:])
        # checking date is valid
        if 32 < day < 0 or 13 < month < 0 or 2100 < year < 1900:
            return 0
        else:
            # if the current date is older than the stored date
            if year < year_check:
                birthdate = i
    return birthdate


def remove_file(image_path):
    """removes the file with the given image name.
    if the file is not an image, or the file does not exist, returns 1
    otherwise, returns 0"""
    # if the file doesnt exist, return error
    if not os.path.exists(image_path):
        return 1

    # if the file is not an image, return error
    f_type = imghdr.what(image_path)
    if not f_type:
        return 1

    # if the file exists, and is an image, delete it
    os.remove(image_path)
    return 0
