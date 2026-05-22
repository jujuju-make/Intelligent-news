from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass

class AIChat(Base):
    __tablename__ = "ai_chat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 建立外键，指向 user 表的 id 字段
    user_id: Mapped[int] = mapped_column(Integer)

    message: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)