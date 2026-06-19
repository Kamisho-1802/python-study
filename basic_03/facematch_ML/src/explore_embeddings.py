"""フェーズ1 — 顔の埋め込みを理解する。

使い方:
  data/ 配下に自分の顔写真2枚（me_1.jpg, me_2.jpg）などを置いてから実行する。

    python src/explore_embeddings.py

学習メモ:
  - 埋め込み(embedding): 顔画像を512個の数値ベクトルに変換したもの。
    同じ人は近く、別人は遠く配置されるよう学習済みモデルが作る。
  - distance が小さい = 似ている。
  - represent は顔が複数写っているとベクトルを複数返す。1人だけの写真を使う。
"""

import argparse

from deepface import DeepFace

from config import DETECTOR, MODEL


def compare(img1: str, img2: str) -> None:
    """2枚の顔の類似度を表示する。"""
    result = DeepFace.verify(
        img1_path=img1,
        img2_path=img2,
        model_name=MODEL,
        detector_backend=DETECTOR,
    )
    print("distance:", result["distance"], "same person?:", result["verified"])


def show_embedding(img: str) -> None:
    """生の埋め込みベクトルの次元数を表示する（512になるはず）。"""
    rep = DeepFace.represent(
        img_path=img,
        model_name=MODEL,
        detector_backend=DETECTOR,
    )
    print("検出された顔の数:", len(rep))
    print("ベクトルの次元数:", len(rep[0]["embedding"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="顔の埋め込みを理解する（フェーズ1）")
    parser.add_argument("--img1", default="data/me_1.jpg", help="比較する画像1")
    parser.add_argument("--img2", default="data/me_2.jpg", help="比較する画像2")
    args = parser.parse_args()

    print("=== (1) 2枚の顔の類似度 ===")
    compare(args.img1, args.img2)

    print("\n=== (2) 埋め込みベクトル ===")
    show_embedding(args.img1)


if __name__ == "__main__":
    main()
