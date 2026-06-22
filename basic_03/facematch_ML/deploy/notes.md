# フェーズ5 — AWS デプロイ手順メモ

> ⚠️ **このフェーズは課金が発生します。** 各 AWS 操作は実行前に必ず人間が確認すること。
> 鍵・パスワード・課金の確定操作は人間が行う。Claude には実行させない。

ローカル（フェーズ1〜4）は無料。AWS は完成後に最小構成で試す。

---

## 0. 全体像

```
ローカルで作った index/（celebs.faiss + labels.json）
        │  ① アップロード
        ▼
   S3 バケット（保管庫）
        │  ② EC2 起動時に取得（IAM ロール経由・鍵を書かない）
        ▼
   EC2（Ubuntu）でアプリを実行（uvicorn / gunicorn）
        │  ③ HTTPS で公開
        ▼
   スマホのブラウザ（getUserMedia は HTTPS 必須）
```

- **S3 = 保管**、**EC2 = 実行**。GPU 不要（CPU で動く）。
- 料金の大半は「EC2 の起動時間」と「S3 保管料」。**触らないときは EC2 を停止**。

---

## 1. 【最優先】予算アラートを設定（AWS Budgets）

何よりも先に行う。想定外の課金を早期に検知するため。

1. AWS マネジメントコンソール → **Billing and Cost Management** → **Budgets**。
2. **Create budget** → テンプレート「Monthly cost budget」。
3. 予算額（例: **$5/月**）を設定。
4. しきい値（例: 実績 80% / 100%）でメール通知。通知先に自分のメールを設定。

✅ **完了条件**: 予算超過時にメールが届く設定になっている。

---

## 2. S3 バケットを作成し index/ をアップロード

S3 はオブジェクトストレージ（= ファイル置き場）。

```bash
# バケット名は世界で一意。<your-unique-name> を置き換える
aws s3 mb s3://<your-unique-name>-celeb-index --region ap-northeast-1

# ローカルの index/ を同期（celebs.faiss と labels.json）
aws s3 sync index/ s3://<your-unique-name>-celeb-index/index/
```

- バケットは**公開しない**（デフォルトのブロックパブリックアクセスのまま）。
- `data/celebs/`（元画像）は容量が大きければアップロード任意。インデックスさえあれば検索は動く。

✅ **完了条件**: `aws s3 ls s3://<バケット名>/index/` で 2 ファイルが見える。

---

## 3. IAM ロールを作成（EC2 に S3 読み取り権限を渡す）

> **アクセスキーをコードや Git に絶対に置かない。** EC2 には IAM ロールで権限を渡す。

1. IAM → **Roles** → **Create role**。
2. 信頼されたエンティティ: **AWS service** → **EC2**。
3. ポリシー: まずは **AmazonS3ReadOnlyAccess**（学習用。慣れたら対象バケットだけに絞る）。
4. ロール名: 例 `celeb-ec2-s3-readonly`。

絞り込み版インラインポリシー（おすすめ・対象バケットのみ）:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::<your-unique-name>-celeb-index",
        "arn:aws:s3:::<your-unique-name>-celeb-index/*"
      ]
    }
  ]
}
```

✅ **完了条件**: ロール `celeb-ec2-s3-readonly` が作成済み。

---

## 4. EC2 インスタンスを起動

- **インスタンスタイプ**: `t3.medium` 以上推奨（deepface はメモリを使う。無料枠の `t2.micro` はメモリ不足になりやすい）。
- **AMI（OS）**: Ubuntu Server（LTS）。
- **IAM インスタンスプロファイル**: 手順3で作った `celeb-ec2-s3-readonly` を割り当て。
- **キーペア**: SSH 用。**秘密鍵(.pem)は人間が安全に保管**。Git に入れない。
- **セキュリティグループ**:
  - SSH(22): **自分のIPだけ**に限定。
  - アプリ(8000 など): 動作確認時のみ**自分のIPだけ**に開ける。**常時 0.0.0.0/0 で全開放しない**。

✅ **完了条件**: インスタンスが `running`、SSH で入れる。

---

## 5. EC2 上でセットアップして起動

SSH で接続してから:

```bash
# 接続（人間が秘密鍵で）
ssh -i <your-key>.pem ubuntu@<EC2のパブリックIP>

