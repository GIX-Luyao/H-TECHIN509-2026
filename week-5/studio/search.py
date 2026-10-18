"""Working but repetitive FAQ search. Refactor this file only.
The vectors are word counts, NOT learned semantic embeddings.
"""
import math

FAQS = [
    {"id": "password", "text": "Reset your password using the account portal."},
    {"id": "expenses", "text": "Submit travel expenses with a receipt."},
    {"id": "leave", "text": "Request vacation leave through your manager."},
]
VOCAB = ["password", "account", "travel", "expenses", "receipt", "vacation", "leave", "manager"]


def search(query):
    # Repeated cleanup and vector construction: intentionally awkward.
    q = query.strip().lower().replace("?", "").replace(".", "")
    qv = [q.split().count(word) for word in VOCAB]
    results = []
    for item in FAQS:
        t = item["text"].strip().lower().replace("?", "").replace(".", "")
        v = [t.split().count(word) for word in VOCAB]
        dot = 0.0
        nq = 0.0
        nv = 0.0
        for i in range(len(qv)):
            dot += qv[i] * v[i]
            nq += qv[i] ** 2
            nv += v[i] ** 2
        if nq == 0 or nv == 0:
            score = 0.0
        else:
            score = dot / (math.sqrt(nq) * math.sqrt(nv))
        results.append({"id": item["id"], "score": score})
    best = results[0]
    for row in results:
        if row["score"] > best["score"]:
            best = row
    return {"id": best["id"], "score": best["score"], "scores": results}


def compare_texts(first, second):
    # Same work repeated in a second entry point.
    a = first.strip().lower().replace("?", "").replace(".", "")
    b = second.strip().lower().replace("?", "").replace(".", "")
    av = [a.split().count(word) for word in VOCAB]
    bv = [b.split().count(word) for word in VOCAB]
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(len(av)):
        dot += av[i] * bv[i]
        na += av[i] ** 2
        nb += bv[i] ** 2
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


if __name__ == "__main__":
    result = search("How do I reset my password?")
    for row in result["scores"]:
        print(row["id"], round(row["score"], 4))
    print("Selected FAQ:", result["id"])
