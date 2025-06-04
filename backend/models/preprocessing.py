import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


import re
import string
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk


#downloading the stopwords
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

#initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

#initialize the tokenizer (word -> integer)
tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")

#initialize the set of stopwords
stop_words = set(stopwords.words('english'))


class TextPreprocessor:
    
    def preprocess_text(text):
        #lowercasing the text
        text = text.lower()
    
        #removing tags
        text = re.sub(r'<.*?>','',text)
    
        #removing punctuations
        text = text.translate(str.maketrans('', '', string.punctuation))

        #removing numbers
        text = re.sub(r'\d+','',text)
    
        #removing spaces (extra)
        text = re.sub(r'\s+',' ',text).strip()
        
        #word tokenization
        word_tokens = nltk.word_tokenize(text)
    
        #removing stopwords and lemmatizing
        text = ' '. join([lemmatizer.lemmatize(w) for w in word_tokens if w not in stop_words])
        
        print("Preprocessed text:", text)
        return text 

    def tokenize_text(text):
        #tokenize the text
        tokenizer.fit_on_texts([text])
        #integer sequences:
        sequences = tokenizer.texts_to_sequences([text])
        #padding the seq
        padded_seq = pad_sequences(sequences, maxlen=100, padding='post')
        print("Tokenized and padded sequence:", padded_seq)
        return padded_seq
    
    def sentence_tokenize(texts):
        #split multiple texts into sentences
        sentences = nltk.sent_tokenize(texts)
        print("Tokenized sentences:", sentences)
        return sentences
    
    

TextPreprocessor.preprocess_text("This is a sample text with some <tags> @@@ !! $$$ and numbers 12345. Let's clean it up!")
TextPreprocessor.sentence_tokenize("This is the first sentence. Here is another one! And yet another one. This is 2nd sentences lyammai aba")