# TensorFold TP4, recipe v0.3.5, EXL3 4.0 bpw (our fleet lane since 2026-10-26)

This lane is **bertholomus's recipe [deepseek-v4.1-tensorfold-tp4-4xgb10](https://github.com/bertholomus/deepseek-v4.1-tensorfold-tp4-4xgb10)
v0.3.5**, run as published, on our four DGX Sparks. The engine is his `deepseek-v41-zig-tp4` branch at `0a0b69a`, the weights are his
[DeepSeek-V4.1-Flash-1017-EXL3-4.0bpw](https://huggingface.co/bertholomus/DeepSeek-V4.1-Flash-1017-EXL3-4.0bpw) pack, and the kit, chat
template, run-time inputs, `scripts/serve.sh` and every served setting are his. Follow his `RUNNING.md` to build it; this folder holds only
what we changed and what we measured on our nodes.

What we changed:

1. **Two engine patches** ([`patches/`](patches/)): `0001` reads the RDMA rings' source GID index from `TF_RDMA_GID` (our RoCE v2 entry is
   index 3; the engine fixes it at 5), and `0002` adds the opt-in `TF_SEED_RANDOM` and `TF_TOP_K_MAX` server settings. Both are the same
   changes as the 3.5 bpw lane's `0003` and `0004`, re-exported on top of `0a0b69a` (`0002` needed one hand merge next to the new
   greedy-only check).
2. **Both halves of the RoCE link**: `RDMA_HCA="rocep1s0f0,roceP2p1s0f0"` with the rail-2 addresses that
   [`rail2_all.sh`](../2026-10-17-1017-tensorfold/launch/rail2_all.sh) adds (one cable per node; see the 3.5 bpw lane for the details).
3. **Our fleet server flags**: thinking off by default, the `glm-5.3-flash` alias, temperature 1.0 / top_p 1.0 / top_k 20.
4. **The KV pool at 29,360,128 positions** instead of the recipe's 20,971,520: the largest that keeps at least 7 GiB free on every node
   under load (below).

Launch: [`launch/config.fleet-8000-v035.env`](launch/config.fleet-8000-v035.env) (the recipe's `config.env.example` with our values),
[`launch/start_fleet_v035.sh POOL`](launch/start_fleet_v035.sh) (writes the run config with the pool and starts it), and
[`launch/build.sh`](launch/build.sh) (the engine build in the serving container). The four ranks load in 26-27 s.

One thing that cost us a start: every node needs its own `MODEL_DIR` (config, tokenizer, index and the vision shard), not only rank 0.
The followers fail with `error: FileNotFound` right after the indexer line otherwise.

## Results (2026-10-26, our four Sparks, both rails)

**Bench** (the same prompt set v1 and tool as every lane in this repo, temperature 0, thinking off, pool 29,360,128, no other traffic;
[`results/bench-tf4-v035-p29m-quiet.md`](results/bench-tf4-v035-p29m-quiet.md)):

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) | 3.5 bpw lane (both rails), aggregate |
|---|---|---|---|---|
| C1 | **97.2** | **110.4** | 0.17 | 93.6 |
| C2 | 133.1 | 79.4 | 0.28 | |
| C3 | 157.4 | 63.5 | 0.39 | |
| C4 | 175.0 | 54.3 | 0.50 | |
| C5 | 181.8 | 47.0 | 0.61 | |
| C6 | 195.5 | 41.7 | 0.73 | 213.8 |
| C8 | 206.8 | 34.0 | 0.98 | |
| C16 | 230.7 | 19.8 | 2.01 | |

One stream by category (tok/s): coding 143.7, format 148.3, math 129.4, json 115.1, reasoning 110.3, prose 84.4, summary 79.7,
narrative 72.2. Against the 3.5 bpw lane: level or ahead at one stream, about 9% behind at six.

**Cold prefill** (after a fresh restart with an empty prompt cache, [`results/bench-tf4-v035-p29m-fresh.md`](results/bench-tf4-v035-p29m-fresh.md);
the first run matched it within 3%. The quiet rerun's prefill rows are not cold: the 29.4M pool still held the first run's prompt states, so
the 93,335-token prompt came back in 0.7 s):

