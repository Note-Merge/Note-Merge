import preprocessing_bilstm
import bilstm_model

def train_model(
    input_texts,
    target_texts,
    num_words=10000,
    max_input_len=300,
    max_output_len=400,
    embedding_dim=256,
    lstm_units=512,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
):
    #tokenize and pad the input and target texts
    encoder_input,decoder_input,decoder_target,input_tokenizer,output_tokenizer= preprocessing_bilstm.tokenize_and_pad(
        input_texts,
        target_texts,
        num_words=num_words,
        max_input_len=max_input_len,
        max_output_len=max_output_len
    )
    
    #get vocab sizes
    vocab_size_input = len(input_tokenizer.word_index) + 1
    vocab_size_output = len(output_tokenizer.word_index) + 1
    
    #build the model
    model = bilstm_model.build_model(
        vocab_size_input=vocab_size_input,
        vocab_size_output=vocab_size_output,
        embedding_dim=embedding_dim,
        lstm_units=lstm_units,
        max_input_len=max_input_len,
        max_output_len=max_output_len
    )
    
    #display model summary
    model.summary()
    
    #train the model
    history = model.fit(
        [encoder_input, decoder_input],
        decoder_target,
        epochs = epochs,
        batch_size= batch_size,
        validation_split=validation_split,
        verbose=1
    )
    
    print("Training completed.")
    
    return model, input_tokenizer, output_tokenizer, history
    
    