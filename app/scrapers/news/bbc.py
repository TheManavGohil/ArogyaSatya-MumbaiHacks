import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class BBCScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="BBC News", base_url="https://www.bbc.com")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links
                for h2 in soup.find_all('h2', {'data-testid': 'card-headline'}):
                    title = h2.get_text(strip=True)
                    link_tag = h2.find_parent('a')
                    if not link_tag:
                        continue
                        
                    href = link_tag.get('href')
                    if not href:
                        continue
                        
                    if not href.startswith('http'):
                        url = self.base_url + href
                    else:
                        url = href

                    if '/av/' in url or '/live/' in url:
                        continue

                    # Fetch full content
                    content, images = await self.scrape_article_content(url)
                    
                    articles.append(ScrapedArticle(
                        title=title,
                        content=content,
                        source=self.source_name,
                        url=url,
                        published_at=datetime.utcnow(),
                        images=images[:5]
                    ))
                    
            except Exception as e:
                print(f"Error scraping BBC: {e}")
                
        return articles

    async def scrape_article_content(self, url: str) -> tuple[str, List[str]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                text = ""
                images = []
                
                article_body = soup.find('article')
                if article_body:
                    # Extract text
                    paragraphs = article_body.find_all('div', {'data-component': 'text-block'})
                    if not paragraphs:
                         paragraphs = article_body.find_all('p')
                    text = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
                    
                    # Extract images
                    img_tags = article_body.find_all('img')
                    for img in img_tags:
                        src = img.get('src')
                        if src and src.startswith('http'):
                            images.append(src)
                            
                return text, images
            except Exception:
                return "", []
