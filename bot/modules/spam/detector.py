
"""
Spam Detection System for GuardianAI
Advanced spam and unwanted content detection
"""

import re
import logging
from typing import List, Set
from dataclasses import dataclass

@dataclass
class SpamResult:
    """Spam detection result"""
    is_spam: bool
    confidence: float
    reason: str

class SpamDetector:
    """Advanced spam detection system"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Spam patterns
        self.spam_patterns = [
            # URLs and promotional content
            r'(?i)\b(?:free|win|prize|money|cash|earn|bitcoin|crypto)\b.*(?:click|link|visit)',
            r'(?i)\b(?:telegram|whatsapp|signal).*(?:channel|group|join)\b',
            r'(?i)\b(?:investment|trading|forex|binary)\b.*(?:profit|guarantee)',
            
            # Repetitive patterns
            r'(.)\1{10,}',  # Repeated characters
            r'\b(\w+)\s+\1\s+\1',  # Repeated words
            
            # Suspicious content
            r'(?i)\b(?:nude|sex|porn|xxx|adult|18\+)\b',
            r'(?i)\b(?:hack|crack|cheat|bot|auto)\b.*(?:free|download)',
            
            # Scam indicators
            r'(?i)\b(?:urgent|limited|expire|act now|hurry)\b',
            r'(?i)\b(?:congratulations|winner|selected|chosen)\b',
        ]
        
        # Known spam domains
        self.spam_domains = {
            'bit.ly', 'tinyurl.com', 'short.link', 'cutt.ly',
            # Add more known spam domains
        }
        
        # Compile patterns
        self.compiled_patterns = [re.compile(pattern) for pattern in self.spam_patterns]
    
    async def detect_spam(self, text: str) -> bool:
        """Detect if text is spam"""
        if not text:
            return False
        
        try:
            result = await self._analyze_text(text)
            return result.is_spam
            
        except Exception as e:
            self.logger.error(f"Error detecting spam: {e}")
            return False
    
    async def _analyze_text(self, text: str) -> SpamResult:
        """Analyze text for spam indicators"""
        confidence = 0.0
        reasons = []
        
        # Check against spam patterns
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                confidence += 0.3
                reasons.append(f"Pattern {i+1} matched")
        
        # Check for excessive capitalization
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                confidence += 0.4
                reasons.append("Excessive capitalization")
        
        # Check for excessive punctuation
        punct_ratio = sum(1 for c in text if c in '!?.,;') / len(text) if text else 0
        if punct_ratio > 0.3:
            confidence += 0.3
            reasons.append("Excessive punctuation")
        
        # Check for suspicious URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            domain = self._extract_domain(url)
            if domain in self.spam_domains:
                confidence += 0.5
                reasons.append(f"Spam domain: {domain}")
        
        # Check for repetitive content
        words = text.lower().split()
        if len(words) > 5:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.6:
                confidence += 0.4
                reasons.append("Highly repetitive content")
        
        # Check for emoji spam
        emoji_count = sum(1 for c in text if ord(c) > 0x1F600)
        if len(text) > 0 and emoji_count / len(text) > 0.3:
            confidence += 0.3
            reasons.append("Excessive emojis")
        
        is_spam = confidence > 0.6
        reason = "; ".join(reasons) if reasons else "No spam indicators"
        
        return SpamResult(
            is_spam=is_spam,
            confidence=min(confidence, 1.0),
            reason=reason
        )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            # Simple domain extraction
            domain = url.split('/')[2].lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    async def detect_raid_pattern(self, messages: List[str]) -> bool:
        """Detect coordinated raid patterns"""
        if len(messages) < 3:
            return False
        
        try:
            # Check for identical or very similar messages
            similarity_threshold = 0.8
            
            for i, msg1 in enumerate(messages):
                for msg2 in messages[i+1:]:
                    similarity = self._calculate_similarity(msg1, msg2)
                    if similarity > similarity_threshold:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting raid pattern: {e}")
            return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
