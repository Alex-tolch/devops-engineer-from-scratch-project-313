import os

import sentry_sdk
from flask import Flask
from flask_cors import CORS

from database import init_db
from routes import bp

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    send_default_pii=True,
)

app = Flask(__name__)

CORS(
    app,
    origins=["http://localhost:5173"],
    methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Content-Range", "Range", "Authorization"],
    supports_credentials=True,
)

app.register_blueprint(bp)


@app.errorhandler(404)
def not_found(error):
    return {"detail": "Not Found"}, 404


@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal Server Error"}, 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
