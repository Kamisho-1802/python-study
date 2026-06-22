"""フェーズ2 — 有名人ベクトルDBを作る（インデックス作成）。

事前準備:
  data/celebs/<人物名>/*.jpg の形で有名人画像を配置する。
  公開データセット（ライセンス確認済み）を使うこと。

実行（プロジェクト直下から）:
  python src/build_index.py

生成物:
  index/celebs.faiss   … FAISS インデックス（正規化済みベクトル, 内積=コサイン類似度）
  index/labels.json    … ベクトルと同じ順番で並んだ人物名のリスト

学習メモ:
  - 正規化 + 内積 = コサイン類似度。normalize_L2 で長さを1にしてから
    内積を取ると向きの近さ（コサイン類似度）になる。検索側も同じ正規化が必要。
  - 同一人物の複数画像はそれぞれ別ベクトルとして登録してよい。
"""

import json

import faiss
import numpy as np
from deepface import DeepFace

from config import DATA_DIR, DETECTOR, INDEX_DIR, INDEX_PATH, LABELS_PATH, MODEL


def build() -> None:
    vectors: list[np.ndarray] = []
    labels: list[str] = []

    if not DATA_DIR.is_dir():
        raise SystemExit(
            f"画像ディレクトリが見つかりません: {DATA_DIR}\n"
            "data/celebs/<人物名>/*.jpg の形で画像を配置してください。"
        )

    for person_dir in sorted(p for p in DATA_DIR.iterdir() if p.is_dir()):
        name = person_dir.name
        for path in sorted(person_dir.iterdir()):
            if not path.is_file():
                continue
            try:
                reps = DeepFace.represent(
                    str(path), model_name=MODEL, detector_backend=DETECTOR
                )
            except ValueError:
                # 顔を検出できなかった画像はスキップする（本番で最も多いエラー）
                print("顔を検出できずスキップ:", path)
                continue
            vectors.append(np.array(reps[0]["embedding"], dtype="float32"))
            labels.append(name)
            print("登録:", path, "->", name)

    if not vectors:
        raise SystemExit("登録できるベクトルが1件もありませんでした。画像を確認してください。")

    mat = np.vstack(vectors).astype("float32")
    faiss.normalize_L2(mat)  # コサイン類似度のための L2 正規化
    index = faiss.IndexFlatIP(mat.shape[1])  # 内積 = 正規化済みならコサイン類似度
    index.add(mat)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False)

    print("登録ベクトル数:", index.ntotal)


if __name__ == "__main__":
    build()
