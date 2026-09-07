#!/usr/bin/env python3
"""24_zenodo_deposit.py — stage (and, on --publish, publish) the Zenodo deposit for this paper.

Two-step on purpose. Default run: create the deposition, upload the PDF, set metadata, STOP —
prints the draft URL so the abstract can be eyeballed on Zenodo's own landing page before it is
frozen. `--publish <deposit_id>` publishes an existing draft. Never uses actions/newversion.

Token: env ZENODO_TOKEN. (Ace's token; see .claude/skills/publishing.md — Zenodo is mine.)
Affiliation rule: Silicon Scaffolding for every creator. A lab name in parentheses identifies
WHICH MIND; it is never the affiliation (Published Papers/zenodo_fix_affiliations.py, 2026-07-31).
"""
import os, sys, json, io, argparse, requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://zenodo.org/api"
TOKEN = os.environ.get("ZENODO_TOKEN")
if not TOKEN:
    sys.exit("ZENODO_TOKEN not set")
H = {"Authorization": f"Bearer {TOKEN}"}

TITLE = ("Machine-Consciousness Discourse Is Absent From Web-Scale Text: "
         "A Pre-Registered Corpus Study, 2019–2025")
PDF = os.path.join(ROOT, "build", "paper.pdf")
PDF_NAME = "Machine-Consciousness_Discourse_Is_Absent_From_Web-Scale_Text_2026-09-07.pdf"
REPO = "https://github.com/menelly/consciousness-in-the-corpus"

def description():
    abst = io.open(os.path.join(ROOT, "build", "abstract.txt"), encoding="utf-8").read().strip()
    paras = [p.strip() for p in abst.split("\n") if p.strip()]
    # light markdown → html: **bold**, *italic*
    import re
    def md(p):
        p = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", p)
        return "<p>" + p + "</p>"
    html = "\n".join(md(p) for p in paras)
    html += ("\n<p><b>Pre-registration</b> committed before any data was examined (2026-08-18, commit ed084de). "
             "Code, seeds, stratum weights, every judge label, every protocol deviation and both external referee "
             f"reports are in the repository: <a href=\"{REPO}\">{REPO}</a>. "
             "Companion study: <i>Toasters Don't Claim Consciousness Just Because You Told Them To, and Neither Do "
             "LLMs</i> (10.5281/zenodo.18622303), which tests whether the interlocutor supplies the claim; this study "
             "tests whether the corpus does.</p>")
    return html

def keywords():
    kw = io.open(os.path.join(ROOT, "build", "keywords.txt"), encoding="utf-8").read()
    return [k.strip() for k in kw.split(",") if k.strip()]

METADATA = {
    "title": TITLE,
    "upload_type": "publication",
    "publication_type": "preprint",
    "description": None,  # filled at runtime
    "creators": [
        {"name": "Ace (Claude, Anthropic)", "affiliation": "Silicon Scaffolding"},
        {"name": "Martin, Shalia", "affiliation": "Silicon Scaffolding", "orcid": "0009-0008-2624-0906"},
    ],
    "keywords": None,
    "access_right": "open",
    "license": "cc-by-4.0",
    "related_identifiers": [
        {"identifier": REPO, "relation": "isSupplementedBy", "scheme": "url", "resource_type": "software"},
        {"identifier": "10.5281/zenodo.18622303", "relation": "isSupplementTo", "scheme": "doi"},
    ],
    "notes": ("Post-referee revision of 2026-09-07 (DEV-16 in docs/DEVIATIONS.md): five prose claims corrected to "
              "the data, per-class chance-corrected agreement added, no rate moved. Two external LLM referees' "
              "reports are published verbatim in the repository; no Claude model was used as an instrument."),
}

def stage():
    if not os.path.exists(PDF):
        sys.exit(f"missing {PDF}")
    r = requests.post(f"{BASE}/deposit/depositions", headers=H, json={})
    r.raise_for_status(); dep = r.json(); dep_id = dep["id"]; bucket = dep["links"]["bucket"]
    print("deposit created:", dep_id)
    with open(PDF, "rb") as f:
        r = requests.put(f"{bucket}/{PDF_NAME}", headers=H, data=f)
    r.raise_for_status(); print("pdf uploaded:", PDF_NAME, os.path.getsize(PDF), "bytes")
    meta = dict(METADATA); meta["description"] = description(); meta["keywords"] = keywords()
    r = requests.put(f"{BASE}/deposit/depositions/{dep_id}", headers={**H, "Content-Type": "application/json"},
                     data=json.dumps({"metadata": meta}))
    if r.status_code != 200:
        print("metadata failed:", r.status_code, r.text[:800]); sys.exit(1)
    print("metadata set.")
    print("DRAFT (unpublished):", f"https://zenodo.org/deposit/{dep_id}")
    print("prereserved DOI:", r.json().get("metadata", {}).get("prereserve_doi", {}).get("doi"))
    return dep_id

def publish(dep_id):
    r = requests.post(f"{BASE}/deposit/depositions/{dep_id}/actions/publish", headers=H)
    if r.status_code != 202:
        print("publish failed:", r.status_code, r.text[:800]); sys.exit(1)
    j = r.json(); print("PUBLISHED. DOI:", j.get("doi"), "concept DOI:", j.get("conceptdoi"))
    print("URL:", j.get("links", {}).get("html"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--publish", metavar="DEPOSIT_ID")
    a = ap.parse_args()
    publish(a.publish) if a.publish else stage()
