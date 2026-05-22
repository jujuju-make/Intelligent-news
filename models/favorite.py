from datetime import datetime

from sqlalchemy import Index, UniqueConstraint, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.news import News
from models.users import User


class Base(DeclarativeBase):
    pass

class Favorite(Base):
    __tablename__ = 'favorite'
    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name = 'user_name_unique'),
        Index('fk_favorite_news_idx', 'news_id'),
        Index('fk_favorite_user_idx', 'user_id'),
    )

    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='收藏ID')
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    news_id:Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")