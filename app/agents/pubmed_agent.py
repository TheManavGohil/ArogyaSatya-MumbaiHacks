import httpx
import xmltodict
from concurrent.futures import ThreadPoolExecutor, as_completed

PUBMED_API_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_pubmed(query: str, max_results: int = 3):
    """Searches PubMed for relevant English articles (Synchronous)."""
    with httpx.Client(timeout=8.0) as client:  # Reduced timeout
        # 1. ESearch to get IDs - filter for English articles
        search_url = f"{PUBMED_API_BASE}/esearch.fcgi"
        # Add language filter to query for English articles only
        filtered_query = f"({query}) AND (English[Language])"
        params = {
            "db": "pubmed",
            "term": filtered_query,
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance"
        }
        try:
            resp = client.get(search_url, params=params, timeout=10.0)
            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # 2. EFetch to get details
            fetch_url = f"{PUBMED_API_BASE}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            fetch_resp = client.get(fetch_url, params=fetch_params, timeout=10.0)
            
            # Parse XML
            articles = []
            doc = xmltodict.parse(fetch_resp.text)
            
            # Handle single vs multiple results structure
            pubmed_articles = doc.get('PubmedArticleSet', {}).get('PubmedArticle', [])
            if isinstance(pubmed_articles, dict):
                pubmed_articles = [pubmed_articles]
                
            for article in pubmed_articles:
                try:
                    medline = article['MedlineCitation']
                    article_data = medline['Article']
                    
                    title = article_data.get('ArticleTitle', 'No Title')
                    
                    # Abstract handling
                    abstract_data = article_data.get('Abstract', {}).get('AbstractText', '')
                    if isinstance(abstract_data, list):
                        abstract = " ".join([item.get('#text', '') for item in abstract_data if isinstance(item, dict)] + [item for item in abstract_data if isinstance(item, str)])
                    elif isinstance(abstract_data, dict):
                        abstract = abstract_data.get('#text', '')
                    else:
                        abstract = str(abstract_data)
                        
                    # ID
                    pmid = medline.get('PMID', {}).get('#text', '')
                    
                    articles.append({
                        "source": "PubMed",
                        "title": title,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "snippet": abstract[:500] + "..." if len(abstract) > 500 else abstract
                    })
                except Exception as e:
                    print(f"Error parsing PubMed article: {e}")
                    continue
                    
            return articles
            
        except Exception as e:
            print(f"PubMed search failed: {e}")
            return []

def _search_pubmed_for_claim(claim: str) -> tuple:
    """Search PubMed for a single claim - for parallel execution."""
    if not claim or len(claim.strip()) < 5:
        return claim, []
    articles = search_pubmed(claim)
    return claim, articles


def pubmed_node(state):
    print("---PUBMED AGENT (Parallel)---")
    claims = state["claims"]
    evidence_map = state.get("evidence", {})

    valid_claims = [c for c in claims if c and len(c.strip()) >= 5]

    if not valid_claims:
        return {"evidence": evidence_map}

    # Parallel PubMed searches
    max_workers = min(len(valid_claims), 3)  # Limit concurrent PubMed requests

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_search_pubmed_for_claim, claim): claim for claim in valid_claims}

        for future in as_completed(futures):
            try:
                claim, articles = future.result(timeout=10)
                if articles:
                    current_evidence = evidence_map.get(claim, [])
                    # Prepend PubMed results to prioritize them
                    evidence_map[claim] = articles + current_evidence
                    print(f"Found {len(articles)} PubMed articles for: '{claim[:40]}...'")
            except Exception as e:
                print(f"PubMed search failed: {e}")

    return {"evidence": evidence_map}
