import werkzeug
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_cors.decorator import cross_origin

from waitress import serve

from inference import get_prediction

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
cors = CORS(app, resources={r"/api": {"origins": 'http://localhost:port/'}})


@app.route("/api", methods=["POST"])
@cross_origin()
def api_predict():
    if request.method != "POST":
        return 'Bad Request', 400

    if "file" not in request.files:
        return 'Bad Request', 400

    file = request.files.get("file")
    if not file:
        return 'Bad Request', 400

    image_byte = file.read()
    predict_tags = get_prediction(image_byte=image_byte)
    print("predict_tags: ", predict_tags)
    if predict_tags is None:
        return 'Internal Sever Error', 500

    return jsonify({'predict_tags': predict_tags})


@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_file_size(error):
    return 'The uploaded image size was larger than 10MB.', 413


if __name__ == "__main__":
    # app.run()
    serve(app, host='0.0.0.0', port=5000)
