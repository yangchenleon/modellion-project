from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_filename: Mapped[str] = mapped_column(Text, nullable=False)
    image_hash: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    minio_path: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    product = relationship("Product", back_populates="images")

    __table_args__ = (
        UniqueConstraint("product_id", "image_filename", name="uq_product_image_filename"),
        Index("ix_images_product_id", "product_id"),
    )
