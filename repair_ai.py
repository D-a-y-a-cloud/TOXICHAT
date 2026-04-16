import os
import subprocess
import sys

# Paths
root_dir = os.path.dirname(os.path.abspath(__file__))
train_script = os.path.join(root_dir, "train_model.py")
models_dir = os.path.join(root_dir, "models")

print("====================================================")
print("🔧 TOXICHAT AI REPAIR & RE-LINKER")
print("====================================================")

# 1. Clean old models
print("🧹 Step 1: Removing old binary-incompatible models...")
for f in ["model.pkl", "tfidf_vectorizer.pkl"]:
    p = os.path.join(models_dir, f)
    if os.path.exists(p):
        try:
            os.remove(p)
            print(f"   Deleted: {f}")
        except Exception as e:
            print(f"   Error deleting {f}: {e}")

# 2. Run training locally
print("\n🧠 Step 2: Retraining AI specifically for your computer...")
print("   (This ensures 100% compatibility with your Python version)")
print("----------------------------------------------------")

try:
    # Run the training script via the current python interpreter
    result = subprocess.run([sys.executable, train_script], capture_output=False, text=True)
    if result.returncode == 0:
        print("----------------------------------------------------")
        print("✅ AI SUCCESSFULLY RE-TRAINED!")
    else:
        print("\n❌ Error during retraining. Please check the logs above.")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Execution error: {e}")
    sys.exit(1)

# 3. Final Verification
print("\n🔗 Step 3: Verifying final link...")
model_path = os.path.join(models_dir, "model.pkl")
if os.path.exists(model_path):
    print("✅ SUCCESS: AI model is now linked and active!")
    print("\n🚀 RESTART your backend (the 'backend_link.py' window) to load the new AI!")
else:
    print("❌ FAILED: Model file was not generated.")

print("====================================================")
