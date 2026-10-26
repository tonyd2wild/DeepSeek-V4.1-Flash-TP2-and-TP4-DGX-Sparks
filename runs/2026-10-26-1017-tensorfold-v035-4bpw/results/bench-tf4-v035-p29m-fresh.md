## tf4-v035-p29m-fresh (2026-10-26T23:36:39Z)

fresh restart, empty prompt cache, cold prefill, pool 29360128

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (8 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 96.39 | 109.61 | 0.177 |

### Per-stream tok/s by category

| category | C1 |
|---|---|
| coding | 140.09 |
| json | 113.88 |
| narrative | 71.65 |
| prose | 85.31 |
| math | 129.74 |
| reasoning | 109.35 |
| summary | 78.98 |
| format | 147.84 |
| ceiling_count | 170.69 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2950 | 1.711 | 1724.0 |
| 8000 | 11592 | 4.845 | 2392.7 |
| 32000 | 46810 | 18.197 | 2572.4 |
| 64000 | 93335 | 36.607 | 2549.6 |
