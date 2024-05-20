import os

from PIL import Image
from flask import Flask, render_template, jsonify, request, url_for, send_from_directory
import cloudinary
import cloudinary.uploader
from inference_sdk import InferenceHTTPClient
from werkzeug.utils import secure_filename

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="G612WzEzRuy4vjhLaSTF"
)
MODEL_ID = "plant-disease-kkt3g/1"

cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit


def perform_inference(file):
    """Helper function to perform inference using the Roboflow API."""
    try:
        # Save the file to the upload folder
        # filename = secure_filename(file.filename)
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(file_path)

        # Perform inference
        # https://universe.roboflow.com/shiv-xbj9m/plant-disease-kkt3g/model/1
        result = CLIENT.infer(file, model_id="plant-disease-kkt3g/1")
        print(result)

        # Delete the file after inference
        # os.remove(file)

        return result, None
    except Exception as e:
        return None, str(e)


@app.route('/')
def index():
    return render_template('index.html')


# @app.route("/infer", methods=['POST'])
# def infer_image():
#     if request.method == 'POST':
#         file_to_upload = request.files['file']
#         result, error = perform_inference(file_to_upload)
#         if error:
#             return jsonify({'message': 'Inference failed', 'error': error}), 500
#
#         print(result)
#         return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the image (convert to grayscale in this example)
        image = Image.open(file_path).convert('L')
        processed_filename = 'processed_' + filename
        processed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        image.save(processed_file_path)

        # https://universe.roboflow.com/shiv-xbj9m/plant-disease-kkt3g/model/1
        result, _ = perform_inference(processed_file_path)
        if result['predictions']:
            r = "Powdery Mildew is captured with confidence " + str(
                int(result['predictions'][0]['confidence'] * 100)) + " %"
        else:
            r = "No Powdery Mildew is captured"
        return jsonify({
            "message": r,
            "image_url": url_for('uploaded_file', filename=processed_filename)
        })


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
