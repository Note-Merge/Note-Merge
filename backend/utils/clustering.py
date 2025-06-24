# import os
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# from bertopic import BERTopic
# import preprocessing
# import pdfplumber
# from collections import defaultdict
# import re
# import spacy
# import json
# import fitz 
# import camelot
# from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
# import fitz
# import io
# from PIL import Image


# from fpdf import FPDF
# from hdbscan import HDBSCAN
# from bertopic import BERTopic
# from umap import UMAP
# from sentence_transformers import SentenceTransformer

# import globals
# from remove_tables import remove_and_extract_tables, store_table_data


# def remove_header_footer_from_pdf(doc_path, header=True, footer=True):
#     try:
#     #########################################################################################
#         tables_data, new_path = remove_and_extract_tables(doc_path)
#         store_table_data(tables_data)
#     ########################################################################################
#         doc = fitz.open(new_path)
#         for page in doc:
#             rect = page.rect
#             height = rect.y1  # Page height in points

#             # Initialize crop values
#             top, bottom = 0, 0

#             # Match page height and decide crop margins
#             if height == 540:  # PPT
#                 if header: top = 20
#                 if footer: bottom = 20
#             elif height == 792:  # US Letter
#                 if header: top = 60
#                 if footer: bottom = 75
#             elif height == 842:  # A4
#                 if header: top = 60
#                 if footer: bottom = 80
#             else:
#                 print(f"Unknown page height: {height}, skipping crop.")


#             #page.add_redact_annot(footer_area, fill=(1, 1, 1))  # white fill
#             #page.add_redact_annot(header_area, fill=(1,1,1)) #white fill header
#             #page.apply_redactions()
#             page.set_cropbox(fitz.Rect(rect.x0, rect.y0 + top, rect.x1, rect.y1 - bottom))

#         # Save the cleaned file
#         out_path = f"no_header_footer_{globals.count}.pdf"
#         doc.save(out_path)
#     finally:
#         doc.close()
#         return out_path



    
# def extract_text_from_pdf(doc_path,contains_header,contains_footer):
#         new_path = remove_header_footer_from_pdf(doc_path,contains_header,contains_footer)
#         sentences_all = []
#         print(new_path)
    
#         pdf = fitz.open(new_path)
#         for page in pdf:
#             text = page.get_text() 
#             print(text)
#             if text:
#                 lines = text.split("\n")
#                 # Clean and filter lines
#                 clean_lines = []
            
#                 for line in lines:
#                     line = line.strip()
                
#                     if not line or len(line) < 5:
#                         continue  # skip short lines
                    
#                     # Remove known noise patterns
#                     if re.match(r"^[-–—•●]?\s*\d+[.)]?$", line):  # items like '1.', 'b)', '2)'
#                         continue
                    
#                     if re.search(r"(table\s+\d+|exercise\s+\d+|figure\s+\d+|fill the blanks|^\(\w+\)$|^\-+\s*\d+\s*\-+)", line.lower()):
#                         continue
                    
#                     # Skip headers/footers with specific patterns
#                     if re.search(r"(^ENVE\s+\d+|^\-\s*\d+\s*\-|page\s+\d+)", line, re.IGNORECASE):
#                         continue
                    
#                     if re.fullmatch(r"[a-zA-Z]\.?", line.strip()):
#                         continue

#                     # Skip lines that are mostly symbols
#                     if len(re.sub(r'[^\w\s]', '', line)) < len(line) * 0.5:
#                         continue
                    
#                     if line.strip() in ['a.', 'b.', 'c.', 'd.', 'e.', 'f.', 'g.', 'h.', 'i.', 'j.']:
#                         continue
                    
#                     if line.strip() in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']:
#                         continue
                    
#                     if any(x in line.lower() for x in ["chapter", "table of contents", "page", "figure", "university", "author", "copyright"]):
#                         continue
                    
#                     clean_lines.append(line)
            
