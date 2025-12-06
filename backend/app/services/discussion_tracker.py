"""
Track what has been discussed to avoid repetition in deliberations
"""
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

class DiscussionTracker:
    """Track discussed topics and evidence to encourage new perspectives"""
    
    def __init__(self):
        # Track which evidence items have been mentioned
        self.evidence_mentioned: Set[int] = set()
        self.evidence_mention_count: Dict[int, int] = defaultdict(int)
        
        # Track key points made about each evidence
        self.evidence_arguments: Dict[int, List[str]] = defaultdict(list)
        
        # Track who said what
        self.juror_contributions: Dict[str, List[str]] = defaultdict(list)
        
        # Track common phrases to avoid repetition
        self.common_phrases_used: Set[str] = set()
        
    def extract_evidence_numbers(self, statement: str) -> List[int]:
        """Extract evidence numbers mentioned in a statement"""
        # Look for patterns like #1, Evidence #2, Evidence 3, etc.
        patterns = [
            r'#(\d+)',
            r'Evidence #(\d+)',
            r'Evidence (\d+)',
            r'evidence #(\d+)',
            r'evidence (\d+)'
        ]
        
        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, statement)
            numbers.extend([int(n) for n in matches])
        
        return list(set(numbers))
    
    def extract_key_phrases(self, statement: str) -> List[str]:
        """Extract key phrases that shouldn't be repeated"""
        key_phrases = []
        
        # Common phrases that get repeated
        repetitive_patterns = [
            r'1 in \d+ million',
            r'glove.{0,10}fit',
            r'25 minutes',
            r'timeline.{0,10}tight',
            r'domestic violence',
            r'history of abuse',
            r'DNA.{0,10}strong',
            r'blood trail',
            r'suicide note',
            r'police conspiracy',
            r'planted evidence'
        ]
        
        for pattern in repetitive_patterns:
            if re.search(pattern, statement, re.IGNORECASE):
                key_phrases.append(pattern)
        
        return key_phrases
    
    def update_from_statement(self, juror_name: str, statement: str):
        """Update tracker with information from a new statement"""
        # Track evidence mentioned
        evidence_nums = self.extract_evidence_numbers(statement)
        for num in evidence_nums:
            self.evidence_mentioned.add(num)
            self.evidence_mention_count[num] += 1
        
        # Track key phrases
        phrases = self.extract_key_phrases(statement)
        self.common_phrases_used.update(phrases)
        
        # Track juror contribution
        self.juror_contributions[juror_name].append(statement)
    
    def get_discussion_context(self) -> str:
        """Get context about what's been discussed"""
        context_parts = []
        
        # Most discussed evidence
        if self.evidence_mention_count:
            most_discussed = sorted(self.evidence_mention_count.items(), 
                                  key=lambda x: x[1], reverse=True)[:3]
            context_parts.append(f"Most discussed evidence: {[f'#{num}' for num, _ in most_discussed]}")
        
        # Evidence not yet discussed
        all_evidence_nums = set(range(1, 16))  # Assuming 15 pieces of evidence
        not_discussed = all_evidence_nums - self.evidence_mentioned
        if not_discussed and len(not_discussed) < 10:
            context_parts.append(f"Not yet discussed: {sorted(not_discussed)}")
        
        return " | ".join(context_parts) if context_parts else ""
    
    def get_guidance_for_next_speaker(self, juror_name: str) -> str:
        """Get guidance for what the next speaker should focus on"""
        guidance = []
        
        # Encourage discussing new evidence
        all_evidence_nums = set(range(1, 16))
        not_discussed = all_evidence_nums - self.evidence_mentioned
        
        if not_discussed:
            guidance.append(f"Consider discussing evidence items that haven't been mentioned yet: {sorted(not_discussed)[:3]}")
        
        # Discourage over-discussed topics
        overdiscussed = [num for num, count in self.evidence_mention_count.items() if count >= 3]
        if overdiscussed:
            guidance.append(f"Avoid repeating analysis of #{overdiscussed[0]} unless adding new perspective")
        
        # Encourage building on others
        if len(self.juror_contributions) > 2:
            guidance.append("Reference what other jurors said and add your unique perspective")
        
        # Avoid repetitive phrases
        if len(self.common_phrases_used) > 5:
            guidance.append("Use fresh language - avoid repeating common observations")
        
        return " | ".join(guidance)
    
    def should_mention_evidence(self, evidence_num: int) -> bool:
        """Check if it's appropriate to mention this evidence again"""
        mention_count = self.evidence_mention_count.get(evidence_num, 0)
        
        # Allow first 3 mentions freely
        if mention_count < 3:
            return True
        
        # After that, only if making a new point
        return mention_count < 5  # Hard limit at 5 mentions