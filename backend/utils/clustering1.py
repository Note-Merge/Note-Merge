# import pytesseract
# import os
# import cv2
# from bertopic import BERTopic
# import preprocessing
# from collections import defaultdict
# import re
# import json
# from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
# import fitz
# import numpy as np
# from PIL import Image
# from fpdf import FPDF
# from hdbscan import HDBSCAN
# from bertopic import BERTopic
# from umap import UMAP
# from sentence_transformers import SentenceTransformer


# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# def preprocess_image_for_ocr(img_np):
#     try:
#         # Convert to grayscale
#         gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        
#         # Apply denoising
#         denoised = cv2.fastNlMeansDenoising(gray)
        
#         #apply thresholding 
#         # Thresholding to get binary image
#         _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
#         #morphological operations to remove noise
#         kernel = np.ones((1,1),np.uint8)
#         cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE,kernel)
#         return cleaned
#     except Exception as e:
#         print(f"Error in preprocessing image: {e}")
#         return cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)


# #classify lines based on their content
# def classify_line(line):
#     line_lower = line.lower()
    
#     if any(p in line_lower for p in [
#         'what is', 'how to', 'why does', 'when is', 'where is',
#         'which of', 'find the', 'calculate', 'determine', 'solve',
#         'prove that', 'show that', 'explain', 'discuss', 'analyze',
#         'compare', 'contrast', 'evaluate', 'describe'
#     ]) or line.strip().endswith('?'):
#         return "Question: " + line
    
#     elif any(p in line_lower for p in [
#         'is defined as', 'is called', 'refers to', 'means that',
#         'is the process', 'is a method', 'definition:', 'definition of',
#         'the term', 'the concept', 'the process of', 'the method of','the way to',
#         'defined as', 'called as', 'referred to','denotes','is coined','is termed'
#     ]):
#         return "Definition: " + line
    
#     elif any(p in line for p in [
#         '=', '≠', '≈', '≡', '∫', '∑', '∏', '∂', '∇', 'Δ', 'δ',
#         'sin(', 'cos(', 'tan(', 'log(', 'ln(', 'exp(', 'sqrt(',
#         'α', 'β', 'θ', 'λ', 'μ', 'π', '±', '÷',
#         '∞', '∈', '∉', '⊂', '⊆', '∩', '→', '←', '↔'
#     ]) and len(re.findall(r'[a-zA-Z0-9]', line)) > 2:
#         return "Formula: " + line
    
#     # Theorem/proposition detection
#     elif any(p in line_lower for p in [
#         'theorem', 'proposition', 'lemma', 'corollary',
#         'proof:', 'qed', 'thus proved', 'hence proved'
#     ]):
#         return "Theorem: " + line
    
#     elif any(p in line_lower for p in [
#          'for example', 'example:', 'e.g.', 'consider', 'suppose',
#         'let us', 'instance', 'case study', 'illustration',
#         'for instance', 'such as', 'like', 'as an example', 'to illustrate', 'to demonstrate', 'to show', 'to explain'
#     ]):
#         return "Example: " + line
    
#     elif re.match(r'^\s*[•·▪▫◦‣⁃]\s+', line) or re.match(r'^\s*\d+[\.\)]\s+', line):
#         return "List Item: " + line
    
#     return line


# def is_noise(line):
#     line = line.strip()
    
#     # Check if the line is empty or too short
#     if not line or len(line) < 3:
#         return True
    
#     noise_patterns = [
#         # Academic document structure
#         r'^(abstract|keywords?|introduction|conclusion|references|bibliography)$',
#         r'^(chapter|section|subsection|appendix)\s+\d+',
#         r'^(part|volume|book)\s+[ivxlc\d]+',
        
#         # Institutional info
#         r'(university|college|institute|department|faculty)',
#         r'(copyright|©|all rights reserved)',
#         r'^(author|title|date|publisher):',
#         r'isbn\s*:?\s*\d',
        
#         r'enve\s*\d{3}',  # Course codes like ENVE 101
#         r'chapter\s+[ivxlc\d]+',  # Roman or numeric chapter headers
#         r'-\s*\d+\s*-',  # Dashes with numbers in between
        
#         # Navigation elements
#         r'^(table of contents|contents|index)$',
#         r'^(next|previous|back|forward|home|page)$',
#         r'^(see also|related|further reading)',
        
#         # Figures and tables
#         r'^(figure|fig|table|tbl|chart|graph)\s+\d+',
#         r'^(source:|caption:|note:)',
        
