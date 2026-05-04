from sqlalchemy import Column, Boolean, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.associationproxy import association_proxy
from .database import Base

#=========================================#
# ユーザー（User）のテーブル
#=========================================#
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owned_groups = relationship("Group", back_populates="owner_user")
    membership = relationship("Membership", back_populates="user")
    progresses = relationship("Progress", back_populates="user")

    joined_groups = association_proxy("membership", "group")

#=========================================#
# 輪講グループ（Group）のテーブル設計図
# 本（Book）のテーブル設計図を統合
#=========================================#
class Group(Base):
    __tablename__ = "groups"

# 輪講グループ（Group）
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    owner = Column(Integer, ForeignKey("users.id"))
    is_lock = Column(Boolean, default=False)
    password_hash = Column(String, nullable=True)

# 本（Book）
    title = Column(String, index=True)
    total_pages = Column(Integer)

    author = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    self_link = Column(String, nullable=True)
    api_id = Column(String)
    api_etag = Column(String)
    small_cover_url = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)

# リレーションシップ
    owner_user = relationship("User", back_populates="owned_groups")
    membership = relationship("Membership", back_populates="group")
    progresses = relationship("Progress", back_populates="group")

    members = association_proxy("membership", "user")

#=========================================#
# 輪講グループとユーザの中間テーブル
#=========================================#
class Membership(Base):
    __tablename__ = "membership"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="membership")
    group = relationship("Group", back_populates="membership")

#=========================================#
# 読書進捗ログ（Progress）のテーブル設計図
#=========================================#
class Progress(Base):
    __tablename__ = "progresses"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    memo = Column(String, nullable=True)
    url = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    start_page = Column(Integer)
    end_page = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="progresses")
    group = relationship("Group", back_populates="progresses")