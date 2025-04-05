#!/usr/bin/env python3
"""
Analytics Agent Tools - Functions for fetching platform metrics,
generating reports, and creating visualizations.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import openai
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI()

async def fetch_platform_metrics(
    client: Any,
    platform: str,
    start_date: datetime,
    end_date: datetime,
    metrics: List[str]
) -> Dict[str, Any]:
    """
    Fetch metrics from a social media platform
    
    Args:
        client: Platform client
        platform: Platform name
        start_date: Start date for data
        end_date: End date for data
        metrics: List of metrics to fetch
        
    Returns:
        Dictionary of platform metrics
    """
    logger.info(f"Fetching {platform} metrics from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        platform_metrics = {
            "platform": platform,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary_metrics": {},
            "daily_metrics": []
        }
        
        # Generate sample summary metrics
        platform_metrics["summary_metrics"] = generate_sample_summary_metrics(platform, metrics)
        
        # Generate sample daily metrics
        current_date = start_date
        while current_date <= end_date:
            daily_data = {
                "date": current_date.isoformat(),
                "metrics": generate_sample_daily_metrics(platform, metrics, current_date)
            }
            platform_metrics["daily_metrics"].append(daily_data)
            current_date += timedelta(days=1)
        
        return platform_metrics
        
    except Exception as e:
        logger.error(f"Error fetching {platform} metrics: {str(e)}")
        return {
            "platform": platform,
            "error": str(e),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }

def generate_sample_summary_metrics(platform: str, metrics: List[str]) -> Dict[str, Any]:
    """Generate sample summary metrics for demo purposes"""
    summary = {}
    
    # Platform-specific baseline values
    baselines = {
        "instagram": {
            "impressions": 10000,
            "reach": 8000,
            "followers": 5000,
            "likes": 2000,
            "comments": 200,
            "shares": 100,
            "saves": 150,
            "profile_visits": 500,
            "clicks": 300,
            "engagement_rate": 3.5
        },
        "twitter": {
            "impressions": 15000,
            "reach": 12000,
            "followers": 8000,
            "likes": 1500,
            "comments": 300,
            "retweets": 200,
            "quotes": 50,
            "profile_visits": 400,
            "clicks": 250,
            "engagement_rate": 2.8
        },
        "linkedin": {
            "impressions": 8000,
            "reach": 6000,
            "followers": 3000,
            "likes": 800,
            "comments": 150,
            "shares": 80,
            "profile_visits": 300,
            "clicks": 400,
            "engagement_rate": 2.2
        }
    }
    
    # Use platform-specific baseline or default
    baseline = baselines.get(platform, baselines["instagram"])
    
    # Generate metrics
    for metric in metrics:
        if metric in baseline:
            # Add some randomness to the baseline value
            value = baseline[metric] * random.uniform(0.9, 1.1)
            
            # Format based on metric type
            if metric == "engagement_rate":
                summary[metric] = round(value, 2)
            else:
                summary[metric] = int(value)
    
    # Add growth metrics
    if "followers" in summary:
        summary["follower_growth"] = int(summary["followers"] * random.uniform(0.01, 0.05))
        summary["follower_growth_rate"] = round(summary["follower_growth"] / summary["followers"] * 100, 2)
    
    return summary

def generate_sample_daily_metrics(platform: str, metrics: List[str], date: datetime) -> Dict[str, Any]:
    """Generate sample daily metrics for demo purposes"""
    daily_metrics = {}
    
    # Platform-specific baseline values
    baselines = {
        "instagram": {
            "impressions": 300,
            "reach": 250,
            "new_followers": 10,
            "likes": 80,
            "comments": 8,
            "shares": 5,
            "saves": 6,
            "profile_visits": 20,
            "clicks": 15
        },
        "twitter": {
            "impressions": 500,
            "reach": 400,
            "new_followers": 15,
            "likes": 60,
            "comments": 12,
            "retweets": 8,
            "quotes": 2,
            "profile_visits": 18,
            "clicks": 10
        },
        "linkedin": {
            "impressions": 250,
            "reach": 200,
            "new_followers": 8,
            "likes": 30,
            "comments": 6,
            "shares": 4,
            "profile_visits": 15,
            "clicks": 20
        }
    }
    
    # Use platform-specific baseline or default
    baseline = baselines.get(platform, baselines["instagram"])
    
    # Apply day-of-week effect (weekends typically lower)
    weekday = date.weekday()
    if weekday >= 5:  # Weekend
        day_multiplier = 0.7
    else:  # Weekday
        day_multiplier = 1.0 + (0.1 * (2 - abs(weekday - 2)))  # Peak on Wednesday
    
    # Generate metrics
    for metric in metrics:
        # Convert engagement_rate to daily metrics
        if metric == "engagement_rate":
            continue
            
        # Convert followers to new_followers for daily
        if metric == "followers":
            metric_key = "new_followers"
        else:
            metric_key = metric
            
        if metric_key in baseline:
            # Add some randomness and apply day of week effect
            value = baseline[metric_key] * random.uniform(0.8, 1.2) * day_multiplier
            daily_metrics[metric_key] = int(value)
    
    # Calculate daily engagement rate if needed
    if "engagement_rate" in metrics:
        if "likes" in daily_metrics and "comments" in daily_metrics:
            if "impressions" in daily_metrics and daily_metrics["impressions"] > 0:
                engagement = (daily_metrics["likes"] + daily_metrics["comments"] * 2)
                daily_metrics["engagement_rate"] = round(engagement / daily_metrics["impressions"] * 100, 2)
            elif "reach" in daily_metrics and daily_metrics["reach"] > 0:
                engagement = (daily_metrics["likes"] + daily_metrics["comments"] * 2)
                daily_metrics["engagement_rate"] = round(engagement / daily_metrics["reach"] * 100, 2)
    
    return daily_metrics

async def generate_performance_report(
    platform_data: Dict[str, Any],
    report_type: str = "comprehensive_report",
    report_template: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a performance report from platform data
    
    Args:
        platform_data: Data fetched from platforms
        report_type: Type of report to generate
        report_template: Template for the report structure
        
    Returns:
        Generated report content
    """
    logger.info(f"Generating {report_type} performance report")
    
    # Extract date range for context
    date_range = platform_data.get("date_range", {})
    start_date = date_range.get("start_date", "")
    end_date = date_range.get("end_date", "")
    
    # Extract platform data
    platforms = platform_data.get("platforms", {})
    
    # Create prompt based on report type
    if report_type == "executive_summary":
        prompt = create_executive_summary_prompt(platforms, start_date, end_date)
    elif report_type == "metrics_snapshot":
        prompt = create_metrics_snapshot_prompt(platforms, start_date, end_date)
    else:  # comprehensive_report
        prompt = create_comprehensive_report_prompt(platforms, start_date, end_date)
    
    try:
        # Call LLM to generate the report
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert social media analyst who creates clear, data-driven reports with actionable insights."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        report_content = json.loads(response.choices[0].message.content)
        
        # Add metadata
        report_content["generated_at"] = datetime.now().isoformat()
        report_content["report_type"] = report_type
        report_content["date_range"] = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        return report_content
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {
            "error": str(e),
            "report_type": report_type,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "generated_at": datetime.now().isoformat(),
            "sections": {
                "error_message": f"Failed to generate report: {str(e)}"
            }
        }

