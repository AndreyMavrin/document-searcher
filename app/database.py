from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from elasticsearch import Elasticsearch
from app import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

es = Elasticsearch(
    config.ELASTICSEARCH_URL,
    verify_certs=False,
    ssl_show_warn=False
)