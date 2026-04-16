"""
ML Service — Loads the toxicity detection model and provides predictions.
Falls back to a simple keyword-based classifier if no model files exist.
"""
import os
import re
import numpy as np

# Globals
_toxic_pipeline = None
_ready = False

# ══════════════════════════════════════════════════════════════
# TOXICITY CONFIG
# ══════════════════════════════════════════════════════════════
TOXICITY_THRESHOLD = 0.5

# Profanity & Hate Speech (Backup Filter)
TOXIC_KEYWORDS = [
    # Severe Profanity
    'fuck', 'fucking', 'fucker', 'bitch', 'shit', 'piss', 'cunt', 'slut', 'whore',
    'dick', 'pussy', 'asshole', 'bastard', 'motherfucker', 
    # Insults & Toxicity
    'idiot', 'stupid', 'dumb', 'moron', 'retard', 'trash', 'garbage', 'scum', 
    'loser', 'worthless', 'ugly', 'disgusting', 'pathetic', 'shut up', 'get lost',
    'hate', 'kill', 'die', 'murder', 'suicide', 'hell', 'damn', 'crap'
]


def load_model():
    """Load the Deep Learning Transformer from Hugging Face."""
    global _toxic_pipeline, _ready
    try:
        from transformers import pipeline
        import warnings
        
        print(f"📡 [DEBUG] AI instantiating Deep Learning model from Hugging Face...")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _toxic_pipeline = pipeline("text-classification", model="martin-ha/toxic-comment-model")
            
        _ready = True
        print(f"✅ [SUCCESS] AI Linked: Deep Learning Pipeline Active")
    except Exception as e:
        print(f"❌ [CRITICAL] AI load error: {e}")
        _ready = False


def _clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    return ' '.join(text.split())


# Safe Word Bypass (Always low score)
SAFE_WORDS = [
    'hello', 'hi', 'hey', 'bye', 'goodbye', 'father', 'mother', 'brother', 
    'sister', 'family', 'friend', 'love', 'amazing', 'great', 'good',
    'how', 'are', 'you', 'doing', 'what', 'where', 'why', 'who', 'when',
    'thanks', 'thank', 'please', 'ok', 'okay', 'yes', 'no'
]

# Common safe phrases that should never be toxic
SAFE_PHRASES = [
    'how are you', 'how are you doing', 'what are you doing', 
    'whats up', 'what is up', 'good morning', 'good night',
    'see you', 'take care', 'have a good day'
]


def predict_toxicity(text: str) -> dict:
    """
    Predict toxicity for a given text with Safe calibration.
    Returns: {"score": float, "label": str, "is_flagged": bool}
    """
    if not text or not text.strip():
        return {"score": 0.0, "label": "non-toxic", "is_flagged": False}

    # ── Safe Word Bypass ─────────────────────────────────────
    text_lower = text.lower()
    
    # Check exact safe phrases
    if any(phrase in text_lower for phrase in SAFE_PHRASES):
        return {"score": 0.05, "label": "non-toxic", "is_flagged": False}
        
    # Check if text is just safe words
    words = text_lower.split()
    if words and all(w in SAFE_WORDS for w in words):
        return {"score": 0.05, "label": "non-toxic", "is_flagged": False}

    # Verify if it possesses ANY potential toxicity in keywords
    has_toxic_keyword = any(re.search(rf'\b{re.escape(kw)}\b', text_lower) for kw in TOXIC_KEYWORDS)

    # ── Use ML model if available ────────────────────────────
    if _ready and _toxic_pipeline is not None:
        try:
            cleaned = _clean_text(text)
            if not cleaned.strip():
                return {"score": 0.05, "label": "non-toxic", "is_flagged": False}
                
            model_out = _toxic_pipeline(cleaned)[0]
            label_pred = model_out['label'].lower() # e.g. 'toxic' or 'non-toxic'
            model_score = float(model_out['score'])
            
            # The model outputs a probability for the winning label.
            # Convert this to a single toxicity score between 0 and 1
            if label_pred == 'toxic':
                score = model_score
            else:
                score = 1.0 - model_score

            # ── AI CALIBRATION (SMOOTHING) ───────────────────
            # Deep Learning (MLP) can hallucinate on small inputs.
            # If the model thinks it's toxic, but there are NO toxic keywords at all, 
            # we forcefully penalize the score to prevent false positives on normal conversation.
            if score >= 0.5 and not has_toxic_keyword:
                score = score * 0.4  # Drastically reduce confidence if no bad words exist
            
            if score < 0.5:
                score = (score ** 2) / 2  # Squaring makes low numbers even lower
            
            score = max(0.0, min(1.0, score))
            label = "toxic" if score >= 0.5 else "non-toxic"
            is_flagged = score >= TOXICITY_THRESHOLD
            return {"score": round(score, 4), "label": label, "is_flagged": is_flagged}
        except Exception as e:
            print(f"ML prediction error: {e}, falling back to keywords")

    # ── Fallback: keyword-based scoring ──────────────────────
    text_lower = text.lower()
    
    # Use word boundaries (\b) to match whole words ONLY
    # This prevents 'hello' from matching 'hell'
    keyword_hits = 0
    for kw in TOXIC_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', text_lower):
            keyword_hits += 1
            
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    excl_ratio = text.count('!') / max(len(text), 1)

    # Heuristic scoring (Hits gain MUCH more weight now)
    # 1.0 (100%) for even a single toxic word hit
    score = min(1.0, keyword_hits * 1.0 + caps_ratio * 0.5 + excl_ratio * 1.0)
    
    label = "toxic" if score >= 0.5 else "non-toxic"
    is_flagged = score >= TOXICITY_THRESHOLD

    return {"score": round(score, 4), "label": label, "is_flagged": is_flagged}


# Load model on import
load_model()
