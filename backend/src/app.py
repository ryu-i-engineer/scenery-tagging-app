import werkzeug

from flask import Flask, redirect, render_template, request, jsonify
from base64 import b64encode
from inference import get_prediction

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files.get("file")
        if not file:
            return 'Bad Request', 400

        image_byte = file.read()
        predict_class = get_prediction(image_byte=image_byte)
        uploaded_image = b64encode(image_byte).decode("utf-8")
        return render_template("result.html", uploaded_image=uploaded_image, predict_class=predict_class)

    return render_template("index.html")


@app.route("/api", methods=["POST"])
def api_predict():
    if request.method != "POST":
        return 'Bad Request', 400

    if "file" not in request.files:
        return 'Bad Request', 400

    file = request.files.get("file")
    if not file:
        return 'Bad Request', 400

    image_byte = file.read()
    predict_class = get_prediction(image_byte=image_byte)

    return jsonify({'predict_class': predict_class})


@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_file_size(error):
    return 'The uploaded image size was larger than 10MB.', 413


if __name__ == "__main__":
    app.run(debug=True)
