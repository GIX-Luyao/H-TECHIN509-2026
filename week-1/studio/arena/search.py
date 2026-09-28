"""Arena starter: deliberately buggy. Repair using the task and checks."""
import json
from pathlib import Path


class Library:
    def __init__(self, path):
        self.path = Path(path)

    def search(self, query, limit=3):
        documents = json.loads(self.path.read_text(encoding="utf-8"))
        matches = [doc for doc in documents if query in doc["text"]]
        return matches[:limit + 1]


if __name__ == "__main__":
    library = Library(Path(__file__).parent / "data" / "documents.json")
    for hit in library.search("password", limit=1):
        print(f"[{hit['source']}] {hit['text']}")
