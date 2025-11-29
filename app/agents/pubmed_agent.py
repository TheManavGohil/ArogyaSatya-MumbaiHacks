import httpx
import xmltodict

PUBMED_API_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_pubmed(query: str, max_results: int = 3):
    """Searches PubMed for relevant articles (Synchronous)."""
    with httpx.Client() as client:
        # 1. ESearch to get IDs
        search_url = f"{PUBMED_API_BASE}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
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

def pubmed_node(state):
    print("---PUBMED AGENT (Sync)---")
    claims = state["claims"]
    evidence_map = state.get("evidence", {})
    
    for claim in claims:
        if not claim or len(claim.strip()) < 5:
            continue
            
        print(f"Searching PubMed for: {claim}")
        articles = search_pubmed(claim)
        
        if articles:
            current_evidence = evidence_map.get(claim, [])
            # Prepend PubMed results to prioritize them
            evidence_map[claim] = articles + current_evidence
            print(f"Found {len(articles)} PubMed articles for: {claim}")
            
    return {"evidence": evidence_map}
