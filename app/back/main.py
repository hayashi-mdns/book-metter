from fastapi import FastAPI
from .database import engine
from . import models
from .routers import users, books, auth 

# ============================== #
# 1. このファイル(main.py)の役割
# アプリケーションの「総合受付（エントリーポイント）」です。
# サーバーを起動した際に一番最初に読み込まれ、全体の初期設定を行います。

# 2. なにをしている？
# ① データベースの初期化: models.py の設計図をもとにテーブルを作成します。
# ② アプリの起動: FastAPIの本体（app）を立ち上げます。
# ③ ルーティングの振り分け: リクエストを各専門のファイル（routers）に委譲します。
# ============================== #

# データベースのテーブル作成（すでに存在する場合はスキップされる）
models.Base.metadata.create_all(bind=engine)

# FastAPIのインスタンスを作成します。これがアプリケーションの本体になります。
app = FastAPI()

# --- ルーターの登録 ---
# ここで各ファイルの router を登録することで、URLごとに処理を別ファイルに分割できます。

# 認証関連 (login, signup, /me など)
app.include_router(auth.router)
# ユーザー関連
app.include_router(users.router)
# 本・進捗関連
app.include_router(books.router) 

# --- ヘルスチェック用のシンプルなエンドポイント ---
# サーバーが正常に起動しているかを確認するためのエンドポイントです。
@app.get("/api/health")
def health_check():
    return {"status": "ok"}