## tf4-v035-p29m-quiet (2026-10-26T23:28:39Z)

v0.3.5 4.0bpw pool 29360128, quiet rerun 2026-10-26 evening, both rails

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (8 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 97.2 | 110.39 | 0.172 |
| C2 | 133.12 | 79.4 | 0.278 |
| C3 | 157.35 | 63.48 | 0.388 |
| C4 | 174.97 | 54.33 | 0.495 |
| C5 | 181.78 | 47.04 | 0.609 |
| C6 | 195.46 | 41.69 | 0.726 |
| C8 | 206.82 | 34.02 | 0.975 |
| C16 | 230.72 | 19.83 | 2.005 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 | C8 | C16 |
|---|---|---|---|---|---|---|---|---|
| coding | 143.73 | 100.39 | 79.07 | 66.88 | 58.09 | 52.05 | 40.93 | 22.24 |
| json | 115.08 | 80.53 | 65.87 | 55.31 | 46.68 | 41.31 | 33.67 | 19.86 |
| narrative | 72.24 | 53.04 | 44.37 | 37.92 | 33.8 | 31.34 | 25.89 | 16.87 |
| prose | 84.44 | 58.51 | 49.86 | 44.67 | 38.23 | 36.05 | 29.53 | 18.7 |
| math | 129.4 | 98.85 | 75.02 | 63.45 | 58.53 | 48.83 | 41.14 | 22.88 |
| reasoning | 110.26 | 81.03 | 69.47 | 56.7 | 47.25 | 41.7 | 35.32 | 20.58 |
| summary | 79.7 | 61.23 | 45.47 | 41.2 | 35.21 | 31.17 | 25.43 | 14.61 |
| format | 148.31 | 101.63 | 78.69 | 68.47 | 58.55 | 51.07 | 40.22 | 22.88 |
| ceiling_count | 169.07 | 135.48 | 103.02 | 87.91 | 79.52 | 68.85 | 56.16 | 29.93 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2950 | 0.526 | 5604.6 |
| 8000 | 11592 | 0.712 | 16274.0 |
| 32000 | 46810 | 0.903 | 51817.5 |
| 64000 | 93335 | 0.698 | 133781.6 |
