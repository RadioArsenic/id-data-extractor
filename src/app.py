import os, shutil
from ocr.ocr import extract_information, clean_up_data
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename


# for holding the uploading images
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# area to put api keys
VALID_API_KEYS = ["JPkxhc9cGFv35OWu267fsx8R6uZj29GL"]


# Security check for user whether contain api key
@app.before_request
def check_api_key():
    """
    The function and api call `extract_data` takes in the http POST request with an image file. 
    This image file goes through the extracted_data() function to retrieve the ID details, which is
    then formated and send back through a JSON object

    :param (headers) information: Header "selectedOption" containing state and image binary in the body
    :return: formated string, or 0 if an error occurred
    """
    api_key = request.headers.get("x-api-key")
    if api_key is None or api_key not in VALID_API_KEYS:
        return jsonify(error="Missing or invalid API key."), 403


def allowed_file(filename):
    """
    The function `allowed_file()` checks for whether the image file coming in is the allowed image types

    :param information: the name of the image file
    :return: 1 if file type is acceptable, 0 if file type is not 
    """
    if("." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS):
        return 1
    return 0


# Receives an image from
@app.route("/extract_data", methods=["POST"])
def extract_data():
    """
    The function and api call `extract_data` takes in the http POST request with an image file. 
    This image file goes through the extracted_data() function to retrieve the ID details, which is
    then formated and send back through a JSON object

    :param (headers) information: Header "selectedOption" containing state and image binary in the body
    :return: formated string, or 0 if an error occurred
    """
    # checks to see whether the folder to contain file exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # check if the post request has File type with key value :"ID_image"
    if "ID_image" not in request.files:
        print(request.files)
        return jsonify({"error": "No File with appropriate key value for extraction"}), 400
    
    #retrieves the value of key "ID_image"
    file = request.files["ID_image"]
    if file.filename == "":
        return jsonify({"error": "No image content in file of request"}), 400

    # Extracting the selectedOption value from the request
    state = formatted_state(request.form.get("selectedOption"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        filepath = "./uploads/" + filename

        # Calls the OCR program to process the image and extract the data
        extracted_data = extract_information(filepath, state)

        # deletes the images from the client after text has been extracted
        if os.path.isdir("./uploads"):
            shutil.rmtree("./uploads")

        # Cleans up the data and checks validity of dates
        extracted_data = clean_up_data(extracted_data)
        if extracted_data == 0:
            return jsonify({"error": "Improper image please retake."}), 400

        return (
            jsonify(
                {
                    "success": "Information received successfully!",
                    "name": extracted_data["name"],
                    "address": extracted_data["address"],
                    "expiry_date": extracted_data["expiry_date"],
                    "date_of_birth": extracted_data["date_of_birth"],
                }
            ),
            200,
        )
    return jsonify({"error": "File type not allowed."}), 400


def formatted_state(state):
    """
    The function `formatted_state` takes in the state selected from the flutter app and 
    formats it to approprate format for ocr program.

    :param information: A string from the flutter app of the state chose in a presentable format
    :return: formated string, or 0 if an error occurred
    """
    formatted = "AUSTRALIA"
    if state == "Western Australia":
        formatted = formatted + "_WA"
    elif state == "New South Wales":
        formatted = formatted + "_NSW"
    elif state == "Victoria":
        formatted = formatted + "_VIC"
    elif state == "Northern Territory":
        formatted = formatted + "_NT"
    elif state == "Australian Capital Territory":
        formatted = formatted + "_ACT"
    elif state == "Southern Australia":
        formatted = formatted + "_SA"
    elif state == "Tasmania":
        formatted = formatted + "_TAS"
    elif state == "Queensland":
        formatted = formatted + "_QLD"
    elif state == "PASSPORT":
        formatted = formatted + "_PASSPORT"
    if formatted == "AUSTRALIA":
        return 0
    return formatted


if __name__ == "__main__":
    app.run(debug=True, ssl_context=("cert.pem", "key.pem"))
