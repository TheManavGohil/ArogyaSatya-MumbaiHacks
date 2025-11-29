import json
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from io import BytesIO
import httpx
from app.core.config import settings

# Initialize Local VLM (Moondream2)
# We use a specific revision for stability as recommended by the model authors
MODEL_ID = "vikhyatk/moondream2"
REVISION = "2024-08-26"

print(f"Loading local VLM: {MODEL_ID}...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, 
        trust_remote_code=True, 
        revision=REVISION
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    
    # Move to GPU if available
    if torch.cuda.is_available():
        model = model.to("cuda")
        print("VLM loaded on CUDA")
    else:
        print("VLM loaded on CPU")
        
    model.eval()
except Exception as e:
    print(f"Failed to load VLM: {e}")
    model = None
    tokenizer = None

def vlm_node(state):
    print("---VLM NODE (Local)---")
    images = state.get("images", [])
    
    if not images:
        print("No images to analyze.")
        return {"image_analysis": []}
    
    if not model or not tokenizer:
        print("VLM model not loaded.")
        return {"image_analysis": [{"error": "Model not loaded"}]}
        
    results = []
    
    # Analyze up to 3 images
    for img_url in images[:3]:
        try:
            print(f"Downloading and analyzing image: {img_url}")
            
            # Download image
            with httpx.Client() as client:
                response = client.get(img_url, timeout=10.0)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            
            # Process with Moondream
            enc_image = model.encode_image(image)
            
            # 1. Describe
            description = model.answer_question(enc_image, "Describe this image in detail.", tokenizer)
            
            # 2. Extract Claims
            claims_text = model.answer_question(enc_image, "List any medical or healthcare claims made in this image. If none, say 'None'.", tokenizer)
            
            # Parse claims
            claims = []
            if "None" not in claims_text:
                claims = [c.strip() for c in claims_text.split('\n') if c.strip()]
            
            analysis = {
                "description": description,
                "claims": claims
            }
                
            results.append({
                "url": img_url,
                "analysis": analysis
            })
            
        except Exception as e:
            print(f"Error analyzing image {img_url}: {e}")
            results.append({
                "url": img_url,
                "analysis": {"description": f"Error: {str(e)}", "claims": []}
            })
            
    return {"image_analysis": results}
