import pytesseract
import cv2
import numpy as np


def imageToText(image_path):
    # Load the image
    image = cv2.imread('WA-driver-license.jpeg')

    # Resize image
    image = cv2.resize(image,(620,413), interpolation=cv2.INTER_CUBIC)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold the image to convert non-black areas to white
    _, thresholded = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

    # Create an all-white image of the same size as the original image
    result = np.ones_like(image) * 255

    # Copy the black areas from the original image to the result
    result[thresholded == 0] = image[thresholded == 0]

    # Save or display the resulting image
    cv2.imwrite('result_image.jpg', result)

    # Display the result (optional)
    cv2.imshow('Result Image', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Extract text from image
    text = pytesseract.image_to_string(result, config = '--psm 6 --oem 3', lang='eng')

print(imageToText("WA-driver-license.jpeg"))
print("---------------------------------------")
print(imageToText("Victoria-driver-license.jpg"))
print("---------------------------------------")
print(imageToText("NSW-driver-license.jpg"))
