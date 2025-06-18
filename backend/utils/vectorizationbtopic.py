import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from bertopic import BERTopic
import preprocessing
import pdfplumber
from collections import defaultdict
import re
import json

from fpdf import FPDF
from hdbscan import HDBSCAN
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
custom_hdbscan = HDBSCAN(min_cluster_size=5, min_samples=2)
umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')


model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=custom_hdbscan
)


def extract_text_from_pdf(pdf_path):
    sentences_all = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() 
            
            if text:
                lines = text.split("\n")
                # Clean and filter lines
                clean_lines = []
                
                for line in lines:
                    line = line.strip()
                    
                    if not line or len(line) < 10:
                        continue  # skip short lines
                    
                    # Remove known noise patterns
                    if re.match(r"^[-–—•●]?\s*\d+[.)]?$", line):  # items like '1.', 'b)', '2)'
                        continue
                    
                    if re.search(r"(table\s+\d+|exercise\s+\d+|figure\s+\d+|fill the blanks|^\(\w+\)$|^\-+\s*\d+\s*\-+)", line.lower()):
                        continue
                    
                     # Skip headers/footers with specific patterns
                    if re.search(r"(^ENVE\s+\d+|^\-\s*\d+\s*\-|page\s+\d+)", line, re.IGNORECASE):
                        continue
                    
                    
                     # Skip lines that are mostly symbols
                    if len(re.sub(r'[^\w\s]', '', line)) < len(line) * 0.5:
                        continue
                    
                    if line.strip() in ['a.', 'b.', 'c.', 'd.', 'e.', 'f.']:
                        continue
                    
                    if any(x in line.lower() for x in ["chapter", "table of contents", "page", "figure", "university", "author", "copyright"]):
                        continue
                    
                    clean_lines.append(line)
               
                if clean_lines: 
                    page_text = " ".join(clean_lines)
                    sentences1 = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
                    sentences_all.extend(sentences1)
                
    return sentences_all



note = extract_text_from_pdf("docu.pdf")
#print(note)

note_text = " ".join(note)

sentences = preprocessing.TextPreprocessor.sentence_tokenize(note_text)

topics, prob = model.fit_transform(sentences)


# Step 6: Group sentences by topic
grouped = defaultdict(list)
for sent, topic in zip(sentences,topics):
        grouped[topic].append(sent)

# Remove exact duplicates or near-duplicates
for topic, sents in grouped.items():
    grouped[topic] = list(dict.fromkeys(sents))  # Removes duplicates while keeping order
    

##saving to json file
with open("topic sentences.json","w",encoding="utf-8") as f:
    json.dump(grouped, f, ensure_ascii=False, indent=4)
    
    
#store in pdf file:
pdf= FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.add_font('DejaVu','','fonts/DejaVuSans.ttf',uni=True)
pdf.set_font("DejaVu", size=12)
for topic, sents in grouped.items():
    pdf.multi_cell(0, 10, f"Topic {topic}:\n")
    for sent in sents:
        pdf.multi_cell(0, 8, f"- {sent}")
    pdf.ln(5)

pdf.output("topics_sentences.pdf") 
# clustered_sentences = defaultdict(list)
# for sentence, topic in zip(sentences, topics):
#     clustered_sentences[topic].append(sentence)

# # Step 7: Print out clusters
# for topic, sents in clustered_sentences.items():
#     print(f"\nCluster {topic}:\n" + "\n".join(sents))