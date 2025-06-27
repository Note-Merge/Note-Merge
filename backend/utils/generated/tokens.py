import json
from tqdm import tqdm

# -------- CONFIG --------
INPUT_JSON = "merged_split.json"
OUTPUT_JSON = "merged_tagged.json"
formatted_data = []

# -------- LOGIC --------
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

for key, content in tqdm(data.items(), desc="Formatting Entries"):
    paragraphs = content.get("paragraphs", [])
    label = content.get("label", "")
    
    is_merged = key.startswith("merged_topic")

    if is_merged:
        # Split groups by '++++'
        paragraph_groups = []
        current_group = []

        for p in paragraphs:
            if p.strip() == "++++":
                if current_group:
                    paragraph_groups.append("\n".join(current_group))
                    current_group = []
            else:
                current_group.append(p.strip())
        if current_group:
            paragraph_groups.append("\n".join(current_group))

        input_text = "<task:merge> <sos>\n" + "\n\n++++\n\n".join(paragraph_groups) + "\n<eos>"
    else:
        # For file_topic (single paragraph group)
        cleaned_paragraphs = "\n".join([p.strip() for p in paragraphs if p.strip()])
        input_text = "<task:clean> <sos>\n" + cleaned_paragraphs + "\n<eos>"

    formatted_data.append({
        "key": key,
        "label": label,
        "input": input_text
    })

# -------- SAVE OUTPUT --------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(formatted_data, f, indent=4, ensure_ascii=False)

print(f"✅ Done! Saved formatted data to: {OUTPUT_JSON}")
