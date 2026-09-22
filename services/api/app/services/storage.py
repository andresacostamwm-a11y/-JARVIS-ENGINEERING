from pathlib import Path
from app.core.config import get_settings
ROOT=Path('/tmp/jarvis-uploads')
def _client():
 import boto3
 s=get_settings();return boto3.client('s3',endpoint_url=f"http://{s.minio_endpoint}",aws_access_key_id=s.minio_access_key,aws_secret_access_key=s.minio_secret_key)
def ensure_bucket():
 try:
  c=_client();s=get_settings();names=[b['Name'] for b in c.list_buckets().get('Buckets',[])];c.create_bucket(Bucket=s.minio_bucket) if s.minio_bucket not in names else None
 except Exception:ROOT.mkdir(parents=True,exist_ok=True)
def put_object(key,data,content_type='application/octet-stream'):
 try:_client().put_object(Bucket=get_settings().minio_bucket,Key=key,Body=data,ContentType=content_type)
 except Exception:ROOT.mkdir(parents=True,exist_ok=True);(ROOT/key.replace('/','_')).write_bytes(data)
 return key
def get_object(key):
 try:return _client().get_object(Bucket=get_settings().minio_bucket,Key=key)['Body'].read()
 except Exception:return (ROOT/key.replace('/','_')).read_bytes()
