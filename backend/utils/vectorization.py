from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
from preprocessing import TextPreprocessor
import pandas as pd
from collections import defaultdict
import fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def display_lda_topics(model, vectorizer, top_n=5):
    words = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(model.components_):
        top_features = [words[i] for i in topic.argsort()[:-top_n - 1:-1]]
        print(f"Topic {topic_idx + 1}: {', '.join(top_features)}")

def tf_vectorize_sentences(sentences):
    tf_vectorizer= TfidfVectorizer()
    tf_vectors = tf_vectorizer.fit_transform(sentences)
    return tf_vectors


tf_vectorize_sentences(["Hi Hello how are you? I am file upto now."])

def cv_vectorize_sentences(sentences):
    cv_vectorizer=CountVectorizer()
    cv_vectors= cv_vectorizer.fit_transform(sentences)
    return cv_vectors

def cluster_sentences(vectors, n_clusters=5):
    model=AgglomerativeClustering(n_clusters=n_clusters,linkage='ward')
    labels = model.fit_predict(vectors.toarray())
    return labels

def lda_modeling(vectors,n_topics=5):
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(vectors)
    lda_topics=lda.transform(vectors)
    lda_labels = np.argmax(lda_topics,axis=1)
    return lda_topics,lda_labels



# #note = extract_text_from_pdf("docu.pdf")
# #note = """AI advancements are transforming industries like healthcare and finance
#     Rising global temperatures are a critical focus in climate change research.
#     Early childhood education is crucial for cognitive and social development.
#     AI algorithms now handle tasks such as image recognition and natural language processing.
#     Melting ice caps and extreme weather events highlight the urgency of environmental studies.
#     Investments in early education programs improve academic performance and reduce inequalities.
#     Climate change strategies aim to promote sustainability and preserve the environment.
#     Educators stress the importance of nurturing environments for young children's growth."""

note = """Dogs are great pets because they are friendly and loyal.
They love to play and go for walks in the park.
Many people enjoy spending time with their dogs. Cats, on the other hand, are more independent and quiet.
They like to nap in sunny spots and play with toys.
Both dogs and cats make wonderful companions.
Reading books is another fun activity that many people enjoy.
It can take you on adventures and help you learn new things.
Whether you have a pet or a good book, both can bring joy and comfort to your life."""

sentences = TextPreprocessor.sentence_tokenize(note)
preprocessed = [TextPreprocessor.preprocess_text(s) for s in sentences]
tf_vectors = tf_vectorize_sentences(preprocessed)
cv_vectors = cv_vectorize_sentences(preprocessed)

n_samples = tf_vectors.shape[0]
n_clusters = min(2,n_samples)

cluster_labels = cluster_sentences(tf_vectors, n_clusters=n_clusters)
lda_topics, lda_labels = lda_modeling(tf_vectors, n_topics=10)

df= pd.DataFrame({
    "Original": sentences,
    "Preprocessed": preprocessed,
    "Cluster Labels": cluster_labels,
    "LDA Topics": lda_labels
    
})

#print(df)

def merge_small_paragraphs(paragraphs, min_length=2):
    merged = []
    temp = ""
    count = 0
    for p in paragraphs:
        s_count = len(p.split('. '))
        if s_count < min_length:
            temp += " " + p
            count += s_count
            if count >= min_length:
                merged.append(temp.strip())
                temp = ""
                count = 0
        else:
            if temp:
                merged.append(temp.strip())
                temp = ""
                count = 0
            merged.append(p.strip())
    if temp:
        merged.append(temp.strip())
    return merged


def group_sentences_by_cluster_and_topic(sentences, cluster_labels, lda_labels):
    grouped = defaultdict(list)
    
    for idx, sentence in enumerate(sentences):
        key = (cluster_labels[idx], lda_labels[idx])  # Combine both labels
        grouped[key].append(sentence)
    
    # Now form paragraphs from sentence groups
    paragraphs = [' '.join(grouped[k]) for k in sorted(grouped.keys())]
    return paragraphs

paragraphs = group_sentences_by_cluster_and_topic(sentences, cluster_labels, lda_labels)

merged_paragraphs = merge_small_paragraphs(paragraphs)

# Print
for idx, para in enumerate(merged_paragraphs):
    print(f"\n--- Paragraph {idx+1} ---\n{para}")