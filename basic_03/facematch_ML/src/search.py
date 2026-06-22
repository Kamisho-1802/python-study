"""フェーズ3 — 検索ロジック。

事前条件:
  フェーズ2（build_index.py）で index/celebs.faiss と index/labels.json を
  生成しておくこと。

学習メモ:
  - インデックス側と同じ正規化（normalize_L2）をクエリ側でも必ず行う。
    片方だけだとコサイン類似度がおかしくなる。
  - 顔が検出できない/複数いるケースを必ず処理する（本番で最も多いエラー）。
  - インデックスとラベルは初回呼び出し時に1度だけ読み込む（遅延ロード）。
"""

import json
import os
import sys

import faiss
import numpy as np
from deepface import DeepFace

# uvicorn から src.main 経由で import される場合でも `from config import` が
# 効くよう、このファイルのあるディレクトリを import パスに加える。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DETECTOR, INDEX_PATH, LABELS_PATH, MODEL  # noqa: E402

_index = None
_labels = None


def _load():
    """FAISS インデックスとラベルを1度だけ読み込む。"""
    global _index, _labels
    if _index is None:
        if not (INDEX_PATH.exists() and LABELS_PATH.exists()):
            raise FileNotFoundError(
                "インデックスが見つかりません。先にフェーズ2を実行してください: "
                "python src/build_index.py"
            )
        _index = faiss.read_index(str(INDEX_PATH))
        with open(LABELS_PATH, encoding="utf-8") as f:
            _labels = json.load(f)
    return _index, _labels


def find_lookalike(img_path: str, k: int = 3):
    """img_path の顔に似ている有名人を上位 k 人返す。

    戻り値は成功時 list[dict]、エラー時 dict（error キー）。
    """
    index, labels = _load()

    try:
        reps = DeepFace.represent(
            img_path, model_name=MODEL, detector_backend=DETECTOR
        )
    except ValueError:
        # enforce_detection=True（既定）では顔が無いと ValueError になる
        return {"error": "顔が見つかりませんでした"}

    if len(reps) == 0:
        return {"error": "顔が見つかりませんでした"}
    if len(reps) > 1:
        return {"error": "顔が複数写っています。1人で撮影してください"}

    q = np.array(reps[0]["embedding"], dtype="float32")[None, :]
    faiss.normalize_L2(q)  # インデックス側と同じ正規化（コサイン類似度のため）

    # 検索数が登録数を超えないように丸める
    k = min(k, index.ntotal)
    sims, idx = index.search(q, k)

    return [
        {"name": labels[i], "similarity": round(float(s), 4)}
        for s, i in zip(sims[0], idx[0])
        if i != -1
    ]
