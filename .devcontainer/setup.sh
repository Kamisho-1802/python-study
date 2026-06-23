#!/usr/bin/env bash
#
# Codespaces/Dev Container のコンテナ作成時に自動実行されるセットアップ。
# facematch_ML を動かすために必要な準備をまとめて行う。
set -euo pipefail

echo "==> OpenCV(cv2) 用のシステムライブラリを導入"
# libgl1       : libGL.so.1 を提供（これが無いと cv2 の import が失敗する）
# libglib2.0-0 : libgthread-2.0.so.0 を提供（cv2 が後で要求しがち）
sudo apt-get update
sudo apt-get install -y --no-install-recommends libgl1 libglib2.0-0
sudo rm -rf /var/lib/apt/lists/*

# このスクリプトの場所から facematch_ML へ移動（実行場所に依存しない）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../basic_03/facematch_ML" && pwd)"
cd "$PROJECT_DIR"

echo "==> 仮想環境(.venv)を用意"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

echo "==> 依存ライブラリをインストール（数分かかります）"
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "==> セットアップ完了"
echo "    使うときは次で有効化してください:"
echo "    source basic_03/facematch_ML/.venv/bin/activate"
