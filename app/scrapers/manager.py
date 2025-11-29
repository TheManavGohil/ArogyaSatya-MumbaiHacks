import asyncio
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import RawContent
from app.scrapers.news.bbc import BBCScraper
from app.scrapers.news.cnn import CNNScraper
from app.scrapers.news.hindustan_times import HTScraper
from app.scrapers.news.reuters import ReutersScraper
from app.scrapers.news.nyt import NYTScraper
from app.scrapers.news.al_jazeera import AlJazeeraScraper
from app.scrapers.news.toi import TOIScraper
from app.scrapers.twitter_scraper import TwitterScraper

HEALTHCARE_KEYWORDS = [
    "virus", "vaccine", "disease", "health", "doctor", "hospital", 
    "pandemic", "epidemic", "medicine", "treatment", "cure", "symptom",
    "infection", "who", "cdc", "medical", "patient", "drug", "pharma"
]

class ScraperManager:
    def __init__(self):
        self.scrapers = [
            BBCScraper(),
            CNNScraper(),
            HTScraper(),
            ReutersScraper(),
            NYTScraper(),
            AlJazeeraScraper(),
            TOIScraper(),
            TwitterScraper()
        ]

    def is_healthcare_related(self, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in HEALTHCARE_KEYWORDS)

    async def run_all_scrapers(self, db: AsyncSession):
        print("Starting scrape cycle...")
        for scraper in self.scrapers:
            print(f"Running {scraper.source_name} scraper...")
            try:
                articles = await scraper.scrape()
                print(f"Found {len(articles)} items from {scraper.source_name}")
                
                # Deduplicate by URL within the batch
                unique_articles = {}
                for art in articles:
                    if art.url not in unique_articles:
                        unique_articles[art.url] = art
                
                # Filter for healthcare content
                healthcare_articles = []
                for art in unique_articles.values():
                    if self.is_healthcare_related(art.title) or self.is_healthcare_related(art.content):
                        healthcare_articles.append(art)
                
                print(f"Filtered {len(healthcare_articles)} healthcare items from {scraper.source_name}")

                for scraped_article in healthcare_articles:
                    # Check if content already exists in DB
                    result = await db.execute(select(RawContent).where(RawContent.url == scraped_article.url))
                    existing_content = result.scalars().first()
                    
                    if not existing_content:
                        new_content = RawContent(
                            source_id=scraped_article.source,
                            external_id=scraped_article.url, # Use URL as external ID for now
                            url=scraped_article.url,
                            content_type="text",
                            title=scraped_article.title,
                            text_content=scraped_article.content,
                            published_at=scraped_article.published_at
                        )
                        db.add(new_content)
                        
                    # Save Images
                    for img_url in scraped_article.images:
                        # Check if image already exists
                        result_img = await db.execute(select(RawContent).where(RawContent.url == img_url))
                        existing_img = result_img.scalars().first()
                        
                        if not existing_img:
                            new_image = RawContent(
                                source_id=scraped_article.source,
                                external_id=img_url,
                                url=img_url,
                                content_type="image",
                                title=f"Image from: {scraped_article.title}",
                                text_content=f"Parent Article: {scraped_article.url}", # Link back to article
                                media_url=img_url,
                                published_at=scraped_article.published_at
                            )
                            db.add(new_image)
                
                await db.commit()
                print(f"Saved new healthcare items from {scraper.source_name}")
                
            except Exception as e:
                print(f"Error running {scraper.source_name} scraper: {e}")
                await db.rollback()
        print("Scrape cycle completed.")
