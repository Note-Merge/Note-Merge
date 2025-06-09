import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
import numpy as np
import preprocessing


#model initialization:
model = SentenceTransformer('all-MiniLM-L6-v2')

note = """Dogs are great pets because they are friendly and loyal.
They love to play and go for walks in the park.
Many people enjoy spending time with their dogs. Cats, on the other hand, are more independent and quiet.
They like to nap in sunny spots and play with toys.
Both dogs and cats make wonderful companions.
Reading books is another fun activity that many people enjoy.
It can take you on adventures and help you learn new things.
Whether you have a pet or a good book, both can bring joy and comfort to your life."""

note = preprocessing.TextPreprocessor.sentence_tokenize(note)

#encoding the texts
embeddings = model.encode(note,convert_to_tensor=True)

#moving embeddings to the cpu and converting to numpy
embeddings_np= embeddings.cpu() .numpy()


#Perform clustering using Agglomerative Clustering
clustering_model = AgglomerativeClustering(n_clusters = 4)
clustering_labels = clustering_model.fit_predict(embeddings_np)


#displaying the clustered result
print(len(clustering_labels))

clustered_sentences ={}
for sentence_id,cluster_id in enumerate(clustering_labels):
    if cluster_id not in clustered_sentences:
        clustered_sentences[cluster_id]=[]
    clustered_sentences[cluster_id].append(note[sentence_id])

for cluster_id,sentence_list in clustered_sentences.items():
    print(f"Cluster {cluster_id} : {', '.join(sentence_list)}")