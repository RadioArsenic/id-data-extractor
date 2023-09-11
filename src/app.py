from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

#for holding the uploading images
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    return "Hello World, flask!"

#function for testing api call, this api call returns the ascii of a character
@app.route("/api", methods = ['GET'])
def return_ascii():
    dictionary = {}
    inputchr = str(request.args['query'])
    answer = str(ord(inputchr))
    dictionary['output'] = answer
    return jsonify(dictionary)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    # check if the post request has the file part
    # if 'file' not in request.files:
    #     return jsonify({'error': 'No file part in the request.'}), 400
    
    # file name has to be "file" in order for it to work
    file = request.files['file']

    # if user does not select file, browser submits an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': 'File uploaded successfully!', 'filename': filename}), 200

    return jsonify({'error': 'File type not allowed.'}), 400



if __name__ == "__main__":
    app.run(debug=True)