| prompt tokens | TTFT (s) | prefill tok/s | 3.5 bpw lane (both rails) |
|---|---|---|---|
| 2,950 | 1.71 | 1,724 | |
| 11,592 | 4.85 | 2,393 | 2,140 |
| 46,810 | 18.20 | 2,572 | |
| 93,335 | 36.61 | 2,550 | 2,215 (42.1 s) |

**A short reply during a long prompt.** While a 131,072-token prompt was being read, three short chats answered in 1.85, 2.46 and 1.99 s.
On the 3.5 bpw lane's engine (`5940208`) a prompt pass runs whole at admission and no decode round runs meanwhile, so the same short chat
waited out the whole read; the recipe's `TF_FILL_CHUNKS=1` / `TF_FILL_MANY=1` read prompts in pieces while other requests wait.

**Checks:**

| check | result |
|---|---|
| sanity (chat, alias, tool call, tool round trip, thinking on request, image) | 6 of 6 |
| 131,072-token needle | found; read at 2,398 tok/s with three short chats in between |
| 600,000-token needle, twice (at pools 26.2M and 29.4M), each with 16 streams x 3 replies running | found both times; 96 of 96 replies, 0 errors |

## The KV pool on our nodes

The pool is allocated when the ranks load. At 4.0 bpw it costs the same as at 3.5 bpw, about 0.87 GiB per 1M positions on every node.
Rank 0, the head node, also runs the API server and a 2 GiB prompt cache, so it always has the least room.

| pool (positions) | free after load, rank 0 / ranks 1-3 (GiB) | lowest free under load, rank 0 / ranks 1-3 | engine's "left after the 12.2 GiB reserve" |
|---|---|---|---|
| 20,971,520 (the recipe's) | 15.6 / 17.1 | | 3.8 GiB |
| 25,165,824 | 12.3 / 13.7-13.8 | | 0.3 GiB |
| 26,214,400 | 11.5 / 13.0-13.1 | 9.87 / 11.9-12.0 | 0.0 GiB |
| **29,360,128** | **8.9 / 10.4-10.6** | **7.08 / 8.4-8.6** | 0.0 GiB |

"Under load" is a 600,000-token needle prompt plus 16 streams x 3 replies, and for 29,360,128 also the full C1-C16 bench
([`results/memmin_under_load.txt`](results/memmin_under_load.txt), sampled every 0.5 s by [`tools/memmin.sh`](tools/memmin.sh)). We stop at
29,360,128 because the next step would take rank 0 under 6 GiB free under load. The engine reports 0.0 GiB left above about 25.5M
positions and served every test anyway; the recipe keeps a 9 GiB floor plus a 2 GiB margin and stops at 20,971,520, so treat our number
as the ceiling for nodes that run nothing else.

16 streams at a full 1,048,576 context use 16,777,216 positions; the rest of the pool keeps finished conversations' states, which a
follow-up turn resumes from instead of reading its prompt again.

## The uncensored overlay

The Keys `wo_b` overlay that our uncensored 3.5 bpw lane uses (layers 10-35, EXL3 6 bpw `mul1`) has the same tensor format as this
pack's `wo_b`, so its EXL3 sidecar patches into copies of these rank caches the same way
([`runs/2026-10-18-1017-tensorfold-uncensored/`](../2026-10-18-1017-tensorfold-uncensored/)). Not applied yet.

## Files

- `launch/`: `config.fleet-8000-v035.env`, `start_fleet_v035.sh`, `build.sh`
- `patches/`: `0001` (`TF_RDMA_GID`), `0002` (`TF_SEED_RANDOM`, `TF_TOP_K_MAX`), on top of `0a0b69a`
- `tools/`: `load16.py` (N concurrent chat streams), `memmin.sh` (lowest MemAvailable sampler); the long-prompt checks are
  [`long_check.py`](../2026-10-17-1017-tensorfold/tools/long_check.py) and the bench is
  [`v41bench_tf.py`](../2026-10-17-1017-tensorfold/tools/v41bench_tf.py)
- `results/`: the three bench reports (md and json: first run, quiet rerun, fresh-restart cold prefill), `long_prompts.jsonl`, `memmin_under_load.txt`
