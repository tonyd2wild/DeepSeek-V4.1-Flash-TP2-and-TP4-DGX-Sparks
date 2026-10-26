#!/usr/bin/env python3
"""load16.py BASE N ROUNDS : N concurrent chat streams, ROUNDS replies each (400 tokens, temperature 0.7), report tok/s and errors"""
import json, sys, time, threading, urllib.request
base, n, rounds = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
P = ["Write a Python function that merges two sorted lists, with tests.", "Explain how a refrigerator works in plain English.",
     "Write a 300-word story about a sneaker collector in Atlanta.", "List 10 tips for filming YouTube reviews, one line each.",
     "Explain TCP vs UDP with examples.", "Write a JSON object describing a fictional product with 8 fields."]
res, errs = [], []
def w(i):
    for r in range(rounds):
        b = json.dumps({"model": "deepseek-v4.1-flash", "messages": [{"role": "user", "content": P[(i + r) % len(P)]}], "max_tokens": 400, "temperature": 0.7}).encode()
        t = time.time()
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(base + "/v1/chat/completions", data=b, headers={"Content-Type": "application/json"}), timeout=900))
            res.append((d["usage"]["completion_tokens"], time.time() - t))
        except Exception as e:
            errs.append(str(e)[:120])
t0 = time.time(); ts = [threading.Thread(target=w, args=(i,)) for i in range(n)]
[t.start() for t in ts]; [t.join() for t in ts]
dt = time.time() - t0; tok = sum(r[0] for r in res)
print(json.dumps({"streams": n, "replies": len(res), "errors": len(errs), "tokens": tok, "wall_s": round(dt, 1), "agg_tok_s": round(tok / dt, 1), "err_sample": errs[:2]}))
