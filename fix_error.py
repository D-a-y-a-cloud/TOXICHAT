import os
import json
import subprocess

root_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(root_dir, "frontend")
package_json_path = os.path.join(frontend_dir, "package.json")

print("==================================================")
print("🛠️ Fixing Tailwind Webpack Configuration")
print("==================================================")

# Update package.json safely
try:
    with open(package_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["dependencies"]["tailwindcss"] = "^3.4.17"

    with open(package_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("✅ Downgraded 'tailwindcss' to stable v3.4.17 in package.json")
except Exception as e:
    print(f"Error modifying package.json: {e}")

print("\n📦 Running 'npm install' inside the CORRECT frontend folder...")
cmd = "npm install"
result = subprocess.run(cmd, cwd=frontend_dir, shell=True)

if result.returncode == 0:
    print("\n✅ Setup completely fixed and dependencies resolved!")
    print("🎉 IMPORTANT FINAL STEP:")
    print("    Go to your terminal where 'npm start' is currently running.")
    print("    Press Ctrl+C to kill it, type 'Y', and then type 'npm start' again.")
else:
    print("\n❌ npm install failed. Please check the errors above.")
