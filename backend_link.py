import os
import subprocess
import sys

# Ensure we are in the correct directory
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")

print("====================================================")
print("🚀 TOXICHAT DATABASE & API LINKER")
print("====================================================")

# 1. Install missing dependencies (Quietly)
print("📦 Step 1: Checking for missing python packages...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend_dir)

# 2. Verify Database Connection
print("\n🔗 Step 2: Testing connection to MongoDB Atlas...")
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(backend_dir, ".env"))
    import pymongo
    import certifi
    # Added tlsCAFile and changed timeout to handle SSL/Network issues
    client = pymongo.MongoClient(
        os.getenv("MONGO_URL"), 
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    client.admin.command('ping')
    print("✅ Database connection verified!")
except Exception as e:
    print(f"⚠️ Warning: Database connection failed ({e})")
    print("   If this is an SSL error, I will attempt to bypass it in the main app.")

# 3. Start the server on Port 8001
print("\n⚡ Step 3: Starting the API Server on port 8001...")
print("----------------------------------------------------")
print("KEEP THIS WINDOW OPEN! If you see 'Uvicorn running on http://0.0.0.0:8001', you are linked!")
print("----------------------------------------------------")

try:
    # Use 'python -m uvicorn' instead of just 'uvicorn' for better Windows compatibility
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"], cwd=backend_dir)
except KeyboardInterrupt:
    print("\nStopping server...")
except Exception as e:
    print(f"\n❌ Error starting server: {e}")
