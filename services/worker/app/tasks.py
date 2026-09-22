import os,sys
sys.path.insert(0,'/api')
from app.celery_app import celery
@celery.task(name='worker.tasks.ingest_document')
def ingest_document(document_id):
 from uuid import UUID
 from sqlalchemy import create_engine
 from sqlalchemy.orm import sessionmaker
 from app.models import Document,DocumentChunk
 from app.services.rag.search import chunk_text
 from app.services.storage import get_object
 db=sessionmaker(bind=create_engine(os.getenv('DATABASE_URL')))()
 try:
  d=db.query(Document).filter(Document.id==UUID(document_id)).first()
  if not d:return {'ok':False,'error':'not found'}
  d.status='processing';db.commit();data=get_object(d.storage_key);text=data.decode('utf-8',errors='ignore') or f'[Binary document {d.filename}; extraction COMING SOON]'
  db.query(DocumentChunk).filter(DocumentChunk.document_id==d.id).delete()
  chunks=chunk_text(text)
  for i,c in enumerate(chunks):db.add(DocumentChunk(document_id=d.id,chunk_index=i,content=c,meta={'engine':'celery-v1'}))
  d.status='ready';db.commit();return {'ok':True,'chunks':len(chunks)}
 except Exception as e:db.rollback();return {'ok':False,'error':str(e)}
 finally:db.close()
