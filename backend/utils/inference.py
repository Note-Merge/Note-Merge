from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences as pad_sequencees
import pickle
import numpy as np


#loadining model
model = load_model("saved/bilstm_model.h5")

#load tokenizers
with open("saved/input_tokenizer.pkl", "rb") as f:
    input_tokenizer = pickle.load(f)
    
with open("saved/output_tokenizer.pkl", "rb") as f:
    output_tokenizer = pickle.load(f)
    
input_text = " "
input_seq = input_tokenizer.texts_to_sequences([input_text])
input_seq = pad_sequencees(input_seq, maxlen =350, padding='post')

#run inference
predicted_seq = model.predict(input_seq)
predicted_ids = np.argmax(predicted_seq[0], axis=-1)

#decode predicted 
reverse_output_word_index = {v: k for k,v in output_tokenizer.word_index.items()}
predicted_text = ' '.join([reverse_output_word_index.get(id,'') for id in predicted_ids if id>0])

printf("Predicted text: ", predicted_text)