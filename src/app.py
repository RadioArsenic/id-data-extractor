import os, shutil
from src.OCR import imageToText
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
    # check if the post request has the file part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    # file name has to be "file" in order for it to work
    file = request.files["file"]

    # if user does not select file, browser submits an empty part without filename
    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    # Extracting the selectedOption value from the request
    state = formatedState(request.form.get("selectedOption"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        filepath = "./uploads/" + filename

        ###################################################### To be changed with actual OCR code
        extractedData = imageToText(filepath)
        # extractedData = "error"

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

def formatedState(state):
    if (state == "Western Australia"):
        return "AUSTRALIA_WA"
    if (state == "New South Wales"):
        return "AUSTRALIA_NSW"
    if (state == "Victoria"):
        return "AUSTRALIA_WA"
    if (state == "Northern Territory"):
        return "AUSTRALIA_NT"
    if (state == "Australian Capital Territory"):
        return "AUSTRALIA_ACT"
    if (state == "Southern Australia"):
        return "AUSTRALIA_SA"
    if (state == "Tasmania"):
        return "AUSTRALIA_TAS"
    if (state == "Queensland"):
        return "AUSTRALIA_QL"
    if (state == "PASSPORT"):
        return "AUSTRALIA"
    

if __name__ == "__main__":
    app.run(ssl_context=("cert.pem", "key.pem"))
