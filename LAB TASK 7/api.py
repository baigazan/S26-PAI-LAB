from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None

    if request.method == 'POST':
        url = "https://dog.ceo/api/breeds/image/random"
        response = requests.get(url)
        data = response.json()
        image_url = data["message"]

    return render_template("index.html", image_url=image_url)


if __name__ == "__main__":
    app.run(debug=True)