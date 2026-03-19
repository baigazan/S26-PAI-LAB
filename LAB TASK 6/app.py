from flask import Flask, render_template, request
import os
from yolo import detect_herd

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        output_path, count = detect_herd(filepath)

        return render_template("result.html",
                               image=output_path,
                               count=count)

    return "No file uploaded"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=True)