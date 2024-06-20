import os

import requests
from flask import Flask, render_template, jsonify, request
import cloudinary
import cloudinary.uploader
import cloudinary.api
from inference_sdk import InferenceHTTPClient
# import firebase_admin
# from firebase_admin import credentials, db
from flask_socketio import SocketIO
from pymongo import MongoClient
import threading

cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="G612WzEzRuy4vjhLaSTF"
)

MODEL_ID = "plant-disease-kkt3g/1"

# cred = credentials.Certificate("drone-keys.json")
#
# firebase_admin.initialize_app(cred, {'databaseURL': 'https://drone-7dba9-default-rtdb.firebaseio.com'})
#
# ref = db.reference('/')

app = Flask(__name__)

socketio = SocketIO(app)

# MongoDB connection
client = MongoClient('mongodb+srv://ahmedmahdy1420:p1FiayTc5IxFt5De@cluster0.18q1cq3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.sensor_data
collection = db.readings


# Fetch data from MongoDB
def fetch_data():
    cursor = collection.find().sort('timestamp', -1).limit(10)
    return list(cursor)


# Monitor MongoDB for changes
def monitor_changes():
    with collection.watch() as stream:
        for change in stream:
            socketio.emit('new_data', fetch_data())


# Run the monitor_changes function in a separate thread
thread = threading.Thread(target=monitor_changes)
thread.start()


@app.route('/')
def index():
    data = fetch_data()
    print(data)
    return render_template('index.html', data=data)


@socketio.on('connect')
def handle_connect():
    socketio.emit('new_data', fetch_data())


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Upload the file to Cloudinary
    print(f"file {file}")
    upload_result = cloudinary.uploader.upload(file)
    image_url = upload_result.get('secure_url')

    return jsonify({
        "message": "Uploaded Successfully",
        "image_url": image_url
    }), 200


@app.route('/check-cloudinary', methods=['GET'])
def check_cloudinary():
    resources = cloudinary.api.resources(type="upload", max_results=10)
    results = []
    for resource in resources['resources']:
        public_id = resource['public_id']
        url = resource['url']

        # Download the image
        response = requests.get(url)
        if response.status_code == 200:
            # secure_url = resource['secure_url']
            secure_url = resource['url']
            print(f"url {resource['url']}")
            print(f"secure_url {resource['secure_url']}")
            # Perform inference
            result, _ = perform_inference(secure_url)
            if result['predictions']:
                r = "Powdery Mildew is captured with confidence " + str(
                    int(result['predictions'][0]['confidence'] * 100)) + " %"
            else:
                r = "No Powdery Mildew is captured"

            results.append({
                "message": r,
                "image_url": secure_url
            })
        else:
            results.append({
                "message": "Failed to download image",
                "image_url": url
            })

    return jsonify({"results": results})

@app.route('/delete_all_images', methods=['DELETE'])
def delete_all_images():
    try:
        # Fetch all resources
        resources = cloudinary.api.resources(type='upload')

        # Loop through each resource and delete it
        for resource in resources['resources']:
            cloudinary.uploader.destroy(resource['public_id'])

        return jsonify({"message": "All images deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def perform_inference(file):
    """Helper function to perform inference using the Roboflow API."""
    try:
        # Perform inference
        # https://universe.roboflow.com/shiv-xbj9m/plant-disease-kkt3g/model/1
        result = CLIENT.infer(file, model_id="plant-disease-kkt3g/1")
        print(result)
        return result, None
    except Exception as e:
        print(e)
        return None, str(e)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