#         # Exercise/problem markers
#         r'^(exercise|problem|question|quiz|test)\s+\d+$',
#         r'^(homework|assignment)\s+\d+',
        
#         # List markers and formatting
#         r'^[a-j]\.?$',  # Single letter list items
#         r'^[ivxlc]+\.?$',  # Roman numerals
#         r'^[-–—•●○◦▪▫]\s*$',  # Bullet points alone
#         r'^\d+\.?\s*$',  # Numbers alone
        
#         # Formatting artifacts
#         r'^\s*[\_\-\=\*\#\~]{3,}\s*$',  # Horizontal lines
#         r'^\s*\.{3,}\s*$',  # Ellipsis
#         r'^\s*\|+\s*$',  # Vertical bars
#         r'^\s*\++\s*$',  # Plus signs
        
#         # Page elements
#         r'page\s+\d+',
#         r'^\d+$',  # Page numbers alone
#         r'^(header|footer|watermark)',
        
#         # Common OCR artifacts
#         r'^[^\w\s]{3,}$',  # Strings of special characters
#         r'[□■▢▣▤▥▦▧▨▩▪▫▬▭▮▯]{2,}',  # Box characters
        
#         # Web/digital artifacts
#         r'^(click here|download|print|save|share)$',
#         r'www\.|http[s]?://',
#         r'@\w+\.(com|org|edu|net)',
        
#         # Timestamps/dates in isolation
#         r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$',
#         r'^\d{1,2}:\d{2}(\s*(am|pm))?$',
#     ]   
#     for pattern in noise_patterns:
#         if re.search(pattern, line.strip(), re.IGNORECASE):
#             return True
#     return False

    
# def extract_text_from_pdf(doc_path,ocr_enabled= True):
#         doc= fitz.open(doc_path)
#         sentences_all = []
        
#          # Custom OCR configuration for better accuracy
#         ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\'-+=/\\ '
    
#         for page_num,page in enumerate(doc):
#             lines = []   
            
            
#             #extraction of text-based lines
#             text = page.get_text("text")
#             text_content_length = len(text.strip())
            
#             if text:
#                 for line in text.split("\n"):
#                     line = line.strip()
#                     line = re.sub(r'\bENVE\s*\d{3}[:\-]?', '', line)  # Remove 'ENVE 101:'
#                     line = re.sub(r'\bChapter\s+[IVXLC\d]+', '', line, flags=re.IGNORECASE)  # Remove 'Chapter I'
#                     line = re.sub(r'\b-\s*\d+\s*-', '', line)  # Remove '- 2 -' or '- 4 -'
#                     if len(line) >= 5 and not is_noise(line):
#                     # Create a normalized version for duplicate detection
#                      normalized_line = re.sub(r'\s+', ' ', line.lower().strip())
                    
#                     if normalized_line not in seen_lines:
#                         seen_lines.add(normalized_line)
#                         tagged_line = classify_line(line)
#                         lines.append(tagged_line)
            
#             #OCR for images if enabled
#             if ocr_enabled and (text_content_length < 100 or len(lines) < 5):
#                 try:
#                     print(f"Applying OCR to page {page_num + 1} (text content: {text_content_length} chars)")
                
#                     # Get pixmap with high DPI for better OCR
#                     pix = page.get_pixmap(dpi=300)
#                     img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                     img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
#                     # ===== NEW: Apply image preprocessing =====
#                     processed_img = preprocess_image_for_ocr(img_np)
                    
#                     # ===== NEW: Use custom OCR configuration =====
#                     ocr_text = pytesseract.image_to_string(processed_img, config=ocr_config)
                    
#                     # ===== NEW: Track OCR success =====
#                     if ocr_text.strip():
#                         print(f"OCR extracted {len(ocr_text.strip())} characters from page {page_num + 1}")
#                     else:
#                         print(f"OCR returned no text for page {page_num + 1}")
                    
#                     for line in ocr_text.split("\n"):
#                         line = line.strip()
#                         if len(line) >= 5 and not is_noise(line):
#                             tagged_line = classify_line(line)
#                             lines.append(tagged_line)
                            
#                 except Exception as e:
#                     print(f"OCR failed for page {page_num + 1}: {e}")
#                     # Continue processing without OCR for this page
        
#             elif ocr_enabled:
#                 print(f"Skipping OCR for page {page_num + 1} (sufficient text found: {text_content_length} chars)")
            
