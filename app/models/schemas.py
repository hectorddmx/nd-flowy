from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StatusTag(str, Enum):
    """Status tags for kanban columns."""

    BACKLOG = "BACKLOG"
    BLOCKED = "BLOCKED"
    TODO = "TODO"
    WIP = "WIP"
    TEST = "TEST"
    DONE = "DONE"


class NodeResponse(BaseModel):
    """Response schema for a Workflowy node from API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    parent_id: str | None = None
    name: str | None = None
    note: str | None = None
    priority: int = 0
    layout_mode: str | None = Field(None, alias="layoutMode")
    completed_at: datetime | None = Field(None, alias="completedAt")
    created_at: datetime | None = Field(None, alias="createdAt")
    modified_at: datetime | None = Field(None, alias="modifiedAt")


class NodeCacheResponse(BaseModel):
    """Response schema for a cached node."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: str | None = None
    name: str | None = None
    note: str | None = None
    priority: int = 0
    layout_mode: str | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    cached_at: datetime
    breadcrumb: str | None = None
    status_tag: StatusTag | None = None
    color_priority: int = 99


class FilterHistoryCreate(BaseModel):
    """Schema for creating a filter history entry."""

    filter_text: str


class FilterHistoryResponse(BaseModel):
    """Response schema for filter history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filter_text: str
    used_at: datetime


class StatusUpdateRequest(BaseModel):
    """Request schema for updating a node's status tag."""

    status: StatusTag


class RefreshResponse(BaseModel):
    """Response schema for refresh operation."""

    nodes_cached: int
    wip_node_id: str | None = None
