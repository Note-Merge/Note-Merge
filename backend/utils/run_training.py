import pickle
import pandas as pd
import training

#importing dataset
csv_file_path = "dataset/d1.csv"

#paths to save model tokenizers
model_save_path = "saved/bilstm_model.h5"
input_tokenizer_path = "saved/input_tokenizer.pkl"
output_tokenizer_path = "saved/output_tokenizer.pkl"

#parameters for the model
NUM_WORDS = 10000          #vocab size for tokenizer
MAX_INPUT_LEN = 350         #max length of input text
MAX_OUTPUT_LEN = 400
EMBEDDING_DIM = 256
LSTM_UNITS = 256  
BATCH_SIZE = 8
VALIDATION_SPLIT = 0.2
EPOCHS = 50


#loading and cleaning the dataset
print("Loading dataset...")
try:
    df= pd.read_csv(csv_file_path, on_bad_lines="skip")
except FileNotFoundError:
    print(f"Error: The file {csv_file_path} does not exist.")
    exit()
    
#clean data by dropping rows with NaN values   
df.dropna(subset=["input", "output"], inplace=True)
#string typechecking for data
df['input'] = df['input'].astype(str)
df['output'] = df['output'].astype(str)
print(f"Dataset loaded with {len(df)} entries.")

#balancing the dataset by downsampling
print("Balancing dataset...")
df_merge = df[df['input'].str.contains("<task:merge>",na=False)]
df_clean = df[df['input'].str.contains("<task:clean>",na=False)]

print(f"Entries for merge task: {len(df_merge)}")
print(f"Entries for clean task: {len(df_clean)}")

#determine the size of smaller group
min_size = min(len(df_merge),len(df_clean))

if min_size > 0:
    df_merge_balanced = df_merge.sample(n=min_size,random_state=42)
    df_clean_balanced = df_clean.sample(n=min_size,random_state=42)
    
    #combine the balanced dfs
    df_balanced = pd.concat([df_merge_balanced, df_clean_balanced])
    print(f"Balanced dataset size: {len(df_balanced)}")
else:
    print("Error: One of the task groups is empty. Cannot balance dataset.")
    df_balanced=df
    
#shuffliong the dataset
df_final = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
print("Dataset shuffled.")

#run the training
input_texts = df_final['input'].tolist()
target_texts = df_final['output'].tolist()
print("Starting model training...")

model, input_tokenizer, output_tokenizer, history = training.train_model(
    input_texts=input_texts,
    target_texts=target_texts,
    num_words=NUM_WORDS,
    max_input_len=MAX_INPUT_LEN,
    max_output_len=MAX_OUTPUT_LEN,
    embedding_dim=EMBEDDING_DIM,
    lstm_units=LSTM_UNITS,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_split=VALIDATION_SPLIT
)

print("Model training completed.")
print("Saving model and tokenizers...")
model.save(model_save_path)
print(f"Model saved to {model_save_path}")

with open(input_tokenizer_path, "wb") as f:
    pickle.dump(input_tokenizer, f)
print(f"Input tokenizer saved to {input_tokenizer_path}")

with open(output_tokenizer_path, "wb") as f:
    pickle.dump(output_tokenizer, f)
print(f"Output tokenizer saved to {output_tokenizer_path}")

print("All components saved successfully.")