import os
import shutil
import subprocess

root_dir = os.path.dirname(os.path.abspath(__file__))
bad_node_modules = os.path.join(root_dir, "node_modules")
bad_package_json = os.path.join(root_dir, "package.json")
bad_package_lock = os.path.join(root_dir, "package-lock.json")

print("==================================================")
print("🧹 STAGE 1: Cleaning up accidental root installs...")
print("==================================================")

for path in [bad_node_modules, bad_package_json, bad_package_lock]:
    if os.path.exists(path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
            print(f"Removed: {path}")
        except Exception as e:
            print(f"Warning: Could not remove {path}. It might be in use.")

frontend_dir = os.path.join(root_dir, "frontend")

print("\n==================================================")
print("📦 STAGE 2: Installing in the CORRECT folder...")
print("==================================================")
cmd = "npm install tailwindcss postcss autoprefixer framer-motion three @react-three/fiber@8 @react-three/drei@9 lucide-react --legacy-peer-deps"

print(f"Running inside '{frontend_dir}':\n> {cmd}\nThis might take a minute...")

# Run the installation inside the frontend directory
result = subprocess.run(cmd, cwd=frontend_dir, shell=True)

if result.returncode == 0:
    print("\n✅ Install successful! Now initializing Tailwind...")
    subprocess.run("npx tailwindcss init -p", cwd=frontend_dir, shell=True)
    print("\n🎉 ALL DONE! Please completely stop your React server, then run `npm start` again!")
else:
    print("\n❌ npm install failed. Please check the errors above.")
