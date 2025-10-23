from __future__ import annotations

import json
import os
import shutil
import tempfile
import zipfile
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import require_admin
from ..models import Product, Image
from ..schemas import ImportItem, ImportReport
from ..minio_client import md5_of_file, put_file
from ..utils import parse_price_to_int, parse_release_date
from ..translation import translate_product_name

router = APIRouter()


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _is_image_file(filename: str) -> bool:
    fname = filename.lower()
    return any(fname.endswith(ext) for ext in IMAGE_EXTS)


def _import_images_for_product(db: Session, base_dir: str, product_id: int) -> tuple[int, int]:
    """返回 (added, skipped) 数量。根目录下的图片标记为 is_cover=True，images/ 下为 False。"""
    added = 0
    skipped = 0

    # 根目录头像图
    for entry in os.listdir(base_dir):
        full_path = os.path.join(base_dir, entry)
        if os.path.isfile(full_path) and _is_image_file(entry):
            try:
                img_hash = md5_of_file(full_path)
                exists = db.query(Image).filter(Image.image_hash == img_hash).one_or_none()
                if exists:
                    skipped += 1
                    continue
                object_name = f"{product_id}/{img_hash}_{entry}"
                put_file(full_path, object_name)
                db.add(Image(product_id=product_id, image_filename=entry, image_hash=img_hash, minio_path=object_name, is_cover=True))
                added += 1
            except Exception:
                skipped += 1

    # 详情图目录 images/
    images_dir = os.path.join(base_dir, "images")
    if os.path.isdir(images_dir):
        for entry in sorted(os.listdir(images_dir)):
            full_path = os.path.join(images_dir, entry)
            if os.path.isfile(full_path) and _is_image_file(entry):
                try:
                    img_hash = md5_of_file(full_path)
                    exists = db.query(Image).filter(Image.image_hash == img_hash).one_or_none()
                    if exists:
                        skipped += 1
                        continue
                    object_name = f"{product_id}/{img_hash}_{entry}"
                    put_file(full_path, object_name)
                    db.add(Image(product_id=product_id, image_filename=entry, image_hash=img_hash, minio_path=object_name, is_cover=False))
                    added += 1
                except Exception:
                    skipped += 1

    db.commit()
    return added, skipped


@router.post("/json", response_model=ImportReport, dependencies=[Depends(require_admin)])
async def import_from_json(db: Annotated[Session, Depends(get_db)], include_images: bool = Query(default=True, description="是否从DATA_DIR读取并上传图片")) -> ImportReport:
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

    if include_images:
        if len(items) != 1:
            errors.append("包含多条产品时不导入图片（请单产品目录导入）")
        else:
            # 根据 URL 回查产品 ID
            it = items[0]
            product = db.query(Product).filter(Product.url == it.url).one_or_none()
            if product:
                try:
                    added_imgs, skipped_imgs = _import_images_for_product(db, settings.DATA_DIR, product.id)
                    if added_imgs == 0 and skipped_imgs == 0:
                        errors.append("未发现可导入的图片")
                except Exception as e:
                    errors.append(f"导入图片失败: {e}")
            else:
                errors.append("未找到对应产品，跳过图片导入")

    return ImportReport(total=len(items), created=created, updated=updated, errors=errors)


def _is_product_dir(path: str) -> bool:
    """判断目录是否为产品目录（包含 product_details.json）"""
    return os.path.isfile(os.path.join(path, "product_details.json"))


def _process_product_dir(db: Session, product_dir: str) -> tuple[int, int, int, int, List[str]]:
    """
    处理单个产品目录
    返回: (created, updated, images_added, images_skipped, errors)
    """
    created = 0
    updated = 0
    images_added = 0
    images_skipped = 0
    errors: List[str] = []
    
    try:
        # 读取 product_details.json
        json_path = os.path.join(product_dir, "product_details.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items: List[ImportItem]
            if isinstance(data, list):
                items = [ImportItem.model_validate(i) for i in data]
            else:
                items = [ImportItem.model_validate(data)]
        
        if len(items) != 1:
            errors.append("目录包含多条产品，跳过")
            return created, updated, images_added, images_skipped, errors
        
        it = items[0]
        
        # Upsert 产品
        existing = db.query(Product).filter(Product.url == it.url).one_or_none()
        
        # 翻译产品名称
        cn_name = None
        if it.product_name:
            cn_name = translate_product_name(it.product_name)
        
        if existing is None:
            entity = Product(
                product_name=it.product_name,
                product_name_cn=cn_name,
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
            db.commit()
            db.refresh(entity)
            created += 1
            product_id = entity.id
        else:
            existing.product_name = it.product_name or existing.product_name
            # 总是更新翻译，即使用 None（翻译失败）
            existing.product_name_cn = cn_name
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
            db.commit()
            updated += 1
            product_id = existing.id
        
        # 导入图片
        try:
            a, s = _import_images_for_product(db, product_dir, product_id)
            images_added += a
            images_skipped += s
        except Exception as e:
            errors.append(f"导入图片失败: {e}")
            
    except Exception as e:
        errors.append(f"处理失败: {e}")
    
    return created, updated, images_added, images_skipped, errors


@router.post("/zip", response_model=ImportReport, dependencies=[Depends(require_admin)])
async def import_from_zip(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> ImportReport:
    """
    批量导入：接收ZIP压缩包，遍历包含 product_details.json 的子目录并导入
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"接收到ZIP文件上传请求: {file.filename}")
    
    if not file.filename or not file.filename.endswith(('.zip', '.ZIP')):
        raise HTTPException(status_code=400, detail="仅支持 ZIP 格式")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 保存上传的文件
        zip_path = os.path.join(temp_dir, file.filename)
        with open(zip_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 解压ZIP
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 遍历所有子目录，查找包含 product_details.json 的目录
        total_created = 0
        total_updated = 0
        total_images_added = 0
        total_images_skipped = 0
        all_errors: List[str] = []
        
        for root, dirs, files in os.walk(extract_dir):
            if _is_product_dir(root):
                dir_name = os.path.basename(root)
                created, updated, images_added, images_skipped, errors = _process_product_dir(db, root)
                total_created += created
                total_updated += updated
                total_images_added += images_added
                total_images_skipped += images_skipped
                for err in errors:
                    all_errors.append(f"{dir_name}: {err}")
        
        return ImportReport(
            total=total_created + total_updated,
            created=total_created,
            updated=total_updated,
            errors=all_errors,
        )
    
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
