import json
import os

notebook_path = r"c:\Users\aruns\Downloads\Toxicity_Escalation_ML_Project (1).ipynb"

print(f"Reading notebook: {notebook_path}")

try:
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Search for !pip install and replace it with %pip install
    changes_made = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = cell.get("source", [])
            for i, line in enumerate(source):
                if line.lstrip().startswith("!pip install"):
                    source[i] = line.replace("!pip install", "%pip install", 1)
                    changes_made += 1

    if changes_made > 0:
        with open(notebook_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1)
        print(f"✅ Success! Replaced {changes_made} instances of '!pip install' with '%pip install'.")
        print("The warnings in VS Code should disappear momentarily.")
    else:
        print("No '!pip install' found. It might have already been fixed!")

except Exception as e:
    print(f"❌ Error: {e}")