def create_executive_summary_prompt(platforms: Dict[str, Any], start_date: str, end_date: str) -> str:
    """Create a prompt for executive summary report"""
    
    platforms_data = []
    for platform, data in platforms.items():
        summary = data.get("summary_metrics", {})
        platforms_data.append({
            "platform": platform,
            "summary_metrics": summary
        })
    
    prompt = f"""
    Generate an executive summary report for social media performance from {start_date} to {end_date}.
    
    PLATFORM DATA:
    {json.dumps(platforms_data, indent=2)}
    
    Create a concise executive summary with these sections:
    1. Overview - A high-level summary of overall social media performance
    2. Key Metrics - Highlight the most important metrics across platforms
    3. Trends - Identify any notable trends in the data
    4. Recommendations - Suggest 2-3 actionable recommendations
    
    Format your response as a JSON object with these keys:
    - "title": The report title
    - "sections": An object with keys for each section (overview, key_metrics, trends, recommendations)
    - "summary": A one-paragraph overall summary
    
    Keep the executive summary concise and focused on insights that would matter to leadership.
    """
    
    return prompt

def create_metrics_snapshot_prompt(platforms: Dict[str, Any], start_date: str, end_date: str) -> str:
    """Create a prompt for metrics snapshot report"""
    
    platforms_data = []
    for platform, data in platforms.items():
        summary = data.get("summary_metrics", {})
        platforms_data.append({
            "platform": platform,
            "summary_metrics": summary
        })
    
    prompt = f"""
    Generate a metrics snapshot report for social media performance from {start_date} to {end_date}.
    
    PLATFORM DATA:
    {json.dumps(platforms_data, indent=2)}
    
    Create a brief metrics snapshot with these sections:
    1. Key Metrics - The most important metrics across platforms
    2. Change from Previous - Compare current metrics to previous period (assume 5-10% growth as baseline)
    
    Format your response as a JSON object with these keys:
    - "title": The report title
    - "sections": An object with keys for each section (key_metrics, change_from_previous)
    - "summary": A one-paragraph overall summary
    
    Keep the snapshot very concise, focused purely on the numbers and their basic interpretation.
    """
    
    return prompt

