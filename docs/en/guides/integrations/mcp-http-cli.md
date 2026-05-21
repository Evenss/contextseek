# MCP, HTTP & CLI

SeekContext exposes the same operations through three surfaces:

| Surface | When to use |
|---------|-------------|
| **Python SDK** | In-process agents and services |
| **CLI** | Scripts, cron, local debugging |
| **HTTP API** | Language-agnostic services, gateways |
| **MCP** | IDE agents (Cursor, Claude Desktop) and tool-calling hosts |

All paths call the same `SeekContext` client logic (storage, retrieval, evolution).

---

## CLI (`seekcontext`)

Installed with the package:

```bash
pip install seekcontext
seekcontext --help
```

Assumes `.env` in cwd or repo root (see [Configuration](../../getting-started/configuration.md)).

### Commands

| Command | Description |
|---------|-------------|
| `add` | Write one item |
| `retrieve` | Ranked search (`--k`, optional `--full`) |
| `expand` | Load L2 by comma-separated `--ids` |
| `compact` | Run evolution (`--dry-run`) |
| `forget` | Soft-delete (`--item-id`, `--reason`) |
| `delete` | Hard delete (`--no-propagate` optional) |
| `overview` | Stage counts + evolution hints |
| `dream` | Dream cycle (`--dry-run`) |
| `feedback` | Score delta (`--score`, `--reason`) |
| `upstream` | Upstream link walk |
| `evidence-chain` | Full evidence DAG (`--max-depth`) |
| `chain-confidence` | Aggregate confidence |
| `tools` | Print built-in LLM tool specs (`--format openai\|anthropic`) |
| `skill-tools` | Export skill-stage tools as definitions |
| `skill-context` | Render skill prompt block |
| `skill-import` | Import Hermes/OpenAI/MCP skill files |
| `items` | List scope items (`--stage` filter) |
| `metrics` | Prometheus text (if audit/metrics enabled) |

### Examples

```bash
# Write
seekcontext add \
  --scope acme/proj/user \
  --content "Prefer concise answers in Chinese" \
  --source cli \
  --tags preference,language

# Search (L1 summaries)
seekcontext retrieve \
  --scope acme/proj/user \
  --query "language preference" \
  --k 5

# Full L2 in one shot
seekcontext retrieve \
  --scope acme/proj/user \
  --query "language preference" \
  --k 3 \
  --full

# Expand selected ids
seekcontext expand --scope acme/proj/user --ids id1,id2

# Maintenance
seekcontext overview --scope acme/proj/user
seekcontext compact --scope acme/proj/user
seekcontext dream --scope acme/proj/user --dry-run

seekcontext forget --scope acme/proj/user --item-id abc123 --reason cleanup
seekcontext delete --scope acme/proj/user --item-id abc123 --reason gdpr

# Provenance
seekcontext upstream --scope acme/proj/user --item-id abc123
seekcontext evidence-chain --scope acme/proj/user --item-id abc123 --max-depth 8
```

CLI output is **JSON** on stdout for machine parsing.

### Programmatic CLI

```python
from seekcontext.cli.main import run_cli

exit_code = run_cli(["retrieve", "--scope", "t/p/u", "--query", "test", "--k", "5"])
```

Pass `client=my_seek_context` to inject a test double.

---

## HTTP API (FastAPI)

Install:

```bash
pip install "seekcontext[http]"
```

Run:

```bash
uvicorn seekcontext.http.server:app --host 0.0.0.0 --port 8000
# Or: make demo-http  (127.0.0.1:8000 with reload)
```

OpenAPI docs: `http://localhost:8000/docs`

### Routes

| Method | Path | Body highlights |
|--------|------|-----------------|
| `POST` | `/add` | `scope`, `content`, `source`, `tags[]` |
| `POST` | `/retrieve` | `scope`, `query`, `k`, `full`, `filters`, `include_deleted` |
| `POST` | `/expand` | `scope`, `ids[]` |
| `POST` | `/forget` | `scope`, `item_id`, `reason` |
| `POST` | `/delete` | `scope`, `item_id`, `reason`, `propagate` |
| `POST` | `/compact` | `scope`, `dry_run` |
| `POST` | `/dream` | `scope`, `dry_run` |
| `POST` | `/feedback` | `scope`, `item_id`, `score`, `reason` |
| `POST` | `/upstream` | `scope`, `item_id` |
| `POST` | `/evidence_chain` | `scope`, `item_id`, `max_depth` |
| `POST` | `/chain_confidence` | `scope`, `item_id` |
| `POST` | `/skill_tools` | `scope`, `fmt`, `query`, `k` |
| `POST` | `/skill_context` | `scope`, `query`, `k` |
| `POST` | `/items` | `scope`, optional `stage` |
| `GET` | `/overview?scope=...` | Query param `scope` |
| `GET` | `/metrics` | Prometheus text |
| `GET` | `/health` | `{"status":"ok","version":"<package>"}` (also in OpenAPI `info.version`) |

