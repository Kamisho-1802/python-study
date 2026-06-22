"""フェーズ3 — FastAPI アプリ。

起動（プロジェクト直下から）:
  uvicorn src.main:app --reload --port 8000

確認:
  http://localhost:8000/docs から /analyze に画像をアップロードしてテストする。

プライバシー要件（第11章）:
  撮影画像はメモリ/一時ファイルで処理し、サーバに永続保存しない。
  NamedTemporaryFile の with を抜けると一時ファイルは自動削除される。
"""

import os
import shutil
import sys
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles

# このファイルのあるディレクトリを import パスに加え、search を読めるようにする
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search import find_lookalike  # noqa: E402

app = FastAPI(title="Celebrity Lookalike")


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """アップロードされた画像を判定し、似ている有名人を JSON で返す。

    どんな失敗でも 500（HTMLのトレースバック）で落とさず、必ず JSON を返す。
    こうしておくと、フロント側は常に res.json() でき、原因が画面に出る。
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp.flush()
            result = find_lookalike(tmp.name, k=3)  # with を抜けると一時ファイルは自動削除
        return {"matches": result}
    except FileNotFoundError:
        # インデックス未生成（フェーズ2をまだ実行していない）
        return {
            "matches": {
                "error": "インデックスがありません。先に python src/build_index.py を実行してください"
            }
        }
    except Exception as e:  # noqa: BLE001
        # 想定外の例外も握りつぶさず、理由を JSON で返す（サーバは落とさない）
        return {"matches": {"error": f"判定に失敗しました: {type(e).__name__}: {e}"}}


# フェーズ4の web/ を配信する（まだ index.html が無い場合は / は 404 になる）
_WEB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web"
)
app.mount("/", StaticFiles(directory=_WEB_DIR, html=True), name="web")
