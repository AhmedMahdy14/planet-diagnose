import os
from flask import Flask, render_template, jsonify, request
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

app = Flask(__name__)


@app.route("/upload", methods=['POST'])
def upload_file():
    cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

    if request.method == 'POST':
        file_to_upload = request.files['file']
        app.logger.info('%s file_to_upload', file_to_upload)
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload)
            app.logger.info(upload_result)
            return jsonify(upload_result)


@app.route('/')
def hello_world():
    # from inference_sdk import InferenceHTTPClient
    # CLIENT = InferenceHTTPClient(
    #     api_url="https://detect.roboflow.com",
    #     api_key="G612WzEzRuy4vjhLaSTF"
    # )

    # https://universe.roboflow.com/shiv-xbj9m/plant-disease-kkt3g/model/1
    # result = CLIENT.infer("./dd.jpeg", model_id="plant-disease-kkt3g/1")

    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
