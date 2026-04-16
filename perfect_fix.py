import os
import shutil
import subprocess
import json

root_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(root_dir, "frontend")

print("====================================================")
print("🚀 FOOLPROOF FINAL FIX: Cleaning your project...")
print("====================================================")

# 1. Agreesively Clean the poisoning root directory
for filename in ["node_modules", "package.json", "package-lock.json"]:
    path = os.path.join(root_dir, filename)
    if os.path.exists(path):
        try:
            print(f"Removing poisoning file: {path}...")
            # Use Windows native commands for force delete (handling locked files better)
            if os.path.isdir(path):
                subprocess.run(f'rmdir /s /q "{path}"', shell=True)
            else:
                os.remove(path)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove {filename}. (Probably in use).")

# 2. Fix the Frontend .env (Disable Source Maps to prevent 3D library crashes)
env_path = os.path.join(frontend_dir, ".env")
sourcemap_config = "GENERATE_SOURCEMAP=false\n"
try:
    with open(env_path, 'a+') as f:
        f.seek(0)
        content = f.read()
        if "GENERATE_SOURCEMAP" not in content:
            f.write(sourcemap_config)
            print("✅ Added GENERATE_SOURCEMAP=false to frontend/.env")
except Exception as e:
    print(f"⚠️ Warning: Could not update .env: {e}")

# 3. Ensure frontend/package.json is perfect
package_json_path = os.path.join(frontend_dir, "package.json")
try:
    with open(package_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Force the tailwind stable version
    data["dependencies"]["tailwindcss"] = "^3.4.17"
    
    with open(package_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("✅ Verified stable Tailwind v3 in frontend/package.json")
except Exception as e:
    print(f"Error checking package.json: {e}")

# 4. Final npm install in the correct place
print("\n📦 FINAL INSTALLATION in the frontend folder...")
result = subprocess.run("npm install --legacy-peer-deps", cwd=frontend_dir, shell=True)

if result.returncode == 0:
    print("\n✅✅ PERFECT FIX APPLIED SUCCESSFULY!")
    print("\n🎉 HOW TO RUN:")
    print("1. Click your terminal and press Ctrl+C to stop anything currently running.")
    print("2. Type: cd frontend")
    print("3. Type: npm start")
    print("\nWait 10 seconds. Your browser will open to the beautiful 3D dashboard!")
else:
    print("\n❌ npm install failed. Please ensure you have no other npm terminals open.")
