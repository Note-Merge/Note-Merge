from keras.models import Model
from keras.layers import Input,Embedding,LSTM, Dense, Bidirectional,Concatenate,Dropout,LayerNormalization,Attention,TimeDistributed
from keras.optimizers import Adam


# Function to create a BiLSTM model for sequence-to-sequence tasks
def build_model (
    vocab_size_input,
    vocab_size_output,
    embedding_dim=256,         #word vector size
    lstm_units=512,             #lstm memory capacity
    max_input_len=450,          
    max_output_len=550,
    dropout_rate=0.3,           #regularization strength for randomly droping connections during training
    ):      
    
    
    #Encoder:
    encoder_inputs= Input(shape=(max_input_len,),name="encoder_input")
    
    #embedding layer for encoder
    enc_embedding = Embedding(
        input_dim=vocab_size_input,
        output_dim=embedding_dim,
        trainable=True,
        mask_zero=True,
        name="encoder_embedding"
        )(encoder_inputs)
    
    #Bidirectional LSTM for encoder
    encoder_bi_lstm= Bidirectional(
        LSTM(
            units=lstm_units,
            return_state=True,
            return_sequences=True,
            name="encoder_lstm",
            dropout=dropout_rate,
            recurrent_dropout=dropout_rate
            ),
        merge_mode='concat',
        name="bidirectional_lstm"
     )(enc_embedding)
    
    #unpacking bidirectional outputs and states
    encoder_outputs, forward_h,forward_c, backward_h,backward_c = encoder_bi_lstm    
    
    #combine forward and backward final states
    #Concatenating forward and backward states
    state_h = Dense(
        lstm_units,
        activation='tanh',
        name="state_h_combiner"
        )(Concatenate()([forward_h,backward_h]))
    
    state_c = Dense(
        lstm_units,
        activation='tanh',
        name="state_c_combiner"
    )(Concatenate()([forward_c,backward_c]))
    
    encoder_outputs_proj = TimeDistributed(Dense(lstm_units))(encoder_outputs)

    
    #Decoder:
    decoder_inputs = Input(shape =(max_output_len,),name="decoder_input")
    
    #Embedding layer for decoder
    dec_embedding = Embedding(
        input_dim=vocab_size_output,
        output_dim=embedding_dim,
        mask_zero=True,
        trainable=True,
        name ="decoder_embedding"
    )(decoder_inputs)
    
    #LSTM as decoder
    decoder_lstm = LSTM(
        units=lstm_units,
        return_sequences=True,
        return_state=True,
        name="decoder_lstm",
        dropout=dropout_rate,
        recurrent_dropout=dropout_rate
        )
    
    #initialize decoder with encoder's understanding
    decoder_outputs, decoder_h, decoder_c = decoder_lstm(
        dec_embedding,
        initial_state=[state_h,state_c]
    )
    
    #Attention Mechanism- Connecing decoder to encoder outputs
    attention_layer= Attention(
        name="attention_mechanism",
        use_scale=True
    )
     
    #computing attention context vector ( decoder focusinhg and encoder output)
    context_vector = attention_layer([decoder_outputs, encoder_outputs_proj])
    
    #Concatenating context vector with decoder outputs
    decoder_combined = Concatenate(
        axis=-1,
        name="decoder_attention_concatenation"
    )([
        decoder_outputs,
        context_vector
    ])
    
    #adding layer normalization for training stability
    decoder_normalized = LayerNormalization(name="decoder_layer_norm")(decoder_combined)
    
    #adding dropout for regularization
    decoder_dropout = Dropout(
        rate=dropout_rate,
        name="decoder_dropout"
    )(decoder_normalized)
    
    #Final Dense layer to convert decoder outputs to vocabulary size
    #Output layer
    decoder_dense = Dense(
        vocab_size_output,
        activation='softmax',
        name="output_dense"
    )
    
    decoder_outputs = decoder_dense(decoder_dropout)
    
    #defining the model
    model = Model(
        inputs=[encoder_inputs, decoder_inputs],
        outputs=decoder_outputs,
        name="BiLSTM_Seq2Seq_Attention_Model"
        )
    
    #optimizer and loss function
    optimizer = Adam(
        learning_rate=0.001,  # You can adjust the learning rate as needed
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-8,
    )
    
    loss_function = 'sparse_categorical_crossentropy'  # Suitable for multi-class classification tasks
    
    # Compiling the model
    model.compile(
        optimizer=optimizer,
        loss=loss_function,
        metrics=['accuracy']
    )
    
    return model

