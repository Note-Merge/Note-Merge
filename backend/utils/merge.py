import training
from keras.preprocessing.sequence import pad_sequences
import numpy as np

def merge_clusters(
    model,
    input_tokenizer,
    output_tokenizer,
    cluster1,
    cluster2,
    max_input_len=300,
    max_output_len=400,
):
    
    #combine clusters
    combined_input = f"{cluster1} [SEP] {cluster2}"
    
    #tokenize input
    input_seq = input_tokenizer.texts_to_sequences([combined_input])
    input_paded = pad_sequences(input_seq, maxlen=max_input_len, padding='post')
    
    #create decoder input sequence
    start_token_id = output_tokenizer.word_index.get('<sos>', 1)
    decoder_input = np.zeros((1,max_output_len))
    decoder_input[0,0]= start_token_id
    
    
    #generate output sequence word by word
    merged_words = []
    
    for i in range(1,max_output_len):
        
        #predict next word
        predictions = model.predict([input_paded,decoder_input],verbose =0)
        predicted_id = np.argmax(predictions[0,i-1, :])
        
        #conver id to word
        predicted_word = output_tokenizer.index_word.get(predicted_id,'<UNK>')
        
        #stop if end token reached
        if predicted_word == '<eos>':
            break
        
        #append predicted word to output
        merged_words.append(predicted_word)
        decoder_input[0,i] = predicted_id
    
    #join words to form merged cluster text
    merged_cluster_text = ' '.join(merged_words)
    
    return merged_cluster_text

            