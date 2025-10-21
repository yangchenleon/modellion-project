from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Auth
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Products
class ProductBase(BaseModel):
    product_name: Optional[str] = None
    price: Optional[str] = None
    release_date: Optional[str] = None
    article_content: Optional[str] = None
    url: str
    product_tag: Optional[str] = None
    series: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    price: Optional[str] = None
    release_date: Optional[str] = None
    article_content: Optional[str] = None
    url: Optional[str] = None
    product_tag: Optional[str] = None
    series: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    product_name: Optional[str]
    price: Optional[str]
    release_date: Optional[str]
    article_content: Optional[str]
    url: str
    product_tag: Optional[str]
    series: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int


class Page(BaseModel):
    items: List[ProductOut]
    meta: PageMeta


class ProductQuery(BaseModel):
    name: Optional[str] = Field(default=None, description="名称包含")
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    release_from: Optional[date] = None
    release_to: Optional[date] = None
    tag: Optional[str] = None
    series: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    has_images: Optional[bool] = None
    sort_by: Optional[str] = Field(default="created_at")
    sort_order: Optional[str] = Field(default="desc")
    page: int = 1
    page_size: int = 20


# Images
class ImageOut(BaseModel):
    id: int
    product_id: int
    image_filename: str
    image_hash: Optional[str]
    minio_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PresignResponse(BaseModel):
    url: str


# Import
class ImportItem(BaseModel):
    product_name: Optional[str] = None
    image_links: Optional[List[str]] = None
    product_info: Optional[dict] = None
    article_content: Optional[str] = None
    url: str
    product_tag: Optional[str] = None
    series: Optional[str] = None


class ImportReport(BaseModel):
    total: int
    created: int
    updated: int
    errors: List[str]


# Stats
class StatsOverview(BaseModel):
    products_total: int
    by_tag: dict
    by_series: dict
    with_images: int
    without_images: int
    recent: List[ProductOut]
