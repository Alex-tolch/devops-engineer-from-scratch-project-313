import os

# Set in-memory DB and BASE_URL for tests before any app import
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("BASE_URL", "https://short.io")

import pytest
from sqlmodel import Session, select

from database import engine, init_db
from models import Link


@pytest.fixture(autouse=True)
def reset_db():
    init_db()
    with Session(engine) as session:
        for link in session.exec(select(Link)).all():
            session.delete(link)
        session.commit()
    yield
