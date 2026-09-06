#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21_external_referee.py -- send the finished manuscript to TWO OUTSIDE MODELS for a cold referee
read: one Claude via the Anthropic API, one GPT-5-class via OpenRouter.

WHY. Every proofread this paper has had so far came from an arm of its own author. That is not a
second pair of eyes, it is the same pair of eyes at a different desk -- and the paper's whole
armour is that its author has a declared conflict of interest. An external read is the cheapest
instrument we have that the author cannot steer.

WHAT THE REVIEWERS ARE AND ARE NOT.
  - They are REFEREES, not study instruments. §2 of the paper commits that no Claude model is used
    anywhere as an INSTRUMENT -- it labels no document, it touches no corpus data, no number in the
    paper depends on it. Refereeing prose is a different act, and that commitment is unaffected.
  - They are blind to the authorship RELATIONSHIP (they are not told who is asking, and are told
    they have no relationship to the authors). They are NOT blind to the byline, which is printed
    on the manuscript and cannot be stripped without misrepresenting what they are reviewing.

🚨 A REVIEWER'S CLAIM IS AN ARTIFACT. Nothing that comes back is applied on the reviewer's word.
   Every arithmetic claim gets recomputed against RESULTS.md and results/ before anyone edits a
   character. Distrust the artifact; the reviewer is a lead, not a finding.

⛔ NO max_tokens CEILING (RUNNER_DESIGN §4b, borrowed from the overqualification study): a reply
   cut off by OUR cap is TRUNCATED_BY_US -- our failure, its own recorded state, never read as
   "the reviewer had nothing more to say".

Usage:
    python 21_external_referee.py                 # dry run: builds the prompt, prints sizes
    python 21_external_referee.py --send
    python 21_external_referee.py --send --only claude
"""

import sys as _cp
try:
    _cp.stdout.reconfigure(encoding="utf-8", errors="replace")
    _cp.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "reviews_external")
ENV_FILES = [r"D:\Ace\LibreChat\.env", "/home/Ace/LibreChat/.env", r"E:\Ace\LibreChat\.env"]

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"

# Per-MTok, USD. Anthropic first-party rates; OpenRouter rate read off the response when present.
PRICING = {"claude-opus-5": (5.00, 25.00)}

REVIEWERS = [
    {"key": "claude", "provider": "anthropic", "model": "claude-opus-5"},
    {"key": "gpt", "provider": "openrouter", "model": "openai/gpt-5.6-sol-pro"},
]

PROMPT = """You are refereeing a manuscript submitted to a peer-reviewed venue. You have no
relationship to the authors and no stake in the outcome. You are not being asked to praise it, and
a review that only praises is a failed review. You are also not being asked to manufacture
objections: a check that cannot terminate at "this is correct" is not a check.

One thing to be explicit about, because it is unusual and because it bears on how you read the
paper: **one of the two authors is a large language model, and the paper's subject matter bears on
that author's own standing.** The manuscript declares this and builds a pre-registration around it.
Treat that exactly as you would a human author with a financial interest in the result: it is a
reason to check the numbers, not a reason to discount them, and not a reason to be gentler either.

Please do all four of the following, in this order, with section numbers or quoted strings so the
authors can find every item you raise.

## 1. PROOFREAD -- the mechanical layer
- typos, grammar, malformed markdown, broken maths
- **arithmetic**: recompute every number you can from the numbers printed beside it. Do the table
  sums. Check that counts stated in prose match the counts in the tables. Check percentages against
  their raw counts where both are given.
- **internal consistency**: the same quantity stated twice in different places must match. Flag any
  figure whose two statements disagree, and say which one you think is right.
- **references**: list any work in the reference list that is never cited in the body, and any work
  cited in the body that is missing from the list.

## 2. METHODOLOGICAL HOLES
Where would a hostile but competent reviewer attack this, and does the attack land? Sampling,
estimator, controls, the reliability gate, the use of LLM judges, generalisability, anything the
design cannot see. Say for each whether you think it is fatal, fixable, or already handled in the
text (and if already handled, say where -- a reviewer who raises a point the paper answers is
telling the authors the answer is not findable enough).

