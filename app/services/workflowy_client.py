import re
from datetime import datetime

import httpx

from app.models.schemas import StatusTag


class WorkflowyClient:
    """Client for the Workflowy API."""

    # Regex to extract status tags from node names
    STATUS_TAG_PATTERN = re.compile(r"#(BACKLOG|BLOCKED|TODO|WIP|TEST|DONE)\b", re.IGNORECASE)

    # Regex to extract Workflowy color classes from HTML spans
    COLOR_PATTERN = re.compile(r'class="[^"]*bc-(red|orange|yellow|green|blue|purple|pink|sky|teal|gray)[^"]*"')

    # Color priority for sorting (lower = higher priority, shown first)
    COLOR_PRIORITY = {
        "red": 1,
        "orange": 2,
        "yellow": 3,
        "pink": 4,
        "purple": 5,
        "blue": 6,
        "sky": 7,
        "teal": 8,
        "green": 9,
        "gray": 10,
        None: 99,  # No color = lowest priority
    }

    def __init__(self, api_key: str, base_url: str = "https://workflowy.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def export_all_nodes(self) -> list[dict]:
        """
        GET /nodes-export - returns all nodes (1 req/min limit).

        Returns a flat list of all nodes with parent_id for hierarchy reconstruction.
        """
        client = await self._get_client()
        response = await client.get("/nodes-export")
        response.raise_for_status()
        data = response.json()
        return data.get("nodes", [])

    async def get_node(self, node_id: str) -> dict:
        """GET /nodes/:id - get a single node."""
        client = await self._get_client()
        response = await client.get(f"/nodes/{node_id}")
        response.raise_for_status()
        data = response.json()
        return data.get("node", data)

    async def list_children(self, parent_id: str) -> list[dict]:
        """GET /nodes?parent_id=X - list children of a node."""
        client = await self._get_client()
        response = await client.get("/nodes", params={"parent_id": parent_id})
        response.raise_for_status()
        data = response.json()
        return data.get("nodes", [])

    async def complete_node(self, node_id: str) -> None:
        """POST /nodes/:id/complete - mark a node as complete."""
        client = await self._get_client()
        response = await client.post(f"/nodes/{node_id}/complete")
        response.raise_for_status()

    async def uncomplete_node(self, node_id: str) -> None:
        """POST /nodes/:id/uncomplete - mark a node as incomplete."""
        client = await self._get_client()
        response = await client.post(f"/nodes/{node_id}/uncomplete")
        response.raise_for_status()

    async def update_node(self, node_id: str, name: str | None = None, note: str | None = None) -> None:
        """POST /nodes/:id - update a node's name and/or note."""
        client = await self._get_client()
        data = {}
        if name is not None:
            data["name"] = name
        if note is not None:
            data["note"] = note
        response = await client.post(f"/nodes/{node_id}", json=data)
        response.raise_for_status()

    async def create_node(
        self,
        parent_id: str,
        name: str,
        note: str | None = None,
        position: str = "top",
    ) -> dict:
        """POST /nodes - create a new node."""
        client = await self._get_client()
        data = {
            "parent_id": parent_id,
            "name": name,
            "position": position,
        }
        if note is not None:
            data["note"] = note
        response = await client.post("/nodes", json=data)
        response.raise_for_status()
        return response.json()

    async def move_node(self, node_id: str, parent_id: str, position: str = "top") -> None:
        """POST /nodes/:id/move - move a node to a new parent."""
        client = await self._get_client()
        data = {
            "parent_id": parent_id,
            "position": position,
        }
        response = await client.post(f"/nodes/{node_id}/move", json=data)
        response.raise_for_status()

    async def delete_node(self, node_id: str) -> None:
        """DELETE /nodes/:id - delete a node permanently."""
        client = await self._get_client()
        response = await client.delete(f"/nodes/{node_id}")
        response.raise_for_status()

    async def get_targets(self) -> list[dict]:
        """GET /targets - list all shortcuts and system targets."""
        client = await self._get_client()
        response = await client.get("/targets")
        response.raise_for_status()
        data = response.json()
        return data.get("targets", [])

    @classmethod
    def extract_status_tag(cls, name: str | None) -> StatusTag | None:
        """Extract status tag from a node name."""
        if not name:
            return None
        match = cls.STATUS_TAG_PATTERN.search(name)
        if match:
            tag = match.group(1).upper()
            return StatusTag(tag)
        return None

    @classmethod
    def extract_color(cls, name: str | None) -> str | None:
        """Extract Workflowy color class from node name HTML."""
        if not name:
            return None
        match = cls.COLOR_PATTERN.search(name)
        if match:
            return match.group(1)
        return None

    @classmethod
    def get_color_priority(cls, name: str | None) -> int:
        """Get sorting priority based on color (lower = higher priority)."""
        color = cls.extract_color(name)
        return cls.COLOR_PRIORITY.get(color, 99)

    @classmethod
    def update_status_tag(cls, name: str | None, new_status: StatusTag) -> str:
        """Update or add a status tag in a node name."""
        if not name:
            return f"#{new_status.value}"

        # Remove existing status tag
        new_name = cls.STATUS_TAG_PATTERN.sub("", name).strip()

        # Add new status tag
        return f"{new_name} #{new_status.value}".strip()

    @classmethod
    def parse_timestamp(cls, timestamp: int | None) -> datetime | None:
        """Convert Unix timestamp to datetime."""
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp)

    @classmethod
    def find_wip_node(cls, nodes: list[dict]) -> dict | None:
        """Find the WIP root node in a list of nodes."""
        for node in nodes:
            name = node.get("name", "")
            if name and name.strip().upper() == "WIP":
                return node
        return None

    @classmethod
    def build_node_tree(cls, nodes: list[dict]) -> dict[str, list[dict]]:
        """
        Build a tree structure from flat node list.

        Returns a dict mapping parent_id -> list of child nodes.
        """
        tree: dict[str, list[dict]] = {}
        for node in nodes:
            parent_id = node.get("parent_id")
            if parent_id not in tree:
                tree[parent_id] = []
            tree[parent_id].append(node)

        # Sort children by priority
        for children in tree.values():
            children.sort(key=lambda n: n.get("priority", 0))

        return tree

    @classmethod
    def compute_breadcrumb(
        cls,
        node_id: str,
        nodes_by_id: dict[str, dict],
        max_depth: int = 10,
    ) -> str:
        """Compute the breadcrumb path for a node (excluding the node itself)."""
        path = []
        node = nodes_by_id.get(node_id)
        if not node:
            return ""

        # Start from parent, not the node itself
        current_id = node.get("parent_id")
        depth = 0

        while current_id and depth < max_depth:
            parent_node = nodes_by_id.get(current_id)
            if not parent_node:
                break
            name = parent_node.get("name", "").strip()
            if name:
                # Remove status tags from breadcrumb
                clean_name = cls.STATUS_TAG_PATTERN.sub("", name).strip()
                path.append(clean_name)
            current_id = parent_node.get("parent_id")
            depth += 1

        # Reverse to get root-to-leaf order
        path.reverse()
        return " > ".join(path)
