from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from APP.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="user")  # user or admin
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user",
                                                             cascade="all, delete-orphan")

    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user",
                                                     cascade="all, delete-orphan")