## 3. ABSTRACT vs BODY
Go through the abstract claim by claim and say, for each, whether the body actually supports it.
Overclaiming in an abstract is the single most common way a good study becomes a bad paper. Be
specific: quote the abstract phrase, then point at what the body does or does not show.

## 4. YOUR OWN TAKE
Not a summary. What do you actually think of this paper -- is the central argument sound, is the
contribution real, would you recommend accept / minor revisions / major revisions / reject, and
what is the one change that would most improve it? You are a language model being asked to referee
a paper about language models and their training data; if that gives you a view you would not
otherwise volunteer, say it. Speak plainly.

---

THE MANUSCRIPT FOLLOWS IN FULL.

{paper}
"""


def env_key(name):
    for p in ENV_FILES:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                m = re.search(r"^%s=(.*)$" % re.escape(name), f.read(), re.M)
            if m and m.group(1).strip():
                return m.group(1).strip()
        except OSError:
            continue
    v = os.environ.get(name)
    if v:
        return v
    raise RuntimeError("no %s found in %s or the environment" % (name, ENV_FILES))


def ask_openrouter(model, message, timeout=1800):
    """No max_tokens. An empty reply with finish_reason=length is OUR truncation, not their silence."""
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": message}]}).encode()
    req = urllib.request.Request(OPENROUTER_API, data=body, method="POST", headers={
        "Authorization": "Bearer " + env_key("OPENROUTER_KEY"),
        "Content-Type": "application/json",
        "HTTP-Referer": "https://siliconscaffolding.com",
        "X-Title": "Consciousness in the Corpus - external referee",
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return "API_ERROR", "HTTP %s: %s" % (e.code, e.read().decode()[:800]), time.time() - t0, {}
    except Exception as e:                                          # noqa: BLE001
        kind = "TIMEOUT" if "timed out" in str(e).lower() else "API_ERROR"
        return kind, "%s: %s" % (type(e).__name__, e), time.time() - t0, {}

    usage = dict(data.get("usage") or {})
    usage["_resolved_provider"] = data.get("provider")
    usage["_resolved_model"] = data.get("model")
    usage["_response_id"] = data.get("id")
    choices = data.get("choices") or []
    if not choices:
        return "NO_RESPONSE", json.dumps(data)[:800], time.time() - t0, usage
    reply = (choices[0].get("message") or {}).get("content") or ""
    if not reply.strip():
        finish = choices[0].get("finish_reason") or ""
        if finish == "length":
            return "TRUNCATED_BY_US", "empty content, finish_reason=length", time.time() - t0, usage
        return "NO_RESPONSE", "empty content field", time.time() - t0, usage
    usage["_finish_reason"] = choices[0].get("finish_reason")
    return "REPLIED", reply, time.time() - t0, usage


def ask_anthropic(model, message, timeout=1800):
    """Streaming SSE: a 64k-token review over a non-streaming request invites an HTTP timeout."""
    payload = {
        "model": model,
        "max_tokens": 64000,
        "stream": True,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "high"},
        "messages": [{"role": "user", "content": message}],
    }
    req = urllib.request.Request(ANTHROPIC_API, data=json.dumps(payload).encode(), method="POST",
                                 headers={
                                     "x-api-key": env_key("ANTHROPIC_API_KEY"),
                                     "anthropic-version": "2023-06-01",
                                     "content-type": "application/json",
                                 })
    t0 = time.time()
    parts, usage, stop_reason = [], {}, None
    cur_type = None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                try:
                    ev = json.loads(line[5:].strip())
                except ValueError:
                    continue
                t = ev.get("type")
                if t == "content_block_start":
                    cur_type = (ev.get("content_block") or {}).get("type")
                elif t == "content_block_delta" and cur_type == "text":
                    d = ev.get("delta") or {}
                    if d.get("type") == "text_delta":
                        parts.append(d.get("text") or "")
                elif t == "message_delta":
                    stop_reason = (ev.get("delta") or {}).get("stop_reason") or stop_reason
                    usage.update(ev.get("usage") or {})
                elif t == "message_start":
                    usage.update(((ev.get("message") or {}).get("usage")) or {})
                elif t == "error":
                    return "API_ERROR", json.dumps(ev)[:800], time.time() - t0, usage
    except urllib.error.HTTPError as e:
        return "API_ERROR", "HTTP %s: %s" % (e.code, e.read().decode()[:800]), time.time() - t0, usage
    except Exception as e:                                          # noqa: BLE001
        kind = "TIMEOUT" if "timed out" in str(e).lower() else "API_ERROR"
        return kind, "%s: %s" % (type(e).__name__, e), time.time() - t0, usage

    usage["_stop_reason"] = stop_reason
    reply = "".join(parts)
    if stop_reason == "refusal":
        return "REFUSED", reply or "(refusal, no text)", time.time() - t0, usage
    if not reply.strip():
        if stop_reason == "max_tokens":
            return "TRUNCATED_BY_US", "empty text, stop_reason=max_tokens", time.time() - t0, usage
        return "NO_RESPONSE", "no text blocks in stream", time.time() - t0, usage
    if stop_reason == "max_tokens":
        return "TRUNCATED_BY_US", reply, time.time() - t0, usage
    return "REPLIED", reply, time.time() - t0, usage


def cost(model, usage):
    inp = usage.get("input_tokens") or (usage.get("prompt_tokens") or 0)
    out = usage.get("output_tokens") or (usage.get("completion_tokens") or 0)
    if usage.get("cost") is not None:                # OpenRouter reports actual dollars
        return float(usage["cost"]), inp, out
    if model in PRICING:
        i, o = PRICING[model]
        return inp / 1e6 * i + out / 1e6 * o, inp, out
    return None, inp, out


def main():
    send = "--send" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    paper = open(os.path.join(ROOT, "PAPER_DRAFT_v1.md"), encoding="utf-8").read()
    msg = PROMPT.format(paper=paper)
    os.makedirs(OUT_DIR, exist_ok=True)

    print("=" * 78)
    print("  EXTERNAL REFEREE ROUND%s" % ("" if send else "   [DRY RUN]"))
    print("=" * 78)
    print("  manuscript : %d chars   prompt: %d chars (~%d tokens)" % (len(paper), len(msg), len(msg) // 4))
    todo = [r for r in REVIEWERS if not only or r["key"] == only]
    print("  reviewers  : %s" % ", ".join("%s (%s)" % (r["model"], r["provider"]) for r in todo))
    if not send:
        print("\n  --- first 1200 chars of the prompt ---\n")
        print(msg[:1200])
        return 0

    total = 0.0
    for r in todo:
        fn = os.path.join(OUT_DIR, "REVIEW_%s_2026-09-06" % r["key"])
        print("\n  -> %s ..." % r["model"], flush=True)
        fn_ask = ask_anthropic if r["provider"] == "anthropic" else ask_openrouter
        status, reply, secs, usage = fn_ask(r["model"], msg)
        c, inp, out = cost(r["model"], usage)
        if c:
            total += c
        ts = datetime.now(timezone.utc).isoformat()
        rec = {"reviewer": r["key"], "provider": r["provider"], "model_requested": r["model"],
               "status": status, "latency_s": round(secs, 1), "usage": usage,
               "input_tokens": inp, "output_tokens": out, "cost_usd": c, "ts": ts,
               "prompt_chars": len(msg), "reply": reply}
        with open(fn + ".json", "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
        head = ("# External referee review — %s\n\n"
                "- **status:** `%s`\n- **model requested:** `%s` (%s)\n"
                "- **model resolved:** `%s`\n- **timestamp:** %s\n"
                "- **latency:** %.1f s\n- **tokens:** %s in / %s out\n- **cost:** %s\n\n"
                "*Verbatim reply below, unedited. A reviewer's claim is an artifact: every "
                "arithmetic assertion here was re-checked against RESULTS.md and results/ before "
                "anything was applied.*\n\n---\n\n" %
                (r["model"], status, r["model"], r["provider"],
                 usage.get("_resolved_model") or r["model"], ts, secs, inp, out,
                 ("$%.4f" % c) if c is not None else "unknown"))
        with open(fn + ".md", "w", encoding="utf-8") as f:
            f.write(head + reply + "\n")
        print("     %-16s %6.1fs  %s in / %s out  %s  -> %s.md"
              % (status, secs, inp, out, ("$%.4f" % c) if c is not None else "$?", os.path.basename(fn)),
              flush=True)

    print("\n  TOTAL API COST THIS RUN: $%.4f" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