def create_comprehensive_report_prompt(platforms: Dict[str, Any], start_date: str, end_date: str) -> str:
    """Create a prompt for comprehensive report"""
    
    # Prepare data for prompt (simplified to avoid token limits)
    platforms_summary = {}
    for platform, data in platforms.items():
        platforms_summary[platform] = {
            "summary_metrics": data.get("summary_metrics", {}),
            "daily_metrics_sample": data.get("daily_metrics", [])[:3]  # Just include a sample
        }
    
    prompt = f"""
    Generate a comprehensive social media analytics report for the period from {start_date} to {end_date}.
    
    PLATFORM DATA SUMMARY:
    {json.dumps(platforms_summary, indent=2)}
    
    Create a detailed report with these sections:
    1. Executive Summary - Overview of performance across all platforms
    2. Platform Analysis - Individual analysis of each platform's performance
    3. Content Performance - Analysis of what content worked best
    4. Audience Insights - Insights about audience behavior and demographics
    5. Competitor Analysis - Brief comparison to industry benchmarks
    6. Recommendations - Detailed, actionable recommendations for improvement
    
    Format your response as a JSON object with these keys:
    - "title": The report title
    - "sections": An object with keys for each section above
    - "summary": A concise executive summary
    - "key_insights": An array of the most important insights
    - "recommendations": An array of actionable recommendations
    
    Make the report data-driven, insightful, and focused on actionable recommendations.
    """
    
    return prompt

