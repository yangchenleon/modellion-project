from __future__ import annotations

import hashlib
import os
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error

from .config import get_settings


def get_minio_client() -> Minio:
    s = get_settings()
    return Minio(
        s.MINIO_ENDPOINT,
        access_key=s.MINIO_ACCESS_KEY,
        secret_key=s.MINIO_SECRET_KEY,
        secure=s.MINIO_USE_SECURE,
    )


def get_bucket_name() -> str:
    return get_settings().MINIO_BUCKET


def md5_of_file(path: str) -> str:
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()


def put_file(local_path: str, object_name: str) -> str:
    client = get_minio_client()
    bucket = get_bucket_name()
    client.fput_object(bucket, object_name, local_path)
    return f"{bucket}/{object_name}"


def _normalize_object_name(minio_path: str) -> str:
    bucket = get_bucket_name()
    if minio_path.startswith(f"{bucket}/"):
        return minio_path[len(bucket) + 1 :]
    return minio_path


def presigned_url(minio_path: str, expires_seconds: int = 3600) -> str:
    client = get_minio_client()
    bucket = get_bucket_name()
    object_name = _normalize_object_name(minio_path)
    return client.presigned_get_object(bucket, object_name, expires=timedelta(seconds=expires_seconds))


def remove_object(minio_path: str) -> None:
    client = get_minio_client()
    bucket = get_bucket_name()
    object_name = _normalize_object_name(minio_path)
    client.remove_object(bucket, object_name)
