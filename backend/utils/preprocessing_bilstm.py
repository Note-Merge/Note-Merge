from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np


def tokenize_and_pad(input,target,num_words=10000,max_input_len=300,max_output_len=400):
    #(INPUT) Tokenizer for encoder
    input_tokenizer = Tokenizer(num_words=num_words, oov_token="<OOV>")
    input_tokenizer.fit_on_texts(input)
    input_sequences = input_tokenizer.texts_to_sequences(input)
    input_padded = pad_sequences(input_sequences,maxlen=max_input_len,padding="post")
    encoder_input = input_padded
    
    #(OUTPUT) Tokenizer for decoder (merged texts)
    output_tokenizer = Tokenizer(num_words=num_words, oov_token="<OOV>")
    output_tokenizer.fit_on_texts(target)
    
    #adding sos and eos tokens for indicating start and end of sequence
    target = [f"<sos> {txt} <eos>" for txt in target]
    output_sequences = output_tokenizer.texts_to_sequences(target)
    output_padded = pad_sequences(output_sequences,maxlen=max_output_len,padding="post")
    decoder_input= output_padded
    
    #decoder target shifted by one to left
    decoder_target = np.zeros_like(decoder_input)
    decoder_target[:, :-1] = decoder_input[:, 1:]
    
    return encoder_input, decoder_input, decoder_target,input_tokenizer,output_tokenizer