import os

from sqlmodel import Session, create_engine

from models import Link

_db_url = os.environ.get("DATABASE_URL", "").strip()

engine = create_engine(
    _db_url or "sqlite:///./links.db",
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in (_db_url or "sqlite") else {},
)


def init_db() -> None:
    Link.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
