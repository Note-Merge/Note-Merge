import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'



from bertopic import BERTopic
import preprocessing
import pdfplumber
from collections import defaultdict
import re
import spacy
import json
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import fitz
import io
from PIL import Image


from fpdf import FPDF
from hdbscan import HDBSCAN
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer


nlp = spacy.load("en_core_web_sm")

def classify_line_spacy(line):
    line = line.strip()
    if not line or len(line) < 3:
        return None

    doc = nlp(line)
    line_lower = line.lower()

    # --- 1. Ends with a question mark ---
    if line.endswith('?'):
        return "Question: " + line

    # --- 2. Starts with WH-word (what, why, when, etc.) ---
    if doc[0].lower_ in ['what', 'why', 'when', 'where', 'how', 'which', 'who']:
        return "Question: " + line

    # --- 3. Imperative task-style sentence ---
    task_verbs = [
        'explain', 'evaluate', 'compare', 'contrast', 'discuss',
        'analyze', 'define', 'describe', 'justify', 'interpret', 'illustrate'
    ]

    # If it starts with a verb that’s often used in questions or instructions
    if doc[0].pos_ == "VERB" and doc[0].lemma_.lower() in task_verbs:
        return "Question: " + line

    # --- DEFINITION ---
    if re.search(r'\b(is|are|was|were)\s+(defined as|known as|referred to as|called|termed|means)\b', line_lower):
        return "Definition: " + line
    if re.search(r'\bdefinition of\b|\brefers to\b|\bdenotes\b', line_lower):
        return "Definition: " + line

    # --- FORMULA ---
    formula_symbols = ['=', '≠', '≈', '≡', '∫', '∑', '∏', '∂', '∇', 'Δ', 'δ',
                       'sin(', 'cos(', 'tan(', 'log(', 'ln(', 'exp(', 'sqrt(',
                       'α', 'β', 'θ', 'λ', 'μ', 'π', '±', '÷', '∞', '∈', '∉',
                       '⊂', '⊆', '∩', '→', '←', '↔']
    if any(sym in line for sym in formula_symbols) or re.match(r'^[A-Za-z0-9\s]+\s*=\s*.*$', line):
        return "Formula: " + line

    # --- THEOREM ---
    if re.search(r'\b(theorem|lemma|corollary|proposition|proof|qed|hence proved|thus proved)\b', line_lower):
        return "Theorem: " + line

    # --- EXAMPLE ---
    if re.search(r'\b(for example|e\.g\.|example:|consider|suppose|let us|case study|illustration|such as|to illustrate|to demonstrate)\b', line_lower):
        return "Example: " + line

    # --- LIST ITEM ---
    if re.match(r'^\s*(•|·|▪|▫|◦|‣|⁃|\d+[\.\)]|[a-zA-Z][\.\)])\s+', line):
        return "List Item: " + line

    return line  # Default return original line


def classify_line(line):
    line_lower = line.lower()

    # Define keyword patterns with word boundaries
    question_patterns = [
        r'\bwhat is\b', r'\bhow to\b', r'\bwhy does\b', r'\bwhen is\b', r'\bwhere is\b',
        r'\bwhich of\b', r'\bfind the\b', r'\bcalculate\b', r'\bdetermine\b', r'\bsolve\b',
        r'\bprove that\b', r'\bshow that\b', r'\bexplain\b', r'\bdiscuss\b', r'\banalyze\b',
        r'\bcompare\b', r'\bcontrast\b', r'\bdescribe\b'
    ]

    definition_patterns = [
        r'\bis defined as\b', r'\bis called\b', r'\brefers to\b', r'\bmeans that\b',
        r'\bis the process\b', r'\bis a method\b', r'\bdefinition[: ]', r'\bdefinition of\b',
        r'\bthe term\b', r'\bthe concept\b', r'\bthe process of\b', r'\bthe method of\b',
        r'\bdefined as\b', r'\bcalled as\b', r'\breferred to\b', r'\bdenotes\b',
        r'\bis coined\b', r'\bis termed\b'
    ]

    formula_symbols = [
        '=', '≠', '≈', '≡', '∫', '∑', '∏', '∂', '∇', 'Δ', 'δ',
        'sin(', 'cos(', 'tan(', 'log(', 'ln(', 'exp(', 'sqrt(',
        'α', 'β', 'θ', 'λ', 'μ', 'π', '±', '÷', '∞', '∈', '∉', '⊂', '⊆', '∩', '→', '←', '↔'
    ]

    theorem_patterns = [
        r'\btheorem\b', r'\bproposition\b', r'\blemma\b', r'\bcorollary\b',
        r'\bproof:\b', r'\bqed\b', r'\bthus proved\b', r'\bhence proved\b'
    ]

    example_patterns = [
        r'\bfor example\b', r'\bexample:\b', r'\be\.g\.\b', r'\bconsider\b', r'\bsuppose\b',
        r'\blet us\b', r'\binstance\b', r'\bcase study\b', r'\billustration\b',
        r'\bfor instance\b', r'\bsuch as\b', r'\blike\b', r'\bas an example\b',
        r'\bto illustrate\b', r'\bto demonstrate\b', r'\bto show\b', r'\bto explain\b'
    ]

    list_item_pattern = r'^\s*(•|·|▪|▫|◦|‣|⁃|\d+[\.\)]|[a-zA-Z][\.\)])\s+'

    # Check for classification using regex
    if any(re.search(p, line_lower) for p in question_patterns) or line.strip().endswith('?'):
        return "Question: " + line

    if any(re.search(p, line_lower) for p in definition_patterns):
        return "Definition: " + line

    if any(sym in line for sym in formula_symbols) and len(re.findall(r'[a-zA-Z0-9]', line)) > 2:
        return "Formula: " + line

    if any(re.search(p, line_lower) for p in theorem_patterns):
        return "Theorem: " + line

    if any(re.search(p, line_lower) for p in example_patterns):
        return "Example: " + line

    if re.match(list_item_pattern, line):
        return "List Item: " + line

    return line  # return original line if no classification matches
    
    
