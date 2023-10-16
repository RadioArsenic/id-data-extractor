import cv2
import numpy as np
import pytesseract
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
            "address": [],
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
            "address": [],
            "expiry_date": [(210, 265, 140, 20)],
            "date_of_birth": [(210, 185, 150, 20)],
        }


def crop_image_roi(image, roi):
    """
    The function `crop_image_roi` takes an image and a region of interest (ROI) as input, and returns the
    cropped image corresponding to the ROI.

    :param image: The image parameter is the input image from which you want to crop a region of
    interest (ROI)
    :param roi: The "roi" parameter is a list or tuple containing the coordinates and dimensions of the
    region of interest (ROI) in the image.
    :return: the cropped region of interest (ROI) from the input image.
    """
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])
    ]
    return roi_cropped


def preprocessing(image):
    """
    The function takes an image as input and performs various preprocessing techniques on it to make it
    more readable by the OCR function.

    :param image: The image that you want to preprocess
    :return: the preprocessed image, which is stored in the variable "result".
    """
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


def display_image(image):
    """
    The function `display_image` takes an image as input and displays it in a window titled "Result
    Image".

    :param image: The parameter "image" is the image that you want to display. It should be a valid
    image object that can be read by the OpenCV library
    """
    cv2.imshow("Result Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def extract_information(image_path, location):
    """
    The function `extract_information` takes an image path and location as input, loads the image,
    resizes it, matches it with a base image based on the location, extracts information from specific
    regions of interest (ROIs) in the image using OCR, and returns the extracted information as a
    dictionary.

    :param image_path: The path to the image file that you want to extract information from. It should be
    a string representing the file path
    :param location: A string that specifies the location or type of identification document.
    :return: a dictionary containing extracted information from the image.
    """
    information = {}

    # Load the image
    image = cv2.imread(image_path)

    # Resize Image
    image = cv2.resize(image, (620, 413), interpolation=cv2.INTER_CUBIC)

    # Load the base image
    # String formatting would be cleaner but would require the image types to be the same
    if location == "AUSTRALIA_WA":
        base_image = cv2.imread("./ocr/test_images/WA-driver-license.jpeg")
    elif location == "AUSTRALIA_VIC":
        base_image = cv2.imread("./ocr/test_images/VIC-driver-license.jpg")
    elif location == "AUSTRALIA_TAS":
        base_image = cv2.imread("./ocr/test_images/TAS-driver-license.jpeg")
    elif location == "AUSTRALIA_SA":
        base_image = cv2.imread("./ocr/test_images/SA-driver-license.png")
    elif location == "AUSTRALIA_QLD":
        base_image = cv2.imread("./ocr/test_images/QLD-driver-license.jpg")
    elif location == "AUSTRALIA_NT":
        base_image = cv2.imread("./ocr/test_images/NT-driver-license.png")
    elif location == "AUSTRALIA_NSW":
        base_image = cv2.imread("./ocr/test_images/NSW-driver-license.jpg")
    elif location == "AUSTRALIA_ACT":
        base_image = cv2.imread("./ocr/test_images/ACT-driver-license.png")
    elif location == "AUSTRALIA_PASSPORT":
        base_image = cv2.imread("./ocr/test_images/AUS-passport.jpg")

    for key, roi in getattr(ImageConstantROI.CCCD, location).items():
        data = ""
        for r in roi:
            crop_img = crop_image_roi(image, r)
            crop_img = preprocessing(crop_img)
            data += (
                pytesseract.image_to_string(
                    crop_img, config="--psm 6 --oem 3", lang="eng"
                )
                .replace("\n", " ")
                .strip()
                + " "
            )
        information[key] = data.strip()

        if location == "AUSTRALIA_SA" or location == "AUSTRALIA_ACT":
            parts = information["name"].split()
            information["name"] = f"{' '.join(parts[1:])} {parts[0]}"

    return information


def date_builder(day, month, year):
    """
    The function `date_builder` is a helper function that formats a date into "dd-mm-yyyy".

    :param day: The day parameter is the numerical representation of the day in the date. For example,
    if the date is January 15th, the day parameter would be 15
    :param month: The month parameter is the numerical representation of the month in the date. For
    example, January would be represented by 1, February by 2, and so on
    :param year: The year parameter is the numerical representation of the year. For example, if you
    want to format the date as "01-01-2022", the year parameter would be 2022
    :return: a formatted date string in the format "dd-mm-yyyy".
    """
    return f"{day}-{month}-{year}"


def adjust_zeros(date):
    """
    the `adjust_zeros` function replaces any 0s or Os that have been incorrectly detected by the OCR program.
    :param date: a string that represents a date in various formats
    :return: the same date with any incorrect 0s and Os replaced
    """
    length = len(date)
    # transforming to uppercase
    date = date.upper()

    # for each accepted date layout, replace Os and 0s
    if length == 8:
        formatted_date = date.replace("O", "0")
    elif length == 9:
        formatted_date = (
            date[:2].replace("O", "0")
            + date[2:5].replace("0", "O")
            + date[5:].replace("O", "0")
        )
    elif length == 10:
        formatted_date = date.replace("O", "0")
    elif length == 11:
        formatted_date = (
            date[:2].replace("O", "0")
            + date[2:7].replace("0", "O")
            + date[7:].replace("O", "0")
        )
    elif length == 12:
        formatted_date = (
            date[:2].replace("O", "0")
            + date[2:8].replace("0", "O")
            + date[8:].replace("O", "0")
        )
    # the date is not in an accepted format
    else:
        return 0

    return formatted_date


def month_conversion(month):
    """
    The function `month_conversion` is a helper function that converts a month from letter format to
    number format.

    :param month: The parameter "month" is a string representing a month in letter format
    :return: The function `month_conversion` returns the corresponding number format of the given month
    abbreviation. If the given month is not found in the dictionary `month_dict`, it returns "00".
    """
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
    """
    The `date_formatter` function takes a single date in various formats and transforms it into the
    dd-mm-yyyy format.

    :param text: A string that represents a date in various formats
    :return: the formatted date in the dd-mm-yyyy format.
    """
    # date to return
    date = ""

    # replacing incorrect 0s and Os
    text = adjust_zeros(text)

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
    """
    The function `validate_date` takes a date as input and checks if it is a valid date, returning the
    input date if valid or 0 if invalid.

    :param date: A string representing a date in the format "dd-mm-yyyy"
    :return: 0 if the input date is invalid, or the input date itself if it is valid.
    """
    # retrieving parts of date
    try:
        day = int(date[:2])
        month = int(date[3:5])
        year = int(date[6:])
    except:
        return 0
    # checking date is valid
    # if the month has under 31 days
    if day == 31 and (
        month == 2 or month == 4 or month == 6 or month == 9 or month == 11
    ):
        return 0
    # if the month is feb
    if month == 2:
        if day == 30:
            return 0
        # checking for leap year
        if day == 29:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) == False:
                return 0
    # if the day is invalid
    if 31 < day or day < 1:
        return 0
    # if the month is invalid
    if 13 < month or month < 1:
        return 0
    # if the year is invalid
    if year < 1900 or year > 2100:
        return 0
    # else, date is valid
    else:
        return date


def remove_file(image_path):
    """
    The `remove_file` function removes a file with the given image path if it exists and is an image,
    otherwise it returns 0.

    :param image_path: The path of the image file that you want to remove
    :return:  0 if the file does not exist or is not an image, otherwise it returns 1 if the file exists
    and is an image and is successfully deleted.
    """
    # if the file doesnt exist, return error
    if not os.path.exists(image_path):
        return 0

    # if the file is not an image, return error
    f_type = imghdr.what(image_path)
    if not f_type:
        return 0

    # if the file exists, and is an image, delete it
    os.remove(image_path)
    return 1


def clean_up_data(information):
    """
    The function `clean_up_data` takes in information extracted from a document, cleans and validates
    the data, and returns the cleaned information.

    :param information: A dictionary in the format returned by extract_information()
    :return: the cleaned up information dictionary, or 0 if an error occurred
    """
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

    remove_file("result_image.jpg")

    return information
