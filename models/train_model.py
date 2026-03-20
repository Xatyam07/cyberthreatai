import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle

print("Loading dataset...")

df = pd.read_csv("data/clean_data.csv")

print("Dataset loaded!")

# 🔥 VERY IMPORTANT FIXES
df = df.dropna()                  # remove NaN rows
df['text'] = df['text'].astype(str)  # force convert to string
df = df[df['text'].str.strip() != ""]  # remove empty text

print("Empty rows removed!")

# Split input and output
X = df['text']
y = df['label']

print("Converting text to numbers (TF-IDF)...")

vectorizer = TfidfVectorizer(max_features=5000)
X_vectorized = vectorizer.fit_transform(X)

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, y, test_size=0.2, random_state=42
)

print("Training model...")

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("🎉 Model Accuracy:", accuracy)

# Save model
pickle.dump(model, open("models/phishing_model.pkl", "wb"))
pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))

print("✅ Model saved successfully!")
