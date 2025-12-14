import time
import requests
import os
import google.generativeai as genai
from scraper import scrape_smart

# --- SECURE CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- CONFIGURE AI AGENT ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    # model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("⚠️ WARNING: Gemini API Key missing. AI features disabled.")
    model = None

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

SENT_CACHE = []

# --- AI GENERATOR FUNCTION ---
def generate_ai_update(topic="status"):
    if not model: return None
    
    try:
        if topic == "startup":
            prompt = "Write a short, high-energy Telegram message announcing that 'TitanFlow Systems are Online'. Mention that we are scanning Jumia and Kilimall for price glitches. Use emojis. Keep it under 20 words."
        elif topic == "pulse":
            prompt = "Write a very short, professional 'Market Pulse' update for a deal-hunting channel. Say that scanning is active but no major price anomalies detected yet. Encourage patience. Use emojis (Scope, Robot, Green Circle). Keep it under 15 words."
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# --- TELEGRAM SENDER ---
def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- BUSINESS LOGIC ---
def check_filters(product_name, category_rules):
    name_lower = product_name.lower()
    for bad_word in category_rules['forbidden']:
        if bad_word in name_lower: return False 
            
    has_required = False
    for good_word in category_rules['must_have']:
        if good_word in name_lower:
            has_required = True
            break
    return has_required

def send_marketing_alert(item):
    if item['name'] in SENT_CACHE: return
    print(f"💎 PREMIUM FIND: {item['name']}")
    
    msg = (
        f"💎 <b>TITANFLOW GOLD SIGNAL</b> 💎\n\n"
        f"🚀 <b>ITEM:</b> {item['name']}\n"
        f"📉 <b>PRICE:</b> KSh {item['price']} (Massive Drop)\n"
        f"🏪 <b>SOURCE:</b> {item['source']}\n"
        f"⚡ <b>URGENCY:</b> High Demand!\n\n"
        f"<a href='{item['link']}'>👉 CLICK TO BUY IMMEDIATELY 👈</a>"
    )
    send_telegram_msg(msg)
    SENT_CACHE.append(item['name']) 

# --- MAIN ENGINE ---
def run_sniper_engine():
    print("🚀 TITANFLOW: AI AGENT ACTIVE...")
    
    # 1. Send Startup Message (AI Generated)
    startup_msg = generate_ai_update("startup")
    if startup_msg: send_telegram_msg(f"<b>🤖 SYSTEM STATUS:</b>\n{startup_msg}")

    loop_count = 0

    while True:
        loop_count += 1
        
        # 2. Regular Scanning Loop
        for target in TARGETS:
            print(f"\n--- Scanning {target['name']} ---")
            products = scrape_smart(target['url'])
            
            found = 0
            for p in products:
                if p['price'] > 50 and p['price'] <= target['trigger_price']:
                    if check_filters(p['name'], target):
                        send_marketing_alert(p)
                        found += 1
                        time.sleep(1) 
            
            time.sleep(5)

        # 3. AI "Heartbeat" Message (Every 30 loops / approx 1 hour)
        if loop_count % 30 == 0:
            print("Creating AI Market Pulse...")
            pulse_msg = generate_ai_update("pulse")
            if pulse_msg: 
                send_telegram_msg(f"<b>📡 MARKET PULSE:</b>\n{pulse_msg}")
            
            # Clear cache occasionally
            if len(SENT_CACHE) > 500: SENT_CACHE.clear()

        print("\n💤 Cycle Complete...")
        time.sleep(120)