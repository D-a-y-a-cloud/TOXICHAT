import joblib
import os
import traceback

print("Testing model load...")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
TFIDF_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")

print(f"Model path: {MODEL_PATH} -> Exists? {os.path.exists(MODEL_PATH)}")
print(f"TFIDF path: {TFIDF_PATH} -> Exists? {os.path.exists(TFIDF_PATH)}")

try:
    print("Loading model...")
    model = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded: {type(model)}")
    
    print("Loading vectorizer...")
    vectorizer = joblib.load(TFIDF_PATH)
    print(f"✅ Vectorizer loaded: {type(vectorizer)}")
except Exception as e:
    print("❌ ERROR LOADING MODEL:")
    traceback.print_exc()
