from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import Base,engine,SessionLocal
from app.api.v1 import api_router
from app.db.seed import seed_demo
@asynccontextmanager
async def lifespan(app):
 Base.metadata.create_all(bind=engine);s=get_settings()
 if s.demo_seed:
  db=SessionLocal()
  try:seed_demo(db)
  finally:db.close()
 yield
s=get_settings();app=FastAPI(title=s.app_name,version=s.app_version,lifespan=lifespan,docs_url='/docs',openapi_url='/openapi.json')
app.add_middleware(CORSMiddleware,allow_origins=s.cors_origin_list,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(api_router)
@app.get('/')
def root():return {'name':s.app_name,'version':s.app_version,'docs':'/docs','health':'/api/v1/health'}
