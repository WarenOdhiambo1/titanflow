# Use an official Python runtime with Chrome support
FROM python:3.9-slim

# 1. Install System Dependencies (Chrome needs these)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 3. Set up the App
WORKDIR /app
COPY . /app

# 4. Install Python Libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Command to run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
