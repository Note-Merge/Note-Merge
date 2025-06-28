import os
from keras.callbacks import EarlyStopping, TensorBoard
import preprocessing_bilstm
import bilstm_model

def train_model(
    input_texts,
    target_texts,
    num_words=10000,
    max_input_len=450,
    max_output_len=500,
    embedding_dim=256,
    lstm_units=512,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
):
    #tokenize and pad the input and target texts
    print("Starting tokenization and padding...")
    encoder_input,decoder_input,decoder_target,input_tokenizer,output_tokenizer= preprocessing_bilstm.tokenize_and_pad(
        input_texts,
        target_texts,
        num_words=num_words,
        max_input_len=max_input_len,
        max_output_len=max_output_len
    )
    print("Tokenization and padding completed.")
    
    #get vocab sizes from the tokenizers for models embedding layers
    vocab_size_input = len(input_tokenizer.word_index) + 1
    vocab_size_output = len(output_tokenizer.word_index) + 1
    print(f"Vocab size for input :{vocab_size_input}")
    print(f"Vocab size for output :{vocab_size_output}")
    
    print("\n--- DEBUGGING ARGUMENT TYPES ---")
    print(f"Value: {vocab_size_input}, Type: {type(vocab_size_input)}")
    print(f"Value: {embedding_dim}, Type: {type(embedding_dim)}")
    print(f"Value: {lstm_units}, Type: {type(lstm_units)}")
    print(f"Value: {max_input_len}, Type: {type(max_input_len)}")
    print("--------------------------------\n")
    # ============================================
    
    
    #build the model
    print("Building the BiLSTM model...")
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
    print("Model built was success.")
    
    #Setting up callbacks
    early_stopping_callback = EarlyStopping(
        monitor='val_loss',       #monitor metric
        patience=10,          #number of epochs with no improvement after which training will be stopped
        verbose=1,           #to log when training is stopped
        restore_best_weights=True    #to restore model weights from the epoch with the best value of the monitored metric
    )
    
    #tensorboard for visualizing training progress
    log_dir ="logs"
    os.makedirs(log_dir, exist_ok=True)  #create log directory if it doesn't exist
    tensorBoard_callback = TensorBoard(log_dir=log_dir,histogram_freq=1)
    print("Callbacks set up completed ( EarlyStopping, TensorBoard).")


    #train the model
    history = model.fit(
        [encoder_input, decoder_input],
        decoder_target,
        epochs = epochs,
        batch_size= batch_size,
        validation_split=validation_split,
        callbacks=[early_stopping_callback, tensorBoard_callback],
        verbose=1
    )
    
    print("Training completed.")
    
    return model, input_tokenizer, output_tokenizer, history
    
    