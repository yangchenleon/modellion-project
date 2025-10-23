from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[Optional[str]] = mapped_column(Text)
    product_name_cn: Mapped[Optional[str]] = mapped_column(Text)  # 中文翻译
    price: Mapped[Optional[str]] = mapped_column(Text)
    release_date: Mapped[Optional[str]] = mapped_column(Text)
    article_content: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    product_tag: Mapped[Optional[str]] = mapped_column(Text)
    series: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # minimal evolution for efficient filter/sort
    price_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    release_date_value: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    images: Mapped[List["Image"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_products_common", "product_name", "price", "release_date", "product_tag", "series", "created_at"),
        Index("ix_products_price_value", "price_value"),
        Index("ix_products_release_date_value", "release_date_value"),
    )
