import os

from flask import Flask
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


app = Flask(__name__)


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


@app.errorhandler(404)
def not_found(error):
    return {"error": "Not Found"}, 404


@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal Server Error"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
