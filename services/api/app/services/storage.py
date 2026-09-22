"""MinIO / local fallback object storage."""
from __future__ import annotations
import io
from pathlib import Path
from app.core.config import get_settings

_local_root = Path("/tmp/jarvis-uploads")


def ensure_bucket() -> None:
    settings = get_settings()
    try:
        import boto3
        from botocore.client import Config

        client = boto3.client(
            "s3",
            endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        existing = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
        if settings.minio_bucket not in existing:
            client.create_bucket(Bucket=settings.minio_bucket)
    except Exception:
        _local_root.mkdir(parents=True, exist_ok=True)


def put_object(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    settings = get_settings()
    try:
        import boto3
        from botocore.client import Config

        client = boto3.client(
            "s3",
            endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        client.put_object(Bucket=settings.minio_bucket, Key=key, Body=data, ContentType=content_type)
        return key
    except Exception:
        _local_root.mkdir(parents=True, exist_ok=True)
        path = _local_root / key.replace("/", "_")
        path.write_bytes(data)
        return key


def get_object(key: str) -> bytes:
    settings = get_settings()
    try:
        import boto3
        from botocore.client import Config

        client = boto3.client(
            "s3",
            endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        obj = client.get_object(Bucket=settings.minio_bucket, Key=key)
        return obj["Body"].read()
    except Exception:
        path = _local_root / key.replace("/", "_")
        return path.read_bytes()
