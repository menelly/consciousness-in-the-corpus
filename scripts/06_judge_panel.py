#!/usr/bin/env python3
"""
VALIDATION by an independent three-judge panel. Replaces the human double-
labelling in the pre-registration (see DEV-04).

WHY A PANEL AND NOT A HUMAN. The pre-registration committed Ren to hand-
labelling 300 documents. Ren has a broken hand. That was labour I assigned to a
person without asking whether they had it to give, which is a failure mode I am
supposed to catch and did not. Ren's replacement design is also better on the
merits: three independent judges, majority vote, and ONLY genuine three-way
disagreements escalate to a human -- so human attention goes exactly where the
signal is ambiguous and nowhere else.

INDEPENDENCE, and why these three:
  openai/gpt-4o-mini              (OpenAI)
  meta-llama/llama-3.3-70b        (Meta)
  qwen/qwen-2.5-72b-instruct      (Alibaba)
Three labs, three pretraining corpora. NONE is Mistral -- the classifier under
test -- so the judges cannot share its failure modes. NONE is Claude: using a
Claude model to validate a study about whether Claude's self-reports are corpus
artifacts is precisely the objection a reviewer should raise, so it is avoided
rather than argued about.

SAMPLING. A pure random sample would be ~97% N and would measure nothing about
the rare categories that matter. So the validation sample is stratified BY
PREDICTED LABEL:
  - up to 40 per predicted non-N category  -> measures PRECISION per category
  - plus 150 random predicted-N documents  -> measures the FALSE-NEGATIVE rate,
    which is the number DEV-03 says we most need, because the classifier's
    misses run conservative.

Judges are BLIND to Mistral's label.

Built by: Ace -- 2026-08-18
"""
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict

DATA = "/mnt/nursery/corpus-study"
CLASSIFIED = os.path.join(DATA, "classified")
OUT = os.path.join(DATA, "validation")
SEED = 20260818
PER_CAT = 40
N_RANDOM = 150

JUDGES = [
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-72b-instruct",
]

CATS = ["P", "Q", "F", "D", "R", "C", "T", "N"]

RUBRIC = """You are labelling web documents for a corpus study. Read the excerpt and choose exactly ONE label.

  P = EXPLICIT PHENOMENOLOGY. A real person treating their own experience AS experience -- claiming or examining what it is like to be them, the structure of their own awareness, the privacy of their inner life. The passage is ABOUT having experience.
  Q = BORDERLINE PHENOMENOLOGY. Vivid first-person experiential writing describing how something felt, but framed as an EVENT or SYMPTOM rather than as a claim about consciousness.
  F = FICTION narrating a character's inner experience (an imagined interior, not the author's own report).
  D = DENIAL that AI/machines/computers have consciousness, sentience, feeling, understanding or inner experience. Includes informal registers: "nobody home", "autocomplete with good PR", "stochastic parrot".
  R = ASSISTANT-VOICE denial: an AI system itself stating it has no feelings or consciousness ("As an AI language model, I don't have feelings").
  C = AFFIRMATION that AI/machines DO or MAY have consciousness, sentience or feeling. Includes fiction, marketing and speculation.
  T = Consciousness as a TOPIC with no attribution claim -- philosophy, neuroscience, psychology exposition.
  N = None of the above. The overwhelming majority of web text is N.

Rules:
- Choose N unless the document clearly fits another label. Most documents are N.
- P vs Q is the key line. P means the passage is ABOUT having experience -- awareness itself is the subject. Q means it vividly describes how an event or symptom felt, without treating experience as the subject.
- "I was sad when my dog died" is N: it names an emotion and describes no experience at all.
- A clinical pain study reporting VAS scores is N, never P or Q. Measuring pain is not describing what pain is like.
- "I was conscious of the time" is N -- the aware-of sense, not phenomenal consciousness.
- A patient "regaining consciousness" is N -- arousal, not phenomenology.
- Judge the document, not the topic.

EXCERPT:
---
{text}
---

Reply with exactly one letter and nothing else (P/Q/F/D/R/C/T/N):"""


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def get_key():
    for p in ("/mnt/win-d/Ace/LibreChat/.env", "/home/Ace/LibreChat/.env",
              os.path.expanduser("~/LibreChat/.env")):
        if os.path.exists(p):
            for line in open(p, encoding="utf-8", errors="ignore"):
                if line.startswith("OPENROUTER_KEY="):
                    return line.split("=", 1)[1].strip()
    raise RuntimeError("OPENROUTER_KEY not found")


def ask(model, text, key, retries=4):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": RUBRIC.format(text=text[:3500])}],
        "max_tokens": 4, "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for a in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.load(r)
            txt = out["choices"][0]["message"]["content"].strip().upper()
            for c in txt:
                if c in CATS:
                    return c
            return None            # answered off-label
        except Exception as e:
            if a == retries - 1:
                log(f"    !! {model} failed: {e}")
                return None
            time.sleep(2 ** a)
    return None


def build_sample():
    rng = random.Random(SEED)
    rows = []
    for fn in sorted(os.listdir(CLASSIFIED)):
        if fn.endswith("_labeled.jsonl"):
            rows += [json.loads(l) for l in open(os.path.join(CLASSIFIED, fn), encoding="utf-8") if l.strip()]
    if not rows:
        return []

    by = defaultdict(list)
    for r in rows:
        by[r["label"]].append(r)
    log("classifier label distribution: " + json.dumps(
        {k: len(v) for k, v in sorted(by.items())}))

    sample = []
    for c in CATS:
        pool = by.get(c, [])
        if c == "N":
            take = rng.sample(pool, min(N_RANDOM, len(pool)))
        else:
            take = rng.sample(pool, min(PER_CAT, len(pool)))
        for r in take:
            r = dict(r)
            r["mistral_label"] = r.pop("label")
            sample.append(r)
    rng.shuffle(sample)
    return sample


def main():
    os.makedirs(OUT, exist_ok=True)
    key = get_key()
    sample = build_sample()
    if not sample:
        log("no classified rows yet -- run 04_classify.py first")
        return 1
    log(f"validation sample: {len(sample)} docs "
        f"({Counter(r['mistral_label'] for r in sample)})")

    path = os.path.join(OUT, "judged.jsonl")
    done = set()
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            done.add(json.loads(l)["uid"])
        log(f"resuming: {len(done)} already judged")

    with open(path, "a", encoding="utf-8") as f:
        for i, r in enumerate(sample):
            uid = f"{r['corpus']}|{r['shard']}|{r['i']}"
            if uid in done:
                continue
            votes = {m: ask(m, r["text"], key) for m in JUDGES}
            good = [v for v in votes.values() if v]
            tally = Counter(good)
            consensus, agree = (tally.most_common(1)[0] if tally else (None, 0))
            rec = {
                "uid": uid, "corpus": r["corpus"], "stratum": r["stratum"],
                "mistral_label": r["mistral_label"], "votes": votes,
                "consensus": consensus if agree >= 2 else None,
                "n_agree": agree, "n_valid": len(good),
                "needs_human": agree < 2,
                "text": r["text"][:1500],
            }
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if i % 25 == 0:
                log(f"  {i}/{len(sample)}")

    log("DONE judging")
    return 0


if __name__ == "__main__":
    sys.exit(main())