async def analyze_audience_demographics(
    client: Any,
    platform: str,
    include_demographics: bool = True
) -> Dict[str, Any]:
    """
    Analyze audience demographics and behavior
    
    Args:
        client: Platform client
        platform: Platform name
        include_demographics: Whether to include demographic data
        
    Returns:
        Dictionary of audience analysis
    """
    logger.info(f"Analyzing audience demographics for {platform}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        audience_data = {
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "total_followers": 0,
            "follower_growth": {
                "last_7_days": 0,
                "last_30_days": 0,
                "growth_rate": 0
            },
            "engagement": {
                "average_engagement_rate": 0,
                "most_engaging_content_types": []
            }
        }
        
        # Generate sample demographic data if requested
        if include_demographics:
            audience_data["demographics"] = generate_sample_demographics(platform)
        
        # Generate sample follower metrics
        follower_metrics = generate_sample_follower_metrics(platform)
        audience_data["total_followers"] = follower_metrics["total_followers"]
        audience_data["follower_growth"] = follower_metrics["follower_growth"]
        
        # Generate sample engagement metrics
        engagement_metrics = generate_sample_engagement_metrics(platform)
        audience_data["engagement"] = engagement_metrics
        
        # Generate sample audience interests
        audience_data["interests"] = generate_sample_interests(platform)
        
        # Generate sample active times
        audience_data["active_times"] = generate_sample_active_times()
        
        return audience_data
        
    except Exception as e:
        logger.error(f"Error analyzing audience for {platform}: {str(e)}")
        return {
            "platform": platform,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def generate_sample_demographics(platform: str) -> Dict[str, Any]:
    """Generate sample demographic data for demo purposes"""
    
    # Platform-specific demographic skews
    if platform == "instagram":
        age_distribution = {
            "18-24": 35,
            "25-34": 30,
            "35-44": 18,
            "45-54": 10,
            "55+": 7
        }
        gender_distribution = {
            "female": 58,
            "male": 41,
            "other": 1
        }
    elif platform == "twitter":
        age_distribution = {
            "18-24": 30,
            "25-34": 32,
            "35-44": 20,
            "45-54": 12,
            "55+": 6
        }
        gender_distribution = {
            "female": 48,
            "male": 51,
            "other": 1
        }
    elif platform == "linkedin":
        age_distribution = {
            "18-24": 15,
            "25-34": 35,
            "35-44": 30,
            "45-54": 15,
            "55+": 5
        }
        gender_distribution = {
            "female": 45,
            "male": 54,
            "other": 1
        }
    else:
        # Default values
        age_distribution = {
            "18-24": 25,
            "25-34": 30,
            "35-44": 25,
            "45-54": 15,
            "55+": 5
        }
        gender_distribution = {
            "female": 50,
            "male": 49,
            "other": 1
        }
    
    # Generate location data
    locations = {
        "United States": random.randint(30, 60),
        "United Kingdom": random.randint(5, 15),
        "Canada": random.randint(5, 10),
        "Australia": random.randint(3, 8),
        "Germany": random.randint(2, 7),
        "France": random.randint(2, 7),
        "Other": 0
    }
    
    # Ensure locations sum to 100%
    total = sum(locations.values())
    if total < 100:
        locations["Other"] = 100 - total
    
    return {
        "age_distribution": age_distribution,
        "gender_distribution": gender_distribution,
        "locations": locations,
        "languages": {
            "English": random.randint(70, 90),
            "Spanish": random.randint(3, 10),
            "French": random.randint(2, 5),
            "German": random.randint(2, 5),
            "Other": random.randint(2, 10)
        }
    }

def generate_sample_follower_metrics(platform: str) -> Dict[str, Any]:
    """Generate sample follower metrics for demo purposes"""
    
    # Platform-specific baseline values
    if platform == "instagram":
        total_followers = random.randint(4000, 6000)
    elif platform == "twitter":
        total_followers = random.randint(7000, 9000)
    elif platform == "linkedin":
        total_followers = random.randint(2500, 3500)
    else:
        total_followers = random.randint(3000, 7000)
    
    # Generate growth metrics
    last_7_days = int(total_followers * random.uniform(0.01, 0.03))
    last_30_days = int(total_followers * random.uniform(0.03, 0.08))
    growth_rate = round((last_30_days / total_followers) * 100, 2)
    
    return {
        "total_followers": total_followers,
        "follower_growth": {
            "last_7_days": last_7_days,
            "last_30_days": last_30_days,
            "growth_rate": growth_rate
        }
    }

def generate_sample_engagement_metrics(platform: str) -> Dict[str, Any]:
    """Generate sample engagement metrics for demo purposes"""
    
    # Platform-specific engagement rates
    if platform == "instagram":
        avg_rate = round(random.uniform(2.8, 4.2), 2)
        content_types = ["Carousel Posts", "Reels", "Stories"]
    elif platform == "twitter":
        avg_rate = round(random.uniform(1.5, 3.0), 2)
        content_types = ["Media Tweets", "Polls", "Threads"]
    elif platform == "linkedin":
        avg_rate = round(random.uniform(2.0, 3.5), 2)
        content_types = ["Industry Insights", "Company Updates", "Professional Tips"]
    else:
        avg_rate = round(random.uniform(2.0, 3.5), 2)
        content_types = ["Photos", "Videos", "Text Updates"]
    
    # Randomize the order of content types by engagement
    random.shuffle(content_types)
    
    return {
        "average_engagement_rate": avg_rate,
        "most_engaging_content_types": content_types,
        "engagement_by_type": {
            "likes": random.randint(60, 80),
            "comments": random.randint(10, 25),
            "shares": random.randint(5, 15),
            "saves": random.randint(5, 15) if platform == "instagram" else 0
        }
    }

def generate_sample_interests(platform: str) -> List[Dict[str, Any]]:
    """Generate sample audience interests for demo purposes"""
    
    # Common interest categories
    all_interests = [
        "Technology", "Business", "Entertainment", "Sports", "Health & Fitness",
        "Food & Dining", "Travel", "Fashion", "Home & Garden", "Arts & Culture",
        "Science", "Education", "Finance", "Gaming", "Beauty", "Outdoors"
    ]
    
    # Select 5-8 random interests
    num_interests = random.randint(5, 8)
    selected_interests = random.sample(all_interests, num_interests)
    
    # Assign affinity scores (0-100)
    interests = []
    for interest in selected_interests:
        interests.append({
            "category": interest,
            "affinity_score": random.randint(30, 95)
        })
    
    # Sort by affinity score (highest first)
    interests.sort(key=lambda x: x["affinity_score"], reverse=True)
    
    return interests

def generate_sample_active_times() -> Dict[str, Any]:
    """Generate sample active times for demo purposes"""
    
    # Generate day of week activity
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_activity = {}
    
    # Weekdays tend to have higher activity than weekends
    for day in days:
        if day in ["Saturday", "Sunday"]:
            day_activity[day] = random.randint(60, 85)
        else:
            day_activity[day] = random.randint(80, 100)
    
    # Generate time of day activity
    time_ranges = [
        "12am-3am", "3am-6am", "6am-9am", "9am-12pm",
        "12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am"
    ]
    
    time_activity = {}
    
    # Most activity during working hours and evening
    for time_range in time_ranges:
        if time_range in ["12am-3am", "3am-6am"]:
            time_activity[time_range] = random.randint(10, 30)
        elif time_range in ["6am-9am", "9am-12pm"]:
            time_activity[time_range] = random.randint(50, 80)
        elif time_range in ["12pm-3pm", "3pm-6pm"]:
            time_activity[time_range] = random.randint(70, 90)
        else:  # Evening
            time_activity[time_range] = random.randint(80, 100)
    
    return {
        "most_active_days": days[:3],  # Top 3 days
        "day_activity": day_activity,
        "most_active_times": ["6pm-9pm", "9pm-12am", "3pm-6pm"],  # Top 3 times
        "time_activity": time_activity
    }

async def identify_content_trends(
    platform_data: Dict[str, Any],
    trend_type: str = "content_performance"
) -> Dict[str, Any]:
    """
    Identify trends in platform data
    
    Args:
        platform_data: Data fetched from platforms
        trend_type: Type of trends to identify
        
    Returns:
        Dictionary of identified trends
    """
    logger.info(f"Identifying {trend_type} trends in platform data")
    
    # Extract platforms data
    platforms = platform_data.get("platforms", {})
    date_range = platform_data.get("date_range", {})
    
    try:
        # Prepare data for analysis
        trend_analysis = {
            "timestamp": datetime.now().isoformat(),
            "trend_type": trend_type,
            "date_range": date_range,
            "platform_trends": {},
            "cross_platform_trends": []
        }
        
        # Analyze each platform
        for platform_name, platform_data in platforms.items():
            if trend_type == "content_performance":
                platform_trends = identify_content_performance_trends(platform_name, platform_data)
            elif trend_type == "audience_growth":
                platform_trends = identify_audience_growth_trends(platform_name, platform_data)
            elif trend_type == "engagement_patterns":
                platform_trends = identify_engagement_pattern_trends(platform_name, platform_data)
            else:
                # Default to content performance
                platform_trends = identify_content_performance_trends(platform_name, platform_data)
            
            trend_analysis["platform_trends"][platform_name] = platform_trends
        
        # Generate cross-platform trends using LLM
        if len(platforms) > 1:
            prompt = create_cross_platform_trends_prompt(trend_analysis, trend_type)
            
            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an expert social media analyst specializing in cross-platform trend analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            cross_platform_trends = json.loads(response.choices[0].message.content)
            trend_analysis["cross_platform_trends"] = cross_platform_trends.get("trends", [])
        
        return trend_analysis
        
    except Exception as e:
        logger.error(f"Error identifying trends: {str(e)}")
        return {
            "error": str(e),
            "trend_type": trend_type,
            "timestamp": datetime.now().isoformat()
        }

def identify_content_performance_trends(platform: str, platform_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify content performance trends for a platform"""
    
    daily_metrics = platform_data.get("daily_metrics", [])
    summary_metrics = platform_data.get("summary_metrics", {})
    
    # Return empty trends if insufficient data
    if not daily_metrics:
        return {"trends": []}
    
    # Convert to DataFrame for analysis
    data = []
    for day_data in daily_metrics:
        date = day_data.get("date", "")
        metrics = day_data.get("metrics", {})
        row = {"date": date}
        row.update(metrics)
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Set date index if available
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    
    # Empty trends list to populate
    trends = []
    
    # Identify engagement trends
    if "engagement_rate" in df.columns:
        # Calculate weekly moving average
        if len(df) >= 7:
            df["engagement_ma7"] = df["engagement_rate"].rolling(window=7).mean()
            
            # Check if trend is up or down
            first_ma = df["engagement_ma7"].dropna().iloc[0] if not df["engagement_ma7"].dropna().empty else 0
            last_ma = df["engagement_ma7"].dropna().iloc[-1] if not df["engagement_ma7"].dropna().empty else 0
            
            if last_ma > first_ma * 1.1:  # 10% increase
                trends.append({
                    "trend": "Rising engagement",
                    "metric": "engagement_rate",
                    "change": f"{round((last_ma - first_ma) / first_ma * 100, 1)}%",
                    "direction": "up"
                })
            elif last_ma < first_ma * 0.9:  # 10% decrease
                trends.append({
                    "trend": "Declining engagement",
                    "metric": "engagement_rate",
                    "change": f"{round((last_ma - first_ma) / first_ma * 100, 1)}%",
                    "direction": "down"
                })
    
    # Identify audience growth trends
    if "new_followers" in df.columns:
        total_new_followers = df["new_followers"].sum()
        avg_daily_growth = df["new_followers"].mean()
        
        if avg_daily_growth > 0:
            trends.append({
                "trend": "Audience growth",
                "metric": "new_followers",
                "total": int(total_new_followers),
                "daily_average": round(avg_daily_growth, 1),
                "direction": "up"
            })
    
    # Identify content type trends - placeholder for actual implementation
    trends.append({
        "trend": f"Top content format for {platform}",
        "format": "Carousel" if platform == "instagram" else ("Threads" if platform == "twitter" else "Articles"),
        "insight": f"Consider creating more {platform}-optimized content in this format"
    })
    
    # Find peak days
    if len(df) >= 7:
        for metric in ["likes", "comments", "shares"]:
            if metric in df.columns:
                peak_day = df[metric].idxmax()
                peak_value = df[metric].max()
                
                trends.append({
                    "trend": f"Peak {metric}",
                    "date": peak_day.strftime("%Y-%m-%d") if isinstance(peak_day, pd.Timestamp) else str(peak_day),
                    "value": int(peak_value),
                    "insight": f"Analyze content posted on this date to understand what resonated with the audience"
                })
    
    return {
        "platform": platform,
        "trends": trends,
        "insight_summary": f"Performance analysis for {platform} reveals {len(trends)} key trends to monitor"
    }

def identify_audience_growth_trends(platform: str, platform_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify audience growth trends for a platform"""
    # Similar implementation to content_performance_trends but focused on audience metrics
    # For brevity, returning a placeholder
    return {
        "platform": platform,
        "trends": [
            {
                "trend": "Consistent follower growth",
                "metric": "new_followers",
                "insight": "Account is growing steadily, indicating content resonates with the target audience"
            },
            {
                "trend": "Engagement-to-follower ratio",
                "metric": "engagement_rate",
                "insight": "Engagement is growing faster than followers, suggesting increasing relevance"
            }
        ],
        "insight_summary": f"Audience growth analysis for {platform} shows positive momentum"
    }

def identify_engagement_pattern_trends(platform: str, platform_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify engagement pattern trends for a platform"""
    # Similar implementation to content_performance_trends but focused on engagement patterns
    # For brevity, returning a placeholder
    return {
        "platform": platform,
        "trends": [
            {
                "trend": "Time-of-day engagement",
                "pattern": "Peak engagement during evening hours (6pm-9pm)",
                "insight": "Schedule high-value content during peak engagement hours"
            },
            {
                "trend": "Comment-to-like ratio",
                "pattern": "Increasing meaningful interactions",
                "insight": "Content is generating more conversation, indicating deeper engagement"
            }
        ],
        "insight_summary": f"Engagement pattern analysis for {platform} reveals optimal posting strategies"
    }

def create_cross_platform_trends_prompt(trend_analysis: Dict[str, Any], trend_type: str) -> str:
    """Create a prompt for identifying cross-platform trends"""
    
    platform_trends = json.dumps(trend_analysis.get("platform_trends", {}), indent=2)
    
    prompt = f"""
    Analyze the following platform-specific trends and identify cross-platform patterns and insights.
    
    TREND TYPE: {trend_type}
    
    PLATFORM TRENDS:
    {platform_trends}
    
    Identify 3-5 cross-platform trends or patterns based on the data above.
    For each trend, include:
    1. The trend name
    2. Platforms where this trend is observed
    3. Relevant metrics
    4. Strategic insight or recommendation
    
    Format your response as a JSON object with a single key "trends" containing an array of trend objects.
    Each trend object should have keys for "name", "platforms", "metrics", and "insight".
    """
    
    return prompt

async def create_visualization(
    data: Dict[str, Any],
    visualization_type: str,
    title: str,
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a data visualization
    
    Args:
        data: Data to visualize
        visualization_type: Type of visualization
        title: Visualization title
        preferences: Visualization preferences
        
    Returns:
        Dictionary with visualization metadata and file path
    """
    logger.info(f"Creating {visualization_type} visualization: {title}")
    
    # Get preferences
    color_scheme = preferences.get("color_scheme", ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"])
    dimensions = preferences.get("default_dimensions", [1200, 800])
    include_branding = preferences.get("include_branding", True)
    
    try:
        # Create figure
        plt.figure(figsize=(dimensions[0]/100, dimensions[1]/100), dpi=100)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Apply custom color scheme
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=color_scheme)
        
        # Generate the appropriate visualization
        if visualization_type == "engagement_metrics":
            fig = create_engagement_metrics_viz(data, title, color_scheme)
        elif visualization_type == "audience_growth":
            fig = create_audience_growth_viz(data, title, color_scheme)
        elif visualization_type == "platform_comparison":
            fig = create_platform_comparison_viz(data, title, color_scheme)
        else:
            # Default to engagement metrics
            fig = create_engagement_metrics_viz(data, title, color_scheme)
        
        # Add branding if requested
        if include_branding:
            fig.text(0.99, 0.01, "Created by Analytics Agent", 
                    ha='right', va='bottom', alpha=0.5, fontsize=8)
        
        # Generate filename and save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = title.lower().replace(" ", "_").replace("/", "_")
        filename = f"data/visualizations/{safe_title}_{timestamp}.png"
        
        # Save the figure
        fig.savefig(filename, bbox_inches='tight', dpi=100)
        
        # Close the figure to free memory
        plt.close(fig)
        
        return {
            "title": title,
            "type": visualization_type,
            "file_path": filename,
            "timestamp": datetime.now().isoformat(),
            "dimensions": dimensions
        }
        
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        return {
            "error": str(e),
            "title": title,
            "type": visualization_type,
            "timestamp": datetime.now().isoformat()
        }

def create_engagement_metrics_viz(data: Dict[str, Any], title: str, color_scheme: List[str]) -> Figure:
    """Create engagement metrics visualization"""
    
    platform = data.get("platform", "")
    daily_metrics = data.get("daily_metrics", [])
    
    # Extract dates and metrics
    dates = []
    likes = []
    comments = []
    shares = []
    engagement_rates = []
    
    for day_data in daily_metrics:
        date = datetime.fromisoformat(day_data.get("date", ""))
        metrics = day_data.get("metrics", {})
        
        dates.append(date)
        likes.append(metrics.get("likes", 0))
        comments.append(metrics.get("comments", 0))
        shares.append(metrics.get("shares", 0) if "shares" in metrics else 
                      metrics.get("retweets", 0) if "retweets" in metrics else 0)
        engagement_rates.append(metrics.get("engagement_rate", 0))
    
    # Create figure with two y-axes
    fig, ax1 = plt.subplots()
    
    # First y-axis for engagement counts
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Count')
    
    # Plot engagement metrics
    ax1.plot(dates, likes, color=color_scheme[0], marker='o', linestyle='-', linewidth=2, markersize=5, label='Likes')
    ax1.plot(dates, comments, color=color_scheme[1], marker='s', linestyle='-', linewidth=2, markersize=5, label='Comments')
    ax1.plot(dates, shares, color=color_scheme[2], marker='^', linestyle='-', linewidth=2, markersize=5, label='Shares')
    
    # Format x-axis with dates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    
    # Second y-axis for engagement rate
    ax2 = ax1.twinx()
    ax2.set_ylabel('Engagement Rate (%)')
    ax2.plot(dates, engagement_rates, color=color_scheme[3], marker='d', linestyle='--', linewidth=2, markersize=5, label='Engagement Rate')
    
    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Set title
    plt.title(title)
    
    # Adjust layout
    plt.tight_layout()
    
    # Rotate x-axis labels for better readability
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    return fig

def create_audience_growth_viz(data: Dict[str, Any], title: str, color_scheme: List[str]) -> Figure:
    """Create audience growth visualization"""
    
    platform = data.get("platform", "")
    daily_metrics = data.get("daily_metrics", [])
    
    # Extract dates and metrics
    dates = []
    new_followers = []
    cumulative_followers = []
    
    # Running total for cumulative
    running_total = 0
    
    for day_data in daily_metrics:
        date = datetime.fromisoformat(day_data.get("date", ""))
        metrics = day_data.get("metrics", {})
        
        # Get new followers for this day
        daily_new = metrics.get("new_followers", 0)
        
        dates.append(date)
        new_followers.append(daily_new)
        
        # Add to running total
        running_total += daily_new
        cumulative_followers.append(running_total)
    
    # Create figure with two y-axes
    fig, ax1 = plt.subplots()
    
    # First y-axis for daily new followers
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Daily New Followers')
    
    # Plot daily new followers as bars
    ax1.bar(dates, new_followers, color=color_scheme[0], alpha=0.7, label='New Followers')
    
    # Format x-axis with dates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    
    # Second y-axis for cumulative followers
    ax2 = ax1.twinx()
    ax2.set_ylabel('Cumulative New Followers')
    ax2.plot(dates, cumulative_followers, color=color_scheme[1], marker='o', linestyle='-', linewidth=2, markersize=5, label='Cumulative')
    
    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Set title
    plt.title(title)
    
    # Adjust layout
    plt.tight_layout()
    
    # Rotate x-axis labels for better readability
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    return fig

def create_platform_comparison_viz(data: Dict[str, Any], title: str, color_scheme: List[str]) -> Figure:
    """Create platform comparison visualization"""
    
    platforms = data.get("platforms", {})
    
    # Extract platform names and engagement rates
    platform_names = []
    engagement_rates = []
    follower_counts = []
    post_counts = []
    
    for platform_name, platform_data in platforms.items():
        summary = platform_data.get("summary_metrics", {})
        
        platform_names.append(platform_name.capitalize())
        engagement_rates.append(summary.get("engagement_rate", 0))
        follower_counts.append(summary.get("followers", 0))
        # Estimate post count from daily metrics
        post_counts.append(len(platform_data.get("daily_metrics", [])))
    
    # Create figure for comparison charts
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot engagement rates (bar chart)
    ax1.bar(platform_names, engagement_rates, color=color_scheme[:len(platform_names)])
    ax1.set_ylabel('Engagement Rate (%)')
    ax1.set_title('Engagement Rate by Platform')
    
    # Add values on top of bars
    for i, v in enumerate(engagement_rates):
        ax1.text(i, v + 0.1, str(round(v, 2)) + '%', ha='center')
    
    # Plot followers (bar chart)
    ax2.bar(platform_names, follower_counts, color=color_scheme[-len(platform_names):])
    ax2.set_ylabel('Follower Count')
    ax2.set_title('Followers by Platform')
    
    # Format y-axis labels with k for thousands
    ax2.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    
    # Add values on top of bars
    for i, v in enumerate(follower_counts):
        ax2.text(i, v + (max(follower_counts) * 0.02), format(int(v), ','), ha='center')
    
    # Plot ratio of engagement to followers (pie chart)
    engagement_per_follower = [e / f * 100 if f > 0 else 0 for e, f in zip(engagement_rates, follower_counts)]
    
    ax3.pie(engagement_per_follower, labels=platform_names, autopct='%1.1f%%', 
            colors=color_scheme[:len(platform_names)], startangle=90)
    ax3.set_title('Engagement Per Follower Ratio')
    
    # Set overall title
    fig.suptitle(title, fontsize=16)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    
    return fig

async def export_report_to_format(
    report: Dict[str, Any],
    export_format: str = "pdf"
) -> Dict[str, Any]:
    """
    Export report to a specified format
    
    Args:
        report: Report to export
        export_format: Format to export to (pdf, html, etc.)
        
    Returns:
        Dictionary with export metadata and file path
    """
    logger.info(f"Exporting report to {export_format}")
    
    try:
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_type = report.get("report_type", "analytics")
        filename = f"data/reports/{report_type}_{timestamp}"
        
        if export_format == "json":
            # Save directly as JSON
            with open(f"{filename}.json", "w") as f:
                json.dump(report, f, indent=2)
            
            file_path = f"{filename}.json"
            file_size = os.path.getsize(file_path)
            
        elif export_format == "html":
            # Generate HTML report
            html_content = convert_report_to_html(report)
            
            with open(f"{filename}.html", "w") as f:
                f.write(html_content)
            
            file_path = f"{filename}.html"
            file_size = os.path.getsize(file_path)
            
        elif export_format == "pdf":
            # For demo, we'll just use HTML and note that PDF conversion would require additional libraries
            html_content = convert_report_to_html(report)
            
            with open(f"{filename}.html", "w") as f:
                f.write(html_content)
                
            # Note: In a real implementation, would use a library like weasyprint or reportlab
            # to convert HTML to PDF
            
            file_path = f"{filename}.html"  # Would be .pdf in real implementation
            file_size = os.path.getsize(file_path)
            
        else:
            # Default to JSON
            with open(f"{filename}.json", "w") as f:
                json.dump(report, f, indent=2)
            
            file_path = f"{filename}.json"
            file_size = os.path.getsize(file_path)
        
        return {
            "format": export_format,
            "file_path": file_path,
            "file_size": file_size,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return {
            "error": str(e),
            "format": export_format,
            "timestamp": datetime.now().isoformat()
        }

def convert_report_to_html(report: Dict[str, Any]) -> str:
    """Convert a report to HTML format"""
    
    title = report.get("title", "Analytics Report")
    report_type = report.get("report_type", "analytics")
    date_range = report.get("date_range", {})
    start_date = date_range.get("start_date", "")
    end_date = date_range.get("end_date", "")
    sections = report.get("sections", {})
    
    # Basic HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #f8f9fa; padding: 20px; margin-bottom: 20px; border-bottom: 1px solid #dee2e6; }}
            .section {{ margin-bottom: 30px; }}
            h1 {{ color: #212529; }}
            h2 {{ color: #343a40; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #dee2e6; }}
            th {{ background-color: #f8f9fa; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #f8f9fa; 
                       border-radius: 5px; text-align: center; width: 150px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
            .metric-label {{ font-size: 14px; color: #6c757d; }}
            .visualization {{ margin: 20px 0; max-width: 100%; height: auto; }}
            footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <p>Report Type: {report_type.title()}</p>
                <p>Period: {start_date} - {end_date}</p>
            </div>
    """
    
    # Add each section
    for section_name, section_content in sections.items():
        section_title = section_name.replace("_", " ").title()
        
        html += f"""
            <div class="section">
                <h2>{section_title}</h2>
        """
        
        # If section content is a string, add it directly
        if isinstance(section_content, str):
            html += f"<p>{section_content}</p>"
        # If it's a list, format as bullet points
        elif isinstance(section_content, list):
            html += "<ul>"
            for item in section_content:
                if isinstance(item, str):
                    html += f"<li>{item}</li>"
                elif isinstance(item, dict):
                    # Format dict items based on common patterns
                    if "name" in item and "value" in item:
                        html += f"<li><strong>{item['name']}:</strong> {item['value']}</li>"
                    elif "trend" in item:
                        trend_html = f"<li><strong>{item.get('trend')}</strong>"
                        if "direction" in item:
                            direction = item.get("direction")
                            arrow = "↑" if direction == "up" else "↓" if direction == "down" else "→"
                            trend_html += f" {arrow}"
                        if "change" in item:
                            trend_html += f" ({item.get('change')})"
                        if "insight" in item:
                            trend_html += f"<br>{item.get('insight')}"
                        trend_html += "</li>"
                        html += trend_html
                    else:
                        # Generic dict formatting
                        html += f"<li>{str(item)}</li>"
            html += "</ul>"
        # If it's a dict, format as an appropriate visualization
        elif isinstance(section_content, dict):
            # Check for common dict patterns and format accordingly
            if "metrics" in section_content:
                metrics = section_content["metrics"]
                html += '<div class="metrics-container">'
                for metric_name, metric_value in metrics.items():
                    formatted_name = metric_name.replace("_", " ").title()
                    html += f"""
                        <div class="metric">
                            <div class="metric-value">{metric_value}</div>
                            <div class="metric-label">{formatted_name}</div>
                        </div>
                    """
                html += '</div>'
            else:
                # Generic dict formatting as key-value pairs
                html += "<ul>"
                for key, value in section_content.items():
                    formatted_key = key.replace("_", " ").title()
                    html += f"<li><strong>{formatted_key}:</strong> {value}</li>"
                html += "</ul>"
        
        html += "</div>"
    
    # Add visualizations if available
    if "visualizations" in report:
        html += '<div class="section"><h2>Visualizations</h2>'
        for i, viz in enumerate(report["visualizations"]):
            file_path = viz.get("file_path", "")
            if file_path:
                viz_title = viz.get("title", f"Visualization {i+1}")
                html += f"""
                    <div class="visualization-container">
                        <h3>{viz_title}</h3>
                        <img src="../{file_path}" alt="{viz_title}" class="visualization">
                    </div>
                """
        html += '</div>'
    
    # Add recommendations if available
    if "recommendations" in report:
        html += '<div class="section"><h2>Recommendations</h2><ul>'
        for rec in report["recommendations"]:
            if isinstance(rec, str):
                html += f"<li>{rec}</li>"
            elif isinstance(rec, dict) and "text" in rec:
                html += f"<li>{rec['text']}</li>"
            elif isinstance(rec, dict) and "recommendation" in rec:
                html += f"<li>{rec['recommendation']}</li>"
        html += '</ul></div>'
    
    # Add footer and close HTML
    html += f"""
            <footer>
                Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • Analytics Agent
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html 