#             #Preprocessing 
#             page_text = " ".join(lines)
#             sentences = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
#             sentences_all.extend(sentences)
            
#         return sentences_all
    

# def group_sentences(file_path, output_prefix="output", ocr_enabled=True):
#     embedding_model = SentenceTransformer('all-mpnet-base-v2')
#     custom_hdbscan = HDBSCAN(min_cluster_size=4, min_samples=2,metric='euclidean',cluster_selection_method='eom')
#     umap_model = UMAP(n_neighbors=8, n_components=4, min_dist=0.0, metric='cosine',random_state=42)
    
#     model = BERTopic(
#         embedding_model=embedding_model,
#         umap_model=umap_model,
#         hdbscan_model=custom_hdbscan
#     )

#     sentences = extract_text_from_pdf(file_path,ocr_enabled=ocr_enabled)
#     preprocessed = [preprocessing.TextPreprocessor.preprocess_text(sent) for sent in sentences]

#     topics, probs = model.fit_transform(preprocessed)


#     # Step 6: Group sentences by topic
#     grouped = defaultdict(list)
#     for sent, topic in zip(sentences,topics):
#             if topic != -1:
#                 grouped[topic].append(sent)

#     # Remove exact duplicates or near-duplicates
#     for topic, sents in grouped.items():
#         grouped[topic] = list(dict.fromkeys(sents))  # Removes duplicates while keeping order
        
#     #remove empty topics
#     grouped = {
#         k: list(dict.fromkeys(v))
#         for k, v in grouped.items()
#         if len(v) >= 3 and all(len(s.split()) > 3 for s in v)
#     }

    
#     #remove topic with id -1 (noise)
#     if -1 in grouped:
#         del grouped[-1]
        
#     #create topic labels:
#     topic_labels = {}
#     for topic_id in grouped:
#         words = model.get_topic(topic_id)
#         if words:
#             filtered= [word for word, _ in words if word.lower() not in ENGLISH_STOP_WORDS]
#             filtered = [w for w in filtered if len(w) > 2 and w.isalpha()]
#             label = ", ".join(filtered[:5]) if filtered else "No Label" # Top 5 keywords
#             topic_labels[topic_id] = label
#         else:
#             topic_labels[topic_id] = "No Label"

#     ##saving to json file
#     with open(f"{output_prefix}_clustered.json", "w", encoding="utf-8") as f:
#         json.dump(grouped, f, ensure_ascii=False, indent=4)

#     with open(f"{output_prefix}_topic_labels.json", "w", encoding="utf-8") as f:
#         json.dump(topic_labels, f, ensure_ascii=False, indent=4)
            
#     return grouped, topic_labels
    
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
        
        
        
