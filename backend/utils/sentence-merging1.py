from clustering import group_sentences

import os
import json


from fpdf import FPDF
from sklearn.cluster import AgglomerativeClustering

from sentence_transformers import SentenceTransformer,util
from collections import defaultdict

#initialize model
model = SentenceTransformer('all-mpnet-base-v2')

#process two documents:
file_paths= ["docu.pdf", "docu2.pdf"]
all_grouped = []
all_labels = []

for idx , path in enumerate(file_paths):
    grouped , topic_labels = group_sentences(path, output_prefix=f"output{idx}")    
    all_grouped.append(grouped)
    all_labels.append(topic_labels)
 
#flatten all topics
flat_sentences = []
flat_meta = []

for file_idx, grouped in enumerate(all_grouped):
    for topic_id,sentences in grouped.items():
        text = " ".join(sentences)
        flat_sentences.append(text)
        flat_meta.append({
            "source_file_idx": file_idx,
            "topic_id": topic_id,
            "sentences": sentences,
            "label": all_labels[file_idx].get(topic_id, f"Topic {topic_id}")
        })
        
#getting embeddings from SBERT
embeddings = model.encode(flat_sentences, convert_to_tensor=False)

#clustering using AgglomerativeClustering
clustering = AgglomerativeClustering(
    n_clusters=None,
    distance_threshold=0.45,
    metric='cosine',
    linkage='average'
)
cluster_ids = clustering.fit_predict(embeddings)

#group merged topics
merged_clusters = defaultdict(lambda: {"sentences": [],})
  
  
  
# Generate output in previous format
merged_topics = {}
for idx, cluster_id in enumerate(cluster_ids):
    key = f"merged_topic_{cluster_id}"
    
    if key not in merged_topics:
        merged_topics[key] = {
            "label": flat_meta[idx]["label"],
            "paragraphs": flat_meta[idx]["sentences"]
        }
    else:
        # Merge label if not already present
        if flat_meta[idx]["label"] not in merged_topics[key]["label"]:
            merged_topics[key]["label"] += " / " + flat_meta[idx]["label"]
        # Extend sentences and remove duplicates
        merged_topics[key]["paragraphs"].extend(flat_meta[idx]["sentences"])
        merged_topics[key]["paragraphs"] = list(dict.fromkeys(merged_topics[key]["paragraphs"]))

# Export to JSON
output_dir = "generated1/merged_clusters"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "merged_agglomerative_format.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged_topics, f, ensure_ascii=False, indent=4)

print(f"✅ Merged output saved to: {output_path}")
  
  
# Function to export merged topics to PDF and JSON
def export_pdf_json(merged_topics, output_folder="generated1", base_filename="merged_output"):
    os.makedirs(output_folder, exist_ok=True)

    json_path = os.path.join(output_folder, f"{base_filename}.json")
    pdf_path = os.path.join(output_folder, f"{base_filename}.pdf")

    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(merged_topics, f, ensure_ascii=False, indent=4)

    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    try:
        pdf.add_font('TiemposTextRegular', '', 'fonts/TiemposTextRegular.ttf', uni=True)
        pdf.set_font("TiemposTextRegular", size=12)
    except:
        print("⚠️ Font not found, using default.")
        pdf.set_font("Arial", size=12)

    for topic_id, content in merged_topics.items():
        label = content.get("label", f"Topic {topic_id}")
        paragraphs = content.get("paragraphs", [])

        pdf.set_font("TiemposTextRegular", size=14)
        pdf.multi_cell(0, 10, f"{topic_id}: {label}\n")

        pdf.set_font("TiemposTextRegular", size=12)
        for para in paragraphs:
            pdf.multi_cell(0, 8, f"- {para}")
        pdf.ln(5)

    pdf.output(pdf_path)
    print(f"✅ Exported:\n📄 PDF: {pdf_path}\n📁 JSON: {json_path}")

# Call export
export_pdf_json(merged_topics, output_folder="generated1/merged_clusters", base_filename="merged_agglomerative_output")