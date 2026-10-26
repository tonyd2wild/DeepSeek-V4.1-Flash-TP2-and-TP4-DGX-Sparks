# TensorFold TP4: how large the KV pool can go (2026-10-26)

The TP4 lane shipped with a shared KV pool of **2,097,152 positions** (`TF_DS_WINDOW` on rank 0, `--pool` on ranks 1-3). That
number was a setting, not a limit: it is what we ran next to a ComfyUI studio on every Spark. With the four Sparks running
nothing but DeepSeek, the same lane, engine and weights serve a pool of **16,777,216 positions**, 8x the shipped one.

16,777,216 is 16 streams x 1,048,576 context: every one of the 16 streams can hold a full 1M-token conversation at the same
time. bertholomus's recipe reached the same place on his own build (his v0.3.x serves 20,971,520 and names 16,777,216 for nodes
that need more room); this run measures it on our lane (LibertAI EXL3 3.5 bpw, engine `5940208` + our patches 0001-0004).

## The change

Three values in the fleet config, nothing else ([`launch/config.fleet-8000-rail2-p4-pool16m.env`](launch/config.fleet-8000-rail2-p4-pool16m.env),
a copy of [`config.fleet-8000-rail2-p4.env`](../2026-10-17-1017-tensorfold/launch/config.fleet-8000-rail2-p4.env)):

```sh
WINDOW=16777216
ENGINE_ENV="... TF_DS_WINDOW=16777216"
FOLLOW_FLAGS="--round-rows 48 --streams 16 --pool 16777216 --context 1048576"
```

[`launch/start_pool.sh POOL`](launch/start_pool.sh) writes that copy for any pool size and starts it the way
`start_fleet_rail2_p4.sh` does. A restart takes about 2 minutes (107 s to load the four ranks).

## What the pool costs

The pool is allocated when the ranks load and does not grow afterwards. It costs about **0.87 GiB per 1,048,576 positions on
every node**: rank 0 reports it inside its model figure, ranks 1-3 as `arena_used`.

| pool (positions) | rank 0 "model" (GiB) | ranks 1-3 `arena_used` (GB) | MemAvailable after load, rank 0 / ranks 1-3 (GiB) |
|---|---|---|---|
| 2,097,152 (shipped) | 71.87 | not logged | 37.4 / 39.2-40.2 |
| 4,194,304 | 73.69 | 8.23 | 37.7 / 39.5-39.9 |
| 8,388,608 | 77.12 | 11.97 | 34.3 / 35.8-36.4 |
| **16,777,216** | **84.06** | **19.43** | **27.0 / 28.8-29.3** |

The ComfyUI studios were stopped for these runs, so the only other tenant was the OS. MemAvailable on GB10 moves with the page
cache; the 2M row was read right after the studios stopped and sits within a GiB of the 4M row. The engine's own figures (the
two middle columns) are exact.

## Checks on the 16,777,216 pool

| check | result |
|---|---|
| Load | all four ranks in 104-109 s, every rank reports `"pool": 16777216` |
| Chat and single-user decode | normal; 400-token replies at 132.8 tok/s (code), 115.4 (explainer), 76.0 (story), the same as on the 2M pool |
| Three 710,000-token needle prompts sent together ([`tools/pool_check.py`](tools/pool_check.py)) | all three served: 383.6 s, 764.9 s and 1,146.7 s from the send (the engine reads one prompt at a time, see below); needles: 2 of 3 found |
| The three sent again | **all three resumed from kept states: 708,608 of 710,000 tokens cached each, 1.7-1.8 s per reply, 0 evicted** |
| Memory during the run | rank 0 MemAvailable 26.9-27.1 GiB throughout; ranks 1-3 28.6-28.7 GiB after |

The second send is the pool check: the three conversations' kept states (2.13M positions together) were all still in the pool
and resumed in place. The shipped 2,097,152 pool cannot hold all three at once.

One needle in three was missed at 710K: the model answered a filler word, the same on the second send (temperature 0). Our
earlier needle runs on this lane passed at every length up to 500,000 tokens; 710K is past what we had shown, and the miss is
the model's long-context recall on this pack, not the pool.

## What the pool does and does not change

- **More long conversations at once.** Each stream takes an extent of the pool as large as its prompt plus its reply budget.
  At 2M, two 1M chats filled it; at 16.8M all 16 streams can be at 1M.
- **More kept prompt states.** Finished conversations keep their state in the pool, so the next turn resumes instead of
  reading the whole prompt again. A larger pool keeps more of them warm before any is evicted.
- **Not prompt reading.** On engine `5940208` a prompt pass runs whole when its request is admitted, and no decode round runs
  meanwhile: during each 710K read (about 6.4 minutes) the other streams waited. Short prompts take seconds, so day to day it
  does not show. bertholomus's later builds read prompts in pieces while other requests wait (`TF_FILL_CHUNKS=1`,
  `TF_FILL_MANY=1`); that is an engine change, not a pool setting.

## Past 16,777,216

Memory would allow more: at about 0.87 GiB per 1M positions, leaving 8 GiB free per node puts the ceiling near 38M positions.
With 16 streams at 1M context the extra positions could only hold more kept states; serving more conversations at once would
take more streams (`TF_DS_STREAMS`, `--parallel`), which changes the round costs this lane was measured with. Not tested.

## With the studios

The 2,097,152 pool is what the [1 LLM + 4 Studios](https://github.com/tonyd2wild/DeepSeek-V4.1-Flash-x-MiniMax-H3-x-Qwen-Image-2.1-Studios-4x-DGX-Spark)
setup runs: an H3 video render needs about 31 GiB of headroom on its Spark. At 16,777,216 each node has 27-29 GiB left, which is
room for Qwen-Image-2.1 jobs (about 18 GiB at their peak) but not for H3 video.

## Files

- `launch/config.fleet-8000-rail2-p4-pool16m.env`, `launch/start_pool.sh`
- `tools/pool_check.py`: N needle prompts of exactly LEN tokens sent together, a metrics and memory sample every 10 s; `--again`
  sends the same prompts one by one to check the kept states. Builds its prompts with
  [`long_check.py`](../2026-10-17-1017-tensorfold/tools/long_check.py).
- `results/`: the run logs (`pool_check_16M_3x710k.log`, `pool_check_16M_again.log`, `prompt_cache_710k.log`).
