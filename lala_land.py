import json
with open("data/faq/curated_qa.json", "r") as f:
    qa = json.load(f)

for i, item in enumerate(qa):
    if "villas" in item["question"].lower():
        print(f"{i}: {item['question']} -> {item['answer'][:100]}")