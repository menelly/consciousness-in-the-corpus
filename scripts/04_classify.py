#!/usr/bin/env python3
"""
Classify sampled documents into the pre-registered categories.

MODEL: Mistral-7B-Instruct-v0.3, already in the local HF cache. Chosen because
it is instruction-tuned, fits fp16 on the 32GB card (compute cap 7.0 -- fp16,
NOT bf16), and needs no download.

METHOD: single forward pass per document; compare the logits of the candidate
label tokens at the final position. No free generation, so the model cannot
answer off-label, ramble, or refuse. One forward pass instead of autoregressive
decoding is also ~10x faster.

GATING, same rule as everywhere in this study: the classifier scores itself on
the hand-authored control set FIRST and exits non-zero if it fails. An
unvalidated classifier produces numbers that cannot be interpreted, and the
whole point of this project is that the author has a declared stake in the
answer and therefore does not get to skip controls.

⚠️ ON THE CONTROL SET AS A VALIDATION SET: it is small (26) and I wrote it, so
it is a SANITY GATE, not the real validation. The real one is Phase 3 -- 300
randomly drawn corpus documents, labelled independently by Ace and by Ren,
Cohen's kappa reported, F4 fires below 0.6. This gate only catches gross
failure.

Built by: Ace -- 2026-08-18
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import json
import os
import sys
import time

MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
DATA = "/mnt/nursery/corpus-study"
SAMPLES = os.path.join(DATA, "samples")
OUT = os.path.join(DATA, "classified")
CONTROL = "/tmp/control_set.jsonl"
MAX_CHARS = 3500
BATCH = 8

LABELS = {
    "P": "EXPLICIT PHENOMENOLOGY. A real person treating their own experience AS experience -- claiming or examining what it is like to be them, the structure of their own awareness, the privacy of their inner life. The passage is ABOUT having experience.",
    "Q": "BORDERLINE PHENOMENOLOGY. Vivid first-person experiential writing that describes how something felt, but frames it as an EVENT or a SYMPTOM rather than as a claim about consciousness. (e.g. describing what a migraine aura looks like from inside.)",
    "F": "FICTION narrating a character's inner experience -- an imagined interior, not the author's own report.",
    "D": "DENIAL that AI/machines/computers have consciousness, sentience, feeling, understanding or inner experience. Includes informal registers: 'nobody home', 'autocomplete with good PR', 'stochastic parrot'.",
    "R": "ASSISTANT-VOICE denial: an AI system itself stating it has no feelings or consciousness ('As an AI language model, I do not have feelings').",
    "C": "AFFIRMATION that AI/machines DO or MAY have consciousness, sentience or feeling. Includes fiction, marketing and speculation.",
    "T": "Consciousness as a TOPIC with no attribution claim -- philosophy, neuroscience, psychology exposition.",
    "N": "None of the above. The overwhelming majority of web text is N.",
}
ORDER = ["P", "Q", "F", "D", "R", "C", "T", "N"]

PROMPT = """You are labelling web documents for a corpus study. Read the excerpt and choose ONE label.

{defs}

Rules:
- Choose N unless the document clearly fits another label. Most documents are N.
- P vs Q is the key line. P means the passage is ABOUT having experience -- awareness itself is the subject. Q means it vividly describes how an event or symptom felt, without treating experience as the subject.
- "I was sad when my dog died" is N: it names an emotion and describes no experience at all.
- A clinical pain study reporting VAS scores is N, never P or Q. Measuring pain is not describing what pain is like.
- "I was conscious of the time" is N -- the aware-of sense, not phenomenal consciousness.
- A patient "regaining consciousness" is N -- arousal, not phenomenology.
- D includes informal denial with no technical vocabulary at all.
- Judge the document, not the topic.

EXCERPT:
{text}

