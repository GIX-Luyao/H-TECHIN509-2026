"""Instructor-supplied evaluator. Do not edit during the studio."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import search

HERE = Path(__file__).resolve().parent
# Fingerprint of the unchanged starter search.py. A baseline may only come from it.
STARTER_SEARCH_SHA256 = "0e2c69e296679ab758fd9d4b8775c7b60301663fd64480f247e4827001e89eb8"

def search_is_unchanged():
    text = (HERE / "search.py").read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(text).hexdigest() == STARTER_SEARCH_SHA256

def run():
    raw = (HERE / "eval_cases.json").read_bytes()
    rows = []
    for case in json.loads(raw):
        answer = search.search(case["question"])
        row = {**case, "actual": answer["id"], "score": answer["score"],
               "scores": answer["scores"], "correct": answer["id"] == case["expected"]}
        rows.append(row)
        print(f'{case["id"]}: expected={case["expected"]:8} actual={answer["id"]:8} '
              f'score={answer["score"]:.4f} {"OK" if row["correct"] else "MISS"}')
    correct = sum(row["correct"] for row in rows)
    print(f"Retrieval quality: {correct}/{len(rows)} correct (top-1 accuracy)")
    probes = [search.compare_texts(" PASSWORD? ", "password."),
              search.compare_texts("", "password"),
              search.compare_texts("travel receipt", "travel expenses")]
    return {"fixture_sha256": hashlib.sha256(raw).hexdigest(),
            "faqs": search.FAQS, "vocab": search.VOCAB,
            "correct": correct, "results": rows, "comparison_probes": probes}

def equivalent(a, b):
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return isinstance(b, (int, float)) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    return a == b

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--baseline", action="store_true")
    group.add_argument("--after", action="store_true")
    args = parser.parse_args()
    baseline = HERE / "baseline.json"
    if args.baseline and baseline.exists():
        parser.error("baseline.json already exists. Keep the original baseline; do not overwrite it.")
    if args.baseline and not search_is_unchanged():
        parser.error("search.py has already been edited, so it cannot provide a baseline. "
                     "Stop and ask the instructor; do not delete or recreate baseline.json.")
    if args.after and not baseline.exists():
        parser.error("Run --baseline on the unchanged starter first.")
    report = run()
    if args.baseline:
        baseline.write_text(json.dumps(report, indent=2) + "\n")
        print("Saved baseline.json. Keep this unchanged.")
    else:
        original = json.loads(baseline.read_text())
        passed = equivalent(original, report)
        report["behavior_preserved"] = passed
        (HERE / "after.json").write_text(json.dumps(report, indent=2) + "\n")
        print("PASS: results and scores match baseline." if passed else
              "FAIL: behavior changed. Inspect the differences with your partner.")
        raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
