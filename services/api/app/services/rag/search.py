import re
from sqlalchemy.orm import Session
from app.models import DocumentChunk,Document

def chunk_text(text:str,chunk_size:int=800,overlap:int=100):
 return [text[i:i+chunk_size] for i in range(0,len(text),chunk_size-overlap)] if text.strip() else []
def simple_rag_search(db:Session,query:str,limit:int=5):
 words={w.lower() for w in re.findall(r'\w+',query) if len(w)>2}; hits=[]
 for c in db.query(DocumentChunk).limit(2000).all():
  cw={w.lower() for w in re.findall(r'\w+',c.content)}; score=len(words&cw)/max(len(words),1)
  if score:
   d=db.query(Document).filter(Document.id==c.document_id).first(); hits.append((score,{"score":round(score,4),"chunk_index":c.chunk_index,"content":c.content[:800],"document_id":str(c.document_id),"document_title":d.title if d else None}))
 return [x[1] for x in sorted(hits,key=lambda x:x[0],reverse=True)[:limit]]