#                 if clean_lines: 
#                     page_text = " ".join(clean_lines)
#                     sentences1 = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
#                     sentences_all.extend(sentences1)
#         pdf.close()             
#         return sentences_all
    
    
# def group_sentences(file_path,contains_header,contains_footer,output_prefix="output"):
#     embedding_model = SentenceTransformer('all-mpnet-base-v2')
#     custom_hdbscan = HDBSCAN(min_cluster_size=4, min_samples=2,metric='euclidean',cluster_selection_method='eom')
#     umap_model = UMAP(n_neighbors=6, n_components=5, min_dist=0.0, metric='cosine',random_state=42)
#     model = BERTopic(
#         embedding_model=embedding_model,
#         umap_model=umap_model,
#         hdbscan_model=custom_hdbscan
#     )

#     note = extract_text_from_pdf(file_path,contains_header,contains_footer)
#     #print(note)

#     note_text = " ".join(note)

#     sentences_raw = preprocessing.TextPreprocessor.sentence_tokenize(note_text)
#     #sentences_raw = [preprocessing.TextPreprocessor.stopwords_removal(sent) for sent in sentences_raw]
#     sentences = [preprocessing.TextPreprocessor.preprocess_text(sent) for sent in sentences_raw]
# #    sentences = [sent for sent in sentences if len(sent.split()) > 3]


#     topics, prob = model.fit_transform(sentences)


#     # Step 6: Group sentences by topic
#     grouped = defaultdict(list)
#     for sent, topic in zip(sentences,topics):
#             grouped[topic].append(sent)

#     # Remove exact duplicates or near-duplicates
#     for topic, sents in grouped.items():
#         grouped[topic] = list(dict.fromkeys(sents))  # Removes duplicates while keeping order
        
#     #remove empty topics 
#     grouped = {k: v for k, v in grouped.items() if v}  # Remove empty topics
#     grouped = {k: v for k, v in grouped.items() if len(v) >= 3 and all(len(sent.split()) > 3 for sent in v)}

    
#     #remove topic with id -1 (noise)
#     if -1 in grouped:
#         del grouped[-1]
        
#     #create topic labels:
#     topic_labels = {}
#     for topic_id in grouped.keys():
#         words = model.get_topic(topic_id)
#         if words:
#             filtered= [word for word, _ in words if word.lower() not in ENGLISH_STOP_WORDS]
#             filtered = [w for w in filtered if len(w) > 2 and w.isalpha()]
#             label = ", ".join(filtered[:5]) if filtered else "No Label" # Top 5 keywords
#             topic_labels[topic_id] = label
#         else:
#             topic_labels[topic_id] = "No Label"

#     return grouped, topic_labels

#     ##saving to json file
#     # with open(f"{output_prefix}_clustered.json", "w", encoding="utf-8") as f:
#     #     json.dump(grouped, f, ensure_ascii=False, indent=4)

#     # with open(f"{output_prefix}_topic_labels.json", "w", encoding="utf-8") as f:
#     #     json.dump(topic_labels, f, ensure_ascii=False, indent=4)
            
#     #store in pdf file:
#     # pdf= FPDF()
#     # pdf.set_auto_page_break(auto=True, margin=15)
#     # pdf.add_page()
#     # pdf.add_font('TiemposTextRegular','','fonts/TiemposTextRegular.ttf',uni=True)
#     # pdf.set_font("TiemposTextRegular", size=12)
#     # for topic_id, sents in grouped.items():
#     #     label = topic_labels.get(topic_id, f"Topic {topic_id}")
            
#     #     if topic_id == -1:
#     #         continue
            
#     #     pdf.set_font("TiemposTextRegular", size=14)
#     #     pdf.multi_cell(0, 10, f"Topic {topic_id}: {label} \n")
            
#     #     pdf.set_font("TiemposTextRegular", size=12)
#     #     for sent in sents:
#     #         pdf.multi_cell(0, 8, f"- {sent}")
#     #     pdf.ln(5)

#     # pdf.output(f"{output_prefix}_{file_path}.pdf") 
        
        
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'