### curl examples

```bash
curl -s -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"scope":"t/p/u","content":"hello","source":"curl","tags":["demo"]}'

curl -s -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{"scope":"t/p/u","query":"hello","k":5,"full":false}'

curl -s -X POST http://localhost:8000/expand \
  -H "Content-Type: application/json" \
  -d '{"scope":"t/p/u","ids":["<item-id>"]}'

curl -s "http://localhost:8000/overview?scope=t/p/u"
curl -s http://localhost:8000/health
```

### Retrieve response shape

```json
{
  "items": [
    {
      "id": "...",
      "score": 0.82,
      "layer": "summary",
      "summary": "L1 text ...",
      "content": null,
      "provenance_summary": "source: document; id=wiki/1",
      "stage_confidence": 0.85,
      "recall_path": "phrase,term"
    }
  ],
  "_meta": {
    "layer": "summary",
    "full_via": "expand",
    "hint": "These items contain summaries only..."
  }
}
```

### Custom app embedding

```python
from seekcontext import SeekContext
from seekcontext.http.server import create_app

ctx = SeekContext.from_settings()
app = create_app(client=ctx)
```

---

## MCP server

Model Context Protocol exposes SeekContext tools to hosts that speak JSON-RPC (Cursor, custom agents).

Install: `pip install seekcontext` (HTTP extra optional for SSE transport).

### stdio (local IDE)

```bash
seekcontext-mcp-stdio
```

Configure in MCP client JSON (example):

```json
{
  "mcpServers": {
    "seekcontext": {
      "command": "seekcontext-mcp-stdio",
      "env": {
        "STORAGE_BACKEND": "file",
        "STORAGE_PATH": "/path/to/.seekcontext/data"
      }
    }
  }
}
```

Environment variables are read the same way as the SDK (`.env` + MCP `env` block).

### SSE (remote)

```bash
seekcontext-mcp-sse --host 0.0.0.0 --port 8001
```

Requires `seekcontext[http]` (FastAPI). Clients connect to the SSE endpoint exposed by `MCPRuntime`.

### MCP tools

| Tool | SDK equivalent |
|------|----------------|
| `seekcontext_add` | `add()` |
| `seekcontext_retrieve` | `retrieve()` (`k`, `full`) |
| `seekcontext_expand` | `expand_by_ids()` |
| `seekcontext_forget` | `forget()` |
| `seekcontext_delete` | `delete()` |
| `seekcontext_compact` | `compact()` |
| `seekcontext_dream` | `dream()` |
| `seekcontext_overview` | `overview()` |
| `seekcontext_feedback` | `feedback()` |
| `seekcontext_upstream` | `upstream()` |
| `seekcontext_evidence_chain` | `evidence_chain()` |
| `seekcontext_chain_confidence` | `chain_confidence()` |
| `seekcontext_skill_tools` | `skill_tools()` |
| `seekcontext_skill_context` | `skill_context()` |
| `seekcontext_items` | `items()` |

### Agent workflow with MCP

1. `seekcontext_retrieve` with user question → summaries + ids in JSON.
2. Model decides which ids need detail → `seekcontext_expand`.
3. Optional: `seekcontext_feedback` on ids that helped.
4. Periodic: `seekcontext_compact` on long-running scopes.

### Python embedding

```python
from seekcontext import SeekContext
from seekcontext.mcp.server import SeekContextMCPServer
from seekcontext.mcp.runtime import MCPRuntime

server = SeekContextMCPServer(client=SeekContext.from_settings())
runtime = MCPRuntime(server=server)
response = runtime.handle_request({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {"name": "seekcontext_retrieve", "arguments": {"scope": "t/p/u", "query": "test"}},
})
```

---

## Choosing a surface

| Requirement | Pick |
|-------------|------|
| Lowest latency, full Python | SDK |
| Ops / CI automation | CLI |
| Polyglot microservice | HTTP |
| Cursor / MCP-native agent | MCP stdio |
| Remote MCP consumer | MCP SSE |

Behavior differences are limited to serialization—always use the same **`scope`** convention across surfaces.

---

## Security notes

- HTTP and SSE should sit behind auth (API gateway, mTLS) in production.
- MCP inherits process env—do not pass production keys to untrusted hosts.
- CLI and MCP respect `SECURITY_*` ACL settings when enabled.

## Related

- [Write & retrieve](../write-and-retrieve.md)
- [Configuration](../../getting-started/configuration.md)
- [Observability](../observability.md) — audit + metrics endpoints
