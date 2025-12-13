import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import random

def scrape_jumia(driver, url):
    """Specific logic for Jumia"""
    driver.get(url)
    time.sleep(random.uniform(5, 8))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    products = []
    articles = soup.find_all('article', class_='prd')
    
    for article in articles:
        try:
            name = article.find('h3', class_='name').text
            # Jumia specific link fix
            link_tag = article.find('a', class_='core')
            link = "https://www.jumia.co.ke" + link_tag['href']
            
            # Price cleanup
            price_tag = article.find('div', class_='prc')
            raw_price = price_tag.text if price_tag else "0"
            price = int(raw_price.replace("KSh", "").replace(",", "").strip())
            
            products.append({"name": name, "price": price, "link": link, "source": "Jumia"})
        except: continue
    return products

def scrape_kilimall(driver, url):
    """Specific logic for Kilimall"""
    driver.get(url)
    time.sleep(random.uniform(6, 9)) # Kilimall is slower
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    products = []
    # Kilimall often uses 'product-item' or specific div classes. 
    # This is a generic robust selector for their grid
    items = soup.find_all('div', class_='product-item') 
    
    for item in items:
        try:
            name = item.find('p', class_='product-title').text
            link = "https://www.kilimall.co.ke" + item.find('a')['href']
            
            # Price might be in different tags
            price_tag = item.find('div', class_='product-price')
            raw_price = price_tag.text if price_tag else "0"
            price = int(raw_price.replace("KSh", "").replace(",", "").strip())
            
            products.append({"name": name, "price": price, "link": link, "source": "Kilimall"})
        except: continue
    return products

def scrape_smart(url):
    """Decides which scraper to use based on the link"""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = None
    results = []
    
    try:
        driver = uc.Chrome(options=options, version_main=137)
        
        if "jumia" in url:
            print(f"[*] TitanFlow: Scanning Jumia...")
            results = scrape_jumia(driver, url)
        elif "kilimall" in url:
            print(f"[*] TitanFlow: Scanning Kilimall...")
            results = scrape_kilimall(driver, url)
        elif "jiji" in url:
            print(f"[*] TitanFlow: Jiji support coming in v2 (Anti-Bot is too strong for simple scripts)")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            try: driver.quit()
            except: pass
            
    return results
