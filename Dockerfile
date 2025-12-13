
# Use an official Python runtime (Debian based)
FROM python:3.9-slim

# 1. Install System Dependencies
# We include 'gnupg' and 'ca-certificates' which are strictly required for the keys
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Google Chrome (The Modern Way)
# We use gpg --dearmor instead of apt-key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 3. Set up the App
WORKDIR /app
COPY . /app

# 4. Install Python Libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Command to run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]