"""Tests for kanban board logic."""

import pytest

from app.models.schemas import StatusTag
from app.services.workflowy_client import WorkflowyClient


class TestKanbanColumnAssignment:
    """Tests for assigning nodes to kanban columns."""

    def test_node_with_todo_tag_goes_to_todo_column(self):
        """Test node with #TODO tag is assigned to TODO column."""
        status = WorkflowyClient.extract_status_tag("Task #TODO")
        assert status == StatusTag.TODO

    def test_node_with_wip_tag_goes_to_wip_column(self):
        """Test node with #WIP tag is assigned to WIP column."""
        status = WorkflowyClient.extract_status_tag("Working on task #WIP")
        assert status == StatusTag.WIP

    def test_node_with_blocked_tag_goes_to_blocked_column(self):
        """Test node with #BLOCKED tag is assigned to BLOCKED column."""
        status = WorkflowyClient.extract_status_tag("Blocked task #BLOCKED")
        assert status == StatusTag.BLOCKED

    def test_node_with_test_tag_goes_to_test_column(self):
        """Test node with #TEST tag is assigned to TEST column."""
        status = WorkflowyClient.extract_status_tag("Ready for QA #TEST")
        assert status == StatusTag.TEST

    def test_node_with_done_tag_goes_to_done_column(self):
        """Test node with #DONE tag is assigned to DONE column."""
        status = WorkflowyClient.extract_status_tag("Completed #DONE")
        assert status == StatusTag.DONE

    def test_node_with_backlog_tag_goes_to_backlog_column(self):
        """Test node with #BACKLOG tag is assigned to BACKLOG column."""
        status = WorkflowyClient.extract_status_tag("Future work #BACKLOG")
        assert status == StatusTag.BACKLOG

    def test_node_without_tag_defaults_to_backlog(self):
        """Test node without tag defaults to BACKLOG column."""
        status = WorkflowyClient.extract_status_tag("Task without tag")
        # None means default to BACKLOG
        assert status is None


class TestKanbanStatusTransitions:
    """Tests for status transitions between kanban columns."""

    def test_backlog_to_todo(self):
        """Test moving from BACKLOG to TODO."""
        name = "Task #BACKLOG"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.TODO)
        assert new_name == "Task #TODO"
        assert "#BACKLOG" not in new_name

    def test_todo_to_wip(self):
        """Test moving from TODO to WIP."""
        name = "Task #TODO"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.WIP)
        assert new_name == "Task #WIP"
        assert "#TODO" not in new_name

    def test_wip_to_blocked(self):
        """Test moving from WIP to BLOCKED."""
        name = "Task #WIP"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.BLOCKED)
        assert new_name == "Task #BLOCKED"
        assert "#WIP" not in new_name

    def test_blocked_to_wip(self):
        """Test unblocking a task (BLOCKED -> WIP)."""
        name = "Blocked task #BLOCKED"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.WIP)
        assert new_name == "Blocked task #WIP"
        assert "#BLOCKED" not in new_name

    def test_wip_to_test(self):
        """Test moving from WIP to TEST."""
        name = "Feature #WIP"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.TEST)
        assert new_name == "Feature #TEST"
        assert "#WIP" not in new_name

    def test_test_to_done(self):
        """Test moving from TEST to DONE."""
        name = "Feature #TEST"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.DONE)
        assert new_name == "Feature #DONE"
        assert "#TEST" not in new_name

    def test_done_to_backlog(self):
        """Test reopening a task (DONE -> BACKLOG)."""
        name = "Completed task #DONE"
        new_name = WorkflowyClient.update_status_tag(name, StatusTag.BACKLOG)
        assert new_name == "Completed task #BACKLOG"
        assert "#DONE" not in new_name


class TestFilterParsing:
    """Tests for filter text parsing."""

    def test_single_filter(self):
        """Test parsing single filter."""
        filter_text = "project"
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        assert filters == ["project"]

    def test_multiple_filters(self):
        """Test parsing multiple comma-separated filters."""
        filter_text = "project, urgent, bug"
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        assert filters == ["project", "urgent", "bug"]

    def test_filters_with_extra_spaces(self):
        """Test parsing filters with extra whitespace."""
        filter_text = "  project  ,  urgent  "
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        assert filters == ["project", "urgent"]

    def test_empty_filter(self):
        """Test parsing empty filter."""
        filter_text = ""
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        assert filters == []

    def test_filters_with_empty_segments(self):
        """Test parsing filters with empty comma segments."""
        filter_text = "project,,urgent,"
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        assert filters == ["project", "urgent"]
