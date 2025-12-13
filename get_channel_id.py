import requests

# Your Bot Token
TOKEN = "8308685146:AAGBMJUQVQwSiDsJpL-UMT4nN-x9o6W4FoA"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(URL)
data = response.json()

print(f"DEBUG: {data}") # Prints raw data to help us see everything

# Loop through updates to find the Channel Post
found = False
for result in data.get("result", []):
    if "channel_post" in result:
        chat_id = result["channel_post"]["chat"]["id"]
        chat_title = result["channel_post"]["chat"]["title"]
        print(f"\n✅ FOUND IT!")
        print(f"📢 Channel Name: {chat_title}")
        print(f"🆔 Channel ID: {chat_id}")
        found = True
        break

if not found:
    print("\n❌ No channel messages found.")
    print("👉 Go to your channel, post 'Hello', and run this script again immediately.")
