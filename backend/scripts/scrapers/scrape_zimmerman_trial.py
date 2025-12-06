"""
Scraper for George Zimmerman Trial Documents and Transcripts
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

class ZimmermanTrialScraper:
    def __init__(self):
        self.base_url = "https://famous-trials.com/zimmerman1/"
        self.documents_url = "https://famous-trials.com/zimmerman1/2298-zimmermancourtdox"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.documents = []
    
    def scrape_main_page(self):
        """Scrape the main documents page to get all links"""
        print(f"Scraping main page: {self.documents_url}")
        
        try:
            response = self.session.get(self.documents_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links in the content area
            content_area = soup.find('div', {'class': 'content'}) or soup.find('main') or soup.find('body')
            
            if content_area:
                links = content_area.find_all('a')
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text and len(text) > 10:  # Filter out navigation links
                        # Make absolute URL
                        absolute_url = urljoin(self.base_url, href)
                        
                        # Skip external links and navigation
                        if 'famous-trials.com' in absolute_url and not any(skip in text.lower() for skip in ['home', 'donate', 'powered by']):
                            doc_info = {
                                'title': text,
                                'url': absolute_url,
                                'type': self._categorize_document(text),
                                'date': self._extract_date(text)
                            }
                            self.documents.append(doc_info)
                            print(f"Found: {text}")
            
            # Also look for specific document patterns
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if any(keyword in line for keyword in ['interview', 'affidavit', 'jury', 'verdict', 'instructions', 'testimony']):
                    if len(line) > 20 and '(' in line and ')' in line:
                        # This might be a document title with date
                        self._process_document_line(line)
            
        except Exception as e:
            print(f"Error scraping main page: {e}")
    
    def _categorize_document(self, title: str) -> str:
        """Categorize document based on title"""
        title_lower = title.lower()
        
        if 'interview' in title_lower:
            return 'interview'
        elif 'affidavit' in title_lower:
            return 'legal_document'
        elif 'jury' in title_lower:
            if 'instructions' in title_lower:
                return 'jury_instructions'
            elif 'verdict' in title_lower:
                return 'verdict'
            else:
                return 'jury_document'
        elif 'testimony' in title_lower:
            return 'testimony'
        elif 'autopsy' in title_lower or 'ballistics' in title_lower:
            return 'forensic_report'
        elif 'exhibit' in title_lower:
            return 'exhibit'
        elif 'reenact' in title_lower:
            return 'reenactment'
        else:
            return 'other'
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from document title if present"""
        import re
        
        # Look for dates in parentheses like (2/26/2012) or (6/24/2013)
        date_pattern = r'\((\d{1,2}/\d{1,2}/\d{4})\)'
        match = re.search(date_pattern, text)
        
        if match:
            return match.group(1)
        return None
    
    def _process_document_line(self, line: str):
        """Process a line that might be a document reference"""
        # Check if it's not already in our documents
        if not any(doc['title'] == line for doc in self.documents):
            doc_info = {
                'title': line,
                'url': None,  # We'll need to find the actual URL
                'type': self._categorize_document(line),
                'date': self._extract_date(line)
            }
            self.documents.append(doc_info)
    
    def scrape_document_content(self, url: str) -> Optional[str]:
        """Scrape the actual content of a document"""
        if not url:
            return None
            
        print(f"Scraping document: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove navigation and footer elements
            for element in soup.find_all(['nav', 'footer', 'header']):
                element.decompose()
            
            # Try to find main content
            content = None
            
            # Try different content containers
            for selector in ['article', 'main', '.content', '#content', 'div.document']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # If no specific container, get body text
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator='\n', strip=True)
            
            return content
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_all_documents(self):
        """Scrape all found documents"""
        print(f"\nScraping content for {len(self.documents)} documents...")
        
        for doc in self.documents:
            if doc['url']:
                content = self.scrape_document_content(doc['url'])
                if content:
                    doc['content'] = content
                    doc['content_length'] = len(content)
                else:
                    doc['content'] = "Content not available"
                    doc['content_length'] = 0
                
                # Be polite to the server
                time.sleep(1)
    
    def save_results(self):
        """Save scraped documents to files"""
        # Save as JSON
        with open('zimmerman_trial_documents.json', 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        
        # Save as text file
        with open('zimmerman_trial_documents.txt', 'w', encoding='utf-8') as f:
            f.write("GEORGE ZIMMERMAN TRIAL DOCUMENTS\n")
            f.write("=" * 80 + "\n\n")
            
            for doc in self.documents:
                f.write(f"Title: {doc['title']}\n")
                f.write(f"Type: {doc['type']}\n")
                if doc['date']:
                    f.write(f"Date: {doc['date']}\n")
                if doc['url']:
                    f.write(f"URL: {doc['url']}\n")
                f.write("-" * 40 + "\n")
                if 'content' in doc and doc['content'] != "Content not available":
                    f.write(doc['content'][:1000] + "...\n" if len(doc.get('content', '')) > 1000 else doc.get('content', '') + "\n")
                f.write("\n" + "=" * 80 + "\n\n")
        
        print(f"\nSaved {len(self.documents)} documents to zimmerman_trial_documents.json and .txt")
    
    def get_key_evidence_summary(self) -> Dict[str, List[str]]:
        """Extract key evidence from documents"""
        evidence = {
            'physical_evidence': [],
            'witness_statements': [],
            'medical_evidence': [],
            'timeline_events': [],
            'key_facts': []
        }
        
        # Key facts about the case
        evidence['key_facts'] = [
            "George Zimmerman shot and killed Trayvon Martin on February 26, 2012",
            "The shooting occurred in a gated community in Sanford, Florida",
            "Zimmerman was a neighborhood watch volunteer",
            "Martin was 17 years old, returning from a convenience store",
            "Zimmerman called 911 to report Martin as suspicious",
            "Zimmerman claimed self-defense under Florida's Stand Your Ground law",
            "Zimmerman was charged with second-degree murder",
            "The case sparked national debate about racial profiling and self-defense laws"
        ]
        
        # Extract from documents
        for doc in self.documents:
            if doc['type'] == 'interview' and 'good' in doc['title'].lower():
                evidence['witness_statements'].append(
                    "Jonathan Good: Witnessed Martin on top of Zimmerman during the altercation"
                )
            elif doc['type'] == 'forensic_report':
                evidence['medical_evidence'].append(
                    "Autopsy and ballistics reports documented the trajectory and nature of the fatal shot"
                )
            elif 'emt' in doc['title'].lower():
                evidence['medical_evidence'].append(
                    "EMT Kevin O'Rourke: Provided medical treatment at the scene"
                )
        
        return evidence

def main():
    """Main function to run the scraper"""
    scraper = ZimmermanTrialScraper()
    
    print("Starting George Zimmerman Trial document scraper...")
    
    # Scrape main page to get document list
    scraper.scrape_main_page()
    
    # Scrape individual documents
    scraper.scrape_all_documents()
    
    # Save results
    scraper.save_results()
    
    # Get evidence summary
    evidence = scraper.get_key_evidence_summary()
    
    # Save evidence summary
    with open('zimmerman_evidence_summary.json', 'w', encoding='utf-8') as f:
        json.dump(evidence, f, indent=2)
    
    print("\nEvidence Summary:")
    for category, items in evidence.items():
        if items:
            print(f"\n{category.replace('_', ' ').title()}:")
            for item in items:
                print(f"  - {item}")

if __name__ == "__main__":
    main()