# 有名人そっくり判定アプリ（facematch_ML）

顔の埋め込み（embedding）+ 最近傍探索で「あなたは誰に似ているか」を判定する学習用アプリ。

現在の進捗: **フェーズ2まで**（インデックス作成まで）。

## セットアップ（フェーズ0）

```bash
cd basic_03/facematch_ML

# 仮想環境を作る
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 依存をインストール
pip install -r requirements.txt
```

プロンプト先頭に `(.venv)` が出ているか毎回確認すること。

動作確認:

```bash
python -c "from deepface import DeepFace; print('ok')"
```

> 初回実行時、deepface はモデルの重みを自動ダウンロードする（ネットワーク必要）。

## フェーズ1 — 埋め込みを理解する

`data/` に自分の顔写真2枚（`me_1.jpg`, `me_2.jpg`）を置いて実行:

```bash
python src/explore_embeddings.py
```

- 同一人物2枚で `distance` が小さく、別人で大きくなることを確認する。
- ベクトルの次元数が 512 と表示されることを確認する。

## フェーズ2 — 有名人ベクトルDBを作る

`data/celebs/<人物名>/*.jpg` の形で公開データセット（ライセンス確認済み）を配置して実行:

```bash
python src/build_index.py
```

生成物:
- `index/celebs.faiss`
- `index/labels.json`

`登録ベクトル数` が用意した画像枚数（顔検出失敗分を除く）と一致すれば完了。

## 重要メモ

- モデル/検出器の定数は `src/config.py` に集約。**フェーズ2と以降で変えないこと。**
- 正規化（`normalize_L2`）はインデックス側・検索側の両方で行う。
- `data/` と `index/` は `.gitignore` 済み（容量・プライバシーのため Git に入れない）。

## ディレクトリ

```
facematch_ML/
├── requirements.txt
├── .gitignore
├── data/celebs/       # data/celebs/<人物名>/<画像>.jpg
├── index/             # 生成物（celebs.faiss, labels.json）
├── src/
│   ├── config.py            # モデル等の共通定数
│   ├── explore_embeddings.py# フェーズ1
│   └── build_index.py       # フェーズ2
├── web/               # フェーズ4用（未着手）
└── deploy/            # フェーズ5用（未着手）
```
