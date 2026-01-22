# WorkFlowy API Reference

## Overview

WorkFlowy provides a REST API for programmatic access to outlines and bullet points. The API uses bearer token authentication and returns JSON responses.

## Authentication

All requests require an Authorization header with a bearer token:
```
Authorization: Bearer <YOUR_API_KEY>
```

Obtain your API key from the [API key page](https://workflowy.com/api-key).

## Base URL

```
https://workflowy.com/api/v1
```

## Core Concepts

### Nodes
Nodes represent individual bullet points in WorkFlowy. Each node can contain text, notes, child nodes, and metadata like completion status and timestamps. A node is the fundamental unit of content in WorkFlowy - each node represents a single bullet point that can contain text, have child nodes, and be organized hierarchically.

### Targets
Targets provide shortcuts to specific nodes. These include system targets (inbox) and user-defined shortcuts (home).

---

## Nodes API

### Node Object Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | string | Unique node identifier (UUID) |
| `name` | string | Main bullet text (supports formatting) |
| `note` | string \| null | Additional note content |
| `priority` | number | Sort order among siblings (lower = first) |
| `data.layoutMode` | string | Display mode: "bullets", "todo", "h1", "h2", "h3" |
| `createdAt` | number | Unix timestamp of creation |
| `modifiedAt` | number | Unix timestamp of last modification |
| `completedAt` | number \| null | Completion timestamp or null |

### Endpoints Summary

| Method | Endpoint | Purpose | Rate Limit |
|--------|----------|---------|------------|
| GET | `/nodes-export` | Export all nodes | 1 req/min |
| GET | `/nodes?parent_id=X` | List children | - |
| GET | `/nodes/:id` | Get single node | - |
| POST | `/nodes` | Create node | - |
| POST | `/nodes/:id` | Update node | - |
| POST | `/nodes/:id/complete` | Mark complete | - |
| POST | `/nodes/:id/uncomplete` | Mark incomplete | - |
| POST | `/nodes/:id/move` | Move node | - |
| DELETE | `/nodes/:id` | Delete node | - |

---

### Export All Nodes

**GET** `/nodes-export`

Returns a flat list of all nodes with `parent_id` for hierarchy reconstruction. **Rate limited to 1 request per minute**.

**Response:**
```json
[
  {
    "id": "uuid-1",
    "parent_id": null,
    "name": "Root node",
    "note": null,
    "priority": 0,
    "data": { "layoutMode": "bullets" },
    "createdAt": 1700000000,
    "modifiedAt": 1700000000,
    "completedAt": null
  },
  {
    "id": "uuid-2",
    "parent_id": "uuid-1",
    "name": "Child node",
    ...
  }
]
```

---

### Create Node

**POST** `/nodes`

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `parent_id` | Yes | Node UUID, target key ("home", "inbox"), or "None" |
| `name` | Yes | Text content with formatting support |
| `note` | No | Additional note content |
| `layoutMode` | No | Display mode |
| `position` | No | "top" (default) or "bottom" |

**Example:**
```bash
curl -X POST https://workflowy.com/api/v1/nodes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"parent_id": "inbox", "name": "New task"}'
```

---

### Update Node

**POST** `/nodes/:id`

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | No | Updated text |
| `note` | No | Updated note |
| `layoutMode` | No | Updated display mode |

**Example:**
```bash
curl -X POST https://workflowy.com/api/v1/nodes/NODE_UUID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"name": "Updated task text"}'
```

---

### Retrieve Node

**GET** `/nodes/:id`

Returns single node object with all attributes.

**Example:**
```bash
curl https://workflowy.com/api/v1/nodes/NODE_UUID \
  -H "Authorization: Bearer YOUR_KEY"
```

---

### List Nodes

**GET** `/nodes?parent_id={id}`

Returns child nodes **unordered**; sort by `priority` field manually.

**Example:**
```bash
curl "https://workflowy.com/api/v1/nodes?parent_id=NODE_UUID" \
  -H "Authorization: Bearer YOUR_KEY"
```

---

### Delete Node

**DELETE** `/nodes/:id`

Permanently removes node. **This is irreversible.**

---

### Move Node

**POST** `/nodes/:id/move`

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `parent_id` | New parent location |
| `position` | "top" or "bottom" |

---

### Complete Node

**POST** `/nodes/:id/complete`

Marks node as completed with timestamp.

---

### Uncomplete Node

**POST** `/nodes/:id/uncomplete`

Removes completion status.

---

## Targets API

### Target Object Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `key` | string | Unique identifier (e.g., "home", "inbox") |
| `type` | string | "shortcut" (user-defined) or "system" (managed) |
| `name` | string \| null | Node name or null for uncreated system targets |

### List Targets

**GET** `/targets`

Returns all available shortcuts and system targets.

**Example:**
```bash
curl https://workflowy.com/api/v1/targets \
  -H "Authorization: Bearer YOUR_KEY"
```

---

## Formatting

### Markdown Syntax

| Syntax | layoutMode | Result |
|--------|------------|--------|
| `# text` | "h1" | Level 1 header |
| `## text` | "h2" | Level 2 header |
| `### text` | "h3" | Level 3 header |
| `- text` | "bullets" | Bullet point |
| `- [ ] text` | "todo" | Uncompleted task |
| `- [x] text` | "todo" | Completed task |
| `` ```code``` `` | "code-block" | Code block |
| `> text` | "quote-block" | Quote block |

### Inline Formatting

| Markdown | HTML | Result |
|----------|------|--------|
| `**text**` | `<b>text</b>` | **bold** |
| `*text*` | `<i>text</i>` | *italic* |
| `~~text~~` | `<s>text</s>` | ~~strikethrough~~ |
| `` `text` `` | `<code>text</code>` | inline code |
| `[text](url)` | `<a href="url">text</a>` | hyperlink |

### Dates

Use ISO 8601 format in square brackets:
- `[YYYY-MM-DD]` - Date only
- `[YYYY-MM-DD HH:MM]` - Date with 24-hour time

### Multiline Text

- Single `\n` joins into spaces
- `\n\n` (double newline) creates separate child nodes

---

## Response Format

### Success Response
```json
{ "status": "ok" }
```

### Error Handling

Standard HTTP status codes apply:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `429` - Rate Limited
- `500` - Server Error
