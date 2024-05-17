from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    # from inference_sdk import InferenceHTTPClient
    # CLIENT = InferenceHTTPClient(
    #     api_url="https://detect.roboflow.com",
    #     api_key="G612WzEzRuy4vjhLaSTF"
    # )
    #
    # # 3. Powdery mildew https://universe.roboflow.com/search?q=powdery%C2%A0mildew
    # result = CLIENT.infer("download.png", model_id="tomato-disease-b518h/3")

    return render_template('index.html')


if __name__ == '__main__':
    app.run()
