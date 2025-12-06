"""
Enhanced scraper for George Zimmerman Trial Documents with content extraction
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import PyPDF2
import io

class ZimmermanTrialCompleteScraper:
    def __init__(self):
        self.base_url = "https://famous-trials.com/zimmerman1/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.documents = []
        
        # Key document URLs based on the structure
        self.key_pages = {
            'main_documents': 'https://famous-trials.com/zimmerman1/2298-zimmermancourtdox',
            'trial_account': 'https://famous-trials.com/zimmerman1/2319-home',
            'testimony': 'https://famous-trials.com/zimmerman1/2300-zimtestimony',
            'reports': 'https://famous-trials.com/zimmerman1/2299-zimreports',
            'calls': 'https://famous-trials.com/zimmerman1/2297-zimcalls',
            'verdict': 'https://famous-trials.com/zimmerman1/2315-zimverdictpage',
            'jury_comments': 'https://famous-trials.com/zimmerman1/2316-zimmermanjurycomments'
        }
    
    def scrape_pdf_content(self, url: str) -> Optional[str]:
        """Extract text from PDF documents"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Check if it's actually a PDF
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                try:
                    pdf_file = io.BytesIO(response.content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n"
                    
                    return text.strip()
                except Exception as e:
                    print(f"Error reading PDF {url}: {e}")
                    return f"[PDF content - unable to extract text]"
            else:
                # Not a PDF, return None to try HTML parsing
                return None
                
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
    
    def scrape_page_content(self, url: str, page_type: str = 'general') -> Dict[str, any]:
        """Scrape content from a specific page"""
        print(f"Scraping {page_type} page: {url}")
        
        try:
            # First check if it's a PDF
            pdf_content = self.scrape_pdf_content(url)
            if pdf_content:
                return {
                    'url': url,
                    'type': 'pdf',
                    'content': pdf_content,
                    'page_type': page_type
                }
            
            # Otherwise parse as HTML
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove navigation elements
            for element in soup.find_all(['nav', 'footer', 'script', 'style']):
                element.decompose()
            
            content = {}
            content['url'] = url
            content['type'] = 'html'
            content['page_type'] = page_type
            
            # Extract title
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
            content['title'] = title.get_text(strip=True) if title else 'Unknown Title'
            
            # Extract main content based on page type
            if page_type == 'testimony':
                content['testimonies'] = self._extract_testimonies(soup)
            elif page_type == 'reports':
                content['reports'] = self._extract_reports(soup)
            elif page_type == 'calls':
                content['calls'] = self._extract_calls(soup)
            elif page_type == 'jury_comments':
                content['jury_comments'] = self._extract_jury_comments(soup)
            else:
                # General content extraction
                main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
                if main_content:
                    content['text'] = main_content.get_text(separator='\n', strip=True)
                else:
                    content['text'] = soup.get_text(separator='\n', strip=True)
            
            # Extract any embedded documents or links
            content['embedded_docs'] = self._extract_document_links(soup)
            
            return content
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {'url': url, 'error': str(e), 'page_type': page_type}
    
    def _extract_testimonies(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract testimony information"""
        testimonies = []
        
        # Look for testimony links or sections
        for elem in soup.find_all(['a', 'h3', 'h4']):
            text = elem.get_text(strip=True)
            if 'testimony' in text.lower() or 'witness' in text.lower():
                testimony = {
                    'witness': text,
                    'url': elem.get('href') if elem.name == 'a' else None
                }
                testimonies.append(testimony)
        
        return testimonies
    
    def _extract_reports(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract report information"""
        reports = []
        
        # Look for report links
        for elem in soup.find_all('a'):
            text = elem.get_text(strip=True)
            href = elem.get('href')
            if href and any(keyword in text.lower() for keyword in ['autopsy', 'ballistic', 'medical', 'police', 'report']):
                report = {
                    'title': text,
                    'url': urljoin(self.base_url, href),
                    'type': self._categorize_report(text)
                }
                reports.append(report)
        
        return reports
    
    def _extract_calls(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract 911 call information"""
        calls = []
        
        # Look for call references
        content = soup.get_text()
        lines = content.split('\n')
        
        for line in lines:
            if '911' in line or 'call' in line.lower():
                if len(line.strip()) > 20:
                    calls.append({
                        'description': line.strip(),
                        'type': '911_call'
                    })
        
        return calls
    
    def _extract_jury_comments(self, soup: BeautifulSoup) -> List[str]:
        """Extract jury comments"""
        comments = []
        
        # Look for quoted text or jury statements
        for elem in soup.find_all(['p', 'blockquote']):
            text = elem.get_text(strip=True)
            if len(text) > 50 and ('"' in text or 'juror' in text.lower()):
                comments.append(text)
        
        return comments
    
    def _extract_document_links(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract links to embedded documents"""
        docs = []
        
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href and any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx']):
                docs.append({
                    'title': text or 'Embedded Document',
                    'url': urljoin(self.base_url, href),
                    'type': 'embedded_document'
                })
        
        return docs
    
    def _categorize_report(self, title: str) -> str:
        """Categorize report type"""
        title_lower = title.lower()
        
        if 'autopsy' in title_lower:
            return 'autopsy'
        elif 'ballistic' in title_lower:
            return 'ballistics'
        elif 'medical' in title_lower or 'emt' in title_lower:
            return 'medical'
        elif 'police' in title_lower:
            return 'police'
        else:
            return 'other'
    
    def scrape_all_content(self):
        """Scrape all key pages"""
        all_content = {}
        
        for page_name, url in self.key_pages.items():
            content = self.scrape_page_content(url, page_name)
            all_content[page_name] = content
            
            # Be polite to server
            time.sleep(1)
            
            # Follow embedded document links
            if 'embedded_docs' in content:
                for doc in content['embedded_docs']:
                    if doc['url'] not in [d.get('url') for d in self.documents]:
                        doc_content = self.scrape_pdf_content(doc['url'])
                        if doc_content:
                            self.documents.append({
                                'title': doc['title'],
                                'url': doc['url'],
                                'content': doc_content,
                                'type': 'pdf_document'
                            })
                        time.sleep(0.5)
        
        return all_content
    
    def create_zimmerman_case(self) -> Dict:
        """Create a case structure for jury deliberation"""
        case = {
            "case_type": "murder",
            "case_title": "State of Florida v. George Zimmerman",
            "summary": "George Zimmerman, a neighborhood watch volunteer, shot and killed 17-year-old Trayvon Martin on February 26, 2012, in Sanford, Florida. Zimmerman claims self-defense under Florida's Stand Your Ground law.",
            "key_evidence": [
                "911 call: Zimmerman reported Martin as suspicious person in gated community",
                "Physical evidence: Zimmerman had injuries consistent with a struggle",
                "Witness testimony: Jonathan Good saw Martin on top of Zimmerman",
                "Forensics: Single gunshot wound to Martin's chest at close range",
                "Martin was unarmed, carrying only Skittles and iced tea",
                "Zimmerman did not initially identify himself as neighborhood watch",
                "Dispatcher told Zimmerman 'we don't need you to' follow Martin",
                "Zimmerman's injuries: broken nose, lacerations to back of head",
                "No witness saw the initial confrontation",
                "Martin was on phone with friend Rachel Jeantel during initial encounter",
                "Forensic evidence: Martin's knuckles had abrasions",
                "Zimmerman waived Stand Your Ground hearing, claimed traditional self-defense",
                "Time gap between 911 call and shooting approximately 2 minutes",
                "Zimmerman legally carrying concealed weapon with permit",
                "Martin was staying with father's fiancée in the neighborhood"
            ],
            "prosecution_argument": "Zimmerman profiled, pursued, and confronted Martin based on appearance, creating the confrontation. He had no authority to follow or detain Martin. His injuries were minor and didn't justify deadly force against an unarmed teenager.",
            "defense_argument": "Zimmerman acted in self-defense when Martin attacked him, broke his nose, and slammed his head on concrete. He reasonably feared death or great bodily harm. Martin had opportunity to go home but instead confronted and attacked Zimmerman.",
            "jury_instructions": "To find Zimmerman guilty of second-degree murder, you must find he acted with depraved mind and ill will. For manslaughter, you must find he intentionally committed an act that caused death. If Zimmerman reasonably believed deadly force was necessary to prevent imminent death or great bodily harm, he acted in self-defense.",
            "requires_unanimous": True
        }
        
        return case
    
    def save_results(self, all_content: Dict):
        """Save all scraped content"""
        # Save raw content
        with open('zimmerman_trial_complete_content.json', 'w', encoding='utf-8') as f:
            json.dump(all_content, f, indent=2, ensure_ascii=False)
        
        # Save case for deliberation
        case = self.create_zimmerman_case()
        with open('zimmerman_case_deliberation.json', 'w', encoding='utf-8') as f:
            json.dump(case, f, indent=2)
        
        # Save summary
        with open('zimmerman_trial_summary.txt', 'w', encoding='utf-8') as f:
            f.write("GEORGE ZIMMERMAN TRIAL SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("CASE OVERVIEW:\n")
            f.write("-" * 40 + "\n")
            f.write(case['summary'] + "\n\n")
            
            f.write("KEY EVIDENCE:\n")
            f.write("-" * 40 + "\n")
            for i, evidence in enumerate(case['key_evidence'], 1):
                f.write(f"{i}. {evidence}\n")
            
            f.write("\n\nPROSECUTION ARGUMENT:\n")
            f.write("-" * 40 + "\n")
            f.write(case['prosecution_argument'] + "\n\n")
            
            f.write("DEFENSE ARGUMENT:\n")
            f.write("-" * 40 + "\n")
            f.write(case['defense_argument'] + "\n\n")
        
        print(f"\nSaved Zimmerman trial content to multiple files")
        print(f"- zimmerman_trial_complete_content.json: Raw scraped content")
        print(f"- zimmerman_case_deliberation.json: Case formatted for jury deliberation")
        print(f"- zimmerman_trial_summary.txt: Human-readable summary")

def main():
    """Main function"""
    scraper = ZimmermanTrialCompleteScraper()
    
    print("Starting comprehensive George Zimmerman trial scraper...")
    
    # Scrape all content
    all_content = scraper.scrape_all_content()
    
    # Save results
    scraper.save_results(all_content)
    
    print("\nScraping complete!")

if __name__ == "__main__":
    main()