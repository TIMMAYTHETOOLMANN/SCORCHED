import os, requests, feedparser
from urllib.parse import urlparse

RSS_DIR = '../rss_feeds'
DEST_DIR = '../raw_documents'
LOG_PATH = '../logs/rss_errors.log'

def ensure_dirs():
    """Ensure required directories exist"""
    for dir_path in [RSS_DIR, DEST_DIR, os.path.dirname(LOG_PATH)]:
        os.makedirs(dir_path, exist_ok=True)

def sanitize_filename(url):
    """Extract a safe filename from URL"""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or filename == '/':
        # Generate filename from URL hash if no filename in path
        import hashlib
        filename = hashlib.md5(url.encode()).hexdigest() + '.html'
    return filename

def download_file(url, dest_folder):
    """Download file from URL to destination folder"""
    try:
        filename = sanitize_filename(url)
        dest_path = os.path.join(dest_folder, filename)
        
        if os.path.exists(dest_path):
            print(f"  File already exists: {filename}")
            return filename
            
        print(f"  Downloading: {url}")
        
        # Handle local file URLs
        if url.startswith('file://'):
            print(f"  Skipping local file: {url}")
            return None
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        
        with open(dest_path, 'wb') as f:
            f.write(r.content)
        
        print(f"  Downloaded: {filename} ({len(r.content)} bytes)")
        return filename
        
    except Exception as e:
        error_msg = f"ERROR: {url} - {str(e)}\n"
        print(f"  {error_msg.strip()}")
        with open(LOG_PATH, 'a') as log:
            log.write(error_msg)
        return None

def process_rss(rss_file):
    """Process a single RSS file and download all documents"""
    print(f"\nProcessing RSS file: {rss_file}")
    feed_path = os.path.join(RSS_DIR, rss_file)
    
    if not os.path.exists(feed_path):
        print(f"  RSS file not found: {feed_path}")
        return
        
    feed = feedparser.parse(feed_path)
    
    if feed.bozo:
        print(f"  Warning: RSS feed has parsing issues: {feed.bozo_exception}")
    
    print(f"  Found {len(feed.entries)} entries in RSS feed")
    
    for i, entry in enumerate(feed.entries, 1):
        print(f"  Processing entry {i}: {entry.get('title', 'Untitled')}")
        
        # Check main link
        if hasattr(entry, 'link') and entry.link:
            url = entry.link
            if url.endswith(('.pdf', '.xls', '.xlsx', '.docx', '.html', '.htm')):
                download_file(url, DEST_DIR)
        
        # Check additional links
        for link in entry.get('links', []):
            if isinstance(link, dict) and 'href' in link:
                url = link['href']
                if url.endswith(('.pdf', '.xls', '.xlsx', '.docx', '.html', '.htm')):
                    download_file(url, DEST_DIR)
            elif isinstance(link, str) and link.endswith(('.pdf', '.xls', '.xlsx', '.docx', '.html', '.htm')):
                download_file(link, DEST_DIR)
        
        # Check enclosures
        for enclosure in entry.get('enclosures', []):
            if isinstance(enclosure, dict) and 'href' in enclosure:
                url = enclosure['href']
                if url.endswith(('.pdf', '.xls', '.xlsx', '.docx', '.html', '.htm')):
                    download_file(url, DEST_DIR)

def main():
    """Main function to process all RSS files"""
    print("RSS Document Harvester Starting...")
    print("=" * 50)
    
    ensure_dirs()
    
    if not os.path.exists(RSS_DIR):
        print(f"Error: RSS directory not found: {RSS_DIR}")
        return
    
    rss_files = [f for f in os.listdir(RSS_DIR) if f.endswith('.xml')]
    
    if not rss_files:
        print(f"No RSS files found in {RSS_DIR}")
        print("Please add .xml RSS files to the rss_feeds directory")
        return
    
    print(f"Found {len(rss_files)} RSS files to process")
    
    for rss_file in rss_files:
        try:
            process_rss(rss_file)
        except Exception as e:
            error_msg = f"ERROR processing {rss_file}: {str(e)}\n"
            print(error_msg.strip())
            with open(LOG_PATH, 'a') as log:
                log.write(error_msg)
    
    print("\n" + "=" * 50)
    print("RSS harvesting complete!")
    print(f"Check {DEST_DIR} for downloaded documents")
    print(f"Check {LOG_PATH} for any errors")

if __name__ == "__main__":
    main()