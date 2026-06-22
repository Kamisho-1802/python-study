"""フェーズ1: 顔の埋め込み（embedding）を理解するための学習スクリプト。

使い方:
  data/ 直下に次の3枚を置いてから実行する。
    - data/me_1.jpg   自分の顔（1人だけ写っているもの）
    - data/me_2.jpg   自分の別の顔写真
    - data/celeb.jpg  似ていそうな有名人の顔写真

  (.venv) PS> python src/explore_embeddings.py

確認すること:
  (1) 同一人物（me_1 と me_2）の distance は小さい
  (2) 別人（me_1 と celeb）の distance は大きい
  (3) 埋め込みの次元数が 512
"""

from pathlib import Path

from deepface import DeepFace

from config import MODEL, DETECTOR, ROOT

# data/ 直下（celebs ではなくプロジェクト直下の data/）
DATA = ROOT / "data"


def verify(path1: Path, path2: Path) -> None:
    """2枚の顔の距離（distance）と同一人物判定を表示する。"""
    result = DeepFace.verify(
        img1_path=str(path1),
        img2_path=str(path2),
        model_name=MODEL,
        detector_backend=DETECTOR,
    )
    print(
        f"{path1.name} <-> {path2.name}: "
        f"distance={result['distance']:.4f}  "
        f"same_person={result['verified']}"
    )


def show_embedding(path: Path) -> None:
    """1枚の画像から生の埋め込みベクトルを取り出し、次元数を表示する。"""
    reps = DeepFace.represent(
        img_path=str(path),
        model_name=MODEL,
        detector_backend=DETECTOR,
    )
    # represent は顔ごとにベクトルを返す（リスト）。1人だけの写真を使うこと。
    print(f"{path.name}: 検出された顔の数={len(reps)}, "
          f"ベクトルの次元数={len(reps[0]['embedding'])}")  # 512 になるはず


def main() -> None:
    me_1 = DATA / "me_1.jpg"
    me_2 = DATA / "me_2.jpg"
    celeb = DATA / "celeb.jpg"

    missing = [p.name for p in (me_1, me_2, celeb) if not p.exists()]
    if missing:
        print("次の画像が見つかりません:", ", ".join(missing))
        print(f"これらを {DATA} に置いてから実行してください。")
        return

    print("=== (1)(2) 距離の確認 ===")
    verify(me_1, me_2)   # 同一人物 -> distance 小さい・same_person=True を期待
    verify(me_1, celeb)  # 別人     -> distance 大きい・same_person=False を期待

    print("\n=== (3) 埋め込みの次元数 ===")
    show_embedding(me_1)


if __name__ == "__main__":
    main()
