from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import os 
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

# Constants
BASE_URL = "https://pl.wikipedia.org"
START_URL = f"{BASE_URL}/wiki/Adrian_Zandberg"
USER_AGENT = "ZandbergResearchBot/1.0 (+https://example.com/bot-info)"
REQUEST_DELAY = 2
MAX_PAGES = 1000

class WikipediaScraper:
    def __init__(self):
        self.visited = set()
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{BASE_URL}/robots.txt")
        self.robot_parser.read()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
        self.conn = sqlite3.connect('pages.db')
        self._init_db()
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY,
            name TEXT,
            link TEXT UNIQUE,
            text TEXT,
            howfar INTEGER
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_howfar ON pages (howfar)')
        self.conn.commit()
        
    def _is_valid_url(self, url):
        parsed = urlparse(url)
        if parsed.netloc not in ['pl.wikipedia.org', '']:
            return False
        if not parsed.path.startswith('/wiki/'):
            return False
        if ':' in parsed.path:
            return False
        return True
        
    def _can_fetch(self, url):
        return self.robot_parser.can_fetch(USER_AGENT, url)
        
    def scrape_page(self, url, depth):
        if url in self.visited or not self._is_valid_url(url) or not self._can_fetch(url):
            return None, [], 0
            
        print(f"Scraping: {url} (depth {depth})")
        time.sleep(REQUEST_DELAY)
        
        try:
            page = self.session.get(url, timeout=10)
            page.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None, [], 0
            
        soup = BeautifulSoup(page.content, 'html.parser')
        name = soup.title.string.split(' - ')[0] if soup.title else url
        
        text = ""
        content_div = soup.find(id="mw-content-text")
        if content_div:
            for p in content_div.find_all('p'):
                text += p.get_text() + ' '
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(BASE_URL, href)
            if self._is_valid_url(full_url):
                links.append(full_url)
        
        self.visited.add(url)
        return name, text, links
        
    def save_page(self, name, url, text, depth):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO pages (name, link, text, howfar) 
                VALUES (?, ?, ?, ?)
            ''', (name, url, text, depth))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error saving {url}: {e}")
        
    def scrape_recursive(self, start_url, max_depth):
        queue = [(start_url, 0)]
        
        while queue and len(self.visited) < MAX_PAGES:
            url, depth = queue.pop(0)
            
            if depth > max_depth:
                continue
                
            name, text, links = self.scrape_page(url, depth)
            if name is None:
                continue
                
            self.save_page(name, url, text, depth)
            
            for link in links:
                if link not in self.visited:
                    queue.append((link, depth + 1))
        
    def close(self):
        self.conn.close()
        self.session.close()

def main():
    depth = int(input("How many articles deep do you want to search? (note: more than 1 not reccomended): "))
    
    scraper = WikipediaScraper()
    try:
        cursor = scraper.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pages WHERE howfar <= ?", (depth,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Starting new scrape...")
            scraper.scrape_recursive(START_URL, depth)
        else:
            print(f"Found {count} existing pages at or below depth {depth}")
            
        df = pd.read_sql_query(f"SELECT * FROM pages WHERE howfar <= {depth}", scraper.conn)
        print(f"Found {len(df)} relevant pages")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 
