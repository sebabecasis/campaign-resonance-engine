"""Build a corpus from an operator-reviewed URL inventory."""
from .providers import chunks, digest, extract_passages, scrape


def collect(plan, approved_hash, *, fetch=scrape, extractor=extract_passages):
    if digest(plan) != approved_hash:
        raise PermissionError("Source plan changed since approval")
    companies, failures = {}, []
    for source in plan["sources"]:
        domain, url, label = source["domain"], source["source_url"], source["label"]
        company = companies.setdefault(domain, {"domain": domain, "passages": []})
        try:
            page = fetch(url)
            model = plan.get("extraction_model")
            texts = extractor(page["text"], plan["objective"], model=model) if model else chunks(page["text"])
            company["passages"].extend({"source_url": url, "label": label, "text": t} for t in texts)
        except Exception as exc:
            failures.append({"domain": domain, "source_url": url, "error": type(exc).__name__})
    return {"plan_hash": approved_hash, "corpus": list(companies.values()), "failures": failures}
