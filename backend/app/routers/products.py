from __future__ import annotations

from typing import Annotated, List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status, Response
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, require_admin
from ..models import Image, Product
from ..schemas import Page, PageMeta, ProductCreate, ProductOut, ProductQuery, ProductUpdate
from ..utils import parse_price_to_int, parse_release_date

from datetime import datetime

router = APIRouter()


def _apply_filters(query, params: ProductQuery):
    if params.name:
        query = query.where(Product.product_name.ilike(f"%{params.name}%"))
    if params.tag:
        query = query.where(Product.product_tag == params.tag)
    if params.series:
        query = query.where(Product.series == params.series)
    if params.price_min is not None:
        query = query.where(Product.price_value >= params.price_min)
    if params.price_max is not None:
        query = query.where(Product.price_value <= params.price_max)
    if params.release_from is not None:
        query = query.where(Product.release_date_value >= params.release_from)
    if params.release_to is not None:
        query = query.where(Product.release_date_value <= params.release_to)
    if params.created_from is not None:
        query = query.where(Product.created_at >= params.created_from)
    if params.created_to is not None:
        query = query.where(Product.created_at <= params.created_to)
    if params.has_images is not None:
        if params.has_images:
            query = query.where(
                Product.id.in_(select(Image.product_id).group_by(Image.product_id))
            )
        else:
            query = query.where(
                ~Product.id.in_(select(Image.product_id).group_by(Image.product_id))
            )
    # sort
    sort_col = {
        "created_at": Product.created_at,
        "price": Product.price_value,
        "release_date": Product.release_date_value,
        "product_name": Product.product_name,
    }.get(params.sort_by or "created_at", Product.created_at)
    if (params.sort_order or "desc").lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    return query


@router.get("/", response_model=Page)
async def list_products(
    db: Annotated[Session, Depends(get_db)],
    name: str | None = None,
    tag: str | None = None,
    series: str | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
    release_from: str | None = None,
    release_to: str | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
    has_images: bool | None = None,
    sort_by: str | None = "created_at",
    sort_order: str | None = "desc",
    page: int = 1,
    page_size: int = 20,
) -> Page:
    def parse_dt(v: str | None):
        if not v:
            return None
        try:
            return datetime.fromisoformat(v)
        except Exception:
            return None

    params = ProductQuery(
        name=name,
        tag=tag,
        series=series,
        price_min=price_min,
        price_max=price_max,
        release_from=parse_release_date(release_from),
        release_to=parse_release_date(release_to),
        created_from=parse_dt(created_from),
        created_to=parse_dt(created_to),
        has_images=has_images,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    # base selectable
    base = select(Product)
    base = _apply_filters(base, params)

    # count
    total = db.execute(
        _apply_filters(select(func.count()).select_from(Product), params)
    ).scalar_one()

    # pagination
    offset = max((params.page - 1) * params.page_size, 0)
    items = db.execute(base.offset(offset).limit(params.page_size)).scalars().all()

    return Page(items=[ProductOut.model_validate(i) for i in items], meta=PageMeta(page=page, page_size=page_size, total=total))


@router.post("/", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def create_product(payload: ProductCreate, db: Annotated[Session, Depends(get_db)]) -> ProductOut:
    # uniqueness by url
    exists = db.query(Product).filter(Product.url == payload.url).one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="URL 已存在")
    entity = Product(
        product_name=payload.product_name,
        price=payload.price,
        release_date=payload.release_date,
        article_content=payload.article_content,
        url=payload.url,
        product_tag=payload.product_tag,
        series=payload.series,
        price_value=parse_price_to_int(payload.price),
        release_date_value=parse_release_date(payload.release_date),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return ProductOut.model_validate(entity)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: Annotated[Session, Depends(get_db)]) -> ProductOut:
    entity = db.get(Product, product_id)
    if not entity:
        raise HTTPException(status_code=404, detail="未找到")
    return ProductOut.model_validate(entity)


@router.put("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def update_product(product_id: int, payload: ProductUpdate, db: Annotated[Session, Depends(get_db)]) -> ProductOut:
    entity = db.get(Product, product_id)
    if not entity:
        raise HTTPException(status_code=404, detail="未找到")
    if payload.url and payload.url != entity.url:
        conflict = db.query(Product).filter(Product.url == payload.url).one_or_none()
        if conflict:
            raise HTTPException(status_code=400, detail="URL 已存在")
        entity.url = payload.url
    for field in [
        "product_name",
        "price",
        "release_date",
        "article_content",
        "product_tag",
        "series",
    ]:
        val = getattr(payload, field)
        if val is not None:
            setattr(entity, field, val)
    # maintain derived fields
    entity.price_value = parse_price_to_int(entity.price)
    entity.release_date_value = parse_release_date(entity.release_date)

    db.add(entity)
    db.commit()
    db.refresh(entity)
    return ProductOut.model_validate(entity)


@router.delete("/{product_id}", status_code=204, response_class=Response, dependencies=[Depends(require_admin)])
async def delete_product(product_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    entity = db.get(Product, product_id)
    if not entity:
        raise HTTPException(status_code=404, detail="未找到")
    db.delete(entity)
    db.commit()
    return Response(status_code=204)
