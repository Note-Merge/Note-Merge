import json
from tqdm import tqdm
import google.generativeai as genai

# -------------------------------
# STEP 1: Configure Gemini API
# -------------------------------
GOOGLE_API_KEY = "AIzaSyDMUOpWYLwybV8d8HaSU_EZj3G-kYYkDtY"  # 🔁 Replace with your actual Gemini API Key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------
# STEP 2: Define Prompts
# -------------------------------
def prompt_for_merged(paragraphs: str) -> str:
    return f"""You are given multiple raw paragraphs on the same topic, possibly with overlapping or redundant content.

Your task is to MERGE them into a single, grammatically correct and coherent paragraph. Do not summarize or shorten the information. Retain all unique information while removing exact duplicates and improving sentence structure. Keep the vocabulary as close as possible to the original. Avoid adding new information not present in the input.

The output should be a single paragraph approximately the same length as the input or slightly longer, and suitable for training a BiLSTM model for merging text.

Input:
{paragraphs}

Output:"""

def prompt_for_single(paragraph: str) -> str:
    return f"""You are given a single raw paragraph on a specific topic.

Your task is to CLEAN and IMPROVE the grammar, syntax, and structure while keeping the vocabulary and meaning the same. Do not summarize, shorten, or expand the paragraph. Do not add any new ideas or concepts. The output should be as close as possible in content and length to the input, but grammatically correct and better structured.

This cleaned version will be used as the target for training a BiLSTM model on text improvement.

Input:
{paragraph}

Output:"""

# -------------------------------
# STEP 3: Load merged.json
# -------------------------------
INPUT_FILE = "merged_tagged.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# -------------------------------
# STEP 4: Process Each Entry
# -------------------------------
# merged_outputs = []
# single_outputs = []
# errors = []

# for key, content in tqdm(data.items(), desc="Processing Topics"):
#     paragraphs = content.get("paragraphs", [])
#     label = content.get("label", "")
    
#     # Join paragraphs and skip '++++'
#     joined_input = "\n".join([p.strip() for p in paragraphs if p.strip() and p.strip() != "++++"])

#     # Decide prompt type
#     is_merged = key.startswith("merged_topic")
#     prompt = prompt_for_merged(joined_input) if is_merged else prompt_for_single(joined_input)

#     try:
#         # Query Gemini API
#         response = model.generate_content(prompt)
#         cleaned_output = response.text.strip()

#         output_entry = {
#             "key": key,
#             "label": label,
#             "input": joined_input,
#             "output": cleaned_output
#         }

#         if is_merged:
#             merged_outputs.append(output_entry)
#         else:
#             single_outputs.append(output_entry)

#     except Exception as e:
#         errors.append({
#             "key": key,
#             "label": label,
#             "error": str(e)
#         })
# -------------------------------
# STEP 4: Process Each Entry (Corrected)
# -------------------------------
merged_outputs = []
single_outputs = []
errors = []

# The input 'data' is a list of dictionaries, so we iterate through it directly.
for item in tqdm(data, desc="Processing Topics"):
    try:
        # Get the data directly from the dictionary item
        key = item["key"]
        label = item["label"]
        joined_input = item["input"]  # Use the pre-formatted input string

        # Determine if the task is a merge or a clean
        is_merged = key.startswith("merged_topic")

        # Select the correct prompt function
        if is_merged:
            prompt = prompt_for_merged(joined_input)
        else:
            prompt = prompt_for_single(joined_input)

        # Query Gemini API
        response = model.generate_content(prompt)
        cleaned_output = response.text.strip()

        # Create the output entry
        output_entry = {
            "key": key,
            "label": label,
            "input": joined_input,
            "output": cleaned_output
        }

        # Append to the correct list
        if is_merged:
            merged_outputs.append(output_entry)
        else:
            single_outputs.append(output_entry)

    except KeyError as e:
        errors.append({
            "error": f"Missing key in item: {e}",
            "item": item
        })
    except Exception as e:
        # Use .get() to avoid errors if key is missing in the error log
        errors.append({
            "key": item.get("key", "N/A"),
            "label": item.get("label", "N/A"),
            "error": str(e)
        })



# -------------------------------
# STEP 5: Save Outputs
# -------------------------------
with open("cleaned_merged_topics.json", "w", encoding="utf-8") as f:
    json.dump(merged_outputs, f, indent=4, ensure_ascii=False)

with open("cleaned_file_topics.json", "w", encoding="utf-8") as f:
    json.dump(single_outputs, f, indent=4, ensure_ascii=False)

with open("gemini_errors.json", "w", encoding="utf-8") as f:
    json.dump(errors, f, indent=4, ensure_ascii=False)

print("✅ Done! Outputs saved to:")
print("  • cleaned_merged_topics.json")
print("  • cleaned_file_topics.json")
print("  • gemini_errors.json")
