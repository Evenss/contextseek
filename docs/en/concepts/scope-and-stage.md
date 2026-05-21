# Scope and Stage

Two of the most important attributes on a `ContextItem` are **scope** (where it belongs) and **stage** (how mature it is). Both affect storage, retrieval, and evolution behavior.

---

## Scope: your isolation boundary

Scopes are **path strings** with no enforced schema:

```
{tenant}/{project}/{subject}
```

| Scope | Meaning |
|-------|---------|
| `acme/checkout/user-42` | One shopper's agent memory |
| `acme/platform/on-call` | Shared runbooks for the platform team |
| `demo_tenant/default/alice` | Tutorial data |

`retrieve(scope=...)` searches that prefix and all sub-paths. There is no built-in "search all tenants" — call multiple scopes or funnel data into a shared scope via [DataPlugs](../guides/integrations/dataplugs.md).

### Best practices

- Use **stable IDs** in the last segment (`user-42`, `bot-7`), not display names that may change.
- Put **shared** knowledge in a team scope; do not replicate the same paragraph into thousands of user scopes.
- One logical agent session can use one scope per user; rotate scope only when you intentionally want a clean slate.

### Anti-patterns

| Don't | Why |
|-------|-----|
| `scope="session-" + uuid` per message | Nothing compounds; storage explodes |
| Secrets in `scope` | Scopes appear in logs and audit records |
| Mix unrelated products in one scope | Retrieval noise and policy risk |

---

## Stage: maturity pipeline

```
raw  →  extracted  →  knowledge  →  skill
```

| Stage | Typical inputs | Default confidence weight in hits |
|-------|----------------|-----------------------------------|
| `raw` | Chat turns, tool JSON, fresh traces | 0.3 |
| `extracted` | Miner output, single-step insights | 0.6 |
| `knowledge` | Merged facts, validated runbooks | 0.85 |
| `skill` | Executable playbooks | 1.0 |

**Automatic inference:** if you omit `stage` on `add()`, SeekContext infers it from `source_type` and content shape. With `EVOLUTION_LLM_STAGE_INFER_ENABLED=true`, an LLM classifier may override heuristics.

**Overriding at write time:**

```python
from seekcontext.domain.stages import Stage

# Force a document directly to knowledge
ctx.add("team runbook", scope="acme/sre", source="wiki", stage=Stage.knowledge)
```

**Evolution:** `compact()` promotes `extracted` clusters to `knowledge`. `dream()` generates speculative `extracted` items at idle time. See [Evolution](../guides/evolution.md) for details.

---

## Stability

Stability controls how long an item is retained before decay or archival:

| Value | Meaning | Typical stage |
|-------|---------|---------------|
| `ephemeral` | Expires with the session or task | `raw` (tool calls, temp state) |
| `transient` | Default for raw/extracted; normal decay | `raw`, `extracted` |
| `stable` | Long-lived knowledge | `knowledge` |
| `permanent` | Skills and critical policies; manual delete only | `skill` |

Default stability per stage is determined automatically by SeekContext. Override on `add()`:

```python
from seekcontext.domain.stages import Stability

ctx.add("permanent policy", scope="acme/legal", source="policy-doc",
        stability=Stability.permanent)
```

---

## Design goal: one object, three guarantees

Every record entering SeekContext is expected to be:

| Guarantee | Mechanism |
|-----------|-----------|
| **Retrievable** | Index on write; `retrieve()` with recall + rerank |
| **Traceable** | Mandatory `provenance`; `links`; audit APIs |
| **Evolvable** | `stage` pipeline; `compact()` / `dream()` |

Data without an identifiable source, data that will never be searched, or throwaway buffers should stay outside SeekContext (Redis session cache, raw log files, etc.).

---

## Next steps

- [Context model](context-model.md) — ContextItem fields, Provenance, Links
- [Retrieval model](retrieval-model.md) — L0/L1/L2 tiers and search pipeline
- [Evolution](../guides/evolution.md) — `compact()`, `dream()`, `feedback()`
