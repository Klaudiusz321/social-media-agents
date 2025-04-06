"""
SchedulerAgent - Module for scheduling and posting content to social media platforms.

This package provides a complete solution for scheduling and posting content to various
social media platforms at optimal times. It includes the core scheduler agent,
platform-specific posting modules, and utilities for determining optimal posting times.
"""

from agents.scheduler.scheduler_agent import SchedulerAgent
from agents.scheduler.post_scheduler import PostScheduler
from agents.scheduler.platform_posters.twitter_poster import TwitterPoster
from agents.scheduler.platform_posters.instagram_poster import InstagramPoster
from agents.scheduler.platform_posters.linkedin_poster import LinkedInPoster

__all__ = [
    'SchedulerAgent',
    'PostScheduler',
    'TwitterPoster',
    'InstagramPoster',
    'LinkedInPoster',
]

__version__ = '1.0.0' 