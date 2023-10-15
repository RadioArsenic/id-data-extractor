import cv2
import numpy as np
import pytesseract
import json
import re
import imghdr
import os


class ImageConstantROI:
    class CCCD(object):
        AUSTRALIA_WA = {
            # coordinate format in (x,y,w,h), (x,y) being the top left coordinate of the text
            # "name": [(45, 180, 155, 20), (19, 160, 120, 20)],  # old
            "name": [(40, 180, 160, 25), (10, 155, 130, 25)],
            # "address": [(17, 199, 300, 40)],  # old
            "address": [(10, 199, 300, 50)],
            # "expiry_date": [(17, 270, 140, 26)],  # old
            "expiry_date": [(10, 270, 160, 26)],
            # "date_of_birth": [(200, 270, 140, 26)],  # old
            "date_of_birth": [(200, 270, 180, 26)],
        }
        AUSTRALIA_VIC = {
            "name": [(14, 79, 350, 30)],
            "address": [(14, 128, 350, 90)],
            "expiry_date": [(14, 230, 150, 30)],
            "date_of_birth": [(217, 230, 150, 30)],
        }
        AUSTRALIA_NSW = {
            "name": [(12, 110, 250, 25)],
            "address": [(12, 175, 250, 50)],
            "expiry_date": [(465, 374, 150, 20)],
            "date_of_birth": [(280, 374, 150, 20)],
        }
        AUSTRALIA_NT = {
            "name": [(195, 168, 200, 25), (195, 145, 200, 25)],
            "address": [(195, 280, 200, 50)],
            "expiry_date": [(490, 371, 90, 20)],
            "date_of_birth": [(350, 371, 90, 20)],
        }
        AUSTRALIA_ACT = {
            "name": [(110, 107, 54, 24), (12, 107, 96, 24)],
            "address": [(11, 126, 250, 60)],
            "expiry_date": [(252, 246, 130, 30)],
            "date_of_birth": [(115, 212, 140, 30)],
        }
        AUSTRALIA_SA = {
            "name": [(37, 209, 250, 25)],
            "address": [(16, 234, 250, 50)],
            "expiry_date": [(335, 100, 105, 30)],
            "date_of_birth": [(181, 100, 105, 30)],
        }
        AUSTRALIA_QLD = {
            "name": [(15, 86, 200, 25), (15, 62, 200, 25)],
            "expiry_date": [(347, 198, 75, 25)],
            "date_of_birth": [(215, 122, 120, 22)],
        }
        AUSTRALIA_TAS = {
            "name": [(230, 95, 140, 25), (230, 70, 90, 20)],
            "address": [(230, 125, 170, 55)],
            "expiry_date": [(365, 280, 85, 15)],
            "date_of_birth": [(400, 220, 210, 30)],
        }
        AUSTRALIA_PASSPORT = {
            "name": [(210, 130, 130, 20), (210, 110, 100, 20)],
            "expiry_date": [(210, 265, 140, 20)],
            "date_of_birth": [(210, 185, 150, 20)],
        }


def cropImageRoi(image, roi):
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])
    ]
    return roi_cropped


def preprocessing(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.multiply(gray, 1.5)

    # blur remove noise
    blured1 = cv2.medianBlur(gray, 3)
    blured2 = cv2.medianBlur(gray, 51)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255 * divided / divided.max())

    # Threshold the image to convert non-black areas to white
    th, thresholded = cv2.threshold(normed, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)

    # Create an all-white image of the same size as the original image
    result = np.ones_like(image) * 255

    # Copy the black areas from the original image to the result
    result[thresholded == 0] = image[thresholded == 0]

    # Save or display the resulting image
    cv2.imwrite("result_image.jpg", result)

    return result


def displayImage(image):
    cv2.imshow("Result Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def matchImage(image, baseImage):
    # Declare image size, width height and chanel
    baseH, baseW, baseC = baseImage.shape

    orb = cv2.ORB_create(1000)

    kp, des = orb.detectAndCompute(baseImage, None)

    PER_MATCH = 0.25

    # Detect keypoint on image
    kp1, des1 = orb.detectAndCompute(image, None)

    # Init BF Matcher, find the matches points of two images
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = list(bf.match(des1, des))

    # Select top 30% best matcher
    matches.sort(key=lambda x: x.distance)
    best_matches = matches[: int(len(matches) * PER_MATCH)]

    # Show match img
    imgMatch = cv2.drawMatches(image, kp1, baseImage, kp, best_matches, None, flags=2)
    displayImage(imgMatch)

    # Init source points and destination points for findHomography function.
    srcPoints = np.float32([kp1[m.queryIdx].pt for m in best_matches]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp[m.trainIdx].pt for m in best_matches]).reshape(-1, 1, 2)

    # Find Homography of two images
    matrix_relationship, _ = cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)

    # Transform the image to have the same structure as the base image
    img_final = cv2.warpPerspective(image, matrix_relationship, (baseW, baseH))

    displayImage(img_final)

    return img_final


