from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Selenium
options = Options()
options.add_argument("--headless")  
options.add_argument("--disable-gpu")
service = Service("C:/Users/BP/Downloads/selenum/chromedriver.exe") 
driver = webdriver.Chrome(service=service, options=options)
url = "https://www.vcsheet.com/investors"
driver.get(url)
time.sleep(5) 

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


soup = BeautifulSoup(driver.page_source, 'html.parser')
cards = soup.select('div.list-card.stand-alone.more-space')

data = []

for card in cards:
    try:
        # Name
        name_tag = card.select_one("h3.list-heading.list-pages")
        name = name_tag.text.strip() if name_tag else None


        # Title & Company
        title_tag = card.select_one('.list-title')
        if title_tag and '@' in title_tag.text:
            title_text = title_tag.text.strip().replace('@', ' @ ')
            company = title_text.split('@')[-1].strip()
            title = title_text.split('@')[0].strip()
        else:
            title = None
            company = None

        # Description
        desc_tag = card.find('div', class_="shortdesccard more-top w-richtext")
        description = desc_tag.text.strip() if desc_tag else None

        # Funding Stages
        stages = [s.text.strip() for s in card.select('.pill-item') if 'w-condition-invisible' not in s.get('class', [])]


       
        links = card.select('a.contact-icon')
        email = twitter = linkedin = crunchbase = youtube = ''
        for link in links:
            href = link.get('href', '')
            if 'mailto:' in href:
                email = href.replace('mailto:', '').split('?')[0]
            elif 'twitter.com' in href:
                twitter = href
            elif 'linkedin.com' in href:
                linkedin = href
            elif 'crunchbase.com' in href:
                crunchbase = href
            elif 'youtube.com' in href:
                youtube = href

        data.append({
            'name': name,
            'title': title,
            'company': company,
            'description': description,
            'funding_stages': ', '.join(stages),
            'email': email,
            'twitter': twitter,
            'linkedin': linkedin,
            'crunchbase': crunchbase,
            'youtube': youtube
        })

    except Exception as e:
        print(f"Skipping a card due to error: {e}")
        continue


driver.quit()

df = pd.DataFrame(data)
df.to_csv("investors_data.csv", index=False)
print("✅ Data scraped and saved to investors_data.csv")
