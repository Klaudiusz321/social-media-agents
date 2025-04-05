#!/usr/bin/env python3
"""
Ad Campaign Manager Agent Tools - Functions for creating, managing,
and optimizing ad campaigns across multiple platforms.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI()

async def create_campaign(
    client: Any,
    platform: str,
    campaign_name: str,
    objective: str,
    budget: float,
    start_date: datetime,
    end_date: datetime,
    audience: Dict[str, Any],
    creatives: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create an ad campaign on a specific platform
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_name: Name of the campaign
        objective: Campaign objective
        budget: Budget for the campaign
        start_date: Campaign start date
        end_date: Campaign end date
        audience: Audience targeting parameters
        creatives: Creative assets and copy
        
    Returns:
        Dictionary with campaign creation results
    """
    logger.info(f"Creating {platform} campaign: {campaign_name}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        campaign_id = f"{platform[0:3]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Simulate API call delay
        await asyncio.sleep(1)
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "objective": objective,
            "budget": budget,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": "CREATED",
            "creation_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating {platform} campaign: {str(e)}")
        return {
            "platform": platform,
            "error": str(e),
            "creation_time": datetime.now().isoformat()
        }

async def update_campaign(
    client: Any,
    platform: str,
    campaign_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing ad campaign
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_id: ID of the campaign to update
        updates: Dictionary of updates to apply
        
    Returns:
        Dictionary with update results
    """
    logger.info(f"Updating {platform} campaign: {campaign_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(1)
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "updates": updates,
            "status": "UPDATED",
            "update_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating {platform} campaign: {str(e)}")
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "error": str(e),
            "update_time": datetime.now().isoformat()
        }

async def get_campaign_status(
    client: Any,
    platform: str,
    campaign_id: str
) -> Dict[str, Any]:
    """
    Get the status of an ad campaign
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_id: ID of the campaign
        
    Returns:
        Dictionary with campaign status
    """
    logger.info(f"Getting status for {platform} campaign: {campaign_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        # Generate a random status
        statuses = ["ACTIVE", "PAUSED", "SCHEDULED", "COMPLETED", "PENDING_REVIEW"]
        status = random.choice(statuses)
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "status": status,
            "budget_spent": round(random.uniform(10, 500), 2),
            "budget_remaining": round(random.uniform(10, 500), 2),
            "impressions": random.randint(1000, 50000),
            "check_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting {platform} campaign status: {str(e)}")
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "error": str(e),
            "check_time": datetime.now().isoformat()
        }

async def get_campaign_performance(
    client: Any,
    platform: str,
    campaign_id: str
) -> Dict[str, Any]:
    """
    Get the performance data of an ad campaign
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_id: ID of the campaign
        
    Returns:
        Dictionary with campaign performance data
    """
    logger.info(f"Getting performance for {platform} campaign: {campaign_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(0.7)
        
        # Generate random performance metrics
        impressions = random.randint(5000, 100000)
        clicks = int(impressions * random.uniform(0.01, 0.05))
        spend = round(random.uniform(100, 1000), 2)
        conversions = int(clicks * random.uniform(0.05, 0.2))
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "impressions": impressions,
            "reach": int(impressions * random.uniform(0.7, 0.9)),
            "clicks": clicks,
            "ctr": round((clicks / impressions) * 100, 2),
            "spend": spend,
            "cpc": round(spend / clicks if clicks > 0 else 0, 2),
            "conversions": conversions,
            "conversion_rate": round((conversions / clicks if clicks > 0 else 0) * 100, 2),
            "cost_per_conversion": round(spend / conversions if conversions > 0 else 0, 2),
            "frequency": round(random.uniform(1.1, 3.0), 1),
            "engagement": random.randint(1000, 5000),
            "report_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting {platform} campaign performance: {str(e)}")
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "error": str(e),
            "report_time": datetime.now().isoformat()
        }

async def optimize_campaign_budget(
    performance_data: Dict[str, Any],
    total_budget: float
) -> Dict[str, Any]:
    """
    Optimize the budget allocation across platforms
    
    Args:
        performance_data: Campaign performance data
        total_budget: Total budget to allocate
        
    Returns:
        Dictionary with budget optimization recommendations
    """
    logger.info("Optimizing campaign budget allocation")
    
    platforms_data = performance_data.get("platforms", {})
    campaign_id = performance_data.get("campaign_id")
    
    # Calculate performance metrics for each platform
    platform_metrics = {}
    for platform, data in platforms_data.items():
        if "error" in data:
            continue
            
        impressions = data.get("impressions", 0)
        clicks = data.get("clicks", 0)
        conversions = data.get("conversions", 0)
        spend = data.get("spend", 0)
        
        # Calculate cost efficiency metrics
        cpc = spend / clicks if clicks > 0 else float('inf')
        cpm = (spend / impressions) * 1000 if impressions > 0 else float('inf')
        cpa = spend / conversions if conversions > 0 else float('inf')
        
        platform_metrics[platform] = {
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "cpc": cpc,
            "cpm": cpm,
            "cpa": cpa
        }
    
    # No valid platforms to optimize
    if not platform_metrics:
        return {
            "error": "No valid platform data available for optimization",
            "campaign_id": campaign_id
        }
    
    # Determine optimization weights based on performance
    # Lower CPA/CPC is better, so invert for weighting
    weights = {}
    total_weight = 0
    
    for platform, metrics in platform_metrics.items():
        # Use CPA if available, otherwise CPC, otherwise CPM
        if metrics["conversions"] > 0:
            weight = 1.0 / (metrics["cpa"] + 0.01)
        elif metrics["clicks"] > 0:
            weight = 1.0 / (metrics["cpc"] + 0.01)
        else:
            weight = 1.0 / (metrics["cpm"] + 0.01)
            
        weights[platform] = weight
        total_weight += weight
    
    # Calculate new budget allocation
    budget_allocation = {}
    for platform, weight in weights.items():
        allocation_percent = weight / total_weight
        budget_allocation[platform] = round(total_budget * allocation_percent, 2)
    
    # Generate recommendations
    recommendations = []
    for platform, budget in budget_allocation.items():
        current_budget = platform_metrics[platform]["spend"]
        if budget > current_budget * 1.1:
            recommendations.append(f"Increase {platform} budget from ${current_budget:.2f} to ${budget:.2f} based on better performance")
        elif budget < current_budget * 0.9:
            recommendations.append(f"Decrease {platform} budget from ${current_budget:.2f} to ${budget:.2f} to optimize spending")
    
    return {
        "campaign_id": campaign_id,
        "total_budget": total_budget,
        "budget_allocation": budget_allocation,
        "performance_metrics": platform_metrics,
        "recommendations": recommendations
    }

async def generate_ad_creative(
    platform: str,
    creative_type: str,
    campaign_type: str,
    product_info: Dict[str, Any],
    template: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate ad creative content for a specific platform
    
    Args:
        platform: Platform name
        creative_type: Type of creative (single_image, carousel, video)
        campaign_type: Type of campaign (awareness, engagement, conversion)
        product_info: Information about the product/service
        template: Template for the creative
        
    Returns:
        Dictionary with generated creative content
    """
    logger.info(f"Generating {creative_type} creative for {platform}")
    
    try:
        # Extract product information
        product_name = product_info.get("name", "Product")
        description = product_info.get("description", "")
        features = product_info.get("features", [])
        benefits = product_info.get("benefits", [])
        price = product_info.get("price", "")
        target_audience = product_info.get("target_audience", {})
        
        # Create a prompt for the creative
        prompt = f"""
        Create ad creative content for a {campaign_type} campaign on {platform}.
        
        Product/Service:
        Name: {product_name}
        Description: {description}
        Key Features: {", ".join(features) if features else "N/A"}
        Benefits: {", ".join(benefits) if benefits else "N/A"}
        Price/Offer: {price}
        
        Creative Type: {creative_type}
        Campaign Type: {campaign_type}
        
        Target Audience: {json.dumps(target_audience) if target_audience else "General"}
        
        Generate the following:
        1. Headline(s)
        2. Primary Text/Description
        3. Call to Action
        4. Image/Video Description or Concept
        
        Format the response as a JSON object with appropriate keys.
        """
        
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert ad creative generator that creates platform-specific, high-converting ad content."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the creative content
        creative_content = json.loads(response.choices[0].message.content)
        
        # Add metadata
        creative_content["platform"] = platform
        creative_content["creative_type"] = creative_type
        creative_content["campaign_type"] = campaign_type
        creative_content["generated_at"] = datetime.now().isoformat()
        
        # Platform-specific adjustments
        if platform == "facebook" or platform == "instagram":
            if "headline" in creative_content and len(creative_content["headline"]) > 40:
                creative_content["headline"] = creative_content["headline"][:37] + "..."
                
            if "primary_text" in creative_content and len(creative_content["primary_text"]) > 125:
                creative_content["primary_text"] = creative_content["primary_text"][:122] + "..."
        
        elif platform == "twitter":
            if "primary_text" in creative_content and len(creative_content["primary_text"]) > 280:
                creative_content["primary_text"] = creative_content["primary_text"][:277] + "..."
        
        return creative_content
        
    except Exception as e:
        logger.error(f"Error generating creative: {str(e)}")
        return {
            "platform": platform,
            "creative_type": creative_type,
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }

async def schedule_campaign(
    client: Any,
    platform: str,
    campaign_id: str,
    schedule: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Schedule an ad campaign
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_id: ID of the campaign
        schedule: Scheduling parameters
        
    Returns:
        Dictionary with scheduling results
    """
    logger.info(f"Scheduling {platform} campaign: {campaign_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "schedule": schedule,
            "status": "SCHEDULED",
            "schedule_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scheduling {platform} campaign: {str(e)}")
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "error": str(e),
            "schedule_time": datetime.now().isoformat()
        }

async def pause_campaign(
    client: Any,
    platform: str,
    campaign_id: str
) -> Dict[str, Any]:
    """
    Pause an ad campaign
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_id: ID of the campaign
        
    Returns:
        Dictionary with pause results
    """
    logger.info(f"Pausing {platform} campaign: {campaign_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "status": "PAUSED",
            "pause_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error pausing {platform} campaign: {str(e)}")
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "error": str(e),
            "pause_time": datetime.now().isoformat()
        }

async def resume_campaign(
    client: Any,
    platform: str,
    campaign_id: str
) -> Dict[str, Any]:
    """
    Resume a paused ad campaign
    
    Args:
        client: Platform client
        platform: Platform name
        campaign_id: ID of the campaign
        
    Returns:
        Dictionary with resume results
    """
    logger.info(f"Resuming {platform} campaign: {campaign_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "status": "ACTIVE",
            "resume_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resuming {platform} campaign: {str(e)}")
        return {
            "platform": platform,
            "campaign_id": campaign_id,
            "error": str(e),
            "resume_time": datetime.now().isoformat()
        }

async def create_audience(
    client: Any,
    platform: str,
    audience_name: str,
    audience_definition: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a custom audience for ad targeting
    
    Args:
        client: Platform client
        platform: Platform name
        audience_name: Name of the audience
        audience_definition: Definition of the audience
        
    Returns:
        Dictionary with audience creation results
    """
    logger.info(f"Creating {platform} audience: {audience_name}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(0.8)
        
        audience_id = f"{platform[0:3]}_aud_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "platform": platform,
            "audience_id": audience_id,
            "audience_name": audience_name,
            "audience_definition": audience_definition,
            "estimated_size": random.randint(10000, 1000000),
            "status": "CREATED",
            "creation_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating {platform} audience: {str(e)}")
        return {
            "platform": platform,
            "error": str(e),
            "creation_time": datetime.now().isoformat()
        }

async def get_audience_insights(
    client: Any,
    platform: str,
    audience_id: str
) -> Dict[str, Any]:
    """
    Get insights about a custom audience
    
    Args:
        client: Platform client
        platform: Platform name
        audience_id: ID of the audience
        
    Returns:
        Dictionary with audience insights
    """
    logger.info(f"Getting insights for {platform} audience: {audience_id}")
    
    try:
        # This would call the actual platform API
        # For now, we'll generate sample data
        
        # Simulate API call delay
        await asyncio.sleep(1.2)
        
        # Generate demographic data
        demographics = {
            "age_distribution": {
                "18-24": random.randint(5, 30),
                "25-34": random.randint(20, 40),
                "35-44": random.randint(15, 30),
                "45-54": random.randint(10, 25),
                "55+": random.randint(5, 20)
            },
            "gender_distribution": {
                "male": random.randint(30, 70),
                "female": random.randint(30, 70)
            },
            "location_top_5": [
                {"location": "New York", "percentage": random.randint(5, 15)},
                {"location": "Los Angeles", "percentage": random.randint(4, 12)},
                {"location": "Chicago", "percentage": random.randint(3, 10)},
                {"location": "Houston", "percentage": random.randint(2, 8)},
                {"location": "Miami", "percentage": random.randint(2, 8)}
            ]
        }
        
        # Ensure gender distribution sums to 100%
        male_percent = demographics["gender_distribution"]["male"]
        female_percent = demographics["gender_distribution"]["female"]
        total = male_percent + female_percent
        demographics["gender_distribution"]["male"] = int(male_percent / total * 100)
        demographics["gender_distribution"]["female"] = 100 - demographics["gender_distribution"]["male"]
        
        # Generate interest data
        interests = [
            {"category": "Technology", "affinity_score": random.randint(50, 100)},
            {"category": "Travel", "affinity_score": random.randint(40, 90)},
            {"category": "Fashion", "affinity_score": random.randint(30, 80)},
            {"category": "Food & Dining", "affinity_score": random.randint(30, 80)},
            {"category": "Sports", "affinity_score": random.randint(30, 80)},
            {"category": "Entertainment", "affinity_score": random.randint(40, 90)},
            {"category": "Health & Fitness", "affinity_score": random.randint(30, 80)}
        ]
        
        # Sort interests by affinity score
        interests.sort(key=lambda x: x["affinity_score"], reverse=True)
        
        return {
            "platform": platform,
            "audience_id": audience_id,
            "audience_size": random.randint(10000, 1000000),
            "demographics": demographics,
            "interests": interests,
            "devices": {
                "mobile": random.randint(50, 80),
                "desktop": random.randint(20, 50),
                "tablet": random.randint(5, 15)
            },
            "report_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting {platform} audience insights: {str(e)}")
        return {
            "platform": platform,
            "audience_id": audience_id,
            "error": str(e),
            "report_time": datetime.now().isoformat()
        }

async def analyze_campaign_performance(
    performance_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze campaign performance and generate insights
    
    Args:
        performance_data: Campaign performance data
        
    Returns:
        Dictionary with performance analysis
    """
    logger.info("Analyzing campaign performance")
    
    try:
        # Extract key information
        campaign_name = performance_data.get("campaign_name", "")
        campaign_id = performance_data.get("campaign_id", "")
        platforms = performance_data.get("platforms", {})
        summary = performance_data.get("summary", {})
        
        # Create a prompt for analysis
        platforms_data = []
        for platform, data in platforms.items():
            if "error" not in data:
                platforms_data.append({
                    "platform": platform,
                    "metrics": data
                })
        
        prompt = f"""
        Analyze the following ad campaign performance data and provide insights and recommendations.
        
        Campaign: {campaign_name}
        ID: {campaign_id}
        
        Summary Metrics:
        {json.dumps(summary, indent=2)}
        
        Platform Performance:
        {json.dumps(platforms_data, indent=2)}
        
        Provide the following in your analysis:
        1. Overall Performance Summary
        2. Key Metrics Analysis
        3. Platform Comparison
        4. Areas of Strength
        5. Areas for Improvement
        6. Specific Recommendations (at least 3)
        
        Format your response as a JSON object with appropriate keys for each section.
        """
        
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert ad campaign analyst who provides clear, data-driven insights and actionable recommendations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the analysis
        analysis = json.loads(response.choices[0].message.content)
        
        # Add metadata
        analysis["campaign_id"] = campaign_id
        analysis["campaign_name"] = campaign_name
        analysis["analysis_time"] = datetime.now().isoformat()
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing campaign performance: {str(e)}")
        return {
            "error": str(e),
            "campaign_id": performance_data.get("campaign_id", ""),
            "analysis_time": datetime.now().isoformat()
        }

async def export_campaign_report(
    performance_data: Dict[str, Any],
    report_type: str = "performance",
    export_format: str = "pdf"
) -> Dict[str, Any]:
    """
    Export a campaign report in a specific format
    
    Args:
        performance_data: Campaign performance data
        report_type: Type of report to export
        export_format: Format to export to (pdf, html, etc.)
        
    Returns:
        Dictionary with export metadata and file path
    """
    logger.info(f"Exporting {report_type} report in {export_format} format")
    
    try:
        campaign_name = performance_data.get("campaign_name", "campaign")
        campaign_id = performance_data.get("campaign_id", "")
        analysis = performance_data.get("analysis", {})
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/reports/{report_type}_{campaign_id}_{timestamp}"
        
        if export_format == "json":
            # Save as JSON
            with open(f"{filename}.json", "w") as f:
                json.dump(performance_data, f, indent=2)
            
            file_path = f"{filename}.json"
            file_size = os.path.getsize(file_path)
            
        elif export_format == "html":
            # Generate HTML report
            html_content = generate_html_report(performance_data, report_type)
            
            with open(f"{filename}.html", "w") as f:
                f.write(html_content)
            
            file_path = f"{filename}.html"
            file_size = os.path.getsize(file_path)
            
        elif export_format == "pdf":
            # For demo, we'll just use HTML and note that PDF conversion would require additional libraries
            html_content = generate_html_report(performance_data, report_type)
            
            with open(f"{filename}.html", "w") as f:
                f.write(html_content)
                
            # Note: In a real implementation, would use a library like weasyprint or reportlab
            # to convert HTML to PDF
            
            file_path = f"{filename}.html"  # Would be .pdf in real implementation
            file_size = os.path.getsize(file_path)
            
        else:
            # Default to JSON
            with open(f"{filename}.json", "w") as f:
                json.dump(performance_data, f, indent=2)
            
            file_path = f"{filename}.json"
            file_size = os.path.getsize(file_path)
        
        return {
            "campaign_id": campaign_id,
            "report_type": report_type,
            "format": export_format,
            "file_path": file_path,
            "file_size": file_size,
            "export_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return {
            "error": str(e),
            "campaign_id": performance_data.get("campaign_id", ""),
            "export_time": datetime.now().isoformat()
        }

def generate_html_report(performance_data: Dict[str, Any], report_type: str) -> str:
    """Generate an HTML report from performance data"""
    
    campaign_name = performance_data.get("campaign_name", "Campaign")
    campaign_id = performance_data.get("campaign_id", "")
    summary = performance_data.get("summary", {})
    platforms = performance_data.get("platforms", {})
    analysis = performance_data.get("analysis", {})
    
    # Basic HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{report_type.capitalize()} Report - {campaign_name}</title>
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
            footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{report_type.capitalize()} Report - {campaign_name}</h1>
                <p>Campaign ID: {campaign_id}</p>
                <p>Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
    """
    
    # Summary section
    html += """
            <div class="section">
                <h2>Performance Summary</h2>
                <div class="metrics-container">
    """
    
    for key, value in summary.items():
        label = key.replace("_", " ").title()
        formatted_value = f"${value}" if "cost" in key or "spend" in key else value
        if isinstance(value, float) and "rate" in key:
            formatted_value = f"{value}%"
            
        html += f"""
                    <div class="metric">
                        <div class="metric-value">{formatted_value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
    """
    
    # Platform comparison section
    html += """
            <div class="section">
                <h2>Platform Performance</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Impressions</th>
                            <th>Clicks</th>
                            <th>CTR</th>
                            <th>Conversions</th>
                            <th>Conv. Rate</th>
                            <th>Spend</th>
                            <th>CPC</th>
                            <th>CPA</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for platform, data in platforms.items():
        if "error" in data:
            continue
            
        impressions = data.get("impressions", 0)
        clicks = data.get("clicks", 0)
        ctr = data.get("ctr", 0)
        conversions = data.get("conversions", 0)
        conversion_rate = data.get("conversion_rate", 0)
        spend = data.get("spend", 0)
        cpc = data.get("cpc", 0)
        cost_per_conversion = data.get("cost_per_conversion", 0)
        
        html += f"""
                        <tr>
                            <td>{platform.capitalize()}</td>
                            <td>{impressions:,}</td>
                            <td>{clicks:,}</td>
                            <td>{ctr}%</td>
                            <td>{conversions:,}</td>
                            <td>{conversion_rate}%</td>
                            <td>${spend:.2f}</td>
                            <td>${cpc:.2f}</td>
                            <td>${cost_per_conversion:.2f}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
    """
    
    # Analysis section
    if analysis:
        for section, content in analysis.items():
            if section in ["campaign_id", "campaign_name", "analysis_time"]:
                continue
                
            section_title = section.replace("_", " ").title()
            
            html += f"""
            <div class="section">
                <h2>{section_title}</h2>
            """
            
            if isinstance(content, str):
                html += f"<p>{content}</p>"
            elif isinstance(content, list):
                html += "<ul>"
                for item in content:
                    if isinstance(item, str):
                        html += f"<li>{item}</li>"
                    elif isinstance(item, dict) and "text" in item:
                        html += f"<li>{item['text']}</li>"
                    elif isinstance(item, dict):
                        # Generic dict formatting
                        html += f"<li>{str(item)}</li>"
                html += "</ul>"
            elif isinstance(content, dict):
                # Format dictionary content
                html += "<ul>"
                for key, value in content.items():
                    formatted_key = key.replace("_", " ").title()
                    if isinstance(value, str):
                        html += f"<li><strong>{formatted_key}:</strong> {value}</li>"
                    elif isinstance(value, list):
                        html += f"<li><strong>{formatted_key}:</strong><ul>"
                        for item in value:
                            if isinstance(item, str):
                                html += f"<li>{item}</li>"
                            else:
                                html += f"<li>{str(item)}</li>"
                        html += "</ul></li>"
                    else:
                        html += f"<li><strong>{formatted_key}:</strong> {str(value)}</li>"
                html += "</ul>"
            
            html += "</div>"
    
    # Close the HTML
    html += f"""
            <footer>
                Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Ad Campaign Manager
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html 