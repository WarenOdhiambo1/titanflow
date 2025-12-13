import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading

# Import your business logic function
# We will wrap your 'while True' loop in a function inside snipper_business.py first
from snipper_business import run_sniper_engine 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Run the sniper bot in a separate background thread
    print("🚀 Server Starting... Launching TitanFlow Sniper...")
    loop = asyncio.get_event_loop()
    # We run it in a thread so it doesn't block the website part
    threading.Thread(target=run_sniper_engine, daemon=True).start()
    yield
    # SHUTDOWN
    print("🛑 Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"status": "TitanFlow System Online", "mode": "Sniper Active"}

@app.get("/health")
def health():
    return {"status": "ok"}