def extract_text_from_pdf(doc_path):
        sentences_all = []
    
        with pdfplumber.open(doc_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() 
                
                if text:
                    lines = text.split("\n")
                    # Clean and filter lines
                    clean_lines = []
                
                    for line in lines:
                        line = line.strip()
                    
                        if not line or len(line) < 5:
                            continue  # skip short lines
                        
                        classified_line = classify_line_spacy(line)
                        
                        if classified_line.startswith(("Question:", "Definition:", "Formula:", "Theorem:", "Example:", "List Item:")):
                            clean_lines.append(classified_line)
                            continue
                        
                        # Remove known noise patterns
                        if re.match(r"^[-–—•●]?\s*\d+[.)]?$", line):  # items like '1.', 'b)', '2)'
                            continue
                        
                        if re.search(r"(table\s+\d+|exercise\s+\d+|figure\s+\d+|fill the blanks|^\(\w+\)$|^\-+\s*\d+\s*\-+)", line.lower()):
                            continue
                        
                        # Skip headers/footers with specific patterns
                        if re.search(r"(^ENVE\s+\d+|^\-\s*\d+\s*\-|page\s+\d+)", line, re.IGNORECASE):
                            continue
                        
                        if re.fullmatch(r"[a-zA-Z]\.?", line.strip()):
                            continue

                        # Skip lines that are mostly symbols
                        if len(re.sub(r'[^\w\s]', '', line)) < len(line) * 0.5:
                            continue
                        
                        if line.strip() in ['a.', 'b.', 'c.', 'd.', 'e.', 'f.', 'g.', 'h.', 'i.', 'j.']:
                            continue
                        
                        if line.strip() in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']:
                            continue
                        
                        if any(x in line.lower() for x in ["chapter", "table of contents", "page", "figure", "university", "author", "copyright"]):
                            continue
                        
                        clean_lines.append(line)
                
                    if clean_lines: 
                        page_text = " ".join(clean_lines)
                        sentences1 = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
                        sentences_all.extend(sentences1)
        return sentences_all
    
    
def group_sentences(file_path, output_prefix="output"):
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    custom_hdbscan = HDBSCAN(min_cluster_size=4, min_samples=2,metric='euclidean',cluster_selection_method='eom')
    umap_model = UMAP(n_neighbors=10, n_components=5, min_dist=0.0, metric='cosine',random_state=42)
    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=custom_hdbscan
    )

    note = extract_text_from_pdf(file_path)
    #print(note)

    note_text = " ".join(note)

    sentences_raw = preprocessing.TextPreprocessor.sentence_tokenize(note_text)
    #sentences_raw = [preprocessing.TextPreprocessor.stopwords_removal(sent) for sent in sentences_raw]
    sentences = [preprocessing.TextPreprocessor.preprocess_text(sent) for sent in sentences_raw]
#    sentences = [sent for sent in sentences if len(sent.split()) > 3]


    topics, prob = model.fit_transform(sentences)


    # Step 6: Group sentences by topic
    grouped = defaultdict(list)
    for sent, topic in zip(sentences,topics):
            grouped[topic].append(sent)

    # Remove exact duplicates or near-duplicates
    for topic, sents in grouped.items():
        grouped[topic] = list(dict.fromkeys(sents))  # Removes duplicates while keeping order
        
    #remove empty topics 
    grouped = {k: v for k, v in grouped.items() if v}  # Remove empty topics
    grouped = {k: v for k, v in grouped.items() if len(v) >= 3 and all(len(sent.split()) > 3 for sent in v)}

    
    #remove topic with id -1 (noise)
    if -1 in grouped:
        del grouped[-1]
        
    #create topic labels:
    topic_labels = {}
    for topic_id in grouped.keys():
        words = model.get_topic(topic_id)
        if words:
            filtered= [word for word, _ in words if word.lower() not in ENGLISH_STOP_WORDS]
            filtered = [w for w in filtered if len(w) > 2 and w.isalpha()]
            label = ", ".join(filtered[:5]) if filtered else "No Label" # Top 5 keywords
            topic_labels[topic_id] = label
        else:
            topic_labels[topic_id] = "No Label"

    return grouped, topic_labels

    ##saving to json file
    # with open(f"{output_prefix}_clustered.json", "w", encoding="utf-8") as f:
    #     json.dump(grouped, f, ensure_ascii=False, indent=4)

    # with open(f"{output_prefix}_topic_labels.json", "w", encoding="utf-8") as f:
    #     json.dump(topic_labels, f, ensure_ascii=False, indent=4)
            
    #store in pdf file:
    # pdf= FPDF()
    # pdf.set_auto_page_break(auto=True, margin=15)
    # pdf.add_page()
    # pdf.add_font('TiemposTextRegular','','fonts/TiemposTextRegular.ttf',uni=True)
    # pdf.set_font("TiemposTextRegular", size=12)
    # for topic_id, sents in grouped.items():
    #     label = topic_labels.get(topic_id, f"Topic {topic_id}")
            
    #     if topic_id == -1:
    #         continue
            
    #     pdf.set_font("TiemposTextRegular", size=14)
    #     pdf.multi_cell(0, 10, f"Topic {topic_id}: {label} \n")
            
    #     pdf.set_font("TiemposTextRegular", size=12)
    #     for sent in sents:
    #         pdf.multi_cell(0, 8, f"- {sent}")
    #     pdf.ln(5)

    # pdf.output(f"{output_prefix}_{file_path}.pdf") 
        