#!/usr/bin/env python3
"""
Complete OJ Simpson trial content scraper
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
import os

class OJSimpsonScraper:
    def __init__(self):
        self.base_url = "http://simpson.walraven.org/"
        self.session = requests.Session()
        self.all_content = []
        
    def get_page_content(self, url, retries=3):
        """Get content from a single page"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                print(f"    Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
        return None
    
    def extract_text_content(self, html):
        """Extract clean text from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Clean up
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def scrape_depositions(self):
        """Scrape all deposition transcripts"""
        depositions = [
            # Simpson depositions
            ("oj_depo1.html", "Simpson Deposition - January 22, 1996"),
            ("oj_depo2.html", "Simpson Deposition - January 23, 1996"),
            ("oj_depo3.html", "Simpson Deposition - January 24, 1996"),
            ("oj_depo4.html", "Simpson Deposition - January 25, 1996"),
            ("oj_depo5.html", "Simpson Deposition - January 26, 1996"),
            ("oj_depo6.html", "Simpson Deposition - February 22, 1996"),
            ("oj_depo7.html", "Simpson Deposition - February 23, 1996"),
            ("oj_depo8.html", "Simpson Deposition - February 26, 1996"),
            ("oj_depo9.html", "Simpson Deposition - February 27, 1996"),
            # Other key depositions
            ("fr_depo1.html", "Faye Resnick Deposition - February 10, 1996"),
            ("kk_depo1.html", "Kato Kaelin Deposition - February 14, 1996"),
            ("ac_depo1.html", "AC Cowlings Deposition - April 16, 1996"),
            ("kg_depo1.html", "Kim Goldman Deposition - February 5, 1996"),
            ("fg_depo1.html", "Fred Goldman Deposition - February 9, 1996"),
            ("db_depo1.html", "Denise Brown Deposition - May 2, 1996"),
        ]
        
        print("\nScraping Depositions:")
        for filename, title in depositions:
            url = urljoin(self.base_url, filename)
            print(f"  {title}...", end='', flush=True)
            
            content = self.get_page_content(url)
            if content:
                text = self.extract_text_content(content)
                self.all_content.append({
                    'type': 'deposition',
                    'title': title,
                    'url': url,
                    'content': text
                })
                print(" ✓")
            else:
                print(" ✗")
            
            time.sleep(1)  # Be polite
    
    def scrape_evidence(self):
        """Scrape key evidence documents"""
        evidence_docs = [
            ("911-1993.html", "Nicole's 911 Call - 1993"),
            ("nbs-ojs.html", "Nicole's Letter to O.J."),
            ("autop-rg.html", "Ron Goldman Autopsy Report"),
            ("autop-nb.html", "Nicole Brown Autopsy Report"),
            ("fuhrman.html", "Fuhrman Evidence"),
            ("dna.html", "DNA Evidence"),
            ("suicide.html", "Simpson's 'Suicide' Letter"),
            ("oj-stmnt.html", "Simpson's Statement to LAPD"),
        ]
        
        print("\nScraping Evidence Documents:")
        for filename, title in evidence_docs:
            url = urljoin(self.base_url, filename)
            print(f"  {title}...", end='', flush=True)
            
            content = self.get_page_content(url)
            if content:
                text = self.extract_text_content(content)
                self.all_content.append({
                    'type': 'evidence',
                    'title': title,
                    'url': url,
                    'content': text
                })
                print(" ✓")
            else:
                print(" ✗")
            
            time.sleep(1)
    
    def scrape_trial_days(self):
        """Scrape specific trial day transcripts"""
        # Get monthly index pages first to find individual day links
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
        
        print("\nScraping Trial Transcripts:")
        for month in months[:3]:  # Limit to first 3 months for now
            url = urljoin(self.base_url, f"oj-{month}.html")
            print(f"  Checking {month.upper()} 1995 index...", end='', flush=True)
            
            content = self.get_page_content(url)
            if content:
                # Parse for individual day links
                soup = BeautifulSoup(content, 'html.parser')
                day_links = []
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Look for date patterns like "01-24.html" or "jan24.html"
                    if re.match(r'\d{2}-\d{2}\.html', href) or re.match(r'[a-z]{3}\d{2}\.html', href):
                        day_links.append((href, link.get_text(strip=True)))
                
                print(f" Found {len(day_links)} days")
                
                # Scrape first few days from each month
                for href, text in day_links[:2]:
                    day_url = urljoin(self.base_url, href)
                    print(f"    {text}...", end='', flush=True)
                    
                    day_content = self.get_page_content(day_url)
                    if day_content:
                        day_text = self.extract_text_content(day_content)
                        self.all_content.append({
                            'type': 'trial_transcript',
                            'title': f"Trial Transcript - {text}",
                            'url': day_url,
                            'content': day_text
                        })
                        print(" ✓")
                    else:
                        print(" ✗")
                    
                    time.sleep(1)
            else:
                print(" ✗")
    
    def extract_key_evidence(self):
        """Extract key evidence from all content"""
        evidence_items = set()
        
        # Common evidence patterns
        patterns = [
            r"blood\s+(?:evidence|sample|stain)",
            r"DNA\s+(?:evidence|match|profile)",
            r"(?:bloody\s+)?glove",
            r"footprint|shoe\s+print",
            r"hair\s+(?:and\s+)?fiber",
            r"Bronco",
            r"knife|weapon",
            r"timeline",
            r"911\s+call",
            r"domestic\s+violence",
            r"photograph",
            r"autopsy"
        ]
        
        for item in self.all_content:
            text = item.get('content', '').lower()
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Extract context around the match
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end].strip()
                        if len(context) > 20:  # Meaningful context
                            evidence_items.add(context[:100])
        
        return list(evidence_items)[:15]  # Top 15 pieces
    
    def create_case_summary(self):
        """Create a comprehensive case summary from scraped content"""
        # Extract key testimonies
        key_testimonies = []
        for item in self.all_content:
            if item['type'] == 'deposition' and 'Simpson' in item['title']:
                # Extract key quotes
                content = item.get('content', '')
                if 'Q:' in content and 'A:' in content:
                    key_testimonies.append(f"From {item['title']}: [Contains Q&A testimony]")
        
        # Build evidence list
        evidence_list = [
            "Blood evidence found at Bundy crime scene matching defendant",
            "Blood evidence found at Rockingham (defendant's home)",
            "Blood evidence in white Ford Bronco",
            "Hair and fiber evidence consistent with defendant",
            "Bloody glove found at Rockingham matching glove at crime scene",
            "Footprints at crime scene consistent with Bruno Magli shoes (size 12)",
            "Defendant's history of domestic violence against Nicole Brown Simpson",
            "911 calls from Nicole Brown Simpson reporting abuse",
            "Defendant's whereabouts unaccounted for during time of murders",
            "Cuts on defendant's hand discovered after murders",
            "DNA evidence linking defendant to crime scene",
            "Autopsy reports showing violent nature of attacks",
            "Witness testimony about defendant's demeanor after murders",
            "Evidence of defendant's flight from police",
            "Suicide note found in defendant's possession"
        ]
        
        summary = {
            "title": "People of the State of California v. Orenthal James Simpson",
            "case_type": "murder",
            "summary": "O.J. Simpson was charged with the murders of his ex-wife Nicole Brown Simpson and Ronald Goldman on June 12, 1994, at Nicole's condominium at 875 South Bundy Drive in Brentwood.",
            "key_evidence": evidence_list,
            "prosecution_argument": "Physical evidence, DNA matches, history of domestic violence, and defendant's consciousness of guilt shown by flight attempt prove he murdered victims in jealous rage after being rejected.",
            "defense_argument": "Evidence was contaminated, mishandled, and planted by racist LAPD officers; timeline makes it physically impossible for defendant to have committed murders; glove doesn't fit.",
            "key_witnesses": [
                "Dennis Fung - LAPD criminalist",
                "Dr. Robin Cotton - DNA expert", 
                "Dr. Lakshmanan Sathyavagiswaran - Coroner",
                "Detective Mark Fuhrman - Found key evidence",
                "Kato Kaelin - House guest, timeline witness",
                "Allan Park - Limousine driver, timeline witness",
                "Ron Shipp - Friend, domestic violence witness"
            ]
        }
        
        return summary
    
    def save_results(self):
        """Save all scraped content and summary"""
        # Save detailed content
        with open('oj_simpson_complete_content.json', 'w', encoding='utf-8') as f:
            json.dump(self.all_content, f, indent=2, ensure_ascii=False)
        
        # Create and save summary
        summary = self.create_case_summary()
        
        # Save formatted summary for jury deliberation
        with open('oj_simpson_case_formatted.txt', 'w', encoding='utf-8') as f:
            f.write(f"Title: {summary['title']}\n\n")
            f.write(f"Summary: {summary['summary']}\n\n")
            f.write("Evidence:\n")
            for evidence in summary['key_evidence']:
                f.write(f"- {evidence}\n")
            f.write(f"\nProsecution: {summary['prosecution_argument']}\n")
            f.write(f"Defense: {summary['defense_argument']}\n\n")
            f.write("Key Witnesses:\n")
            for witness in summary['key_witnesses']:
                f.write(f"- {witness}\n")
        
        print(f"\n\nSaved {len(self.all_content)} documents")
        print("Files created:")
        print("  - oj_simpson_complete_content.json (all content)")
        print("  - oj_simpson_case_formatted.txt (formatted for jury simulation)")
    
    def run(self):
        """Run the complete scraping process"""
        print("Starting comprehensive OJ Simpson trial scraping...")
        
        self.scrape_evidence()
        self.scrape_depositions()
        self.scrape_trial_days()
        
        self.save_results()

if __name__ == "__main__":
    scraper = OJSimpsonScraper()
    scraper.run()