# --- 以下 EC2 内 ---
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv git \
  libgl1 libglib2.0-0          # ← OpenCV(cv2) が必要とするシステムライブラリ

# リポジトリ取得（公開リポジトリの場合）
git clone https://github.com/Kamisho-1802/python-study.git
cd python-study/basic_03/facematch_ML

# 仮想環境 + 依存
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# S3 から index/ を取得（IAM ロールがあれば鍵不要）
aws s3 sync s3://<your-unique-name>-celeb-index/index/ index/

# 起動（動作確認）
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

ブラウザで `http://<EC2のIP>:8000/` を開いて動作確認。

> 注: `libgl1 libglib2.0-0` を入れ忘れると `libGL.so.1: cannot open shared object file` で
> deepface の import が失敗する（フェーズ4で踏んだのと同じエラー）。

✅ **完了条件**: EC2 の IP で API が応答し、`/docs` や `/analyze` が動く。

---

## 6. HTTPS 化（スマホ実機で getUserMedia を使うため必須）

`getUserMedia`（カメラ）は HTTPS か localhost でしか動かない。
スマホ実機テストには HTTPS が必要。いずれか:

- **A. 開発用トンネル（手軽・おすすめの最初の一歩）**
  `cloudflared` などでトンネルを張り、HTTPS の URL を得る。独自ドメイン不要。
  ```bash
  # 例（cloudflared をインストール後）
  cloudflared tunnel --url http://localhost:8000
  ```
- **B. Nginx + Let's Encrypt（独自ドメインがある場合）**
  Nginx をリバースプロキシにし、`certbot` で証明書を取得して常時 HTTPS。

> 画像ファイル選択での判定は HTTP でも動く（フェーズ4で追加済み）。
> カメラ撮影だけは HTTPS が必須、という整理。

✅ **完了条件**: スマホ実機（HTTPS）でカメラ撮影 → 判定が通る。

---

## 7. 常駐させる（任意）

確認だけなら不要。常時稼働させたいときは:

- **systemd サービス化**（再起動後も自動起動）。
- 本番は `--reload` を付けず、`gunicorn` + `uvicorn` ワーカーで起動:
  ```bash
  pip install gunicorn
  gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 src.main:app
  ```

systemd ユニット例（`/etc/systemd/system/celeb.service`）:

```ini
[Unit]
Description=Celeb Lookalike API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/python-study/basic_03/facematch_ML
ExecStart=/home/ubuntu/python-study/basic_03/facematch_ML/.venv/bin/gunicorn \
  -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now celeb.service
```

---

## 8. 後片付け（課金を止める）★忘れない

使い終わったら必ず:

```bash
# EC2 を停止（次に使うときに再起動。EBS 保管料は少しかかる）
# → コンソール or:  aws ec2 stop-instances --instance-ids <id>

# 完全にやめるなら削除（Terminate）
# → コンソール or:  aws ec2 terminate-instances --instance-ids <id>
```

- **触っていない間は EC2 を停止**する習慣をつける。
- S3 も不要になったら中身を消してバケット削除。

✅ **完了条件**: EC2 が停止/削除され、課金が止まっている。

---

## チェックリスト（フェーズ5）

- [ ] AWS 予算アラートが有効（最初にやる）
- [ ] S3 に index/ をアップロード済み
- [ ] IAM ロールで EC2 に S3 読み取り権限（アクセスキーを書かない）
- [ ] セキュリティグループは自分のIPに限定（全開放しない）
- [ ] EC2 で `libgl1` を入れてから依存インストール
- [ ] スマホ実機（HTTPS）でカメラ判定が通る
- [ ] 使い終わったら EC2 を停止/削除

---

## 学習メモ（つまずきやすい点）

- **鍵を Git に入れない**: 認証情報は IAM ロール or 環境変数。`.pem` / `aws_credentials*` は `.gitignore` 済み。
- **t2.micro はメモリ不足**: deepface + TensorFlow は重い。`t3.medium` 以上を。
- **HTTPS 必須はカメラだけ**: ファイル選択判定は HTTP でも可（フェーズ4の改修で対応済み）。
- **停止を忘れると課金が続く**: 料金の大半は EC2 起動時間。こまめに止める。
