import asyncio
from typing import List
from datetime import datetime
from twikit import Client
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class TwitterScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="Twitter", base_url="https://twitter.com")
        self.client = Client('en-US')
        # Ensure cookies are loaded. In a real app, you might want to do this more robustly.
        try:
            self.client.load_cookies('cookies_converted.json')
        except Exception as e:
            print(f"Warning: Could not load Twitter cookies: {e}")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []
        try:
            # Search for healthcare related terms directly to be efficient
            # query = '("vaccine" OR "virus" OR "health" OR "disease") since:2025-10-30 lang:en'
            # Using a broader query and letting the manager filter, or specific query here.
            # Let's use a specific query to get relevant tweets.
            query = '(vaccine OR virus OR health OR disease OR pandemic) lang:en'
            
            tweets = await self.client.search_tweet(query, "Latest")
            
            for tweet in tweets:
                # Convert tweet to ScrapedArticle
                # Tweet object structure depends on twikit version, assuming standard attributes
                content = tweet.text
                url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                
                # Parse created_at if possible, otherwise use now
                # tweet.created_at is usually a string, might need parsing
                published_at = datetime.now() 
                
                articles.append(ScrapedArticle(
                    title=f"Tweet by {tweet.user.name}", # Tweets don't have titles
                    content=content,
                    source=self.source_name,
                    url=url,
                    published_at=published_at,
                    author=tweet.user.name
                ))
                
        except Exception as e:
            print(f"Error scraping Twitter: {e}")
            
        return articles
