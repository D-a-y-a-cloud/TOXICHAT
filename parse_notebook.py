"""
Parse the Colab notebook and extract all code cells.
"""
import json

nb_path = r"c:\Users\aruns\Downloads\Toxicity_Escalation_ML_Project (1).ipynb"
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
for i, cell in enumerate(cells):
    cell_type = cell.get('cell_type', '')
    source = ''.join(cell.get('source', []))
    
    # Only show code cells that might be related to model training/saving
    if cell_type == 'code':
        # Check for keywords related to model training/saving
        keywords = ['model', 'fit', 'train', 'save', 'dump', 'tfidf', 'vectorizer', 'predict', 'RandomForest', 'LogisticRegression', 'SVC', 'best']
        if any(kw.lower() in source.lower() for kw in keywords):
            print(f"\n{'='*60}")
            print(f"CELL {i} (code)")
            print(f"{'='*60}")
            print(source[:2000])
            if len(source) > 2000:
                print(f"\n... [truncated, total {len(source)} chars]")
