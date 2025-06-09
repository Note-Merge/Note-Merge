from bertopic import BERTopic
import preprocessing
import pdfplumber
from collections import defaultdict


def extract_text_from_pdf(pdf_path):
    sentences_all = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() 
            
            if text:
                lines = text.split("\n")
                
                clean_lines = []
                for line in lines:
                    line = line.strip()
                    
                    if not line or line.isdigit() or len(line)<5:
                        continue
                    
                    if any(x in line.lower() for x in ["chapter", "table of contents", "page", "figure", "university", "author", "copyright"]):
                        continue
                    
                    clean_lines.append(line)
                
                page_text = " ".join(clean_lines)
                sentences1 = preprocessing.TextPreprocessor.sentence_tokenize(page_text)
                sentences_all.extend(sentences1)
                
    return sentences_all




model = BERTopic(embedding_model='all-MiniLM-L6-v2')

# note = """Dogs are great pets because they are friendly and loyal.
# They love to play and go for walks in the park.
# Many people enjoy spending time with their dogs. Cats, on the other hand, are more independent and quiet.
# They like to nap in sunny spots and play with toys.
# Both dogs and cats make wonderful companions.
# Reading books is another fun activity that many people enjoy.
# It can take you on adventures and help you learn new things.
# Whether you have a pet or a good book, both can bring joy and comfort to your life.
# I love to play with my dog in the park."""

note = extract_text_from_pdf("docu.pdf")

sentences = note

topics, prob = model.fit_transform(sentences)


# Step 6: Group sentences by topic

clustered_sentences = defaultdict(list)
for sentence, topic in zip(sentences, topics):
    clustered_sentences[topic].append(sentence)

# Step 7: Print out clusters
for topic, sents in clustered_sentences.items():
    print(f"\nCluster {topic}:\n" + "\n".join(sents))