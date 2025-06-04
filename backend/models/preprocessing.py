import re
import string
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
import nltk


#downloading the stopwords
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    #lowercasing the text
    text = text.lower()
    
    #removing tags
    text = re.sub(r'<.*?>','',text)
    
    #removing punctuations
    text = re.sub(r'[^\w\s]','',text)
    
    #removing numbers
    text = re.sub(r'\d+','',text)
    
    #removing spaces (extra)
    text = re.sub(r'\s+',' ',text).strip()
    
    #removing stopwords
    text = ' '. join([word for word in text.split() if word not in stop_words])
    
    print("Preprocessed text:", text)
    return text 


preprocess_text("This is a sample text with some <tags> and numbers 12345. Let's clean it up!")