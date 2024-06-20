import os
import requests
from flask import Flask, render_template, jsonify, request
import cloudinary
import cloudinary.uploader
import cloudinary.api
from inference_sdk import InferenceHTTPClient
from flask_sqlalchemy import SQLAlchemy

cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="G612WzEzRuy4vjhLaSTF"
)

MODEL_ID = "plant-disease-kkt3g/1"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
                                                  'postgres://uatngc8vpchqgn:ped841106285a3fde3b5b56635ebd8d23ef777ed2efa4583995eedb32feaf8acb@c5p86clmevrg5s.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dds4v25hrjtbs5')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)


@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    new_entry = SensorData(temperature=data['temperature'], humidity=data['humidity'])
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "Data added"}), 201


@app.route('/data', methods=['GET'])
def get_data():
    results = SensorData.query.all()
    data = [{"temperature": entry.temperature, "humidity": entry.humidity} for entry in results]
    return jsonify(data)


# socketio = SocketIO(app)

# MongoDB connection
# client = MongoClient(
#     'mongodb+srv://ahmedmahdy1420:p1FiayTc5IxFt5De@cluster0.18q1cq3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
# db = client.sensor_data
# collection = db.readings


# Fetch data from MongoDB
# def fetch_data():
#     cursor = collection.find().sort('timestamp', -1).limit(10)
#     return list(cursor)


# Monitor MongoDB for changes
# def monitor_changes():
#     with collection.watch() as stream:
#         for change in stream:
#             socketio.emit('new_data', fetch_data())


# Run the monitor_changes function in a separate thread
# thread = threading.Thread(target=monitor_changes)
# thread.start()
#

@app.route('/')
def index():
    # data = fetch_data()
    # print(data)
    return render_template('index.html')


# @socketio.on('connect')
# def handle_connect():
#     socketio.emit('new_data', fetch_data())
#

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

# Host
# c5p86clmevrg5s.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com
# Database
# dds4v25hrjtbs5
# User
# uatngc8vpchqgn
# Port
# 5432
# Password
# ped841106285a3fde3b5b56635ebd8d23ef777ed2efa4583995eedb32feaf8acb
# URI
# postgres://uatngc8vpchqgn:ped841106285a3fde3b5b56635ebd8d23ef777ed2efa4583995eedb32feaf8acb@c5p86clmevrg5s.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dds4v25hrjtbs5
# Heroku CLI
# heroku pg:psql postgresql-colorful-94934 --app flask-app-ams

# import requests
#
# def send_data_to_heroku(temperature, humidity):
#     url = "https://your-app-name.herokuapp.com/add"
#     data = {
#         "temperature": temperature,
#         "humidity": humidity
#     }
#     response = requests.post(url, json=data)
#     print(response.json())
#
# # Example usage:
# temperature = 22.5
# humidity = 60
# send_data_to_heroku(temperature, humidity)


# heroku run python
# >>> from app import db
# >>> db.create_all()
# >>> exit()
