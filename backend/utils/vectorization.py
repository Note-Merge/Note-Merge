from sklearn.feature_extraction.text import TfidfVectorizer

def vectorize_sentences(sentences):
    vectorizer= TfidfVectorizer()
    vectors = vectorizer.fit_transform(sentences)
    return vectors


vectorize_sentences(["Hi Hello how are you? I am file upto now."])