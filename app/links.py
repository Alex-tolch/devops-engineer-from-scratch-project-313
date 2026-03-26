from typing import Literal

from database import engine
from models import Link
from sqlalchemy import func
from sqlmodel import Session, select


def _get_links_with_total(
    session: Session, range_param: tuple[int, int] | None
) -> tuple[list[Link], int, str]:
    count_row = session.exec(select(func.count()).select_from(Link)).one()
    total = count_row[0] if hasattr(count_row, "__getitem__") else count_row

    if range_param is None:
        links = session.exec(select(Link).order_by(Link.id)).all()
        content_range = "links 0-0/0" if total == 0 else f"links 0-{total - 1}/{total}"
        return (list(links), total, content_range)

    start, end = range_param
    offset = start
    limit = end - start
    links = session.exec(
        select(Link).order_by(Link.id).offset(offset).limit(limit)
    ).all()
    links_list = list(links)
    if total == 0:
        content_range = "links 0-0/0"
    else:
        last = min(start + len(links_list) - 1, total - 1) if links_list else start - 1
        if last < start:
            content_range = f"links 0-0/{total}"
        else:
            content_range = f"links {start}-{last}/{total}"
    return (links_list, total, content_range)


def _short_name_exists(
    session: Session, short_name: str, exclude_id: int | None = None
) -> bool:
    q = select(Link).where(Link.short_name == short_name)
    if exclude_id is not None:
        q = q.where(Link.id != exclude_id)
    return session.exec(q).first() is not None


def _insert_link(session: Session, original_url: str, short_name: str) -> Link:
    link = Link(original_url=original_url, short_name=short_name)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def _update_link_row(
    session: Session, link_id: int, original_url: str, short_name: str
) -> Link | None:
    link = session.get(Link, link_id)
    if not link:
        return None
    link.original_url = original_url
    link.short_name = short_name
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def get_links_with_total(
    range_param: tuple[int, int] | None,
) -> tuple[list[Link], int, str]:
    with Session(engine) as session:
        return _get_links_with_total(session, range_param)


def get_link_by_id(link_id: int) -> Link | None:
    with Session(engine) as session:
        return session.get(Link, link_id)


def get_link_by_short_name(short_name: str) -> Link | None:
    with Session(engine) as session:
        return session.exec(
            select(Link).where(Link.short_name == short_name)
        ).first()


def try_create_link(
    original_url: str, short_name: str
) -> Link | Literal["duplicate"]:
    with Session(engine) as session:
        if _short_name_exists(session, short_name):
            return "duplicate"
        return _insert_link(session, original_url, short_name)


def try_update_link(
    link_id: int, original_url: str, short_name: str
) -> Link | Literal["not_found", "duplicate"]:
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            return "not_found"
        if _short_name_exists(session, short_name, exclude_id=link_id):
            return "duplicate"
        updated = _update_link_row(session, link_id, original_url, short_name)
        return updated if updated is not None else "not_found"


def try_delete_link(link_id: int) -> bool:
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            return False
        session.delete(link)
        session.commit()
        return True
