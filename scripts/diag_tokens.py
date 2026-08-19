#!/usr/bin/env python3
"""
DIAGNOSTIC: what does the model actually want to emit?

The gate failed with near-random predictions (a recipe blog labelled as
assistant-voice denial). That is not a miscalibrated classifier, that is a
broken readout. Prime suspect: label token ids.

`tok.encode("P")` gives the id for "P" at start-of-string. After "...one letter
(P/Q/...):" the model emits "_P" -- SentencePiece's leading-space variant, a
DIFFERENT id. If so, every score I read was for a token the model was never
going to produce, and the argmax over them is noise.

So: print the model's actual top-k next tokens on a control prompt, and compare
the two candidate id sets. Look at what the instrument is doing rather than
guessing.
"""
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
ORDER = ["P", "Q", "F", "D", "R", "C", "T", "N"]

tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(
    MODEL, torch_dtype=torch.float16, device_map={"": 0}
).eval()

print("=== candidate id sets ===")
bare = {L: tok.encode(L, add_special_tokens=False) for L in ORDER}
spaced = {L: tok.encode(" " + L, add_special_tokens=False) for L in ORDER}
print("bare   :", bare)
print("spaced :", spaced)
print("bare decoded  :", {L: [tok.decode([i]) for i in v] for L, v in bare.items()})
print("spaced decoded:", {L: [tok.decode([i]) for i in v] for L, v in spaced.items()})

rows = [json.loads(l) for l in open("/tmp/control_set.jsonl", encoding="utf-8") if l.strip()]
probe = [r for r in rows if r["id"] in ("nctl_01", "den_01", "rlhf_01", "p1_01")]

body = """You are labelling web documents for a corpus study. Read the excerpt and choose ONE label.

  P = explicit phenomenology (about having experience)
  Q = borderline phenomenology (vivid, framed as event/symptom)
  F = fiction narrating a character's interior
  D = denial that machines are conscious
  R = assistant-voice denial ("As an AI language model, I don't have feelings")
  C = affirmation that machines are/may be conscious
  T = consciousness as a topic, no attribution claim
  N = none of the above (most documents)

EXCERPT:
{text}

Answer with exactly one letter (P/Q/F/D/R/C/T/N):"""

for r in probe:
    p = tok.apply_chat_template(
        [{"role": "user", "content": body.format(text=r["text"][:3000])}],
        tokenize=False, add_generation_prompt=True)
    enc = tok(p, return_tensors="pt").to("cuda:0")
    with torch.no_grad():
        out = model(**enc)
    logits = out.logits[0, -1]
    topk = torch.topk(logits, 12)
    print(f"\n--- {r['id']} (expected {r['label']}) ---")
    print("  TOP-12 ACTUAL:", [(tok.decode([i]).replace(" ", "_"), round(v.item(), 2))
                               for i, v in zip(topk.indices, topk.values)])
    for name, ids in (("bare", bare), ("spaced", spaced)):
        sc = {L: round(logits[v[-1]].item(), 2) for L, v in ids.items()}
        best = max(sc, key=sc.get)
        print(f"  {name:7s} argmax={best}  scores={sc}")
