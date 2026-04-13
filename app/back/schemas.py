from pydantic import BaseModel, computed_field
from typing import List, Optional
from datetime import datetime
# ============================== #
# 1.このファイル(schemas.py)の役割を大雑把に説明すると
# APIでやり取りするデータ（リクエストとレスポンス）のクラスを定義し、保証することが主な役割です。

# 2. 役割を詳細に説明すると
# ①データのバリデーション
# 例えば「start_page は絶対にintでなければならない」といったチェックを自動で行います。
# もし間違ったデータが送られてきたら、ここでエラーとして弾き返します。

# ②リクエスト用とレスポンス用のクラスの分離、ベースとなるクラスの定義
# 例えば「BookBase」は本の基本的な情報を定義するクラスで、これを「BookCreate」や「Book」などのクラスが継承しています。
# 一方「BookCreate」クラスはユーザーが本を登録するためのリクエスト用のクラスで、必須項目だけを定義します。
# また、「Book」クラスはレスポンス用のクラスで、IDや作成日時など、DBから自動で付与される項目も含めて定義します。

# ③ORM（データベースモデル）からの自動変換
# 各クラスにある Config: from_attributes = True は、
# 「SQLAlchemyなどのデータベースのオブジェクトを、そのままPydanticのデータ（=JSON）に変換していいよ」
# という意味合いです。

# ④動的なデータの追加
# @computed_field を使った total_read_pages のように、
# 「データベースには保存していないけど、返す直前に計算してAPIのレスポンスに含めたいデータ」を追加することができます。
# ただ、処理が重くなりすぎないように、動的計算処理の機能は必要最低限に留めるのがポイントです。

# 3. このプログラムがやらないこと（Schemasの範囲外のこと）
# ①データベースへの直接アクセス（CRUD操作）
# ②リクエストの受け付け・ルーティング
# ============================== #

#=========================================#
# 進捗ログ（ProgressLog）に関するクラス定義
#=========================================#
# 1. Base (共通基盤)
# ユーザーが進捗ログを作成・更新する際に必要な情報のうち、共通するデータを記述したクラス
class ProgressBase(BaseModel):
    date: str
    start_page: int
    end_page: int
    memo: Optional[str] = None
# 2. Create (登録リクエスト用)
# 進捗を新規登録する際に受け取るデータの形です。今回はBaseと全く同じ項目で良いため、そのまま継承しています。
class ProgressCreate(ProgressBase):
    pass
# 3. DB取得・レスポンス用
# データベースから取得した進捗データをフロントエンドに返す際のデータの形です。
# Baseの項目に加え、DB側で自動採番・記録される id や created_at などを追加しています。
class Progress(ProgressBase):
    id: int
    book_id: int
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True # DBから取得したオブジェクトをそのままJSONに変換するための設定

#=========================================#
# 本の登録（Book）に関するクラス定義
#=========================================#
# 1. Base (共通基盤)
# 本の登録時（リクエスト）と取得時（レスポンス）で共通して使われる基本的なデータ項目を定義します。
class BookBase(BaseModel):
    title: str
    total_pages: int
    target_date: Optional[str] = None  # 目標日が未定の場合に備えてOptionalに

    # 外部APIから取得できなかった場合に備えてOptionalにしている
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    ndl_link: Optional[str] = None
    cover_url: Optional[str] = None
    status: str = "未読"

# 2. Create (登録リクエスト用)
# ユーザーが新しい本を登録する際に、フロントエンドから受け取るデータの形です。
# Baseの項目に加え、「誰の本として登録するか」を指定するために user_id が必須になっています。
# （※この時点ではまだDBに保存されていないため、id はありません）
class BookCreate(BookBase):
    user_id: int

# 3. DB取得・レスポンス用
# データベースから取得した本データを、フロントエンドに返す際のデータの形です。
# Baseの項目に加え、DB側で自動生成される id やタイムスタンプ、紐づく進捗ログなどを追加します。
class Book(BookBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None  
    updated_at: Optional[datetime] = None  #ホーム画面の「最近の20件」の並び替えに必須！
    progress_logs: List[Progress] = []

    # APIがBookを返す時に、自動で「実質の合計ページ」を計算して含める
    @computed_field
    def total_read_pages(self) -> int:
        from .crud import calculate_total_progress
        # ログが空の場合の安全策
        if not self.progress_logs:
            return 0
        return calculate_total_progress(self.progress_logs)

    class Config:
        from_attributes = True

#=========================================#
# ユーザー（User）に関するクラス定義
#=========================================#
# 1. Base (共通基盤)
# ユーザーに関するデータで、リクエスト・レスポンス問わず共通して使う項目です。
class UserBase(BaseModel):
    username: str

# 2. Create (登録リクエスト用)
# アカウントの新規登録時に、フロントエンドから送られてくるデータの形です。
# Baseの項目(username)に加え、登録時に必須となる password をここで受け取ります。
# （※パスワードを受け取るのは「このクラスだけ」に限定します）
class UserCreate(UserBase):
    password: str

# 3. DB取得・レスポンス用
# データベースから取得したユーザー情報をフロントエンドに返す際のデータの形です。
# このクラスには password を含めていません！
# これにより、APIのレスポンスに誤ってパスワードが混入し、画面側に漏洩する事故を防いでいます。
class User(UserBase):
    id: int # DBが自動採番したユーザーID
    created_at: Optional[datetime] = None #アカウント作成日時
    books: List[Book] = []
    # 関連データの入れ子（ネスト）
    # このユーザーが登録している「本」のリスト（Bookスキーマの配列）をまとめて返します。
    # ユーザーのマイページなどを表示する際に、本の一覧も一緒に取得する際に利用。
    books: List[Book] = []

    class Config:
        from_attributes = True

        