import uuid
from pathlib import PurePath

import boto3
from botocore.config import Config

from app.core.config import settings

S3_CLIENT_CONFIG = Config(
    signature_version="s3v4",
    s3={"addressing_style": "virtual"},
)


def s3_client():
    client_kwargs = {
        "region_name": settings.S3_REGION,
        "config": S3_CLIENT_CONFIG,
    }
    if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
        client_kwargs["aws_access_key_id"] = settings.S3_ACCESS_KEY
        client_kwargs["aws_secret_access_key"] = settings.S3_SECRET_KEY
    return boto3.client("s3", **client_kwargs)


IMAGE_EXTENSIONS = {
    "gif",
    "heic",
    "heif",
    "jpeg",
    "jpg",
    "png",
    "webp",
}


def _storage_prefix() -> str:
    return settings.S3_KEY_PREFIX.strip().strip("/")


def storage_key_prefix(car_id: int) -> str:
    prefix = _storage_prefix()
    car_path = f"{car_id}/"
    return f"{prefix}/{car_path}" if prefix else car_path


def make_storage_key(car_id: int, filename: str) -> str:
    cleaned_filename = PurePath(str(filename or "upload.jpg").replace("\\", "/")).name
    suffix = PurePath(cleaned_filename).suffix.lower().lstrip(".")
    ext = suffix if suffix in IMAGE_EXTENSIONS else "jpg"
    return f"{storage_key_prefix(car_id)}{uuid.uuid4().hex}.{ext}"


def is_storage_key_for_car(storage_key: str, car_id: int) -> bool:
    return storage_key.startswith(storage_key_prefix(car_id))


def public_url_for_key(storage_key: str) -> str:
    return f"https://{settings.S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{storage_key}"


def presign_put(storage_key: str, content_type: str) -> str:
    c = s3_client()
    return c.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.S3_BUCKET,
            "Key": storage_key,
            "ContentType": content_type,
        },
        ExpiresIn=60 * 10,
    )


def delete_object(storage_key: str) -> None:
    c = s3_client()
    c.delete_object(Bucket=settings.S3_BUCKET, Key=storage_key)
