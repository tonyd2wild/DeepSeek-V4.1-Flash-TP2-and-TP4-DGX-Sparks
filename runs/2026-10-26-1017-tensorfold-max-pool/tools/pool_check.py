#!/usr/bin/env python3
"""pool_check.py BASE LEN N [--again] : N needle prompts of exactly LEN tokens, sent together (the engine reads them one at a
time), with a metrics and memory sample every 10 s. --again sends the same prompts one by one afterwards: replies that come back
in seconds with nearly all of LEN cached were answered from kept states, so all N states (N*LEN positions) were in the pool together.
2026-10-26: 3 x 710,000 = 2,130,000 positions, more than the shipped 2,097,152 pool holds."""
import json, os, random, sys, time, threading, urllib.request
args = sys.argv[1:]
# the prompt builder of runs/2026-10-17-1017-tensorfold/tools/long_check.py (LONG_CHECK overrides the path)
LC = os.environ.get("LONG_CHECK") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../2026-10-17-1017-tensorfold/tools/long_check.py")
src = open(LC).read().replace("\nmain()", "\n")
lc = {"__name__": "lc"}
exec(compile(src, "long_check", "exec"), lc)
tok, post, WORDS = lc["tok"], lc["post"], lc["WORDS"]
BOS, USER, ASST, THINK_END = lc["BOS"], lc["USER"], lc["ASST"], lc["THINK_END"]
base, n, k = args[0], int(args[1]), int(args[2])
again = "--again" in args  # re-send the same prompts one by one: a kept state answers without a new prompt pass

def filler(rnd, count):
    return " ".join(f"{rnd.choice(WORDS)}{rnd.randint(0, 999)}" for _ in range(count))

def build(seed):
    rnd = random.Random(seed)
    code = "".join(rnd.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(8))
    head = tok(base, BOS + USER)
    tail = tok(base, "\n\nWhat is the secret code mentioned in the text above? Reply with the code only." + ASST + THINK_END)
    room = n - len(head) - len(tail)
    words = filler(rnd, int(room * 0.55))
    cut = words.rfind(" ", 0, int(len(words) * rnd.uniform(0.2, 0.8)))
    ids = tok(base, words[:cut] + f" The secret code is {code}. " + words[cut:])
    while len(ids) < room:
        ids += tok(base, " " + filler(rnd, room - len(ids)))
    return code, head + ids[:room] + tail

jobs = [build(1000 + i) for i in range(k)]
if again:
    for i, (code, ids) in enumerate(jobs):
        t0 = time.time()
        r = post(base, "/v1/completions", {"model": "deepseek-v4.1-flash", "prompt": ids, "max_tokens": 16, "temperature": 0}, timeout=7200)
        u = r.get("usage", {})
        print(json.dumps({"again": i, "prompt_tokens": u.get("prompt_tokens"), "cached": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                          "seconds": round(time.time() - t0, 1), "needle_ok": code in r["choices"][0]["text"]}), flush=True)
    sys.exit(0)
print(json.dumps({"built": k, "len": n, "total_positions": n * k}), flush=True)
done = []

def one(i, code, ids):
    t0 = time.time()
    try:
        r = post(base, "/v1/completions", {"model": "deepseek-v4.1-flash", "prompt": ids, "max_tokens": 16, "temperature": 0}, timeout=7200)
        out = r["choices"][0]["text"]
        print(json.dumps({"req": i, "prompt_tokens": r["usage"]["prompt_tokens"], "seconds": round(time.time() - t0, 1),
                          "needle_ok": code in out, "reply": out[:30]}), flush=True)
    except Exception as e:
        b = getattr(e, "read", lambda: b"")()
        print(json.dumps({"req": i, "error": str(e), "body": b[:300].decode("utf-8", "ignore") if b else ""}), flush=True)
    done.append(i)

ts = [threading.Thread(target=one, args=(i, c, ids)) for i, (c, ids) in enumerate(jobs)]
t0 = time.time()
for t in ts:
    t.start()
while len(done) < k:
    time.sleep(10)
    try:
        m = urllib.request.urlopen(base + "/metrics", timeout=5).read().decode()
        g = {l.split()[0]: l.split()[-1] for l in m.splitlines() if l.startswith("tensorfold:requests_")}
    except Exception:
        g = {}
    av = [int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemAvailable")][0] / 1048576
    print(json.dumps({"t": round(time.time() - t0), "running": g.get("tensorfold:requests_running"),
                      "waiting": g.get("tensorfold:requests_waiting"), "avail_gib": round(av, 1)}), flush=True)
for t in ts:
    t.join()
print("ALL DONE", round(time.time() - t0), "s", flush=True)
