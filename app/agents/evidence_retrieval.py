from app.db.database import get_vector_db
from duckduckgo_search import DDGS
from googlesearch import search as google_search
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Trusted healthcare sources for prioritization
TRUSTED_SOURCES = [
    "who.int", "cdc.gov", "nih.gov", "mayoclinic.org", "webmd.com",
    "healthline.com", "medlineplus.gov", "pubmed.ncbi.nlm.nih.gov",
    "hopkinsmedicine.org", "clevelandclinic.org", "harvard.edu",
    "nhs.uk", "reuters.com", "bbc.com", "nature.com", "sciencedirect.com",
    "thelancet.com", "bmj.com", "jamanetwork.com", "nejm.org"
]

# Non-English TLDs and URL patterns to filter out
NON_ENGLISH_PATTERNS = [
    r'\.cn/', r'\.cn$',  # Chinese
    r'\.jp/', r'\.jp$',  # Japanese
    r'\.kr/', r'\.kr$',  # Korean
    r'\.ru/', r'\.ru$',  # Russian
    r'\.tw/', r'\.tw$',  # Taiwanese
    r'baidu\.com', r'weibo\.com', r'qq\.com', r'163\.com',  # Chinese sites
    r'zhihu\.com', r'sohu\.com', r'sina\.com',  # Chinese sites
]

def is_english_content(url: str, title: str = "", snippet: str = "") -> bool:
    """Check if the content appears to be in English."""
    # Check URL for non-English patterns
    for pattern in NON_ENGLISH_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False

    # Check for Chinese/Japanese/Korean characters in title or snippet
    cjk_pattern = r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]'
    combined_text = f"{title} {snippet}"

    # If more than 10% of characters are CJK, likely not English
    if combined_text:
        cjk_chars = len(re.findall(cjk_pattern, combined_text))
        if cjk_chars > len(combined_text) * 0.1:
            return False

    return True

def is_trusted_source(url: str) -> bool:
    """Check if URL is from a trusted healthcare source."""
    return any(source in url.lower() for source in TRUSTED_SOURCES)

def sort_by_trust(evidence_items: list) -> list:
    """Sort evidence items with trusted sources first."""
    trusted = [item for item in evidence_items if is_trusted_source(item.get('url', ''))]
    untrusted = [item for item in evidence_items if not is_trusted_source(item.get('url', ''))]
    return trusted + untrusted

def search_web_sync(claim):
    """Synchronous web search using DDGS with Google Fallback."""
    evidence_items = []

    # Build healthcare-focused search query
    search_query = f"health medical fact check: {claim}"

    try:
        # 1. Try DuckDuckGo with English region
        with DDGS() as ddgs:
            print(f"[DEBUG] DDG Search: '{claim}'")
            results = ddgs.text(
                search_query,
                region="us-en",  # Force US English results
                safesearch="moderate",
                max_results=5  # Get more results to filter
            )
            if results:
                for r in results:
                    url = r['href']
                    title = r['title']
                    snippet = r['body']

                    # Filter out non-English content
                    if not is_english_content(url, title, snippet):
                        print(f"[DEBUG] Filtered non-English result: {url}")
                        continue

                    evidence_items.append({
                        "source": "DuckDuckGo",
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "trusted": is_trusted_source(url)
                    })
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")

    # 2. Fallback to Google Search if DDG failed or returned nothing
    if len(evidence_items) < 2:
        print(f"[DEBUG] Falling back to Google Search for: '{claim}'")
        try:
            # Add lang parameter for English results
            google_results = google_search(
                f"health fact check {claim}",
                num_results=5,
                advanced=True,
                lang="en"
            )
            for r in google_results:
                url = r.url
                title = r.title
                snippet = r.description if hasattr(r, 'description') else "No snippet available."

                # Filter out non-English content
                if not is_english_content(url, title, snippet):
                    print(f"[DEBUG] Filtered non-English result: {url}")
                    continue

                evidence_items.append({
                    "source": "Google",
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "trusted": is_trusted_source(url)
                })
        except Exception as e:
            print(f"Google search failed: {e}")

    # Sort by trust (trusted sources first) and limit results
    sorted_items = sort_by_trust(evidence_items)
    return sorted_items[:5]  # Return top 5 results

def _search_single_claim(claim: str, local_items: list) -> tuple:
    """Search for a single claim - used for parallel execution."""
    if not claim or len(claim.strip()) < 5:
        return claim, []

    web_items = search_web_sync(claim)
    all_items = web_items + local_items
    return claim, all_items


def evidence_retrieval_node(state):
    print("---EVIDENCE RETRIEVAL NODE (Parallel)---")
    claims = state["claims"]
    evidence_map = {}

    if not claims:
        return {"evidence": evidence_map}

    vector_db = get_vector_db()

    # 1. Local Vector DB - batch query
    local_evidence_map = {}
    for claim in claims:
        results_db = vector_db.query(query_texts=[claim], n_results=2)  # Reduced from 3
        docs = results_db['documents'][0] if results_db['documents'] else []
        local_items = [{"source": "Local DB", "title": "Archived Claim", "url": "#", "snippet": d, "trusted": False} for d in docs]
        local_evidence_map[claim] = local_items

    # 2. Parallel Web Search - search all claims concurrently
    valid_claims = [c for c in claims if c and len(c.strip()) >= 5]

    # Use ThreadPoolExecutor for parallel searches
    max_workers = min(len(valid_claims), 4)  # Limit to 4 concurrent searches

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all search tasks
        futures = {
            executor.submit(_search_single_claim, claim, local_evidence_map.get(claim, [])): claim
            for claim in valid_claims
        }

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                claim, all_items = future.result(timeout=15)  # 15 second timeout per search
                evidence_map[claim] = all_items
                trusted_count = sum(1 for item in all_items if item.get('trusted', False))
                print(f"Retrieved {len(all_items)} evidence ({trusted_count} trusted) for: '{claim[:50]}...'")
            except Exception as e:
                claim = futures[future]
                print(f"Search failed for claim '{claim[:30]}...': {e}")
                evidence_map[claim] = local_evidence_map.get(claim, [])

    return {"evidence": evidence_map}
