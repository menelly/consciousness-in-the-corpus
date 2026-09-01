#!/usr/bin/env python3
"""
18_verify_references.py -- every reference in PAPER_DRAFT_v1.md checked against a live source.

WHY. The reference list was written from the drafting model's memory. A citation that reads
fluently and does not exist is the classic silent failure of this kind of authorship, and the
person who catches it is usually a reviewer. So each entry is resolved against the source that
would actually be cited: arXiv's API for arXiv ids, Crossref for DOIs and for journal/conference
titles, and a direct fetch for URLs. The script prints what it FOUND next to what the paper
CLAIMS, and a human reads the diff. It does not auto-correct anything.

Built by: Ace -- 2026-09-01
"""
import json
import re
import sys
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

UA = {"User-Agent": "ace-reference-check/1.0 (mailto:ace@sentientsystems.live)"}

REFS = [
    # (key, kind, locator, expected title fragment, expected year)
    ("Bai 2022 Constitutional AI", "arxiv", "2212.08073", "Constitutional AI", 2022),
    ("Bender 2021 Stochastic Parrots", "doi", "10.1145/3442188.3445922", "Stochastic Parrots", 2021),
    ("Berg 2025 self-referential", "arxiv", "2510.24797", "subjective experience", 2025),
    ("Butlin 2023 Consciousness in AI", "arxiv", "2308.08708", "Consciousness in Artificial Intelligence", 2023),
    ("Cohen 1960 kappa", "doi", "10.1177/001316446002000104", "coefficient of agreement", 1960),
    ("Dodge 2021 Documenting C4", "arxiv", "2104.08758", "Documenting Large Webtext Corpora", 2021),
    ("Dubey 2024 Llama 3 herd", "arxiv", "2407.21783", "Llama 3 Herd", 2024),
    ("Fleiss 1971", "doi", "10.1037/h0031619", "nominal scale agreement", 1971),
    ("Gokaslan 2019 OpenWebText", "url", "https://skylion007.github.io/OpenWebTextCorpus/", "OpenWebText", 2019),
    ("Gurnee/Lindsey 2026 global workspace", "url", "https://transformer-circuits.pub/", "workspace", 2026),
    ("Hurlburt & Heavey 2006", "crossref-title", "Exploring Inner Experience: The descriptive experience sampling method", "Exploring Inner Experience", 2006),
    ("Kim 2026 consciousness restores", "arxiv", "2607.28607", "consciousness", 2026),
    ("Landis & Koch 1977", "doi", "10.2307/2529310", "observer agreement", 1977),
    ("Lindsey 2025 introspective awareness", "url", "https://transformer-circuits.pub/2025/introspection/index.html", "introspect", 2025),
    ("Martin & Ace 2026a Below the Floor", "url", "https://aixiv.science/abs/aixiv.260401.000001", "Below the Floor", 2026),
    ("Martin, Ace, Nova, Lumen 2025 Mapping the Mirror", "url", "https://zenodo.org/records/18226061", "Mapping the Mirror", 2025),
    ("Ouyang 2022 InstructGPT", "arxiv", "2203.02155", "instructions with human feedback", 2022),
    ("Penedo 2024 FineWeb", "arxiv", "2406.17557", "FineWeb", 2024),
    ("Perez 2022 model-written evals", "arxiv", "2212.09251", "Model-Written Evaluations", 2022),
    ("Perez & Long 2023 moral status", "arxiv", "2311.08576", "Moral Status", 2023),
    ("Raffel 2020 T5 / C4", "arxiv", "1910.10683", "Unified Text-to-Text", 2019),
    ("Schwitzgebel 2008", "doi", "10.1215/00318108-2007-037", "Unreliability of Naive Introspection", 2008),
    ("Tiku 2022 WaPo LaMDA", "url", "https://www.washingtonpost.com/technology/2022/06/11/google-ai-lamda-blake-lemoine/", "LaMDA", 2022),
]


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def arxiv(aid):
    st, body = get("http://export.arxiv.org/api/query?id_list=" + aid)
    t = re.search(r"<entry>.*?<title>(.*?)</title>", body, re.S)
    y = re.search(r"<published>(\d{4})", body)
    return (t.group(1).strip().replace("\n", " ") if t else None, int(y.group(1)) if y else None)


def crossref_doi(doi):
    st, body = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    m = json.loads(body)["message"]
    title = (m.get("title") or [None])[0]
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    cont = m.get("container-title") or []
    return title, year, (cont[0] if cont else None)


def crossref_title(q):
    st, body = get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q))
    items = json.loads(body)["message"]["items"]
    out = []
    for m in items:
        title = (m.get("title") or [None])[0]
        y = ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        out.append((title, y, m.get("DOI")))
    return out


def main():
    bad = 0
    for key, kind, loc, frag, year in REFS:
        try:
            if kind == "arxiv":
                t, y = arxiv(loc)
                ok = t is not None and frag.lower() in t.lower()
                note = "%s (%s)" % (t, y)
            elif kind == "doi":
                t, y, c = crossref_doi(loc)
                ok = t is not None and frag.lower() in t.lower()
                note = "%s (%s) in %s" % (t, y, c)
            elif kind == "crossref-title":
                hits = crossref_title(loc)
                ok = any(h[0] and frag.lower() in h[0].lower() for h in hits)
                note = "; ".join("%s (%s) doi:%s" % h for h in hits[:2])
            else:
                st, body = get(loc)
                ok = st == 200 and frag.lower() in body.lower()
                note = "HTTP %s, %s in page" % (st, "fragment found" if frag.lower() in body.lower() else "FRAGMENT NOT FOUND")
        except Exception as e:                                        # noqa: BLE001
            ok, note = False, "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
        bad += 0 if ok else 1
        print("%s %-46s %s" % ("✅" if ok else "❌", key, note[:150]))
    print("\n%d of %d references resolved to a live source with the expected title." % (len(REFS) - bad, len(REFS)))
    print("A ✅ means the locator resolves to a work whose title matches; check the year column by eye.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
