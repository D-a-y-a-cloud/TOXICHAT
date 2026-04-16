"""
🧠 ToxiChat — Train Emotion Detection ML Model
=================================================
Trains a Deep Learning Multi-Layer Perceptron (MLPClassifier)
to categorize sentences into: Angry, Sad, Frustrated, Neutral.
Outputs:
  - models/emotion_model.pkl
  - models/emotion_vectorizer.pkl
"""

import os
import re
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════
# Emotion Dataset
# ══════════════════════════════════════════════════════════════

dataset = [
    # Angry
    ("I hate you so much", "Angry"),
    ("You are an idiot", "Angry"),
    ("Shut up and leave me alone", "Angry"),
    ("I'm going to kill you", "Angry"),
    ("What the hell is wrong with you", "Angry"),
    ("Fuck off and die", "Angry"),
    ("You completely ruined my life", "Angry"),
    ("I am absolutely furious", "Angry"),
    ("This makes me so angry", "Angry"),
    ("Stupid garbage product", "Angry"),
    ("I despise everything about this", "Angry"),
    
    # Sad
    ("I feel so depressed today", "Sad"),
    ("Everything is just hopeless", "Sad"),
    ("I can't stop crying", "Sad"),
    ("I feel so lonely and empty", "Sad"),
    ("Nobody cares about me anymore", "Sad"),
    ("My heart is completely broken", "Sad"),
    ("I'm just so sad all the time", "Sad"),
    ("I don't think things will ever get better", "Sad"),
    ("It hurts so much to think about it", "Sad"),
    ("I miss the old days when I was happy", "Sad"),
    
    # Frustrated
    ("I give up I can't do this anymore", "Frustrated"),
    ("This is so annoying and tiring", "Frustrated"),
    ("Why does nothing ever work for me", "Frustrated"),
    ("Ugh I am so sick of trying", "Frustrated"),
    ("I am exhausted from trying over and over", "Frustrated"),
    ("Sigh this is taking forever", "Frustrated"),
    ("I am so confused and lost right now", "Frustrated"),
    ("Can someone just tell me what to do", "Frustrated"),
    ("This problem is literally impossible", "Frustrated"),
    ("I am losing my mind over this", "Frustrated"),
    
    # Neutral
    ("The dog went for a walk in the park", "Neutral"),
    ("I need to go to the grocery store", "Neutral"),
    ("What time does the movie start", "Neutral"),
    ("The weather is quite nice today", "Neutral"),
    ("Let's schedule a meeting for tomorrow", "Neutral"),
    ("I had a sandwich for lunch", "Neutral"),
    ("Can you pass me the salt", "Neutral"),
    ("I am typing on my keyboard", "Neutral"),
    ("Hello how are you doing", "Neutral"),
    ("See you later have a good day", "Neutral"),
    ("What are you up to", "Neutral")
]

texts = [d[0] for d in dataset]
labels = [d[1] for d in dataset]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return ' '.join(text.split())

texts_cleaned = [clean_text(t) for t in texts]

# Split validation sets
X_train, X_test, y_train, y_test = train_test_split(
    texts_cleaned, labels, test_size=0.15, random_state=42, stratify=labels
)

# TF-IDF Mapping
vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("\n🧠 Training Deep Learning Emotion Model (MLP)...")
model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    solver='adam',
    max_iter=500,
    random_state=42
)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")

model_path = os.path.join(MODEL_DIR, "emotion_model.pkl")
tfidf_path = os.path.join(MODEL_DIR, "emotion_vectorizer.pkl")

joblib.dump(model, model_path)
joblib.dump(vectorizer, tfidf_path)

print(f"✅ Emotion Model saved to: {model_path}")
print(f"✅ Emotion Vectorizer saved to: {tfidf_path}")
