import os, shutil
from OCR.OCR import extract_information
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
        return jsonify(error="missing or invalid API key"), 403


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
    state = formated_state(request.form.get("selectedOption"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        filepath = "./uploads/" + filename

        ###################################################### To be changed with actual OCR code
        # extractedData = extract_information(filepath, state)
        extractedData = "error"

        # deletes the images from the client after text has been extracted
        if os.path.isdir("./uploads"):
            shutil.rmtree("./uploads")
        if extractedData == "error":
            return jsonify({"error": "improper image please retake"}), 200
        else:
            # parseToJson here
            return (
                jsonify(
                    {
                        "success": "File uploaded successfully!",
                        "filename": filename,
                        "name": "John Doe",
                        "birthdate": "23MAY1999",
                        "address": "13 CHALLIS ST DICKSON ACT 2602" + state,
                        "realdata": extractedData,  # needs to be parsed
                    }
                ),
                200,
            )
    return jsonify({"error": "File type not allowed."}), 400


def formated_state(state):
    formated = "AUSTRALIA"
    if state == "Western Australia":
        formated = formated + "_WA"
    elif state == "New South Wales":
        formated = formated + "_NSW"
    elif state == "Victoria":
        formated = formated + "_VIC"
    elif state == "Northern Territory":
        formated = formated + "_NT"
    elif state == "Australian Capital Territory":
        formated = formated + "_ACT"
    elif state == "Southern Australia":
        formated = formated + "_SA"
    elif state == "Tasmania":
        formated = formated + "_TAS"
    elif state == "Queensland":
        formated = formated + "_QL"
    elif state == "PASSPORT":
        # assuming default is passport
        pass
    return formated


if __name__ == "__main__":
    app.run(debug=True, ssl_context=("cert.pem", "key.pem"))
