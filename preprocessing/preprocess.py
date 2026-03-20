import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

print("Loading dataset...")

df = pd.read_csv("data/phishing_email.csv")
df = df.rename(columns={"text_combined": "text"})

print("Dataset loaded successfully!")

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    words = text.split()
    words = [w for w in words if w not in stop_words]

    return " ".join(words)

df["text"] = df["text"].apply(clean_text)

clean_df = df[["text", "label"]]
clean_df.to_csv("data/clean_data.csv", index=False)

print("✅ Clean dataset saved as data/clean_data.csv")
