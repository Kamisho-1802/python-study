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

import cv2
import faiss
import numpy as np
from deepface import DeepFace

from config import DATA_DIR, DETECTOR, INDEX_DIR, INDEX_PATH, LABELS_PATH, MODEL


def _imread_unicode(path) -> np.ndarray | None:
    """日本語などを含むパスでも画像を読み込む。

    deepface（内部の OpenCV imread）は非英語文字を含むパスを弾く
    （"Input image must not have non-english characters"）。
    そこで np.fromfile + cv2.imdecode で自前に読み込み、
    パス文字列ではなく画像配列(BGR)を DeepFace.represent へ渡す。
    こうすると人物フォルダ名（＝ラベル）を日本語のまま使える。
    読み込めない（壊れている・非対応形式）場合は None を返す。
    """
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:  # noqa: BLE001
        return None


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
            img = _imread_unicode(path)
            if img is None:
                # 画像として読めない（壊れている / 非対応形式）
                print("画像を読み込めずスキップ:", path)
                continue
            try:
                reps = DeepFace.represent(
                    img, model_name=MODEL, detector_backend=DETECTOR
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
