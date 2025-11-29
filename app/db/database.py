import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from chromadb import PersistentClient
from app.core.config import settings

# PostgreSQL Setup
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    # Import models to ensure they are registered with Base.metadata
    import app.db.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ChromaDB Setup
chroma_client = PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="healthcare_claims")

def get_vector_db():
    return collection
