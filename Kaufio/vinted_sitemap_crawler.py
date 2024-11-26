import cloudscraper
import gzip
import xml.etree.ElementTree as ET
from pymongo import MongoClient
from io import BytesIO


client = MongoClient("mongodb://localhost:27017/")
db = client["kaufio_local"]
collection = db["vinted_extracted_urls"]


sitemap_url = "https://www.vinted.cz/sitemaps/fr/cz/items.xml.gz"


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)
response = scraper.get(sitemap_url)
if response.status_code == 200:
    # Step 2: Decompress the .gz file
    with gzip.open(BytesIO(response.content), 'rb') as f:
        xml_content = f.read()

    root = ET.fromstring(xml_content)

    urls_to_insert = []
    for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        urls_to_insert.append({"url": loc})

    if urls_to_insert:
        collection.insert_many(urls_to_insert)
        print(f"Inserted {len(urls_to_insert)} URLs into MongoDB.")
    else:
        print("No URLs found in the sitemap.")
else:
    print(f"Failed to download sitemap: HTTP {response.status_code}")
