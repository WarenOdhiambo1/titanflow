import time
import requests
import os
from scraper import scrape_smart

# --- SECURE CONFIGURATION (LOADS FROM RENDER) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN")
BASE_ID = os.environ.get("BASE_ID")
TABLE_NAME = "Sniper_Log"

# --- SMART CATEGORY DEFINITIONS ---
TARGETS = [
    {
        "name": "High-End Phones (Jumia)",
        "url": "https://www.jumia.co.ke/mobile-phones/apple/?sort=lowest-price",
        "trigger_price": 5000,
        "must_have": ["iphone", "samsung", "pixel", "pro", "max"],
        "forbidden": ["case", "cover", "glass", "screen", "cable", "adapter", "earpiece", "pouch", "protector", "shell"]
    },
    {
        "name": "Smart TVs (Jumia)",
        "url": "https://www.jumia.co.ke/televisions/?sort=lowest-price",
        "trigger_price": 5000,
        "must_have": ["inch", "tv", "smart", "android", "webos", "4k", "fhd"], 
        "forbidden": ["bracket", "mount", "stand", "decoder", "antenna", "remote", "cable", "guard", "protector", "extension", "cleaner"]
    },
    {
        "name": "Official Leather Shoes (Jumia)",
        "url": "https://www.jumia.co.ke/mens-shoes/?sort=lowest-price",
        "trigger_price": 1000,
        "must_have": ["leather", "formal", "oxford", "official", "office", "slip-on", "loafer", "boots"],
        "forbidden": ["sneaker", "sport", "canvas", "flip", "flop", "sandal", "mesh", "knit", "running", "casual", "slide"]
    },
    {
        "name": "Kilimall Treasure Hunt",
        "url": "https://www.kilimall.co.ke/new/flash-sale", 
        "trigger_price": 2000,
        "must_have": ["iphone", "samsung", "tv", "inch", "leather", "laptop", "audio", "sony", "hisense"],
        "forbidden": ["case", "cover", "cable", "protector", "watch", "strap", "holder", "stand", "usb", "ring"]
    }
]

# Track sent items to avoid spamming duplicates
SENT_CACHE = []

def check_filters(product_name, category_rules):
    name_lower = product_name.lower()
    
    # 1. Check FORBIDDEN words (The "Block" List)
    for bad_word in category_rules['forbidden']:
        if bad_word in name_lower:
            return False # Reject: It's junk
            
    # 2. Check REQUIRED words (The "Must Have" List)
    has_required = False
    for good_word in category_rules['must_have']:
        if good_word in name_lower:
            has_required = True
            break
    
    if not has_required:
        return False # Reject: It's vague or not a target brand
        
    return True # APPROVED

def send_marketing_alert(item):
    """Sends the alert and adds to cache to prevent duplicates"""
    if item['name'] in SENT_CACHE:
        return
        
    print(f"💎 PREMIUM FIND: {item['name']}")
    
    msg = (
        f"💎 <b>TITANFLOW GOLD SIGNAL</b> 💎\n\n"
        f"🚀 <b>ITEM:</b> {item['name']}\n"
        f"📉 <b>PRICE:</b> KSh {item['price']} (Massive Drop)\n"
        f"🏪 <b>SOURCE:</b> {item['source']}\n"
        f"⚡ <b>URGENCY:</b> High Demand!\n\n"
        f"<a href='{item['link']}'>👉 CLICK TO BUY IMMEDIATELY 👈</a>"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
        SENT_CACHE.append(item['name']) # Remember we sent this
    except Exception as e:
        print(f"Error sending: {e}")

# --- THE ENGINE WRAPPER (Required for Main.py) ---
def run_sniper_engine():
    print("🚀 TITANFLOW: STRICT MODE ACTIVE (Background)...")
    
    # Check credentials
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ ERROR: Secrets not found! Did you add them to Render Environment Variables?")
        return

    while True:
        for target in TARGETS:
            print(f"\n--- Scanning {target['name']} ---")
            
            # Calls the intelligent scraper we built earlier
            products = scrape_smart(target['url'])
            print(f"[*] Analyzed {len(products)} items...")
            
            found = 0
            for p in products:
                # 1. Price Check (Must be cheap, but not 0/Error)
                if p['price'] > 50 and p['price'] <= target['trigger_price']:
                    # 2. Strict Word Check (Is it a TV/Phone? Not a cable?)
                    if check_filters(p['name'], target):
                        send_marketing_alert(p)
                        found += 1
                        time.sleep(1) 
            
            if found == 0:
                print("   -> No items met strict criteria (Junk filtered).")
                
            time.sleep(5)

        # Clear cache every hour so we can alert again if stock returns
        if len(SENT_CACHE) > 500:
            SENT_CACHE.clear()

        print("\n💤 Cycle Complete...")
        time.sleep(120)