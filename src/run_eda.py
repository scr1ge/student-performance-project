from pathlib import Path
import json, os
root = Path(__file__).resolve().parents[1]
os.chdir(root)
nb = json.loads((root / "notebooks/2practice.ipynb").read_text(encoding="utf-8"))
namespace = {}
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        code = "".join(cell["source"])
        code = code.split("from IPython.display import display, Image")[0]
        exec(compile(code, "2practice.ipynb", "exec"), namespace)
