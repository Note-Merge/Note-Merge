# Combined Best-of-Both BERTopic Pipeline
# =======================================
# Hybrid version: CODE 1 base with selected semantic and OCR features from CODE 2

import os
import re
import json
import fitz
import cv2
import numpy as np
import pytesseract
from PIL import Image
from fpdf import FPDF
from collections import defaultdict
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import preprocessing

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def is_noise(line):
    line = line.strip()
    if not line or len(line) < 3:
        return True
    noise_patterns = [
        r'^[-–—•●]?[ \t]*\d+[.)]?$',
        r'(table\s+\d+|exercise\s+\d+|figure\s+\d+|fill the blanks|^\(\w+\)$|^-+\s*\d+\s*-+)',
        r'(^ENVE\s+\d+|^-\s*\d+\s*-|page\s+\d+)',
        r'^[a-zA-Z]\.?$',
        r'^[1-9]\.$',
        r'(chapter|table of contents|figure|university|author|copyright)',
        r'[^\w\s]{3,}',
        r'(university|college|institute|department)',
        r'chapter\s+[ivxlc\d]+',
        r'\bpage\b\s*\d+',
        r'copyright', r'\d{1,2}/\d{1,2}/\d{2,4}', r'\d+\.?',
        r'^[-\s]*\d+[-\s]*$',
    ]
    for pattern in noise_patterns:
        if re.search(pattern, line.lower()):
            return True
    return False


def classify_line(line):
    line_lower = line.lower()
    if '?' in line:
        return "Question: " + line
    if any(p in line_lower for p in ['definition:', 'is defined as', 'is called', 'is termed', 'means that']):
        return "Definition: " + line
    if any(sym in line for sym in ['=', '≠', '≈', '≡', '∫', '∑', '∏', '∂', '∇', 'Δ', 'δ', 'sin(', 'cos(', 'tan(', 'log(', 'ln(', 'exp(', 'sqrt(', 'α', 'β', 'θ', 'λ', 'μ', 'π', '±', '÷', '∞', '∈', '∉', '⊂', '⊆', '∩', '→', '←', '↔']):
        return "Formula: " + line
    if any(p in line_lower for p in ['example', 'e.g.', 'for instance', 'consider', 'suppose']):
        return "Example: " + line
    return line


def preprocess_image_for_ocr(img_np):
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_text_from_pdf(doc_path, ocr_enabled=True):
    doc = fitz.open(doc_path)
    sentences_all = []
    ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\'-+=/\\ '

    for page_num, page in enumerate(doc):
        lines = []
        text = page.get_text("text")
        text_content_length = len(text.strip())

        if text:
            for line in text.split("\n"):
                line = line.strip()
                if len(line) >= 5 and not is_noise(line):
                    lines.append(classify_line(line))

        if ocr_enabled and (text_content_length < 100 or len(lines) < 5):
            try:
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                processed_img = preprocess_image_for_ocr(img_np)
                ocr_text = pytesseract.image_to_string(processed_img, config=ocr_config)

                for line in ocr_text.split("\n"):
                    line = line.strip()
                    if len(line) >= 5 and not is_noise(line):
                        lines.append(classify_line(line))
            except Exception as e:
                print(f"OCR failed on page {page_num+1}: {e}")

        page_text = " ".join(lines)
        sentences = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
        sentences_all.extend(sentences)

    return sentences_all


def group_sentences(file_path, output_prefix="output", ocr_enabled=True):
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    custom_hdbscan = HDBSCAN(min_cluster_size=4, min_samples=2, metric='euclidean', cluster_selection_method='eom')
    umap_model = UMAP(n_neighbors=10, n_components=5, min_dist=0.0, metric='cosine', random_state=42)

    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=custom_hdbscan
    )

    sentences = extract_text_from_pdf(file_path, ocr_enabled=ocr_enabled)
    preprocessed = [preprocessing.TextPreprocessor.preprocess_text(sent) for sent in sentences]

    topics, _ = model.fit_transform(preprocessed)

    grouped = defaultdict(list)
    for raw_sent, topic in zip(sentences, topics):
        if topic != -1:
            grouped[topic].append(raw_sent)

    grouped = {
        k: list(dict.fromkeys(v))
        for k, v in grouped.items()
        if len(v) >= 3 and all(len(s.split()) > 3 for s in v)
    }

    topic_labels = {}
    for topic_id in grouped:
        words = model.get_topic(topic_id)
        filtered = [w for w, _ in words if w.lower() not in ENGLISH_STOP_WORDS and len(w) > 2 and w.isalpha()]
        topic_labels[topic_id] = ", ".join(filtered[:5]) if filtered else "No Label"

    with open(f"{output_prefix}_clustered.json", "w", encoding="utf-8") as f:
        json.dump(grouped, f, ensure_ascii=False, indent=4)

    with open(f"{output_prefix}_topic_labels.json", "w", encoding="utf-8") as f:
        json.dump(topic_labels, f, ensure_ascii=False, indent=4)

    return grouped, topic_labels
