import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


import textwrap
from bertopic import BERTopic
import preprocessing
from collections import defaultdict,Counter
import re
import json
import fitz 
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


from fpdf import FPDF
from hdbscan import HDBSCAN
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
import globals


def break_long_words(text, max_word_length=100):
    words = text.split()
    new_words = []
    for word in words:
        if len(word) > max_word_length:
            new_words.extend(textwrap.wrap(word, max_word_length))
        else:
            new_words.append(word)
    return ' '.join(new_words)

def clean_text(text):
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII
    text = re.sub(r'\s+', ' ', text).strip()    # remove excess whitespace
    return text

def preprocess_text(text):
    text = clean_text(text)
    text = break_long_words(text)
    return text

# def remove_header_footer_from_pdf(doc_path, header=True, footer=True):
#     doc = fitz.open(doc_path)
#     globals.count += 1

#     for page in doc:
#         rect = page.rect
#         height = rect.y1  # Page height in points

#         # Initialize crop values
#         top, bottom = 0, 0

#         # Match page height and decide crop margins
#         if height == 540:  # PPT
#             if header: top = 20
#             if footer: bottom = 20
#         elif height == 792:  # US Letter
#             if header: top = 60
#             if footer: bottom = 75
#         elif height == 842:  # A4
#             if header: top = 60
#             if footer: bottom = 80
#         else:
#             print(f"Unknown page height: {height}, skipping crop.")

#         # Apply crop (set new visible area)
#         header_area = fitz.Rect(rect.x0,rect.y0+top,rect.x1,rect.y1)
#         footer_area = fitz.Rect(rect.x0,rect.y0,rect.x1,rect.y1-bottom)

#         #page.add_redact_annot(footer_area, fill=(1, 1, 1))  # white fill
#         #page.add_redact_annot(header_area, fill=(1,1,1)) #white fill header
#         #page.apply_redactions()
#         page.set_cropbox(fitz.Rect(rect.x0, rect.y0 + top, rect.x1, rect.y1 - bottom))

#     # Save the cleaned file
#     out_path = f"no_header_footer_{globals.count}.pdf"
#     doc.save(out_path)
#     return out_path