from bertopic import BERTopic
import preprocessing
from collections import defaultdict
import re
import json
import fitz 
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


from fpdf import FPDF
from hdbscan import HDBSCAN
from bertopic import BERTopic
from umap import UMAP
from textwrap import wrap
from sentence_transformers import SentenceTransformer

import globals
from remove_tables import remove_and_extract_tables, store_table_data

max_line_len = 100

def remove_header_footer_from_pdf(doc_path, header=True, footer=True):
    doc = None
    out_path = f"no_header_footer_{globals.count}.pdf"
    
    try:
    #########################################################################################
        tables_data, new_path = remove_and_extract_tables(doc_path)
        store_table_data(tables_data)
    ########################################################################################
        doc = fitz.open(new_path)
        for page in doc:
            rect = page.rect
            height = rect.y1  # Page height in points

            # Initialize crop values
            top, bottom = 0, 0

            # Match page height and decide crop margins
            if height == 540:  # PPT
                if header: top = 20
                if footer: bottom = 20
            elif height == 792:  # US Letter
                if header: top = 60
                if footer: bottom = 75
            elif height == 842:  # A4
                if header: top = 60
                if footer: bottom = 80
            else:
                print(f"Unknown page height: {height}, skipping crop.")


            #page.add_redact_annot(footer_area, fill=(1, 1, 1))  # white fill
            #page.add_redact_annot(header_area, fill=(1,1,1)) #white fill header
            #page.apply_redactions()
            page.set_cropbox(fitz.Rect(rect.x0, rect.y0 + top, rect.x1, rect.y1 - bottom))

        # Save the cleaned file
        doc.save(out_path)
        return out_path
    
    except Exception as e:
        print(f"Error occurred while removing header/footer: {e}")
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception as e:
                print(f"Error occurred while closing the document: {e}")



    
def extract_text_from_pdf(doc_path,contains_header,contains_footer):
        new_path = remove_header_footer_from_pdf(doc_path,contains_header,contains_footer)
        sentences_all = []
        print(new_path)
    
        pdf = fitz.open(new_path)
        for page in pdf:
            text = page.get_text()
            # print(f"Raw text from page {page.number}: {repr(text[:200])}") 
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
        pdf.close()             
        return sentences_all
    
    
def group_sentences(file_path,contains_header,contains_footer,output_prefix="output"):
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    custom_hdbscan = HDBSCAN(min_cluster_size=4, min_samples=2,metric='euclidean',cluster_selection_method='eom')
    umap_model = UMAP(n_neighbors=8, n_components=4, min_dist=0.0, metric='cosine',random_state=42)
    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=custom_hdbscan
    )

    note = extract_text_from_pdf(file_path,contains_header,contains_footer)
    #print(note)
    note_text = " ".join(note)

    sentences_raw = preprocessing.TextPreprocessor.sentence_tokenize(note_text)
    #sentences_raw = [preprocessing.TextPreprocessor.stopwords_removal(sent) for sent in sentences_raw]
    sentences = [preprocessing.TextPreprocessor.preprocess_text(sent) for sent in sentences_raw]
    # sentences = [sent for sent in sentences if len(sent.split()) > 3]
    # sentences = [str(s).strip() for s in sentences if isinstance(s, str) and s.strip()]
    if not sentences:
        raise ValueError("No valid sentences extracted from PDF.")
    # print(f"SENTENCES : {sentences}")


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
    # pdf= FPDF()
    # pdf.set_auto_page_break(auto=True, margin=5)
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
    #         # 
    #         try:
    #             # Try breaking very long unbreakable words
    #             safe_sent = " ".join(wrap(sent, max_line_len, break_long_words=True, break_on_hyphens=False))
    #             pdf.multi_cell(0, 8, f"- {safe_sent}")
    #         except Exception as e:
    #             print(f"⚠️ Skipping a line due to FPDF error: {e}")
    #     pdf.ln(5) 
    # pdf.output(f"{output_prefix}_{file_path}.pdf") 
        
    return grouped, topic_labels