def extract_information(image_path, location):
    information = {}

    # Load the image
    image = cv2.imread(image_path)

    # Resize Image
    resized_image = cv2.resize(image, (620, 413), interpolation=cv2.INTER_CUBIC)
    # displayImage(resized_image)

    # Load the base image
    # String formatting would be cleaner but would require the image types to be the same
    if location == "AUSTRALIA_WA":
        baseImage = cv2.imread("./test_images/WA-driver-license.jpeg")
    elif location == "AUSTRALIA_VIC":
        baseImage = cv2.imread("./test_images/VIC-driver-license.jpg")
    elif location == "AUSTRALIA_TAS":
        baseImage = cv2.imread("./test_images/TAS-driver-license.jpeg")
    elif location == "AUSTRALIA_SA":
        baseImage = cv2.imread("./test_images/SA-driver-license.png")
    elif location == "AUSTRALIA_QLD":
        baseImage = cv2.imread("./test_images/QLD-driver-license.jpg")
    elif location == "AUSTRALIA_NT":
        baseImage = cv2.imread("./test_images/NT-driver-license.png")
    elif location == "AUSTRALIA_NSW":
        baseImage = cv2.imread("./test_images/NSW-driver-license.jpg")
    elif location == "AUSTRALIA_ACT":
        baseImage = cv2.imread("./test_images/ACT-driver-license.png")
    elif location == "AUSTRALIA_PASSPORT":
        baseImage = cv2.imread("./test_images/AUS-passport.jpg")

    # Match the image with base image
    # image = matchImage(resized_image, baseImage)

    image = cv2.resize(image, (620, 413), interpolation=cv2.INTER_CUBIC)

    for key, roi in getattr(ImageConstantROI.CCCD, location).items():
        data = ""
        for r in roi:
            crop_img = cropImageRoi(image, r)
            # displayImage(crop_img)
            crop_img = preprocessing(crop_img)
            data += (
                pytesseract.image_to_string(
                    crop_img, config="--psm 6 --oem 3", lang="eng"
                )
                .replace("\n", " ")
                .strip()
                + " "
            )
            # displayImage(crop_img)
        information[key] = data.strip()
        # print(f"{key} : {data.strip()}")

        if location == "AUSTRALIA_SA" or location == "AUSTRALIA_ACT":
            parts = information["name"].split()
            information["name"] = f"{' '.join(parts[1:])} {parts[0]}"

    return information
    # parsetoJSON(information)


def date_builder(day, month, year):
    """helper function for date_formatter. Formats the date"""
    return f"{day}-{month}-{year}"


def month_conversion(month):
    """helper function for date_detection. Converts the month from letter to number format"""
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
        "JANU": "01",
        "FEBR": "02",
        "MARC": "03",
        "APRI": "04",
        "JUNE": "06",
        "JULY": "07",
        "AUGU": "08",
        "SEPT": "09",
        "OCTO": "10",
        "NOVE": "11",
        "DECE": "12",
    }
    return month_dict.get(month, "00")