def auto_detect_and_remove_headers_footers(doc_path):
    """
    Automatically detects if a PDF has headers/footers and removes them.
    No need to specify if headers/footers exist - the function figures it out!
    
    Args:
        doc_path: Path to the PDF file
    
    Returns:
        Path to the cleaned PDF file
    """
    
    # Step 1: Open the document
    doc = fitz.open(doc_path)
    globals.count += 1
    print(f"🔍 Auto-analyzing document: {doc_path} ({len(doc)} pages)")
    
    # Skip processing if document is too short (less than 3 pages)
    if len(doc) < 3:
        print("Document too short for header/footer detection. Skipping cleanup.")
        # Just save with a new name and return
        out_path = f"unchanged_{globals.count}.pdf"
        doc.save(out_path)
        doc.close()
        return out_path
    
    # Step 2: Collect potential header/footer text from all pages
    header_candidates = []
    footer_candidates = []
    
    print("Phase 1: Scanning all pages for repeating patterns...")
    
    for page_num, page in enumerate(doc):
        rect = page.rect
        page_height = rect.height
        page_width = rect.width
        
        # Look in header area (top 10% of page)
        header_height = page_height * 0.10
        header_area = fitz.Rect(0, 0, page_width, header_height)
        header_text = page.get_text(clip=header_area).strip()
        header_text = ' '.join(header_text.split())  # Clean whitespace
        
        # Look in footer area (bottom 10% of page)
        footer_height = page_height * 0.10
        footer_area = fitz.Rect(0, page_height - footer_height, page_width, page_height)
        footer_text = page.get_text(clip=footer_area).strip()
        footer_text = ' '.join(footer_text.split())  # Clean whitespace
        
        # Only keep text that's not too short and not too long
        if header_text and 4 <= len(header_text) <= 200:
            header_candidates.append(header_text)
        
        if footer_text and 4 <= len(footer_text) <= 200:
            footer_candidates.append(footer_text)
    
    # Step 3: Analyze repetition patterns to detect real headers/footers
    print("Phase 2: Analyzing repetition patterns...")
    
    header_counter = Counter(header_candidates)
    footer_counter = Counter(footer_candidates)
    
    # Calculate dynamic thresholds based on document length
    total_pages = len(doc)
    
    # For headers/footers to be "real", they should appear on at least:
    # - 30% of pages (for long documents)
    # - At least 3 pages (for short documents) 
    # - At least 2 pages (minimum)
    min_repetitions = max(2, min(3, int(total_pages * 0.3)))
    
    print(f"   Document has {total_pages} pages")
    print(f"   Text must appear on at least {min_repetitions} pages to be considered header/footer")
    
    # Find repeating headers
    detected_headers = []
    for text, count in header_counter.items():
        repetition_percentage = (count / total_pages) * 100
        if count >= min_repetitions:
            detected_headers.append(text)
            print(f"   ✅ HEADER detected: '{text[:60]}...' (appears on {count}/{total_pages} pages, {repetition_percentage:.1f}%)")
    
    # Find repeating footers  
    detected_footers = []
    for text, count in footer_counter.items():
        repetition_percentage = (count / total_pages) * 100
        if count >= min_repetitions:
            detected_footers.append(text)
            print(f"   ✅ FOOTER detected: '{text[:60]}...' (appears on {count}/{total_pages} pages, {repetition_percentage:.1f}%)")
    
    # Step 4: Report what we found
    has_headers = len(detected_headers) > 0
    has_footers = len(detected_footers) > 0
    
    print(f"\n📊 Detection Results:")
    print(f"   Headers found: {'YES' if has_headers else 'NO'} ({len(detected_headers)} unique)")
    print(f"   Footers found: {'YES' if has_footers else 'NO'} ({len(detected_footers)} unique)")
    
    # If no headers or footers detected, return original file
    if not has_headers and not has_footers:
        print(" No headers or footers detected. Document is already clean!")
        out_path = f"clean_{globals.count}.pdf"
        doc.save(out_path)
        doc.close()
        return out_path
    
    # Step 5: Remove detected headers and footers
    print(f"\nPhase 3: Removing detected headers and footers...")
    
    pages_modified = 0
    
    for page_num, page in enumerate(doc):
        page_modified = False
        rect = page.rect
        page_height = rect.height
        page_width = rect.width
        
        # Remove headers if we detected any
        if has_headers:
            header_height = page_height * 0.10
            header_area = fitz.Rect(0, 0, page_width, header_height)
            current_header = ' '.join(page.get_text(clip=header_area).split())
            
            if current_header in detected_headers:
                print(f"   Page {page_num + 1}: Removing header")
                page.add_redact_annot(header_area, fill=(1, 1, 1))
                page_modified = True
        
        # Remove footers if we detected any
        if has_footers:
            footer_height = page_height * 0.10
            footer_area = fitz.Rect(0, page_height - footer_height, page_width, page_height)
            current_footer = ' '.join(page.get_text(clip=footer_area).split())
            
            if current_footer in detected_footers:
                print(f"   Page {page_num + 1}: Removing footer")
                page.add_redact_annot(footer_area, fill=(1, 1, 1))
                page_modified = True
        
        if page_modified:
            page.apply_redactions()
            pages_modified += 1
    
    # Step 6: Save the cleaned document
    out_path = f"auto_cleaned_{globals.count}.pdf"
    doc.save(out_path)
    doc.close()
    
    print(f"\n✅ Auto-processing complete!")
    print(f"   - Modified {pages_modified} out of {total_pages} pages")
    print(f"   - Saved as: {out_path}")
    
    return out_path



    
def extract_text_from_pdf(doc_path):
        cleaned_path = auto_detect_and_remove_headers_footers(doc_path)
        sentences_all = []
    
        pdf = fitz.open(cleaned_path)
        for page in pdf:
            text = page.get_text() 
            if text:
                lines = text.split("\n")
                # Clean and filter lines
                clean_lines = []
            
                for line in lines:
                    line = line.strip()
                
                    if not line or len(line) < 5:
                        continue  # skip short lines
                    
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
    umap_model = UMAP(n_neighbors=6, n_components=5, min_dist=0.0, metric='cosine',random_state=42)
    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=custom_hdbscan
    )

    note = extract_text_from_pdf(file_path,)
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

    ##saving to json file
    with open(f"{output_prefix}_clustered.json", "w", encoding="utf-8") as f:
        json.dump(grouped, f, ensure_ascii=False, indent=4)

    with open(f"{output_prefix}_topic_labels.json", "w", encoding="utf-8") as f:
        json.dump(topic_labels, f, ensure_ascii=False, indent=4)
            
    #store in pdf file:
    pdf= FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('TiemposTextRegular','','fonts/TiemposTextRegular.ttf',uni=True)
    pdf.set_font("TiemposTextRegular", size=12)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    for topic_id, sents in grouped.items():
        label = topic_labels.get(topic_id, f"Topic {topic_id}")
            
        if topic_id == -1:
            continue
        
        
        pdf.set_font("TiemposTextRegular", size=14)
        pdf.multi_cell(0, 10, f"Topic {topic_id}: {label} \n")
            
        pdf.set_font("TiemposTextRegular", size=12)
        for sent in sents:
            cleaned = preprocess_text(sent)
            pdf.multi_cell(0, 8, f"- {cleaned}")
        pdf.ln(5)

    pdf.output(f"{output_prefix}_{file_path}.pdf") 
        
    return grouped, topic_labels