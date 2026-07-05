# urirun-inquiry

Investigation by **URI graph**, not log debugging. Turn a problem into a graph of
addressable questions — every claim a URI-proof, every repair a URI-plan, every lesson
back to memory. And the answer to *"why do you stop?"*: **every inquiry emits a next-step
ticket for koru**, so the loop always has a next action and the system runs continuously.

```
intent:// → fleet:// → routes:// → policy:// → provenance:// → event://
→ experience:// → hypothesis:// → evidence:// → rootcause://
→ repair:// → verify:// → reflection:// → skill:// / antipattern:// / task://
```

| module | role |
|---|---|
| `case_store` | an investigation with memory: `case://host/cases/<id>`, evidence graph, root cause |
| `probes` | the systemic checklist (13 questions as URI probes) + the **command-only-after-query** rule |
| `rootcause` | fold evidence → real cause (not "app missing"), recommended next URI, missing inputs |
| `report` | artifact (json/md) + a **next-step ticket** so koru never idles |

**Don't debug logs — investigate the URI graph.** Live on the lenovo email case: root cause =
*"wrong strategy, not a missing app"*, next flow = query→classify→policy→approval→move (safe),
only missing = `secret://mail/main`. Part of the ifURI solution · Apache-2.0
