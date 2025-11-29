from app.db.database import get_vector_db
from duckduckgo_search import DDGS
from googlesearch import search as google_search
import time
import random

def search_web_sync(claim):
    """Synchronous web search using DDGS with Google Fallback."""
    evidence_items = []
    
    # Randomize query to bypass cache/"same link" issues
    # Add a random irrelevant term or just a timestamp to force fresh results logic if needed
    # But better is to just rely on the specific claim text.
    # The "same link" issue usually happens if the claim text is identical or generic.
    
    try:
        # 1. Try DuckDuckGo
        with DDGS() as ddgs:
            print(f"[DEBUG] DDG Search: '{claim}'")
            results = ddgs.text(f"verify claim: {claim}", max_results=3)
            if results:
                for r in results:
                    evidence_items.append({
                        "source": "DuckDuckGo",
                        "title": r['title'],
                        "url": r['href'],
                        "snippet": r['body']
                    })
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")

    # 2. Fallback to Google Search if DDG failed or returned nothing
    if not evidence_items:
        print(f"[DEBUG] Falling back to Google Search for: '{claim}'")
        try:
            # googlesearch-python returns URLs. We might not get snippets easily without scraping.
            # But it's a good fallback for links.
            google_results = google_search(f"verify {claim}", num_results=3, advanced=True)
            for r in google_results:
                evidence_items.append({
                    "source": "Google",
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.description if hasattr(r, 'description') else "No snippet available."
                })
        except Exception as e:
            print(f"Google search failed: {e}")

    return evidence_items

def evidence_retrieval_node(state):
    print("---EVIDENCE RETRIEVAL NODE (Sync + Fallback)---")
    claims = state["claims"]
    evidence_map = {}
    
    vector_db = get_vector_db()
    
    # 1. Local Vector DB
    local_evidence_map = {}
    for claim in claims:
        results_db = vector_db.query(query_texts=[claim], n_results=3)
        docs = results_db['documents'][0] if results_db['documents'] else []
        local_items = [{"source": "Local DB", "title": "Archived Claim", "url": "#", "snippet": d} for d in docs]
        local_evidence_map[claim] = local_items

    # 2. Web Search
    for claim in claims:
        if not claim or len(claim.strip()) < 5:
            print(f"[DEBUG] Skipping invalid claim: '{claim}'")
            continue
            
        web_items = search_web_sync(claim)
            
        # Combine
        all_items = local_evidence_map.get(claim, []) + web_items
        evidence_map[claim] = all_items
        print(f"Retrieved {len(all_items)} evidence items for claim: '{claim}'")
        
    return {"evidence": evidence_map}
