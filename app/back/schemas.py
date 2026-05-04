from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

#=========================================#
# ユーザー（User）
#=========================================#
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

#=========================================#
# 進捗ログ（Progress）← Group より先に定義
#=========================================#
class ProgressBase(BaseModel):
    start_page: int
    end_page: int
    memo: Optional[str] = None  # models.py に合わせて "memo" に統一
    url: Optional[str] = None
    file_type: Optional[str] = None # ユーザが入力することはないかも

class ProgressCreate(ProgressBase):
    pass

class Progress(ProgressBase):
    id: int
    group_id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

#=========================================#
# 輪講グループ（Group）
# 本（Book）を統合済み
#=========================================#
class GroupBase(BaseModel):
    name: str
    owner: int
    is_lock: bool

# class Group(GroupBase): の
# target_book: Optional[Book] = None だったことを考えると、
# Book由来のフィールドはすべてNoneを許容？ 
    title: Optional[str] = None
    total_pages: Optional[int] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    description: Optional[str] = None
    self_link: Optional[str] = None
    api_id: Optional[str] = None
    api_etag: Optional[str] = None
    small_cover_url: Optional[str] = None
    cover_url: Optional[str] = None

class GroupCreate(GroupBase):
    password: str

class Group(GroupBase):
    id: int
    progresses: List[Progress] = []
    members: List[User] = []

    class Config:
        from_attributes = True

#=========================================#
# メンバーシップ（Membership）
#=========================================#
class MembershipBase(BaseModel):
    pass

class GroupMemberCreate(MembershipBase):
    pass

class GroupMember(MembershipBase):
    group_id: int
    user_id: int

    class Config:
        from_attributes = True