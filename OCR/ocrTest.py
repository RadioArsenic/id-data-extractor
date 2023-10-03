import pytesseract
from PIL import Image
import cv2
import json
import numpy as np
import re


# path of the image
image_path = 'WA-driver-license.jpeg'

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# open image
image = Image.open(image_path)

# Scale image size to 800 pixels high
desired_height = 800
aspect_ratio = float(desired_height) / image.height
new_width = int(image.width * aspect_ratio)
resized_image = image.resize((new_width, desired_height))

# OCR recognition using Tesseract
def ocr_license(resized_image):
    try:
        # Convert image to grayscale
        gray_image = cv2.cvtColor(np.array(resized_image), cv2.COLOR_BGR2GRAY)

        # Noise reduction using Gaussian filtering
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # Text recognition using Tesseract
        text = pytesseract.image_to_string(Image.fromarray(blurred_image), lang='eng')

        # Split text by newlines
        lines = text.split('\n')

        # Remove blank lines
        lines = [line.strip() for line in lines if line.strip()]

        # Make sure there are at least 6 lines of text, otherwise the required information cannot be extracted
        if len(lines) < 6:
            raise Exception("Not enough lines of text recognized")

        # Extract driver's license number, surname, first name, address, birthday and driver's license expiration date
        license_number_match = re.search(r'\d{5,}', text)
        if license_number_match:
            license_number = license_number_match.group()
        else:
            raise Exception("Driver's license number not found")

        last_name = lines[6]
        first_name = lines[7]
        address = lines[8] + ' ' + lines[9]  # Merge the text of lines 8 and 9
        birthday = " ".join(lines[11].split()[-3:])
        expiration_date = " ".join(lines[11].split()[:3])

        # Store recognition results in JSON format
        result = {
            "license_number": license_number,
            "last_name": last_name,
            "first_name": first_name,
            "address": address,
            "birthday": birthday,
            "expiration_date": expiration_date
        }

        return json.dumps(result, indent=4)
    except Exception as e:
        print(f"error: {str(e)}")
        return None

# Call the OCR function and print the JSON result
result = ocr_license(resized_image)
if result:
    print(result)
else:
    print("Unable to identify driver's license information.")
