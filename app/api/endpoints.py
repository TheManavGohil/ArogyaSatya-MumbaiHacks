from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from sqlalchemy.future import select
from app.db.models import RawContent, CanonicalClaim, ClaimEvidence

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/trigger-scan")
async def trigger_scan(db: AsyncSession = Depends(get_db)):
    from app.scrapers.manager import ScraperManager
    manager = ScraperManager()
    await manager.run_all_scrapers(db)
    return {"status": "Scan completed"}

@router.get("/articles")
async def list_articles(db: AsyncSession = Depends(get_db)):
    # Return raw content for now, acting as "articles"
    result = await db.execute(select(RawContent).order_by(RawContent.published_at.desc()).limit(20))
    return result.scalars().all()


@router.post("/analyze/{content_id}")
async def analyze_content(content_id: int, db: AsyncSession = Depends(get_db)):
    from app.agents.agent_graph import app_graph
    
    # Fetch content
    result = await db.execute(select(RawContent).where(RawContent.id == content_id))
    content = result.scalars().first()
    
    if not content:
        return {"error": "Content not found"}
        
    # Fetch associated images
    images_result = await db.execute(select(RawContent).where(
        (RawContent.text_content.like(f"%{content.url}%")) & 
        (RawContent.content_type == "image")
    ))
    images = [img.url for img in images_result.scalars().all()]

    # Run Agent Graph
    initial_state = {
        "article_id": content_id, 
        "text": f"{content.title}\n{content.text_content}",
        "images": images,
        "claims": [],
        "verification_results": [],
        "image_analysis": [],
        "final_report": ""
    }
    
    final_state = app_graph.invoke(initial_state)
    
    # Save results to DB (Canonical Claims)
    for res in final_state["verification_results"]:
        # Check if claim already exists (Canonicalization - simple text match for now)
        claim_text = res.get("claim")
        result = await db.execute(select(CanonicalClaim).where(CanonicalClaim.text == claim_text))
        existing_claim = result.scalars().first()
        
        if not existing_claim:
            existing_claim = CanonicalClaim(
                text=claim_text,
                status=res.get("status").lower(),
                explanation=res.get("explanation"),
                confidence_score=1.0 if res.get("status") == "True" else 0.0 # Simplified
            )
            db.add(existing_claim)
            await db.flush()
        
        # Link content to claim
        # Note: We need to handle the many-to-many relationship. 
        # For simplicity in this step, we just ensure the claim exists.
        # Ideally: existing_claim.sources.append(content) 
        
        # Add Evidence
        evidence = ClaimEvidence(
            claim_id=existing_claim.id,
            source_url="Local Vector DB",
            source_reliability="unknown",
            text_snippet=res.get("explanation"), # Using explanation as snippet for now
            supports_claim=(res.get("status") == "True")
        )
        db.add(evidence)
        
    await db.commit()
    
    return {
        "status": "Analysis completed", 
        "report": final_state["final_report"],
        "verification_results": final_state["verification_results"]
    }


@router.post("/analyze-text")
async def analyze_text(text: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    from app.agents.agent_graph import app_graph
    
    # Run Agent Graph
    initial_state = {
        "article_id": None,
        "text": text,
        "claims": [],
        "verification_results": [],
        "final_report": ""
    }
    
    final_state = app_graph.invoke(initial_state)
    
    return {
        "status": "Analysis completed", 
        "report": final_state["final_report"],
        "verification_results": final_state["verification_results"]
    }

@router.get("/trends")
async def get_trends():
    from app.core.trends import TrendAnalyzer
    analyzer = TrendAnalyzer()
    trends = await analyzer.analyze_trends()
    return trends
