from __future__ import annotations

import os
import tempfile
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, require_admin
from ..minio_client import md5_of_file, presigned_url, put_file, remove_object
from ..models import Image, Product
from ..schemas import ImageOut, PresignResponse

router = APIRouter()


@router.get("/product/{product_id}", response_model=List[ImageOut])
async def list_images(product_id: int, db: Annotated[Session, Depends(get_db)]) -> List[ImageOut]:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    items = db.query(Image).filter(Image.product_id == product_id).order_by(Image.created_at.desc()).all()
    return [ImageOut.model_validate(i) for i in items]


@router.post("/upload/{product_id}", response_model=ImageOut, dependencies=[Depends(require_admin)])
async def upload_image(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> ImageOut:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # save temp and compute md5
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        img_hash = md5_of_file(tmp_path)
        exists = db.query(Image).filter(Image.image_hash == img_hash).one_or_none()
        if exists:
            raise HTTPException(status_code=400, detail="图片已存在（MD5 重复）")
        object_name = f"{product_id}/{img_hash}_{file.filename}"
        minio_path = put_file(tmp_path, object_name)
        entity = Image(
            product_id=product_id,
            image_filename=file.filename,
            image_hash=img_hash,
            minio_path=object_name,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return ImageOut.model_validate(entity)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.get("/presign/{image_id}", response_model=PresignResponse)
async def get_presigned(image_id: int, db: Annotated[Session, Depends(get_db)]) -> PresignResponse:
    entity = db.get(Image, image_id)
    if not entity or not entity.minio_path:
        raise HTTPException(status_code=404, detail="图片不存在")
    url = presigned_url(entity.minio_path)
    return PresignResponse(url=url)


@router.delete("/{image_id}", status_code=204, response_class=Response, dependencies=[Depends(require_admin)])
async def delete_image(
    image_id: int,
    db: Annotated[Session, Depends(get_db)],
    delete_object: bool = False,
) -> Response:
    entity = db.get(Image, image_id)
    if not entity:
        raise HTTPException(status_code=404, detail="图片不存在")
    object_name = entity.minio_path
    db.delete(entity)
    db.commit()
    if delete_object and object_name:
        try:
            remove_object(object_name)
        except Exception:
            pass
    return Response(status_code=204)
