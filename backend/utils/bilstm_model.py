from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Embedding,LSTM, Dense, Bidirectional,Concatenate,Dropout,LayerNormalization,Attention,TimeDistributed
from tensorflow.keras.optimizers import Adam


# Function to create a BiLSTM model for sequence-to-sequence tasks
def build_model (
    vocab_size_input,
    vocab_size_output,
    embedding_dim=256,         #word vector size
    lstm_units=256,             #lstm memory capacity
    max_input_len=350,          
    max_output_len=400,
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
    # state_h = Dense(
    #     lstm_units,
    #     activation='tanh',
    #     name="state_h_combiner"
    #     )(Concatenate()([forward_h,backward_h]))
    
    # state_c = Dense(
    #     lstm_units,
    #     activation='tanh',
    #     name="state_c_combiner"
    # )(Concatenate()([forward_c,backward_c]))
    
    # encoder_outputs_proj = TimeDistributed(Dense(lstm_units))(encoder_outputs)
    state_h =Concatenate()([forward_h, backward_h])
    state_c =Concatenate()([forward_c, backward_c])
    encoder_final_state_h =Dense(lstm_units, activation='tanh', name="encoder_state_h_combiner")(state_h)
    encoder_final_state_c =Dense(lstm_units, activation='tanh', name="encoder_state_c_combiner")(state_c)
    encoder_final_states=[encoder_final_state_h,encoder_final_state_c]
    
    #Decoder: using shape none makes model more flexible for inference
    decoder_inputs = Input(shape=(max_output_len,),name="decoder_input")
    
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
        initial_state=encoder_final_states
    )
    
    #project encoder outputs to match decoder's output dimension. 1024 to 512
    encoder_outputs_projected = TimeDistributed(
        Dense(
            lstm_units,
            name="encoder_output_projection"
        )
    )(encoder_outputs)
    
    #Attention Mechanism- Connecing decoder to encoder outputs
    attention_layer= Attention(
        use_scale=True,  # Use scaled dot-product attention
        name="attention_mechanism"
    )
    
    #The attention layer uses the decoder's output sequence as the "query" and the
    # encoder's full output sequence as the "value" and "key".
    #computing attention context vector ( decoder focusinhg and encoder output)
    context_vector,_ = attention_layer([decoder_outputs, encoder_outputs_projected],return_attention_scores=True)
    
    #Concatenating context vector with decoder outputs
    decoder_combined = Concatenate()([
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
    
    final_outputs = decoder_dense(decoder_dropout)
    
    #defining the model
    model = Model(
        inputs=[encoder_inputs, decoder_inputs],
        outputs=final_outputs,
        name="BiLSTM_Seq2Seq_Attention_Model"
        )
    
    #optimizer and loss function
    optimizer = Adam(
        learning_rate=0.001,  #adjust the learning rate as needed
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

