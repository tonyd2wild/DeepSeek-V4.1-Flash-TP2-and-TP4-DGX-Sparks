## tf4-v035-p29m (2026-10-26T22:01:38Z)

v0.3.5 4.0bpw pool 29360128 live fleet endpoint both rails

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (8 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 55.38 | 60.59 | 0.204 |
| C2 | 93.31 | 53.62 | 0.314 |
| C3 | 127.19 | 50.68 | 0.414 |
| C4 | 174.44 | 54.31 | 0.497 |
| C5 | 183.09 | 46.95 | 0.609 |
| C6 | 188.96 | 40.38 | 0.735 |
| C8 | 207.62 | 33.9 | 0.961 |
| C16 | 231.19 | 19.91 | 1.997 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 | C8 | C16 |
|---|---|---|---|---|---|---|---|---|
| coding | 87.78 | 68.38 | 51.93 | 65.81 | 60.33 | 51.97 | 40.3 | 22.77 |
| json | 62.69 | 55.53 | 32.41 | 55.92 | 45.72 | 41.82 | 33.96 | 20.0 |
| narrative | 37.21 | 36.22 | 26.72 | 37.48 | 33.7 | 32.16 | 25.71 | 16.95 |
| prose | 50.67 | 41.29 | 31.44 | 44.39 | 37.79 | 35.62 | 29.33 | 18.76 |
| math | 55.92 | 68.12 | 66.23 | 65.75 | 58.64 | 48.04 | 41.2 | 23.1 |
| reasoning | 52.27 | 60.77 | 72.27 | 55.26 | 47.47 | 33.11 | 35.53 | 20.51 |
| summary | 41.62 | 30.64 | 45.28 | 39.71 | 33.58 | 30.51 | 25.11 | 14.95 |
| format | 96.53 | 68.05 | 79.17 | 70.13 | 58.39 | 49.77 | 40.02 | 22.24 |
| ceiling_count | 107.84 | 52.38 | 104.21 | 88.38 | 77.69 | 68.14 | 56.4 | 29.3 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2950 | 1.321 | 2233.3 |
| 8000 | 11592 | 4.308 | 2690.8 |
| 32000 | 46810 | 18.119 | 2583.5 |
| 64000 | 93335 | 36.259 | 2574.2 |
