"""
Post Scheduler - Module for determining optimal posting times for social media platforms.

This module provides functionality for calculating the best times to post content
on different social media platforms based on platform-specific data and best practices.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

class PostScheduler:
    """
    Determines optimal posting times for different social media platforms.
    
    Uses platform-specific data and best practices to schedule posts at times
    when they are likely to receive maximum engagement.
    """
    
    def __init__(self, time_zone: str = "UTC"):
        """
        Initialize the PostScheduler.
        
        Args:
            time_zone: Time zone for scheduling calculations
        """
        self.logger = logging.getLogger(__name__)
        self.time_zone = time_zone
        
        # Platform-specific optimal posting times
        # Format: (day_of_week, hour, minute)
        # day_of_week: 0 = Monday, 6 = Sunday
        self.optimal_times = {
            "twitter": [
                # Weekday mornings
                (0, 9, 0),  # Monday 9 AM
                (1, 9, 0),  # Tuesday 9 AM
                (2, 9, 0),  # Wednesday 9 AM
                (3, 9, 0),  # Thursday 9 AM
                (4, 9, 0),  # Friday 9 AM
                
                # Weekday midday
                (0, 12, 0),  # Monday 12 PM
                (1, 12, 0),  # Tuesday 12 PM
                (2, 12, 0),  # Wednesday 12 PM
                (3, 12, 0),  # Thursday 12 PM
                (4, 12, 0),  # Friday 12 PM
                
                # Weekday evenings
                (0, 17, 0),  # Monday 5 PM
                (1, 17, 0),  # Tuesday 5 PM
                (2, 17, 0),  # Wednesday 5 PM
                (3, 17, 0),  # Thursday 5 PM
                (4, 17, 0),  # Friday 5 PM
                
                # Weekend times
                (5, 11, 0),  # Saturday 11 AM
                (6, 11, 0),  # Sunday 11 AM
            ],
            "instagram": [
                # Weekday morning
                (0, 10, 30),  # Monday 10:30 AM
                (1, 10, 30),  # Tuesday 10:30 AM
                (2, 10, 30),  # Wednesday 10:30 AM
                (3, 10, 30),  # Thursday 10:30 AM
                (4, 10, 30),  # Friday 10:30 AM
                
                # Weekday evening
                (0, 18, 0),  # Monday 6 PM
                (1, 18, 0),  # Tuesday 6 PM
                (2, 18, 0),  # Wednesday 6 PM
                (3, 18, 0),  # Thursday 6 PM
                (4, 18, 0),  # Friday 6 PM
                
                # Weekend times
                (5, 11, 0),  # Saturday 11 AM
                (5, 19, 0),  # Saturday 7 PM
                (6, 11, 0),  # Sunday 11 AM
                (6, 19, 0),  # Sunday 7 PM
            ],
            "linkedin": [
                # Weekday business hours (focused on Tues-Thurs)
                (1, 10, 0),  # Tuesday 10 AM
                (1, 14, 0),  # Tuesday 2 PM
                (2, 10, 0),  # Wednesday 10 AM
                (2, 14, 0),  # Wednesday 2 PM
                (3, 10, 0),  # Thursday 10 AM
                (3, 14, 0),  # Thursday 2 PM
                (0, 11, 0),  # Monday 11 AM
                (4, 11, 0),  # Friday 11 AM
                # No weekend times for LinkedIn
            ]
        }
        
        self.logger.info("PostScheduler initialized with time zone: %s", time_zone)
    
    def get_optimal_time(
        self, 
        platform: str,
        from_time: Optional[datetime] = None,
        max_days_ahead: int = 7
    ) -> datetime:
        """
        Get the next optimal posting time for a platform.
        
        Args:
            platform: Target platform (twitter, instagram, linkedin)
            from_time: Base time to calculate from (default: now)
            max_days_ahead: Maximum days to look ahead
            
        Returns:
            Datetime representing the next optimal posting time
        """
        platform = platform.lower()
        if platform not in self.optimal_times:
            self.logger.warning("Unsupported platform: %s, using default times", platform)
            platform = "twitter"  # Use Twitter as default
        
        # Use current time if not specified
        if from_time is None:
            from_time = datetime.now()
        
        # Get the current day of week (0 = Monday, 6 = Sunday)
        current_day = from_time.weekday()
        
        # Filter optimal times for this platform
        platform_times = self.optimal_times[platform]
        
        # Check each day starting from today up to max_days_ahead
        for day_offset in range(max_days_ahead):
            target_day = (current_day + day_offset) % 7
            
            # Get optimal times for this day
            day_times = [
                (hour, minute) for day, hour, minute in platform_times 
                if day == target_day
            ]
            
            # Sort times by hour and minute
            day_times.sort()
            
            # If this is today, only consider times in the future
            if day_offset == 0:
                current_hour, current_minute = from_time.hour, from_time.minute
                
                # Filter for times later than current time
                future_times = [
                    (hour, minute) for hour, minute in day_times
                    if hour > current_hour or (hour == current_hour and minute > current_minute)
                ]
                
                day_times = future_times
            
            # If we have valid times for this day, use the first one
            if day_times:
                hour, minute = day_times[0]
                optimal_time = from_time + timedelta(days=day_offset)
                optimal_time = optimal_time.replace(
                    hour=hour, 
                    minute=minute, 
                    second=0, 
                    microsecond=0
                )
                
                self.logger.info(
                    "Next optimal time for %s: %s", 
                    platform, 
                    optimal_time.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                return optimal_time
        
        # If no optimal time found within max_days_ahead, default to tomorrow same time
        default_time = from_time + timedelta(days=1)
        default_time = default_time.replace(second=0, microsecond=0)
        
        self.logger.warning(
            "No optimal time found for %s within %d days, using default: %s",
            platform,
            max_days_ahead,
            default_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return default_time
    
    def get_bulk_schedule(
        self,
        platform: str,
        count: int,
        from_time: Optional[datetime] = None,
        min_hours_between: int = 8
    ) -> List[datetime]:
        """
        Generate a schedule for multiple posts.
        
        Args:
            platform: Target platform
            count: Number of posts to schedule
            from_time: Base time to calculate from (default: now)
            min_hours_between: Minimum hours between posts
            
        Returns:
            List of datetimes for the schedule
        """
        if from_time is None:
            from_time = datetime.now()
        
        schedule = []
        current_time = from_time
        
        for _ in range(count):
            # Get next optimal time
            next_time = self.get_optimal_time(platform, current_time)
            
            # Check if it's too close to previous post
            if schedule and (next_time - schedule[-1]).total_seconds() < min_hours_between * 3600:
                # Force minimum gap
                next_time = schedule[-1] + timedelta(hours=min_hours_between)
            
            schedule.append(next_time)
            
            # Use this time as the basis for the next calculation
            current_time = next_time + timedelta(minutes=1)
        
        return schedule
    
    def get_multi_platform_schedule(
        self,
        platforms: List[str],
        from_time: Optional[datetime] = None,
        stagger_minutes: int = 15
    ) -> Dict[str, datetime]:
        """
        Get optimal posting times for multiple platforms.
        
        Args:
            platforms: List of target platforms
            from_time: Base time to calculate from (default: now)
            stagger_minutes: Minimum minutes between platform posts
            
        Returns:
            Dictionary mapping platforms to optimal posting times
        """
        if from_time is None:
            from_time = datetime.now()
        
        schedule = {}
        current_time = from_time
        
        for platform in platforms:
            # Get next optimal time for this platform
            next_time = self.get_optimal_time(platform, current_time)
            
            # Add to schedule
            schedule[platform] = next_time
            
            # Stagger the next platform by at least stagger_minutes
            current_time = max(
                current_time + timedelta(minutes=stagger_minutes),
                next_time + timedelta(minutes=stagger_minutes)
            )
        
        return schedule 