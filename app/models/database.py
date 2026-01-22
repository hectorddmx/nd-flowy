from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class WipConfig(Base):
    """Store WIP node configuration."""

    __tablename__ = "wip_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wip_node_id: Mapped[str] = mapped_column(Text, nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class NodeCache(Base):
    """Cached Workflowy nodes."""

    __tablename__ = "node_cache"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    parent_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    layout_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    breadcrumb: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_tag: Mapped[str | None] = mapped_column(String(50), nullable=True)


class FilterHistory(Base):
    """Saved filter searches."""

    __tablename__ = "filter_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filter_text: Mapped[str] = mapped_column(Text, nullable=False)
    used_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
