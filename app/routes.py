import os
import re

from flask import Blueprint, redirect, request
from links import (
    get_link_by_id,
    get_link_by_short_name,
    get_links_with_total,
    try_create_link,
    try_delete_link,
    try_update_link,
)
from models import Link

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
    links_list, total, content_range = get_links_with_total(range_param)
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
    result = try_create_link(original_url, short_name)
    if result == "duplicate":
        return {"detail": "short_name already exists"}, 422
    return _link_to_json(result), 201


@bp.route("/api/links/<int:link_id>", methods=["GET"])
def get_link(link_id):
    link = get_link_by_id(link_id)
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
    result = try_update_link(link_id, original_url, short_name)
    if result == "not_found":
        return {"detail": "Not Found"}, 404
    if result == "duplicate":
        return {"detail": "short_name already exists"}, 422
    return _link_to_json(result)


@bp.route("/api/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    if not try_delete_link(link_id):
        return {"detail": "Not Found"}, 404
    return "", 204


@bp.route("/r/<short_name>", methods=["GET"])
def redirect_by_short_name(short_name):
    link = get_link_by_short_name(short_name)
    if not link:
        return {"detail": "Not Found"}, 404
    return redirect(link.original_url, code=302)
