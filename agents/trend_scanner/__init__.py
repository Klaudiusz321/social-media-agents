"""
TrendScannerAgent - A module for scanning social media platforms for trending topics and content formats.

This package provides tools to monitor Twitter/X, Instagram, and LinkedIn for trending hashtags,
topics, and content formats relevant to astronomy, physics, and education.
"""

from .agent import TrendScannerAgent
from .scheduler import TrendScannerScheduler
from .twitter_scanner import TwitterScanner
from .instagram_scanner import InstagramScanner
from .linkedin_scanner import LinkedInScanner
from .cache_manager import CacheManager

__all__ = [
    'TrendScannerAgent',
    'TrendScannerScheduler',
    'TwitterScanner',
    'InstagramScanner',
    'LinkedInScanner',
    'CacheManager'
]

__version__ = '1.0.0' 