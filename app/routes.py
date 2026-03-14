import os
import re

from flask import Blueprint, redirect, request

from database import engine
from links import (
    create_link as create_link_record,
    delete_link as delete_link_record,
    get_link_by_id,
    get_link_by_short_name,
    get_links_with_total,
    short_name_exists,
    update_link as update_link_record,
)
from models import Link
from sqlmodel import Session

bp = Blueprint("api", __name__)


def _base_url() -> str:
    return (os.environ.get("BASE_URL") or "https://short.io").rstrip("/")


def _link_to_json(link: Link) -> dict:
    return {
        "id": link.id,
        "original_url": link.original_url,
        "short_name": link.short_name,
        "short_url": f"{_base_url()}/r/{link.short_name}",
    }


def _parse_range(range_str: str | None) -> tuple[int, int] | None:
    """Parse range=[start,end] from query. Returns (start, end) or None."""
    if not range_str or not range_str.strip():
        return None
    match = re.match(r"^\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]\s*$", range_str.strip())
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    if end < start:
        return None
    return (start, end)


def _validation_error_required() -> tuple[dict, int]:
    return (
        {
            "detail": [
                {"loc": ["body", "original_url"], "msg": "Field required"},
                {"loc": ["body", "short_name"], "msg": "Field required"},
            ]
        },
        422,
    )


@bp.route("/ping", methods=["GET"])
def ping():
    return "pong"


@bp.route("/api/links", methods=["GET"])
def list_links():
    range_param = _parse_range(request.args.get("range"))
    with Session(engine) as session:
        links_list, total, content_range = get_links_with_total(session, range_param)
    return (
        [_link_to_json(link) for link in links_list],
        200,
        {"Content-Range": content_range},
    )


@bp.route("/api/links", methods=["POST"])
def create_link():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        data = {}
    original_url = data.get("original_url")
    short_name = data.get("short_name")
    if not original_url or not short_name:
        return _validation_error_required()
    with Session(engine) as session:
        if short_name_exists(session, short_name):
            return {"detail": "short_name already exists"}, 422
        link = create_link_record(session, original_url, short_name)
    return _link_to_json(link), 201


@bp.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id):
    with Session(engine) as session:
        link = get_link_by_id(session, link_id)
    if not link:
        return {"detail": "Not Found"}, 404
    return _link_to_json(link)


@bp.route("/api/links/<int:link_id>", methods=["PUT"])
def update_link(link_id):
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        data = {}
    original_url = data.get("original_url")
    short_name = data.get("short_name")
    if not original_url or not short_name:
        return _validation_error_required()
    with Session(engine) as session:
        link = get_link_by_id(session, link_id)
        if not link:
            return {"detail": "Not Found"}, 404
        if short_name_exists(session, short_name, exclude_id=link_id):
            return {"detail": "short_name already exists"}, 422
        updated = update_link_record(session, link_id, original_url, short_name)
    return _link_to_json(updated)  # type: ignore[arg-type]


@bp.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    with Session(engine) as session:
        deleted = delete_link_record(session, link_id)
    if not deleted:
        return {"detail": "Not Found"}, 404
    return "", 204


@bp.route("/r/<short_name>", methods=["GET"])
def redirect_by_short_name(short_name):
    with Session(engine) as session:
        link = get_link_by_short_name(session, short_name)
    if not link:
        return {"detail": "Not Found"}, 404
    return redirect(link.original_url, code=302)
