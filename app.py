import os, redis, requests, cloudinary, cloudinary.uploader, cloudinary.api
from flask import Flask, render_template, jsonify, request
from inference_sdk import InferenceHTTPClient

cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="G612WzEzRuy4vjhLaSTF"
)

MODEL_ID = "plant-disease-kkt3g/1"

app = Flask(__name__)

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/api/data', methods=['POST'])
def set_data():
    data = request.json
    temperature = data.get('temperature')
    humidity = data.get('humidity')

    if temperature is None or humidity is None:
        return jsonify({'error': 'Temperature or humidity not provided'}), 400

    redis_client.set('temperature', temperature)
    redis_client.set('humidity', humidity)

    return jsonify({'message': 'Temperature and humidity set'}), 200


@app.route('/api/data', methods=['GET'])
def get_data():
    temperature = redis_client.get('temperature')
    humidity = redis_client.get('humidity')

    if temperature is None or humidity is None:
        return jsonify({'error': 'Temperature or humidity not found'}), 404

    return jsonify({
        'temperature': float(temperature),
        'humidity': float(humidity)
    }), 200


@app.route('/')
def index():
    # data = fetch_data()
    # print(data)
    return render_template('index.html')


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
