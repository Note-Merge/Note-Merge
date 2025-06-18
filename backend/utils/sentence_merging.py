from clustering import group_sentences
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-mpnet-base-v2')

def topic_centroid(sentences):
    embeddings = model.encode(sentences)
    return embeddings.mean(axis=0)
    
    
grouped1, topic_labels1 = group_sentences("docu.pdf", output_prefix="output")
#grouped2, topic_labels2 = group_sentences("docu2.pdf", output_prefix="output2")

topic_label_embeddings = {tid: model.encode(label) for tid,label in topic_labels1.items()}    


print(topic_labels1)
print(grouped1)