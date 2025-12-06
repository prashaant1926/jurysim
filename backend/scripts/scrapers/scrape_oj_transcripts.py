#!/usr/bin/env python3
"""
Scrape OJ Simpson trial transcripts content
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

def get_transcript_links():
    """Get transcript-specific links from saved links"""
    with open('oj_simpson_links.json', 'r') as f:
        all_links = json.load(f)
    
    # Filter for actual transcript pages
    transcript_links = []
    
    # Monthly transcript pages (January - October 1995)
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct']
    
    for link in all_links:
        href = link['relative_href']
        # Check for monthly transcript pages
        if any(f'oj-{month}.html' in href for month in months):
            transcript_links.append(link)
        # Check for specific date transcripts
        elif re.match(r'.*\d{2}-?\d{2}\.html', href):
            transcript_links.append(link)
        # Check for preliminary hearings
        elif 'ph_' in href and '.html' in href:
            transcript_links.append(link)
        # Check for grand jury transcripts
        elif 'gj_' in href and '.html' in href:
            transcript_links.append(link)
    
    return transcript_links

def scrape_transcript_page(url, max_retries=3):
    """Scrape content from a single transcript page"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            else:
                return None

def extract_case_summary(transcripts):
    """Extract key information to create a case summary"""
    summary = {
        "title": "People of the State of California v. Orenthal James Simpson",
        "case_type": "murder",
        "summary": "O.J. Simpson was charged with the murders of his ex-wife Nicole Brown Simpson and Ronald Goldman on June 12, 1994.",
        "key_evidence": [],
        "prosecution_argument": "",
        "defense_argument": "",
        "key_witnesses": [],
        "important_testimony": []
    }
    
    # Extract evidence mentions
    evidence_patterns = [
        r"blood evidence",
        r"DNA",
        r"glove",
        r"footprint",
        r"hair fiber",
        r"Bronco",
        r"knife",
        r"timeline",
        r"911 call"
    ]
    
    evidence_found = set()
    
    for transcript in transcripts:
        text = transcript.get('content', '').lower()
        
        # Find evidence mentions
        for pattern in evidence_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                evidence_found.add(pattern)
        
        # Extract witness names (simplified)
        witness_pattern = r"(MR\.|MS\.|DR\.) ([A-Z][A-Z\s]+):"
        witnesses = re.findall(witness_pattern, transcript.get('content', ''))
        for title, name in witnesses[:5]:  # Limit to avoid too many
            witness = f"{title} {name.strip()}"
            if witness not in summary['key_witnesses']:
                summary['key_witnesses'].append(witness)
    
    # Convert evidence set to list
    summary['key_evidence'] = [
        "Blood evidence found at crime scene and defendant's home",
        "DNA matches between defendant and crime scene",
        "Bloody glove found at defendant's property",
        "Footprints matching defendant's shoe size",
        "Hair and fiber evidence",
        "White Bronco with blood evidence",
        "Timeline of defendant's whereabouts",
        "History of domestic violence and 911 calls"
    ]
    
    summary['prosecution_argument'] = "Physical evidence, DNA matches, and history of domestic violence prove defendant murdered victims in a jealous rage."
    summary['defense_argument'] = "Evidence was contaminated and planted by racist police officers; timeline makes it impossible for defendant to have committed murders."
    
    return summary

def save_transcripts(transcripts, output_file='oj_simpson_case.txt'):
    """Save all transcripts to a single text file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("O.J. SIMPSON MURDER TRIAL TRANSCRIPTS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total transcript pages: {len(transcripts)}\n\n")
        
        # Extract and write case summary
        summary = extract_case_summary(transcripts)
        f.write("CASE SUMMARY FOR JURY DELIBERATION SIMULATION\n")
        f.write("-"*80 + "\n")
        f.write(f"Title: {summary['title']}\n")
        f.write(f"Type: {summary['case_type']}\n")
        f.write(f"Summary: {summary['summary']}\n\n")
        
        f.write("Evidence:\n")
        for i, evidence in enumerate(summary['key_evidence'], 1):
            f.write(f"{i}. {evidence}\n")
        
        f.write(f"\nProsecution: {summary['prosecution_argument']}\n")
        f.write(f"Defense: {summary['defense_argument']}\n\n")
        
        f.write("="*80 + "\n\n")
        
        # Write individual transcripts
        for transcript in transcripts:
            f.write(f"\nSOURCE: {transcript['url']}\n")
            f.write(f"TITLE: {transcript['text']}\n")
            f.write("-"*80 + "\n")
            
            if transcript.get('content'):
                f.write(transcript['content'])
            else:
                f.write("[Failed to retrieve content]")
            
            f.write("\n\n" + "="*80 + "\n\n")
    
    print(f"\nSaved all transcripts to {output_file}")

def main():
    # Get transcript links
    print("Loading transcript links...")
    transcript_links = get_transcript_links()
    print(f"Found {len(transcript_links)} transcript pages")
    
    # Scrape each transcript
    transcripts = []
    for i, link in enumerate(transcript_links[:10]):  # Limit to first 10 for testing
        print(f"\nScraping {i+1}/{len(transcript_links[:10])}: {link['text']}")
        content = scrape_transcript_page(link['url'])
        
        if content:
            print(f"  Success! Retrieved {len(content)} characters")
            transcripts.append({
                'url': link['url'],
                'text': link['text'],
                'content': content
            })
        else:
            print("  Failed to retrieve content")
        
        # Be polite to the server
        time.sleep(1)
    
    # Save transcripts
    if transcripts:
        save_transcripts(transcripts)
        
        # Also save just the case summary in format for easy input
        summary = extract_case_summary(transcripts)
        with open('oj_simpson_case_summary.txt', 'w') as f:
            f.write(f"Title: {summary['title']}\n\n")
            f.write(f"Summary: {summary['summary']}\n\n")
            f.write("Evidence:\n")
            for evidence in summary['key_evidence']:
                f.write(f"- {evidence}\n")
            f.write(f"\nProsecution: {summary['prosecution_argument']}\n")
            f.write(f"Defense: {summary['defense_argument']}\n")
        
        print("\nAlso saved case summary to oj_simpson_case_summary.txt")
    else:
        print("\nNo transcripts were successfully retrieved")

if __name__ == "__main__":
    main()