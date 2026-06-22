# celeb-lookalike — 有名人そっくり判定アプリ

顔の埋め込み（embedding）と最近傍探索で「あなたは誰に似ているか」を判定する Web アプリ。

現在の進捗: **フェーズ4まで**（撮影フロントまで）。フェーズ5（AWS デプロイ）は未着手。

## 構成

```
celeb-lookalike/
├── requirements.txt
├── data/celebs/<人物名>/<画像>.jpg   # 有名人画像（Git 管理外）
├── index/                            # 生成物: celebs.faiss / labels.json（Git 管理外）
├── src/
│   ├── config.py             # モデル等の定数（1か所に集約）
│   ├── explore_embeddings.py # フェーズ1: 埋め込みの理解
│   ├── build_index.py        # フェーズ2: ベクトルDB作成
│   ├── search.py             # フェーズ3: 検索ロジック
│   └── main.py               # フェーズ3: FastAPI アプリ
├── web/index.html            # フェーズ4: 撮影フロント
└── deploy/notes.md           # フェーズ5: AWS 手順メモ（未着手）
```

## セットアップ（フェーズ0）

PowerShell（Windows）の場合:

```powershell
# 仮想環境を作成（Python 3.11）
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1     # PowerShell の場合
# .venv\Scripts\activate.bat   # cmd の場合
pip install -r requirements.txt
```

macOS / Linux の場合:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

プロンプト先頭に `(.venv)` が出ているか毎回確認すること。

> 初回実行時、deepface はモデルの重みを自動ダウンロードする（ネットワーク必要）。

## 使い方

```bash
# フェーズ1: 埋め込みを理解する（data/ に me_1.jpg / me_2.jpg / celeb.jpg を置く）
python src/explore_embeddings.py

# フェーズ2: 有名人ベクトルDBを作る（data/celebs/<人物名>/ に画像を置いてから）
python src/build_index.py

# フェーズ3-4: API + フロントを起動
uvicorn src.main:app --reload --port 8000
# ブラウザで http://localhost:8000/  （撮影フロント）  または  /docs （API ドキュメント）
```

- `/` … カメラで撮影して判定する画面（フェーズ4）
- `/docs` … FastAPI 自動ドキュメント。`/analyze` に画像を直接アップロードしてテストできる
- 顔のない画像・複数人の画像では `{"error": "..."}` が返る

## 重要な注意

- **モデルを途中で変えない**: index 作成と検索で `config.py` の `MODEL`/`DETECTOR` を必ず一致させる。
- **正規化を両側で行う**: index 側・クエリ側の両方で `normalize_L2`（コサイン類似度のため）。
- **撮影画像は保存しない**: 一時ファイルで処理し、判定後に自動削除する（プライバシー要件）。
- **getUserMedia は HTTPS か localhost のみ**: スマホ実機テストは HTTPS が必要（フェーズ5で対応）。
- **AWS は課金注意**: フェーズ5の操作は人間が確認してから実行する。
