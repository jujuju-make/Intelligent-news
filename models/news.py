from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Index
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        comment="更新时间"
    )

class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="分类ID"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name}, sort_order={self.sort_order}>"

class News(Base):
    __tablename__ = "news"

    __table_args__ = (
        Index('fk_news_category_idx','category_id'),
        Index('idx_publish_time', 'publish_time')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="新闻标题")
    description: Mapped[str] = mapped_column(String(500), comment="新闻概述")
    content: Mapped[str] = mapped_column(String(10000), nullable=False, comment="新闻内容")
    image: Mapped[str] = mapped_column(String(50), comment="图片")
    author: Mapped[str] = mapped_column(String(50), nullable=False, comment="新闻作者")
    category_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, comment="")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), comment="发布时间")
