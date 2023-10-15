import os, shutil
from OCR.OCR import extract_information, clean_up_data
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
    api_key = request.headers.get("x-api-key")
    if api_key is None or api_key not in VALID_API_KEYS:
        return jsonify(error="Missing or invalid API key."), 403


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Receives an image from
@app.route("/extractData", methods=["POST"])
def extract_data():
    # checks to see whether the folder to contain file exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # check if the post request has the/a file
    if "file" not in request.files:
        return jsonify({"error": "No file in the request."}), 400

    # file name has to be "file" in order for it to work
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

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
    return formatted


if __name__ == "__main__":
    app.run(debug=True, ssl_context=("cert.pem", "key.pem"))
