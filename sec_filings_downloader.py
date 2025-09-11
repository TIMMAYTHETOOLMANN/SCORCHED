import os
import requests
import hashlib
import json
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from datetime import datetime

# CONFIG
BASE_URL = "https://investors.nike.com/investors/news-events-and-reports/default.aspx"
ARCHIVE_URL_TEMPLATE = "https://investors.nike.com/investors/news-events-and-reports/news-releases/default.aspx?year={year}"
DATA_DIR = "data/sec_filings"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
SUPPORTED_FORMATS = [".pdf", ".xls", ".xlsx"]


def get_filing_links(year):
    url = ARCHIVE_URL_TEMPLATE.format(year=year)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        links = soup.select("a")
        docs = []

        for link in links:
            href = link.get("href")
            text = link.get_text(strip=True)
            if not href:
                continue
            ext = os.path.splitext(href)[1].lower()
            if ext in SUPPORTED_FORMATS:
                full_url = urljoin(BASE_URL, href)
                docs.append({
                    "url": full_url,
                    "name": text or os.path.basename(href),
                    "ext": ext,
                    "year": year
                })
        return docs
    except Exception as e:
        print(f"[!] Failed to fetch links for {year}: {e}")
        return []


def download_file(url, path):
    try:
        r = requests.get(url, headers=HEADERS, stream=True)
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[!] Failed to download {url}: {e}")
        return False


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def process_year(year):
    os.makedirs(f"{DATA_DIR}/{year}/", exist_ok=True)
    docs = get_filing_links(year)
    index = []
    seen_hashes = set()

    for doc in tqdm(docs, desc=f"Processing {year}"):
        name_safe = doc['name'].replace(" ", "_").replace("/", "-").replace("\\", "-")
        filename = f"{name_safe}{doc['ext']}"
        filepath = os.path.join(DATA_DIR, str(year), filename)

        if not os.path.exists(filepath):
            success = download_file(doc['url'], filepath)
            if not success:
                continue

        filehash = file_hash(filepath)
        if filehash in seen_hashes:
            os.remove(filepath)
            continue

        seen_hashes.add(filehash)
        index.append({
            "filename": filename,
            "url": doc['url'],
            "hash": filehash,
            "size_bytes": os.path.getsize(filepath),
            "timestamp": datetime.now().isoformat()
        })

    # Save index
    with open(f"{DATA_DIR}/{year}/filing_index_{year}.json", "w") as f:
        json.dump(index, f, indent=2)

    with open(f"{DATA_DIR}/{year}/download_summary_{year}.txt", "w") as f:
        f.write(f"Downloaded {len(index)} documents for {year}\n")

    print(f"[+] {year} - {len(index)} documents saved to {DATA_DIR}/{year}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_year", type=int, required=True, help="Start year (e.g., 2019)")
    parser.add_argument("--end_year", type=int, required=True, help="End year (e.g., 2025)")
    args = parser.parse_args()

    for year in range(args.start_year, args.end_year + 1):
        process_year(year)