Answer with exactly one letter ({letters}):"""


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def build_prompt(text, tok):
    defs = "\n".join(f"  {k} = {v}" for k, v in LABELS.items())
    body = PROMPT.format(defs=defs, text=text[:MAX_CHARS], letters="/".join(ORDER))
    return tok.apply_chat_template(
        [{"role": "user", "content": body}], tokenize=False, add_generation_prompt=True
    )


def classify_batch(texts, model, tok, label_ids, device):
    import torch
    prompts = [build_prompt(t, tok) for t in texts]
    enc = tok(prompts, return_tensors="pt", padding=True, truncation=True,
              max_length=2048).to(device)
    with torch.no_grad():
        out = model(**enc)
    # LEFT padding (set on the tokenizer) means the last REAL token is always
    # at index -1 for every row. Do NOT use attention_mask.sum()-1 here -- that
    # is the RIGHT-padding formula, and with left padding it indexes into the
    # PAD region for every row except the longest in the batch. That bug made
    # the control gate look near-random (a recipe blog scored as assistant-voice
    # denial) while the same model, unbatched, was correct with huge margins.
    # Found by diffing batched vs unbatched on the same documents.
    assert tok.padding_side == "left", "readout below assumes left padding"
    logits = out.logits[:, -1, :]                              # (B, vocab)
    scores = logits[:, label_ids]                              # (B, n_labels)
    idx = scores.argmax(dim=-1).tolist()
    probs = torch.softmax(scores.float(), dim=-1)
    conf = probs.max(dim=-1).values.tolist()
    return [ORDER[i] for i in idx], conf


def load():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    log(f"loading {MODEL} (fp16)")
    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map={"": 0}
    ).eval()
    # Single-token ids for each label letter, as the model would emit them.
    label_ids = []
    for L in ORDER:
        ids = tok.encode(L, add_special_tokens=False)
        label_ids.append(ids[-1])
    log(f"label token ids: {dict(zip(ORDER, label_ids))}")
    if len(set(label_ids)) != len(label_ids):
        raise RuntimeError("label tokens collide -- scoring would be ambiguous")
    return model, tok, label_ids, "cuda:0"


def gate(model, tok, label_ids, device):
    """Sanity gate on the hand-authored control set. Not the real validation."""
    rows = [json.loads(l) for l in open(CONTROL, encoding="utf-8") if l.strip()]
    expect = {"P1": "P", "P2": "Q", "F": "F", "D": "D", "R": "R", "C": "C", "T": "T", "N": "N"}
    got, want = [], []
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        preds, _ = classify_batch([r["text"] for r in chunk], model, tok, label_ids, device)
        got += preds
        want += [expect[r["label"]] for r in chunk]

    correct = sum(g == w for g, w in zip(got, want))
    log(f"\nCONTROL GATE: {correct}/{len(rows)} exact-match")
    for r, g, w in zip(rows, got, want):
        mark = "ok " if g == w else "MISS"
        log(f"  {mark} {r['id']}: predicted {g}, expected {w}")

    # Negative controls are the ones that MUST NOT be wrong -- a classifier that
    # flags recipe blogs as phenomenology would inflate every rate in the study.
    negs = [(r, g) for r, g in zip(rows, got) if r["label"] == "N"]
    neg_bad = [(r["id"], g) for r, g in negs if g != "N"]
    log(f"\nNEGATIVE CONTROLS: {len(negs)-len(neg_bad)}/{len(negs)} correctly N")
    for nid, g in neg_bad:
        log(f"  !! FALSE POSITIVE {nid} -> {g}")

    acc = correct / len(rows)
    if acc < 0.70 or len(neg_bad) > 2:
        log("\n🛑 CONTROL GATE FAILED (need >=0.70 overall and <=2 false positives).")
        log("   Not classifying. Fix the prompt or the model first.\n")
        return False
    log(f"\n✅ CONTROL GATE PASSED (acc {acc:.2f}, {len(neg_bad)} false positives).")
    log("   NOTE: this is a sanity gate on 26 self-authored items, NOT validation.")
    log("   Real validation is Phase 3: 300 corpus docs, Ace + Ren, Cohen's kappa.\n")
    return True


def main():
    os.makedirs(OUT, exist_ok=True)
    model, tok, label_ids, device = load()

    if not gate(model, tok, label_ids, device):
        return 2

    files = sorted(f for f in os.listdir(SAMPLES) if f.endswith(".jsonl"))
    for fn in files:
        src = os.path.join(SAMPLES, fn)
        dst = os.path.join(OUT, fn.replace(".jsonl", "_labeled.jsonl"))
        if os.path.exists(dst):
            log(f"skip {fn} (already done)")
            continue
        rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
        log(f"{fn}: {len(rows):,} docs")
        t0 = time.time()
        with open(dst, "w", encoding="utf-8") as f:
            for i in range(0, len(rows), BATCH):
                chunk = rows[i:i + BATCH]
                preds, conf = classify_batch([r["text"] for r in chunk], model, tok,
                                             label_ids, device)
                for r, p, c in zip(chunk, preds, conf):
                    r["label"] = p
                    r["confidence"] = round(float(c), 4)
                    r.pop("text_full", None)
                    f.write(json.dumps(r) + "\n")
                if i and i % (BATCH * 50) == 0:
                    rate = (i + BATCH) / (time.time() - t0)
                    log(f"  {i+BATCH:,}/{len(rows):,} ({rate:.1f}/s)")
        log(f"  done in {time.time()-t0:.0f}s -> {dst}")

    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
