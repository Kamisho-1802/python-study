"""プロジェクト全体で共有する定数。

【最重要】index 作成（build_index.py）と検索（search.py）で
MODEL / DETECTOR が一致していないと、まともな結果が出ない。
変更するときは必ずこの1ファイルだけを直し、index を作り直すこと。
"""

from pathlib import Path

# 埋め込みモデル（512次元）。途中で変えない。
MODEL = "Facenet512"

# 顔検出バックエンド。精度重視で retinaface。
DETECTOR = "retinaface"

# プロジェクトのルート（このファイルの1つ上 = src/ の親）
ROOT = Path(__file__).resolve().parent.parent

# 有名人画像の置き場所: data/celebs/<人物名>/<画像>.jpg
DATA_DIR = ROOT / "data" / "celebs"

# 生成物の置き場所
INDEX_DIR = ROOT / "index"
INDEX_PATH = INDEX_DIR / "celebs.faiss"
LABELS_PATH = INDEX_DIR / "labels.json"
