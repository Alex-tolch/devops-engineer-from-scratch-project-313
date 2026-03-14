from models import Link
from sqlalchemy import func
from sqlmodel import Session, select


def get_links_with_total(
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


def get_link_by_id(session: Session, link_id: int) -> Link | None:
    return session.get(Link, link_id)


def get_link_by_short_name(session: Session, short_name: str) -> Link | None:
    return session.exec(select(Link).where(Link.short_name == short_name)).first()


def short_name_exists(
    session: Session, short_name: str, exclude_id: int | None = None
) -> bool:
    q = select(Link).where(Link.short_name == short_name)
    if exclude_id is not None:
        q = q.where(Link.id != exclude_id)
    return session.exec(q).first() is not None


def create_link(session: Session, original_url: str, short_name: str) -> Link:
    link = Link(original_url=original_url, short_name=short_name)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def update_link(
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


def delete_link(session: Session, link_id: int) -> bool:
    link = session.get(Link, link_id)
    if not link:
        return False
    session.delete(link)
    session.commit()
    return True