import pytesseract
import os
import cv2
from bertopic import BERTopic
import preprocessing
from collections import defaultdict
import re
import json
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import fitz
import numpy as np
from PIL import Image
from fpdf import FPDF
from hdbscan import HDBSCAN
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image_for_ocr(img_np):
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply thresholding 
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to remove noise
        kernel = np.ones((1,1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return cleaned
    except Exception as e:
        print(f"Error in preprocessing image: {e}")
        return cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

def classify_line(line):
    line_lower = line.lower()
    
    if any(p in line_lower for p in [
        'what is', 'how to', 'why does', 'when is', 'where is',
        'which of', 'find the', 'calculate', 'determine', 'solve',
        'prove that', 'show that', 'explain', 'discuss', 'analyze',
        'compare', 'contrast', 'evaluate', 'describe'
    ]) or line.strip().endswith('?'):
        return "Question: " + line
    
    elif any(p in line_lower for p in [
        'is defined as', 'is called', 'refers to', 'means that',
        'is the process', 'is a method', 'definition:', 'definition of',
        'the term', 'the concept', 'the process of', 'the method of','the way to',
        'defined as', 'called as', 'referred to','denotes','is coined','is termed'
    ]):
        return "Definition: " + line
    
    elif any(p in line for p in [
        '=', '≠', '≈', '≡', '∫', '∑', '∏', '∂', '∇', 'Δ', 'δ',
        'sin(', 'cos(', 'tan(', 'log(', 'ln(', 'exp(', 'sqrt(',
        'α', 'β', 'θ', 'λ', 'μ', 'π', '±', '÷',
        '∞', '∈', '∉', '⊂', '⊆', '∩', '→', '←', '↔'
    ]) and len(re.findall(r'[a-zA-Z0-9]', line)) > 2:
        return "Formula: " + line
    
    elif any(p in line_lower for p in [
        'theorem', 'proposition', 'lemma', 'corollary',
        'proof:', 'qed', 'thus proved', 'hence proved'
    ]):
        return "Theorem: " + line
    
    elif any(p in line_lower for p in [
         'for example', 'example:', 'e.g.', 'consider', 'suppose',
        'let us', 'instance', 'case study', 'illustration',
        'for instance', 'such as', 'like', 'as an example', 'to illustrate', 'to demonstrate', 'to show', 'to explain'
    ]):
        return "Example: " + line
    
    elif re.match(r'^\s*[•·▪▫◦‣⁃]\s+', line) or re.match(r'^\s*\d+[\.\)]\s+', line):
        return "List Item: " + line
    
    return line

def is_noise(line):
    line = line.strip()
    if not line or len(line) < 3:
        return True
    
    noise_patterns = [
        # Academic document structure
        r'^(abstract|keywords?|introduction|conclusion|references|bibliography)$',
        r'^(chapter|section|subsection|appendix)\s+\d+',
        r'^(part|volume|book)\s+[ivxlc\d]+',
        
        # Headers/footers that repeat
        r'^introduction\s+to\s+(chatgpt|environmental\s+engineering)',
        r'introduction\s+to\s+environmental\s+engineering',
        
        # Institutional info
        r'(university|college|institute|department|faculty)',
        r'(copyright|©|all rights reserved)',
        r'^(author|title|date|publisher):',
        r'isbn\s*:?\s*\d',
        
        r'enve\s*\d{3}',
        r'chapter\s+[ivxlc\d]+',
        r'-\s*\d+\s*-',
        
        # Navigation elements
        r'^(table of contents|contents|index)$',
        r'^(next|previous|back|forward|home|page)$',
        r'^(see also|related|further reading)',
        
        # Figures and tables
        r'^(figure|fig|table|tbl|chart|graph)\s+\d+',
        r'^(source:|caption:|note:)',
        
        # Exercise/problem markers
        r'^(exercise|problem|question|quiz|test)\s+\d+$',
        r'^(homework|assignment)\s+\d+',
        
        # List markers and formatting
        r'^[a-j]\.?$',
        r'^[ivxlc]+\.?$',
        r'^[-–—•●○◦▪▫]\s*$',
        r'^\d+\.?\s*$',
        
        # Formatting artifacts
        r'^\s*[\_\-\=\*\#\~]{3,}\s*$',
        r'^\s*\.{3,}\s*$',
        r'^\s*\|+\s*$',
        r'^\s*\++\s*$',
        
        # Page elements
        r'page\s+\d+',
        r'^\d+$',
        r'^(header|footer|watermark)',
        
        # Common OCR artifacts
        r'^[^\w\s]{3,}$',
        r'[□■▢▣▤▥▦▧▨▩▪▫▬▭▮▯]{2,}',
        
        # Web/digital artifacts
        r'^(click here|download|print|save|share)$',
        r'www\.|http[s]?://',
        r'@\w+\.(com|org|edu|net)',
        
        # Timestamps/dates in isolation
        r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$',
        r'^\d{1,2}:\d{2}(\s*(am|pm))?$',
    ]   
    
    for pattern in noise_patterns:
        if re.search(pattern, line.strip(), re.IGNORECASE):
            return True
    return False

def extract_text_from_pdf(doc_path, ocr_enabled=True):
    doc = fitz.open(doc_path)
    sentences_all = []
    seen_lines = set()  # Track duplicate lines across pages
    
    # Custom OCR configuration for better accuracy
    ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\'-+=/\\ '

    for page_num, page in enumerate(doc):
        lines = []
        
        # Extract text-based content
        text = page.get_text("text")
        text_content_length = len(text.strip())
        
        if text:
            for line in text.split("\n"):
                line = line.strip()
                # Clean up common artifacts
                line = re.sub(r'\bENVE\s*\d{3}[:\-]?', '', line)
                line = re.sub(r'\bChapter\s+[IVXLC\d]+', '', line, flags=re.IGNORECASE)
                line = re.sub(r'\b-\s*\d+\s*-', '', line)
                
                # Skip if line is too short, is noise, or already seen
                if len(line) >= 5 and not is_noise(line):
                    # Create a normalized version for duplicate detection
                    normalized_line = re.sub(r'\s+', ' ', line.lower().strip())
                    
                    if normalized_line not in seen_lines:
                        seen_lines.add(normalized_line)
                        tagged_line = classify_line(line)
                        lines.append(tagged_line)
        
        # Apply OCR if needed and enabled
        if ocr_enabled and (text_content_length < 100 or len(lines) < 5):
            try:
                print(f"Applying OCR to page {page_num + 1} (text content: {text_content_length} chars)")
            
                # Get pixmap with high DPI for better OCR
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # Apply image preprocessing
                processed_img = preprocess_image_for_ocr(img_np)
                
                # Use custom OCR configuration
                ocr_text = pytesseract.image_to_string(processed_img, config=ocr_config)
                
                if ocr_text.strip():
                    print(f"OCR extracted {len(ocr_text.strip())} characters from page {page_num + 1}")
                else:
                    print(f"OCR returned no text for page {page_num + 1}")
                
                for line in ocr_text.split("\n"):
                    line = line.strip()
                    if len(line) >= 5 and not is_noise(line):
                        # Create normalized version for duplicate detection
                        normalized_line = re.sub(r'\s+', ' ', line.lower().strip())
                        
                        if normalized_line not in seen_lines:
                            seen_lines.add(normalized_line)
                            tagged_line = classify_line(line)
                            lines.append(tagged_line)
                        
            except Exception as e:
                print(f"OCR failed for page {page_num + 1}: {e}")
        
        elif ocr_enabled:
            print(f"Skipping OCR for page {page_num + 1} (sufficient text found: {text_content_length} chars)")
        
        # Process page text
        if lines:  # Only process if we have lines
            page_text = " ".join(lines)
            sentences = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
            sentences_all.extend(sentences)
    
    doc.close()
    
    # Final deduplication of sentences
    unique_sentences = []
    seen_sentences = set()
    
    for sentence in sentences_all:
        normalized_sentence = re.sub(r'\s+', ' ', sentence.lower().strip())
        if normalized_sentence not in seen_sentences and len(normalized_sentence) > 10:
            seen_sentences.add(normalized_sentence)
            unique_sentences.append(sentence)
    
    print(f"Extracted {len(unique_sentences)} unique sentences from {len(sentences_all)} total sentences")
    return unique_sentences

def group_sentences(file_path, output_prefix="output", ocr_enabled=True):
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    custom_hdbscan = HDBSCAN(min_cluster_size=4, min_samples=2, metric='euclidean', cluster_selection_method='eom')
    umap_model = UMAP(n_neighbors=8, n_components=4, min_dist=0.0, metric='cosine', random_state=42)
    
    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=custom_hdbscan
    )

    sentences = extract_text_from_pdf(file_path, ocr_enabled=ocr_enabled)
    
    if not sentences:
        print("No sentences extracted from PDF")
        return {}, {}
    
    preprocessed = [preprocessing.TextPreprocessor.preprocess_text(sent) for sent in sentences]
    topics, probs = model.fit_transform(preprocessed)

    # Group sentences by topic
    grouped = defaultdict(list)
    for sent, topic in zip(sentences, topics):
        if topic != -1:
            grouped[topic].append(sent)

    # Remove exact duplicates within each topic
    for topic, sents in grouped.items():
        grouped[topic] = list(dict.fromkeys(sents))
        
    # Remove empty or small topics
    grouped = {
        k: list(dict.fromkeys(v))
        for k, v in grouped.items()
        if len(v) >= 3 and all(len(s.split()) > 3 for s in v)
    }

    # Remove noise topic
    if -1 in grouped:
        del grouped[-1]
        
    # Create topic labels
    topic_labels = {}
    for topic_id in grouped:
        words = model.get_topic(topic_id)
        if words:
            filtered = [word for word, _ in words if word.lower() not in ENGLISH_STOP_WORDS]
            filtered = [w for w in filtered if len(w) > 2 and w.isalpha()]
            label = ", ".join(filtered[:5]) if filtered else "No Label"
            topic_labels[topic_id] = label
        else:
            topic_labels[topic_id] = "No Label"

    # Save to JSON files
    with open(f"{output_prefix}_clustered.json", "w", encoding="utf-8") as f:
        json.dump(grouped, f, ensure_ascii=False, indent=4)

    with open(f"{output_prefix}_topic_labels.json", "w", encoding="utf-8") as f:
        json.dump(topic_labels, f, ensure_ascii=False, indent=4)
            
    return grouped, topic_labels