import os
import time
from datetime import datetime, timedelta
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RawContent
from app.db.database import AsyncSessionLocal

RETENTION_DAYS = 30
TEMP_DIR = "." # Current dir where temp audio files might be saved

async def cleanup_old_content():
    """Deletes RawContent older than RETENTION_DAYS and cleans up temp files."""
    print("---Running Storage Cleanup---")
    
    # 1. Database Cleanup
    cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Find old content count
            result = await session.execute(select(RawContent).where(RawContent.published_at < cutoff_date))
            old_content = result.scalars().all()
            count = len(old_content)
            
            if count > 0:
                print(f"Deleting {count} old content items older than {cutoff_date}")
                await session.execute(delete(RawContent).where(RawContent.published_at < cutoff_date))
            else:
                print("No old content to delete.")

    # 2. File Cleanup (Temp Audio)
    # Delete .mp3 files starting with "temp_" older than 1 hour
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith("temp_") and filename.endswith(".mp3"):
            filepath = os.path.join(TEMP_DIR, filename)
            if os.path.getmtime(filepath) < now - 3600: # 1 hour
                try:
                    os.remove(filepath)
                    print(f"Deleted old temp file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
    
    print("---Cleanup Complete---")
