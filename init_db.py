import asyncio
from app.db.database import init_db, engine

async def main():
    print("Creating database tables...")
    await init_db()
    print("Tables created successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
