from fastapi import FastAPI, HTTPException
from scraper import scrape_jumia_price
from database import init_db, get_cached_product, save_product

# Initialize DB on startup
init_db()

app = FastAPI(title="TitanFlow Data API", description="Premium E-commerce Data Stream")

@app.get("/")
def home():
    return {"status": "Online", "endpoints": "/price/{item_name}"}

@app.get("/price/{item}")
def get_price(item: str):
    # 1. CHECK WAREHOUSE
    cached_data = get_cached_product(item)
    if cached_data:
        print(f"[*] Serving from Cache: {item}")
        return cached_data

    # 2. RUN MINER
    print(f"[*] Cache Miss. Mining Jumia for: {item}...")
    live_data = scrape_jumia_price(item)
    
    # --- DEBUGGING LINE ---
    print(f"DEBUG: Scraper returned: {live_data}") 
    # ----------------------

    # 3. SAVE OR FAIL
    if "product" in live_data:
        save_product(item, live_data["product"], live_data["price"])
        live_data["source"] = "Live Scraping (Fresh)"
        return live_data
    else:
        # Pass the actual error message to the browser
        error_msg = live_data.get("error", "Unknown Error")
        raise HTTPException(status_code=404, detail=f"Scraping Failed: {error_msg}")
