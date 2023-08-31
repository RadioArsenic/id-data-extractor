from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World, flask!"

@app.route("/api", methods = ['GET'])
def return_ascii():
    dictionary = {}
    inputchr = str(request.args['query'])
    answer = str(ord(inputchr))
    dictionary['output'] = answer
    return jsonify(dictionary)

if __name__ == "__main__":
    app.run(debug=True)
