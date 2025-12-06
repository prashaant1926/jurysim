"""
OJ Simpson Trial Context Provider
Provides relevant excerpts from trial transcripts during deliberation
"""
import json
import random
import os
from typing import List, Dict, Optional

class OJSimpsonContext:
    """Provides contextual information from OJ Simpson trial transcripts"""
    
    def __init__(self, json_path: str = "oj_simpson_complete_content.json"):
        self.content = []
        self.depositions = []
        self.evidence_docs = []
        self.trial_transcripts = []
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                self.content = json.load(f)
                
            # Categorize content
            for doc in self.content:
                if doc['type'] == 'deposition':
                    self.depositions.append(doc)
                elif doc['type'] == 'evidence':
                    self.evidence_docs.append(doc)
                elif doc['type'] == 'trial_transcript':
                    self.trial_transcripts.append(doc)
    
    def get_glove_testimony(self) -> List[str]:
        """Get testimony related to the glove evidence"""
        glove_excerpts = []
        
        for doc in self.content:
            content = doc.get('content', '').lower()
            if 'glove' in content:
                lines = doc['content'].split('\n')
                for i, line in enumerate(lines):
                    if 'glove' in line.lower():
                        # Get context around glove mention
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        excerpt = ' '.join(lines[start:end]).strip()
                        if len(excerpt) > 50 and len(excerpt) < 500:
                            glove_excerpts.append(f"From {doc['title']}: {excerpt}")
                        if len(glove_excerpts) >= 5:
                            return glove_excerpts
        
        return glove_excerpts or ["No specific glove testimony found in transcripts"]
    
    def get_timeline_evidence(self) -> List[str]:
        """Get testimony about timeline"""
        timeline_excerpts = []
        
        keywords = ['10:15', '10:40', '10:54', 'limousine', 'kato', 'thump', 'time']
        
        for doc in self.content:
            content = doc.get('content', '').lower()
            for keyword in keywords:
                if keyword in content:
                    lines = doc['content'].split('\n')
                    for i, line in enumerate(lines):
                        if keyword in line.lower():
                            excerpt = line.strip()
                            if len(excerpt) > 30 and len(excerpt) < 300:
                                timeline_excerpts.append(f"{doc['title']}: {excerpt}")
                                break
            
            if len(timeline_excerpts) >= 8:
                break
        
        return timeline_excerpts or ["No specific timeline testimony found"]
    
    def get_dna_evidence(self) -> List[str]:
        """Get DNA evidence details"""
        dna_excerpts = []
        
        for doc in self.evidence_docs:
            if 'DNA' in doc['title']:
                content = doc.get('content', '')
                # Extract key statistics
                lines = content.split('\n')
                for line in lines:
                    if any(word in line for word in ['match', 'probability', 'million', 'billion']):
                        dna_excerpts.append(line.strip())
                        if len(dna_excerpts) >= 5:
                            return dna_excerpts
        
        return dna_excerpts or ["DNA evidence shows matches at multiple locations"]
    
    def get_domestic_violence_history(self) -> List[str]:
        """Get domestic violence evidence"""
        dv_excerpts = []
        
        for doc in self.evidence_docs:
            if '911' in doc['title'] or 'Nicole' in doc['title']:
                content = doc.get('content', '')
                lines = content.split('\n')
                for line in lines[:20]:  # First 20 lines likely most relevant
                    if len(line) > 30 and len(line) < 200:
                        dv_excerpts.append(f"911 Call: {line.strip()}")
                        if len(dv_excerpts) >= 3:
                            break
        
        return dv_excerpts or ["History of 911 calls and documented abuse"]
    
    def get_random_deposition_exchange(self) -> str:
        """Get a random Q&A exchange from depositions"""
        if not self.depositions:
            return "No deposition content available"
        
        # Try to find a good Q&A exchange
        for _ in range(10):  # Try up to 10 times
            doc = random.choice(self.depositions)
            content = doc.get('content', '')
            
            if 'Q:' in content and 'A:' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('Q:') and i+1 < len(lines):
                        question = line.strip()
                        answer = lines[i+1].strip() if lines[i+1].strip().startswith('A:') else ''
                        
                        if answer and 20 < len(question) < 200 and 10 < len(answer) < 200:
                            return f"From {doc['title']}:\n{question}\n{answer}"
        
        return "No suitable Q&A exchange found"
    
    def get_context_for_topic(self, topic: str) -> List[str]:
        """Get context related to a specific topic"""
        topic_lower = topic.lower()
        relevant_excerpts = []
        
        for doc in self.content:
            if topic_lower in doc.get('content', '').lower():
                # Extract sentences containing the topic
                content = doc['content']
                sentences = content.split('.')
                
                for sentence in sentences:
                    if topic_lower in sentence.lower() and 30 < len(sentence) < 300:
                        relevant_excerpts.append(f"{doc['title']}: {sentence.strip()}.")
                        if len(relevant_excerpts) >= 5:
                            return relevant_excerpts
        
        return relevant_excerpts or [f"No specific testimony about {topic} found"]