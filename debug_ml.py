import os
import joblib
import traceback
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(root_dir, "models")
model_path = os.path.join(models_dir, "model.pkl")
tfidf_path = os.path.join(models_dir, "tfidf_vectorizer.pkl")

print("====================================================")
print("🔍 ML MODEL DEBUGGER")
print("====================================================")
print(f"Python Version: {sys.version}")

if not os.path.exists(models_dir):
    print(f"❌ Error: Models directory not found at {models_dir}")
else:
    print(f"✅ Models directory found: {models_dir}")

for p in [model_path, tfidf_path]:
    if os.path.exists(p):
        print(f"✅ Found file: {os.path.basename(p)} ({os.path.getsize(p)} bytes)")
    else:
        print(f"❌ Missing file: {os.path.basename(p)}")

print("\n📦 Attempting to load TF-IDF Vectorizer...")
try:
    vectorizer = joblib.load(tfidf_path)
    print("✅ TF-IDF Vectorizer loaded successfully!")
    print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
except Exception:
    print("❌ Error loading TF-IDF Vectorizer:")
    traceback.print_exc()

print("\n📦 Attempting to load SVM Model...")
try:
    model = joblib.load(model_path)
    print("✅ SVM Model loaded successfully!")
    if hasattr(model, 'classes_'):
        print(f"   Classes: {model.classes_}")
except Exception:
    print("❌ Error loading SVM Model:")
    traceback.print_exc()

print("\n====================================================")
