import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

WEBSITE_DIR = os.path.join(BASE_DIR, "website")
CSS_DIR = os.path.join(BASE_DIR, "css")
JS_DIR = os.path.join(BASE_DIR, "js")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "misuki-development-key"
)


@app.route("/")
def index():
    return send_from_directory(
        WEBSITE_DIR,
        "index.html"
    )


@app.route("/<page>.html")
def website_page(page):
    return send_from_directory(
        WEBSITE_DIR,
        f"{page}.html"
    )


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(
        CSS_DIR,
        filename
    )


@app.route("/js/<path:filename>")
def javascript(filename):
    return send_from_directory(
        JS_DIR,
        filename
    )


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(
        ASSETS_DIR,
        filename
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=False
    )