"""Tests for the Workflowy client."""

import pytest

from app.models.schemas import StatusTag
from app.services.workflowy_client import WorkflowyClient


class TestStatusTagExtraction:
    """Tests for status tag extraction from node names."""

    def test_extract_todo_tag(self):
        """Test extracting #TODO tag."""
        result = WorkflowyClient.extract_status_tag("Fix bug #TODO")
        assert result == StatusTag.TODO

    def test_extract_blocked_tag(self):
        """Test extracting #BLOCKED tag."""
        result = WorkflowyClient.extract_status_tag("Waiting for review #BLOCKED")
        assert result == StatusTag.BLOCKED

    def test_extract_wip_tag(self):
        """Test extracting #WIP tag."""
        result = WorkflowyClient.extract_status_tag("Working on feature #WIP")
        assert result == StatusTag.WIP

    def test_extract_done_tag(self):
        """Test extracting #DONE tag."""
        result = WorkflowyClient.extract_status_tag("Completed task #DONE")
        assert result == StatusTag.DONE

    def test_extract_backlog_tag(self):
        """Test extracting #BACKLOG tag."""
        result = WorkflowyClient.extract_status_tag("Future task #BACKLOG")
        assert result == StatusTag.BACKLOG

    def test_extract_test_tag(self):
        """Test extracting #TEST tag."""
        result = WorkflowyClient.extract_status_tag("Ready for testing #TEST")
        assert result == StatusTag.TEST

    def test_no_tag(self):
        """Test name without a status tag."""
        result = WorkflowyClient.extract_status_tag("Task without tag")
        assert result is None

    def test_empty_name(self):
        """Test empty name."""
        result = WorkflowyClient.extract_status_tag("")
        assert result is None

    def test_none_name(self):
        """Test None name."""
        result = WorkflowyClient.extract_status_tag(None)
        assert result is None

    def test_case_insensitive(self):
        """Test case insensitive extraction."""
        result = WorkflowyClient.extract_status_tag("Task #todo")
        assert result == StatusTag.TODO

        result = WorkflowyClient.extract_status_tag("Task #Todo")
        assert result == StatusTag.TODO


class TestStatusTagUpdate:
    """Tests for updating status tags in node names."""

    def test_add_tag_to_no_tag(self):
        """Test adding tag to name without existing tag."""
        result = WorkflowyClient.update_status_tag("Fix bug", StatusTag.TODO)
        assert result == "Fix bug #TODO"

    def test_replace_existing_tag(self):
        """Test replacing existing tag."""
        result = WorkflowyClient.update_status_tag("Fix bug #TODO", StatusTag.DONE)
        assert result == "Fix bug #DONE"

    def test_replace_blocked_with_wip(self):
        """Test replacing #BLOCKED with #WIP."""
        result = WorkflowyClient.update_status_tag("Task #BLOCKED", StatusTag.WIP)
        assert result == "Task #WIP"

    def test_empty_name(self):
        """Test empty name gets just the tag."""
        result = WorkflowyClient.update_status_tag("", StatusTag.TODO)
        assert result == "#TODO"

    def test_none_name(self):
        """Test None name gets just the tag."""
        result = WorkflowyClient.update_status_tag(None, StatusTag.TODO)
        assert result == "#TODO"


class TestWipNodeFinding:
    """Tests for finding the WIP root node."""

    def test_find_wip_node(self, sample_nodes):
        """Test finding WIP node in list."""
        result = WorkflowyClient.find_wip_node(sample_nodes)
        assert result is not None
        assert result["id"] == "wip-root-123"
        assert result["name"] == "WIP"

    def test_find_wip_case_insensitive(self):
        """Test finding WIP node with different cases."""
        nodes = [{"id": "1", "name": "wip"}]
        result = WorkflowyClient.find_wip_node(nodes)
        assert result is not None
        assert result["id"] == "1"

    def test_no_wip_node(self):
        """Test when no WIP node exists."""
        nodes = [{"id": "1", "name": "Other"}]
        result = WorkflowyClient.find_wip_node(nodes)
        assert result is None


class TestBreadcrumbComputation:
    """Tests for computing breadcrumb paths (excluding current node)."""

    def test_compute_breadcrumb(self, sample_nodes):
        """Test computing breadcrumb for a task (excludes task name)."""
        nodes_by_id = {n["id"]: n for n in sample_nodes}
        result = WorkflowyClient.compute_breadcrumb("task-789", nodes_by_id)
        assert result == "WIP > PERSONAL"

    def test_breadcrumb_removes_status_tags(self, sample_nodes):
        """Test that status tags are removed from breadcrumb."""
        nodes_by_id = {n["id"]: n for n in sample_nodes}
        result = WorkflowyClient.compute_breadcrumb("task-blocked-111", nodes_by_id)
        assert "#BLOCKED" not in result
        assert result == "WIP > PERSONAL"

    def test_breadcrumb_root_node(self, sample_nodes):
        """Test breadcrumb for root node is empty."""
        nodes_by_id = {n["id"]: n for n in sample_nodes}
        result = WorkflowyClient.compute_breadcrumb("wip-root-123", nodes_by_id)
        assert result == ""


class TestNodeTreeBuilding:
    """Tests for building node trees."""

    def test_build_tree(self, sample_nodes):
        """Test building node tree from flat list."""
        tree = WorkflowyClient.build_node_tree(sample_nodes)

        # Root level (parent_id = None)
        assert None in tree
        assert len(tree[None]) == 1
        assert tree[None][0]["name"] == "WIP"

        # WIP children
        assert "wip-root-123" in tree
        assert len(tree["wip-root-123"]) == 1
        assert tree["wip-root-123"][0]["name"] == "PERSONAL"

        # Project children
        assert "project-456" in tree
        assert len(tree["project-456"]) == 3

    def test_tree_sorted_by_priority(self, sample_nodes):
        """Test that tree children are sorted by priority."""
        tree = WorkflowyClient.build_node_tree(sample_nodes)
        children = tree["project-456"]

        # Should be sorted by priority
        priorities = [c["priority"] for c in children]
        assert priorities == sorted(priorities)


class TestTimestampParsing:
    """Tests for timestamp parsing."""

    def test_parse_timestamp(self):
        """Test parsing Unix timestamp."""
        result = WorkflowyClient.parse_timestamp(1700000000)
        assert result is not None
        assert result.year == 2023

    def test_parse_none_timestamp(self):
        """Test parsing None timestamp."""
        result = WorkflowyClient.parse_timestamp(None)
        assert result is None
