from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Image, Product
from ..schemas import ProductOut, StatsOverview

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@router.get("/stats/overview", response_model=StatsOverview)
async def stats_overview(db: Annotated[Session, Depends(get_db)], top: int = 10) -> StatsOverview:
    total = db.execute(select(func.count()).select_from(Product)).scalar_one()
    with_img = db.execute(select(func.count(func.distinct(Image.product_id)))).scalar_one()
    by_tag_rows = db.execute(select(Product.product_tag, func.count()).group_by(Product.product_tag)).all()
    by_series_rows = db.execute(select(Product.series, func.count()).group_by(Product.series)).all()
    recent_items = (
        db.query(Product).order_by(Product.created_at.desc()).limit(top).all()
    )
    return StatsOverview(
        products_total=total,
        by_tag={k or "": v for k, v in by_tag_rows},
        by_series={k or "": v for k, v in by_series_rows},
        with_images=with_img,
        without_images=max(total - with_img, 0),
        recent=[ProductOut.model_validate(i) for i in recent_items],
    )
