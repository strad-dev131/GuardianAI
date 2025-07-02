
"""
Security Scanner for GuardianAI
Detects malicious files, links, and copyright content
"""

import re
import logging
from typing import List, Set
from pathlib import Path
import magic

class SecurityScanner:
    """Advanced security scanning system"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Dangerous file extensions
        self.dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
            '.jar', '.apk', '.deb', '.rpm', '.msi', '.dmg', '.pkg',
            '.sh', '.ps1', '.psm1', '.psd1', '.ps1xml', '.psc1',
        }
        
        # Suspicious keywords in filenames
        self.suspicious_keywords = {
            'crack', 'keygen', 'patch', 'hack', 'cheat', 'trainer',
            'leaked', 'dump', 'breach', 'password', 'passwords',
            'nude', 'porn', 'sex', 'adult', 'xxx', 'nsfw',
        }
        
        # Malicious domains
        self.malicious_domains = {
            'malware.com', 'phishing.net', 'scam.org',
            # Add more known malicious domains
        }
        
        # Copyright indicators
        self.copyright_keywords = {
            'copyright', '©', 'copyrighted', 'pirated', 'cracked',
            'leaked', 'rip', 'webrip', 'dvdrip', 'bluray',
            'torrent', 'magnet:', 'download free', 'full movie',
        }
    
    async def scan_document(self, document) -> bool:
        """Scan document for security threats"""
        try:
            filename = document.file_name.lower() if document.file_name else ""
            mime_type = document.mime_type or ""
            file_size = document.file_size or 0
            
            # Check file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext in self.dangerous_extensions:
                self.logger.warning(f"Dangerous file extension detected: {file_ext}")
                return True
            
            # Check filename for suspicious keywords
            if any(keyword in filename.lower() for keyword in self.suspicious_keywords):
                self.logger.warning(f"Suspicious filename detected: {filename}")
                return True
            
            # Check for copyright indicators
            if self.config.copyright_detection:
                if any(keyword in filename.lower() for keyword in self.copyright_keywords):
                    self.logger.warning(f"Copyright violation suspected: {filename}")
                    return True
            
            # Check file size (suspiciously large files)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                self.logger.warning(f"Unusually large file: {file_size} bytes")
                return True
            
            # Check MIME type
            if mime_type in ['application/x-executable', 'application/x-msdos-program']:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error scanning document: {e}")
            return False
    
    async def scan_audio(self, audio) -> bool:
        """Scan audio file for copyright violations"""
        try:
            if not self.config.copyright_detection:
                return False
            
            filename = audio.file_name.lower() if audio.file_name else ""
            title = audio.title.lower() if audio.title else ""
            performer = audio.performer.lower() if audio.performer else ""
            
            # Check for copyright indicators
            text_to_check = f"{filename} {title} {performer}"
            
            if any(keyword in text_to_check for keyword in self.copyright_keywords):
                self.logger.warning(f"Copyright violation suspected in audio: {filename}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error scanning audio: {e}")
            return False
    
    async def scan_video(self, video) -> bool:
        """Scan video file for copyright violations"""
        try:
            if not self.config.copyright_detection:
                return False
            
            filename = video.file_name.lower() if video.file_name else ""
            file_size = video.file_size or 0
            
            # Check filename for copyright indicators
            if any(keyword in filename for keyword in self.copyright_keywords):
                self.logger.warning(f"Copyright violation suspected in video: {filename}")
                return True
            
            # Check for movie/TV show patterns
            movie_patterns = [
                r'\d{4}.*(?:webrip|dvdrip|bluray|brrip)',
                r'(?:s\d{2}e\d{2}|season \d+)',
                r'(?:1080p|720p|480p).*(?:x264|h264|xvid)',
            ]
            
            for pattern in movie_patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    self.logger.warning(f"Movie/TV pattern detected: {filename}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error scanning video: {e}")
            return False
    
    async def scan_links(self, text: str) -> bool:
        """Scan text for malicious links"""
        try:
            if not self.config.block_suspicious_links:
                return False
            
            # Extract URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            
            for url in urls:
                domain = self._extract_domain(url)
                
                # Check against known malicious domains
                if domain in self.malicious_domains:
                    self.logger.warning(f"Malicious domain detected: {domain}")
                    return True
                
                # Check for suspicious URL patterns
                if await self._is_suspicious_url(url):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error scanning links: {e}")
            return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            domain = url.split('/')[2].lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    async def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious"""
        try:
            url_lower = url.lower()
            
            # Suspicious patterns
            suspicious_patterns = [
                r'bit\.ly|tinyurl|short\.link',  # URL shorteners
                r'download.*(?:free|crack|hack)',
                r'(?:porn|adult|xxx|sex)',
                r'(?:bitcoin|crypto|investment).*(?:scam|fraud)',
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, url_lower):
                    self.logger.warning(f"Suspicious URL pattern: {pattern}")
                    return True
            
            # Check for IP addresses instead of domains
            ip_pattern = r'https?://(?:\d{1,3}\.){3}\d{1,3}'
            if re.match(ip_pattern, url):
                self.logger.warning(f"IP-based URL detected: {url}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking suspicious URL: {e}")
            return False
