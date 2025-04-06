"""
ContentCreatorAgent - Module for generating platform-specific social media content.

This package provides tools to create engaging content tailored for Twitter,
Instagram, and LinkedIn based on trending topics and brand guidelines.
"""

from .agent import ContentCreatorAgent
from .text_generator import TextGenerator
from .image_generator import ImageGenerator
from .platform_formatter import PlatformFormatter
from .brand_guidelines import BrandGuidelinesManager
from .content_moderator import ContentModerator

__all__ = [
    'ContentCreatorAgent',
    'TextGenerator',
    'ImageGenerator',
    'PlatformFormatter',
    'BrandGuidelinesManager',
    'ContentModerator'
]

__version__ = '1.0.0' 