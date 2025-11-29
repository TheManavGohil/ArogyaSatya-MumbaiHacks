from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import CanonicalClaim
from app.db.database import AsyncSessionLocal
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from collections import Counter

class TrendAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    async def analyze_trends(self, top_n=5):
        """
        Analyzes CanonicalClaims to find trending topics using clustering.
        Returns a list of trend clusters with representative claims.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(CanonicalClaim))
            claims = result.scalars().all()
            
        if not claims:
            return []
            
        claim_texts = [c.text for c in claims]
        
        # If too few claims, just return them as individual trends
        if len(claim_texts) < 3:
            return [{"topic": txt, "count": 1} for txt in claim_texts]
            
        # 1. Vectorize
        try:
            X = self.vectorizer.fit_transform(claim_texts)
        except ValueError:
            # Handle empty vocabulary or other vectorizer errors
            return [{"topic": txt, "count": 1} for txt in claim_texts]

        # 2. Cluster (K-Means)
        # Determine K dynamically (e.g., sqrt of N/2, max 10)
        num_clusters = min(max(2, int(len(claim_texts) / 2)), 10)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(X)
        
        # 3. Group and Summarize
        clusters = {}
        for i, label in enumerate(kmeans.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(claim_texts[i])
            
        trends = []
        for label, texts in clusters.items():
            # Find representative text (closest to center? or just most frequent words?)
            # For simplicity, just take the first one or the longest one
            representative = max(texts, key=len)
            trends.append({
                "topic": representative,
                "count": len(texts),
                "examples": texts[:3]
            })
            
        # Sort by count
        trends.sort(key=lambda x: x["count"], reverse=True)
        
        return trends[:top_n]
