import cv2

# Load the image
image = cv2.imread("./test_images/WA-driver-license.jpeg")
image = cv2.resize(image, (620, 413), interpolation=cv2.INTER_CUBIC)


# Callback function for mouse click
def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at coordinates: ({x}, {y})")


# Create a window and display the image
cv2.imshow("Image", image)

# Set up mouse callback for the 'Image' window
cv2.setMouseCallback("Image", get_coordinates)

# Wait for a mouse click and close the window when done
cv2.waitKey(0)
cv2.destroyAllWindows()
