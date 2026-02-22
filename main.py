import os

import sentry_sdk
from flask import Flask, request
from sqlmodel import Session, select

from database import engine, init_db
from models import Link

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    send_default_pii=True,
)

app = Flask(__name__)


def _base_url() -> str:
    return (os.environ.get("BASE_URL") or "https://short.io").rstrip("/")


def _link_to_json(link: Link) -> dict:
    return {
        "id": link.id,
        "original_url": link.original_url,
        "short_name": link.short_name,
        "short_url": f"{_base_url()}/r/{link.short_name}",
    }


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


@app.route("/api/links", methods=["GET"])
def list_links():
    with Session(engine) as session:
        links = session.exec(select(Link).order_by(Link.id)).all()
        return [_link_to_json(link) for link in links]


@app.route("/api/links", methods=["POST"])
def create_link():
    data = request.get_json(silent=True) or {}
    original_url = data.get("original_url")
    short_name = data.get("short_name")
    if not original_url or not short_name:
        return {"error": "original_url and short_name are required"}, 422
    with Session(engine) as session:
        existing = session.exec(
            select(Link).where(Link.short_name == short_name)
        ).first()
        if existing:
            return {"error": "short_name already exists"}, 422
        link = Link(original_url=original_url, short_name=short_name)
        session.add(link)
        session.commit()
        session.refresh(link)
        return _link_to_json(link), 201


@app.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id):
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            return {"error": "Not Found"}, 404
        return _link_to_json(link)


@app.route("/api/links/<int:link_id>", methods=["PUT"])
def update_link(link_id):
    data = request.get_json(silent=True) or {}
    original_url = data.get("original_url")
    short_name = data.get("short_name")
    if not original_url or not short_name:
        return {"error": "original_url and short_name are required"}, 422
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            return {"error": "Not Found"}, 404
        existing = session.exec(
            select(Link).where(Link.short_name == short_name, Link.id != link_id)
        ).first()
        if existing:
            return {"error": "short_name already exists"}, 422
        link.original_url = original_url
        link.short_name = short_name
        session.add(link)
        session.commit()
        session.refresh(link)
        return _link_to_json(link)


@app.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            return {"error": "Not Found"}, 404
        session.delete(link)
        session.commit()
        return "", 204


@app.errorhandler(404)
def not_found(error):
    return {"error": "Not Found"}, 404


@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal Server Error"}, 500


# Create tables on app load (e.g. gunicorn) or when run as script
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
