from datetime import datetime

from sqlmodel import Field, SQLModel


class Link(SQLModel, table=True):
    __tablename__ = "links"

    id: int | None = Field(default=None, primary_key=True)
    original_url: str = Field(max_length=2048)
    short_name: str = Field(max_length=64, unique=True, index=True)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
