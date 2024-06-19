import requests
from flask import Flask, render_template, jsonify, request
import cloudinary
import cloudinary.uploader
import cloudinary.api
from inference_sdk import InferenceHTTPClient
import firebase_admin
from firebase_admin import credentials, db

cloudinary.config(cloud_name="ddgeg9myx", api_key="911351556278827", api_secret="i9GCIpqx7AkzfLtUcUsFVYg652o")

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="G612WzEzRuy4vjhLaSTF"
)

MODEL_ID = "plant-disease-kkt3g/1"
service_account_info = {
    "type": "service_account",
    "project_id": "drone-7dba9",
    "private_key_id": "f44c905d6e0ecf299a33b15fc847b242c10787c7",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDLJPdNaFrAhJRZ\nHtAKUbsTJGny2DaFX7+pJvQYjZIUO0N+UGOkuZ5uYYS5TpxJr+0jMWN/YSQXZeOt\nS2KpXQGyCPaw0DJRulyDHozjNEjnHs6+jCtnmeBWoxfeRYf5mPBp6mbuZ9BqOBi4\n+j0YqIbnKGVYXYp0kfdCbtkbWp1y2f/ki0LSdLZqXTI4okDmAP7EcSZxxxPoFqmM\nSGekOTO5n8rKKBsu6AEeOtiRjUgaQkIn/vgp8Glfsj2v3xmzOgVBBcmsEsMFWX4G\nOm0C8qa/xzKhFGWmbDwxIG3G3DYW9bL1YRgUdAnDNa6/QBouIe0D/u8WvwKGCuZ4\nnBd4fKDZAgMBAAECggEAMyHq3aEWtr6oWIZY9z/7RqYzxNyHXKrtIzaa2lNIIa+J\nHZI+gof2SPJi5gHTdPjDR8h2sulQnFMZK9V90AOJGbcH4RmGkOvHvXlDHS1b7FDk\n2TGO+1TQEv6aU2hNAZZtbTuDDR80ZogYMPdLyZkh261fVQ62ewECq8Ya/7efSfkB\n0gktJVRFI/6SR3I2H2IA7NvcXQN+nKMKv5BhwCW2p9tdTAchuv4gRvf+FnUIzh0X\nip9eg7EeCTmwV3TRFnNZaeC1ePvPBj6kA4Huf7bv32emLuqvEG3O1xn1jAHY4ts1\nyZwY78cghcWylUYTWp4n1RGnY2ivgRAS1R8YlSu+wQKBgQD/sU0MUwl/qTlp59Wr\nmK8gEM1S58OtBBGmVEnB5SOnfg2yeF7temGz72U8GpLHm0ZceFhsR3b+SBomd1j7\nxkz+BDXKv3vAcWSk+eJDrUVd9Ktcr0ADllL3oBCRFJbWoWOV+nHZqlDXkpwyRDTN\nUZEi+5TObMf44mGTBL9/8h+xJwKBgQDLY33KgmBf2Cyfv7iCKHHlbG1OEBlSB/9v\ncC/KfKvp4WfNtsa69NZUDm0+4PSN2wNCLuwte282Cw8go3ZXW1oJBMmMzYg8Zo2k\nn37dk6sOWAcjz01Wd/APmhzTaqUkSk1ykd+PrG7sdwVeRAjufu6cC/3sMYl9sZKr\nhPbylfBd/wKBgQDS8EAx9KcXbFHzLtE1WSbQe0wIIy9oory0zUBz90csvG8sVuVp\nYNcNjGel5/5DMbQgQSAhY+uk53K7XSZJv1RxEqQV+VZscp+nAodJcb6SPnDIa8OR\nsggMRT6lkajGtCnl5tDZ0woSbd7yERbGc44aoBYpHdDzYD9C/F3HfcXrbQKBgQCt\nbaHWq4OYVpH+ihG/0tMD6Yfu96VPoIg8MvJdfB9vaAgGjuM4igu0UzTuWA3QZD+M\nEMzNH6K994Int5rydG/6nr1qNdwEfQIsrOAV+pPywDceXuc4Yz8tXqFT2W0F2+Hc\nXuy96zAOrJLERclD7LJ0F3mnDLqLln5ViSS1yArVawKBgHpCHzJ/zEgdYl/y4ky6\nc0Dv7DM6jN2EzfE7N+qoaSm8hvuM3Eog8SWEt/Ymihwt5YjjSUhgjgJLh7Z1Kcf+\nsjUOJ+HiUmQkhg+4r1vUsPc8ZgS9+Ayr/TB0pfanSdbUrt2n4jLPWBQUkM+mkLp5\nm8puK43EJW3go1ZAXynmzO7t\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-9kezu@drone-7dba9.iam.gserviceaccount.com",
    "client_id": "108569095929246151990",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-9kezu%40drone-7dba9.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Initialize Firebase
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred, {'databaseURL': 'https://drone-7dba9-default-rtdb.firebaseio.com'})
ref = db.reference('/')

app = Flask(__name__)


@app.route('/fetch-firebase-data')
def fetch_firebase_data():
    result = list(ref.order_by_key().limit_to_last(1).get().values())[0]
    s = "Temp:{:.1f} C    Humidity: {}%".format(result['temperature'], result['humidity'])
    print(s)
    return s


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
    app.run(host="0.0.0.0", port=5000)
