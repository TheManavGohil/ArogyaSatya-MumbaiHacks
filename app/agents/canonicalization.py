import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

# Initialize Chroma Client
chroma_client = chromadb.Client()
# Use a simple default embedding function for now
# In production, we might want a specific model like 'all-MiniLM-L6-v2'
embedding_func = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name="canonical_claims",
    embedding_function=embedding_func
)

def canonicalization_node(state):
    print("---CANONICALIZATION NODE---")
    raw_claims = state["claims"]
    canonical_claims = []
    
    for claim_text in raw_claims:
        # Query for similar existing claims
        results = collection.query(
            query_texts=[claim_text],
            n_results=1
        )
        
        existing_id = None
        existing_text = None
        distance = 1.0
        
        if results['ids'] and results['ids'][0]:
            existing_id = results['ids'][0][0]
            existing_text = results['documents'][0][0]
            distance = results['distances'][0][0]
            
        # Threshold for similarity (lower distance = more similar)
        # Adjust this threshold based on embedding model. For L2, 0.3 is often a good starting point.
        SIMILARITY_THRESHOLD = 0.3 
        
        if existing_id and distance < SIMILARITY_THRESHOLD:
            print(f"Mapped '{claim_text}' to existing claim '{existing_text}' (dist: {distance:.4f})")
            canonical_claims.append(existing_text)
        else:
            print(f"New canonical claim: '{claim_text}'")
            # Add new claim to collection
            # In a real app, we'd generate a UUID
            import uuid
            new_id = str(uuid.uuid4())
            collection.add(
                documents=[claim_text],
                ids=[new_id]
            )
            canonical_claims.append(claim_text)
            
    return {"claims": canonical_claims}
