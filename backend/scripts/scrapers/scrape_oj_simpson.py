#!/usr/bin/env python3
"""
Scrape OJ Simpson trial transcript links
"""
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import time

def get_all_links(url):
    """Get all links from the OJ Simpson transcripts page"""
    try:
        # Remove fragment from URL
        base_url = url.split('#')[0]
        
        # Send request
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        links = []
        
        # Get all anchor tags
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True)
            
            # Skip empty links
            if not href or href == '#':
                continue
                
            # Create full URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('#'):
                full_url = base_url + href
            else:
                full_url = urljoin(base_url, href)
            
            links.append({
                'url': full_url,
                'text': link_text,
                'relative_href': href
            })
        
        return links
        
    except Exception as e:
        print(f"Error fetching links: {e}")
        return []

def save_links(links, output_file='oj_simpson_links.json'):
    """Save links to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(links, f, indent=2)
    print(f"Saved {len(links)} links to {output_file}")

def main():
    url = "http://simpson.walraven.org/#transcripts"
    
    print(f"Fetching links from: {url}")
    links = get_all_links(url)
    
    if links:
        print(f"\nFound {len(links)} total links:")
        print("\nAll links:")
        for i, link in enumerate(links):
            print(f"{i+1}. {link['text'][:80] if link['text'] else 'No text'} - {link['relative_href']}")
        
        # Save to file
        save_links(links)
        
        # Also save just URLs to text file
        with open('oj_simpson_urls.txt', 'w') as f:
            for link in links:
                f.write(f"{link['url']}\n")
        print("\nURLs also saved to oj_simpson_urls.txt")
    else:
        print("No links found")

if __name__ == "__main__":
    main()