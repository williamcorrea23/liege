import os
import urllib.request
import urllib.parse
from html.parser import HTMLParser
import zipfile
from pathlib import Path

BASE_URL = "https://liegesantos1.wordpress.com/"
PAGES = [
    "",
    "sobre/",
    "publicacoes/",
    "exposicoes-e-curadorias/"
]

OUTPUT_DIR = "liegesantos_site"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)

class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = set()
        
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for attr, value in attrs:
                if attr == "src":
                    self.images.add(value)

def download_file(url, filepath):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            return data
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

all_images = set()

# Download pages
for page in PAGES:
    url = urllib.parse.urljoin(BASE_URL, page)
    filename = "index.html" if page == "" else f"{page.strip('/')}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    print(f"Downloading page: {url}")
    html_data = download_file(url, filepath)
    
    if html_data:
        parser = ImageParser()
        try:
            parser.feed(html_data.decode('utf-8', errors='ignore'))
            all_images.update(parser.images)
        except Exception as e:
            print(f"Error parsing HTML for {url}: {e}")

# Download images
for img_url in all_images:
    if not img_url.startswith('http'):
        img_url = urllib.parse.urljoin(BASE_URL, img_url)
    
    # Clean up URL parameters
    clean_url = img_url.split('?')[0]
    filename = os.path.basename(clean_url)
    if not filename:
        continue
        
    filepath = os.path.join(OUTPUT_DIR, "images", filename)
    print(f"Downloading image: {img_url}")
    download_file(img_url, filepath)

# Zip everything
print("Creating zip file...")
with zipfile.ZipFile('liegesantos_site.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, OUTPUT_DIR)
            zipf.write(file_path, arcname)

print("Done! Site saved to liegesantos_site.zip")
