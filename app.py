import os
from flask import Flask, render_template, jsonify, request, send_from_directory
import cloudinary
import cloudinary.uploader
from inference_sdk import InferenceHTTPClient

cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="G612WzEzRuy4vjhLaSTF"
)

MODEL_ID = "plant-disease-kkt3g/1"

app = Flask(__name__)


def perform_inference(file):
    """Helper function to perform inference using the Roboflow API."""
    try:
        # Perform inference
        # https://universe.roboflow.com/shiv-xbj9m/plant-disease-kkt3g/model/1
        result = CLIENT.infer(file, model_id="plant-disease-kkt3g/1")
        print(result)
        return result, None
    except Exception as e:
        return None, str(e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Upload the file to Cloudinary
    upload_result = cloudinary.uploader.upload(file)
    image_url = upload_result.get('secure_url')

    # Perform inference using the URL of the uploaded image
    result, error = perform_inference(image_url)
    if error:
        return jsonify({'message': 'Inference failed', 'error': error}), 500

    if result['predictions']:
        response_message = "Powdery Mildew is captured with confidence " + str(
            int(result['predictions'][0]['confidence'] * 100)) + " %"
    else:
        response_message = "No Powdery Mildew is captured"

    return jsonify({
        "message": response_message,
        "image_url": image_url
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
