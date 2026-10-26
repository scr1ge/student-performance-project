from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

SEED = 42
SOURCE_URL = "https://www.kaggle.com/datasets/lainguyn123/student-performance-factors"

def split_data(root):
    root = Path(root)
    raw = root / "data/raw/StudentPerformanceFactors.csv"
    raw_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    df = pd.read_csv(raw)
    order = np.random.default_rng(SEED).permutation(len(df))
    n_base = int(len(df) * 0.60)
    groups = [("data/base/base.csv", order[:n_base])]
    for i, ids in enumerate(np.array_split(order[n_base:], 4), 1):
        groups.append((f"data/incoming/batch_{i:02d}.csv", ids))
    manifest = []
    for relative, ids in groups:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        df.iloc[ids].to_csv(path, index=False, lineterminator="\n")
        manifest.append({"file": relative, "rows": len(ids),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    ids = [int(i) for _, part in groups for i in part]
    assert len(ids) == len(set(ids)) == len(df)
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == raw_hash
    result = {"seed": SEED, "source_url": SOURCE_URL,
              "raw_sha256": raw_hash, "raw_rows": len(df),
              "columns": list(df.columns), "files": manifest,
              "row_indices": {name: [int(i) for i in part] for name, part in groups}}
    path = root / "data/manifests/split_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return pd.DataFrame(manifest)

if __name__ == "__main__":
    print(split_data(Path(__file__).resolve().parents[1]).to_string(index=False))
