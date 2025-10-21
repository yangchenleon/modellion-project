from __future__ import annotations

import json
import os
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import require_admin
from ..models import Product
from ..schemas import ImportItem, ImportReport
from ..utils import parse_price_to_int, parse_release_date

router = APIRouter()


@router.post("/json", response_model=ImportReport, dependencies=[Depends(require_admin)])
async def import_from_json(db: Annotated[Session, Depends(get_db)]) -> ImportReport:
    settings = get_settings()
    file_path = os.path.join(settings.DATA_DIR, "product_details.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="product_details.json 未找到")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        items: List[ImportItem]
        if isinstance(data, list):
            items = [ImportItem.model_validate(i) for i in data]
        else:
            items = [ImportItem.model_validate(data)]

    created = 0
    updated = 0
    errors: List[str] = []

    for idx, it in enumerate(items):
        try:
            existing = db.query(Product).filter(Product.url == it.url).one_or_none()
            if existing is None:
                entity = Product(
                    product_name=it.product_name,
                    price=(it.product_info or {}).get("価格") if it.product_info else None,
                    release_date=(it.product_info or {}).get("発売日") if it.product_info else None,
                    article_content=it.article_content,
                    url=it.url,
                    product_tag=it.product_tag,
                    series=it.series,
                )
                entity.price_value = parse_price_to_int(entity.price)
                entity.release_date_value = parse_release_date(entity.release_date)
                db.add(entity)
                created += 1
            else:
                existing.product_name = it.product_name or existing.product_name
                if it.product_info:
                    price_text = it.product_info.get("価格")
                    release_text = it.product_info.get("発売日")
                    if price_text is not None:
                        existing.price = price_text
                    if release_text is not None:
                        existing.release_date = release_text
                if it.article_content is not None:
                    existing.article_content = it.article_content
                if it.product_tag is not None:
                    existing.product_tag = it.product_tag
                if it.series is not None:
                    existing.series = it.series
                existing.price_value = parse_price_to_int(existing.price)
                existing.release_date_value = parse_release_date(existing.release_date)
                updated += 1
        except Exception as e:
            errors.append(f"index {idx}: {e}")
    db.commit()

    return ImportReport(total=len(items), created=created, updated=updated, errors=errors)