def date_formatter(text):
    """a function to take a single date (that could be in a variety of forms) and transform
    it into the typical dd-mm-yyyy format"""
    # todo correct dates that include O instead of 0
    # date to return
    date = ""

    # regex patterns
    pattern8 = r"\b\d{8}\b"  # 10061990

    pattern3L = r"\d{2}[A-Za-z]{3}\d{4}"  # 10JUN1990
    pattern4L = r"\d{2}[A-Za-z]{4}\d{4}"  # 10SEPT1990

    patternLDash = r"[0-9]{2}-[A-Za-z]{3}-[0-9]{4}"  # 10-JUN-1990
    patternLSlash = r"[0-9]{2}/[A-Za-z]{3}/[0-9]{4}"  # 10/JUN/1990
    patternLDot = r"[0-9]{2}.[A-Za-z]{3}.[0-9]{4}"  # 10.JUN.1990
    patternLSpace = r"\d{2} [A-Za-z]{3} \d{4}"  # 10 JUN 1990

    patternDDash = r"[0-9]{2}-[0-9]{2}-[0-9]{4}"  # 10-06-1990
    patternDSlash = r"[0-9]{2}/[0-9]{2}/[0-9]{4}"  # 10/06/1990
    patternDDot = r"[0-9]{2}.[0-9]{2}.[0-9]{4}"  # 10.06.1990
    patternDSpace = r"\d{2} \d{2} \d{4}"  # 10 06 1990

    pattern4Dash = r"[0-9]{2}-[A-Za-z]{4}-[0-9]{4}"  # 10-SEPT-1990
    pattern4Slash = r"[0-9]{2}/[A-Za-z]{4}/[0-9]{4}"  # 10/SEPT/1990
    pattern4Dot = r"[0-9]{2}.[A-Za-z]{4}.[0-9]{4}"  # 10.SEPT.1990
    pattern4Space = r"\d{2} [A-Za-z]{4} \d{4}"  # 10 SEPT 1990

    # 8 numbers
    matches_8 = re.findall(pattern8, text)
    if len(matches_8) > 0:
        i = matches_8[0]
        date = date_builder(i[:2], i[2:4], i[4:])

    # ddMMMyyyy
    matches_3m = re.findall(pattern3L, text)
    if len(matches_3m) > 0:
        i = matches_3m[0]
        month = month_conversion(i[2:5])
        date = date_builder(i[:2], month, i[5:])

    # ddMMMMyyyy
    matches_4m = re.findall(pattern4L, text)
    if len(matches_4m) > 0:
        i = matches_4m[0]
        month = month_conversion(i[2:6])
        date = date_builder(i[:2], month, i[6:])

    # dd-MMMM-yyyy dd/MMMM/yyyy dd.MMMM.yyyy dd MMMM yyyy
    matches_4dash = re.findall(pattern4Dash, text)
    matches_4dash.extend(re.findall(pattern4Slash, text))
    matches_4dash.extend(re.findall(pattern4Dot, text))
    matches_4dash.extend(re.findall(pattern4Space, text))
    if len(matches_4dash) > 0:
        i = matches_4dash[0]
        month = month_conversion(i[3:7])
        date = date_builder(i[:2], month, i[8:])

    # dd-MMM-yyyy dd/MMM/yyyy dd.MMM.yyyy dd MMM yyyy
    matches_3dash = re.findall(patternLDash, text)
    matches_3dash.extend(re.findall(patternLSlash, text))
    matches_3dash.extend(re.findall(patternLDot, text))
    matches_3dash.extend(re.findall(patternLSpace, text))
    if len(matches_3dash) > 0:
        i = matches_3dash[0]
        month = month_conversion(i[3:6])
        date = date_builder(i[:2], month, i[7:])

    # dd-mm-yyyy dd/mm/yyyy dd.mm.yyyy dd mm yyyy
    matches_2dash = re.findall(patternDDash, text)
    matches_2dash.extend(re.findall(patternDSlash, text))
    matches_2dash.extend(re.findall(patternDDot, text))
    matches_2dash.extend(re.findall(patternDSpace, text))
    if len(matches_2dash) > 0:
        i = matches_2dash[0]
        date = date_builder(i[:2], i[3:5], i[6:])

    return date


def validate_date(date):
    """validates an input date. returns 0 if date is invalid
    otherwise, returns input date"""
    # retrieving parts of date
    day = int(date[:2])
    month = int(date[3:5])
    year = int(date[6:])
    # checking date is valid
    if day == 31 and (
        month == 2 or month == 4 or month == 6 or month == 9 or month == 11
    ):
        return 0
    # todo leap years
    if (day == 30 or day == 29) and month == 2:
        return 0
    if 31 < day or day < 1:
        return 0
    if 13 < month or month < 1:
        return 0
    if year < 1900 or year > 2100:
        return 0
    else:
        return date


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


def parsetoJSON(information):
    """Converts python dictionary to json. Returns 0 if error. Input is information from extract_information()"""
    information["name"] = information["name"].upper()

    if "address" in information:
        information["address"] = re.sub(",", "", information["address"])

    information["expiry_date"] = date_formatter(information["expiry_date"])
    res = validate_date(information["expiry_date"])
    if res == 0:
        return 0

    information["date_of_birth"] = date_formatter(information["date_of_birth"])
    res = validate_date(information["date_of_birth"])
    if res == 0:
        return 0

    with open("id_data.json", "w", encoding="utf-8") as f:
        json.dump(information, f, indent=4)
