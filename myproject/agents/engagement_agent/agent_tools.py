#!/usr/bin/env python3
"""
Engagement Agent Tools - Functions for analyzing engagement metrics,
generating responses to comments, and scheduling engagement actions.
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

async def analyze_post_performance(platform: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the performance of a post based on engagement metrics
    
    Args:
        platform: Social media platform
        post_data: Post data including metrics
        
    Returns:
        Analysis of post performance
    """
    metrics = post_data.get("metrics", {})
    content = post_data.get("content", "")
    post_type = post_data.get("type", "post")
    created_at = post_data.get("created_at", "")
    
    # Calculate key performance indicators
    engagement_rate = calculate_engagement_rate(platform, metrics)
    performance_score = calculate_performance_score(platform, metrics)
    
    # Benchmark against platform averages
    benchmark = benchmark_against_average(platform, metrics, post_type)
    
    # Identify strengths and weaknesses
    strengths_weaknesses = await identify_strengths_weaknesses(
        platform=platform,
        content=content,
        metrics=metrics,
        post_type=post_type
    )
    
    return {
        "engagement_rate": engagement_rate,
        "performance_score": performance_score,
        "benchmark": benchmark,
        "strengths": strengths_weaknesses.get("strengths", []),
        "weaknesses": strengths_weaknesses.get("weaknesses", []),
        "recommendations": strengths_weaknesses.get("recommendations", [])
    }

def calculate_engagement_rate(platform: str, metrics: Dict[str, int]) -> float:
    """Calculate engagement rate based on platform-specific formulas"""
    if not metrics:
        return 0.0
    
    impressions = metrics.get("impressions", 0)
    reach = metrics.get("reach", 0)
    followers = metrics.get("followers", 1)  # Avoid division by zero
    
    likes = metrics.get("likes", 0)
    comments = metrics.get("comments", 0)
    shares = metrics.get("shares", 0)
    saves = metrics.get("saves", 0)
    
    # Platform-specific engagement rate calculations
    if platform == "instagram":
        denominator = reach if reach > 0 else followers
        engagement = (likes + comments * 2 + saves * 3 + shares * 4) / denominator * 100
    elif platform == "twitter":
        denominator = impressions if impressions > 0 else followers
        engagement = (likes + comments * 3 + shares * 5) / denominator * 100
    elif platform == "linkedin":
        denominator = impressions if impressions > 0 else followers
        engagement = (likes + comments * 2 + shares * 4) / denominator * 100
    else:
        # Generic calculation
        denominator = impressions if impressions > 0 else followers
        engagement = (likes + comments + shares) / denominator * 100
    
    return round(engagement, 2)

def calculate_performance_score(platform: str, metrics: Dict[str, int]) -> int:
    """Calculate a performance score (0-100) based on metrics"""
    if not metrics:
        return 0
    
    # Base weights for different engagement types
    weights = {
        "likes": 1,
        "comments": 2,
        "shares": 3,
        "saves": 3,
        "clicks": 2,
        "profile_visits": 2,
        "follows": 4
    }
    
    # Platform-specific weight adjustments
    if platform == "instagram":
        weights["saves"] = 4
    elif platform == "twitter":
        weights["retweets"] = weights.pop("shares")
        weights["quotes"] = 4
    elif platform == "linkedin":
        weights["clicks"] = 3
    
    # Calculate raw score
    raw_score = sum(metrics.get(metric, 0) * weight for metric, weight in weights.items())
    
    # Normalize to 0-100 scale based on followers or impressions
    followers = metrics.get("followers", 100)
    impressions = metrics.get("impressions", followers * 0.3)
    
    # Normalization factor - adjust the divisor based on typical engagement rates
    normalization_factor = max(followers * 0.05, impressions * 0.1)
    
    # Prevent division by zero and cap at 100
    if normalization_factor <= 0:
        return 0
    
    score = min(100, int((raw_score / normalization_factor) * 100))
    return score

def benchmark_against_average(platform: str, metrics: Dict[str, int], post_type: str) -> Dict[str, Any]:
    """Compare post metrics against platform averages"""
    # These would ideally come from a database of benchmarks
    # Using placeholder values for demonstration
    platform_benchmarks = {
        "instagram": {
            "post": {
                "engagement_rate": 3.0,
                "likes_per_follower": 0.08,
                "comments_per_follower": 0.01
            },
            "story": {
                "engagement_rate": 5.0,
                "views_per_follower": 0.3
            },
            "carousel": {
                "engagement_rate": 5.5,
                "likes_per_follower": 0.12,
                "comments_per_follower": 0.02
            }
        },
        "twitter": {
            "post": {
                "engagement_rate": 1.5,
                "likes_per_impression": 0.015,
                "retweets_per_impression": 0.005
            }
        },
        "linkedin": {
            "post": {
                "engagement_rate": 2.0,
                "likes_per_impression": 0.02,
                "comments_per_impression": 0.005
            },
            "article": {
                "engagement_rate": 1.8,
                "clicks_per_impression": 0.1
            }
        }
    }
    
    # Get benchmarks for this platform and post type
    if platform in platform_benchmarks and post_type in platform_benchmarks[platform]:
        benchmarks = platform_benchmarks[platform][post_type]
    else:
        # Default benchmarks if specific ones aren't available
        benchmarks = {
            "engagement_rate": 2.0,
            "likes_per_follower": 0.05,
            "comments_per_follower": 0.005
        }
    
    # Calculate actual metrics for comparison
    followers = metrics.get("followers", 1)  # Avoid division by zero
    impressions = metrics.get("impressions", followers * 0.3)
    
    actual = {
        "engagement_rate": calculate_engagement_rate(platform, metrics),
        "likes_per_follower": metrics.get("likes", 0) / followers,
        "comments_per_follower": metrics.get("comments", 0) / followers
    }
    
    # Add platform-specific metrics
    if platform == "instagram":
        actual["saves_per_follower"] = metrics.get("saves", 0) / followers
    elif platform == "twitter":
        actual["retweets_per_impression"] = metrics.get("retweets", 0) / impressions
    elif platform == "linkedin":
        actual["clicks_per_impression"] = metrics.get("clicks", 0) / impressions
    
    # Compare actual vs benchmark
    comparison = {}
    for key in benchmarks:
        if key in actual:
            benchmark_value = benchmarks[key]
            actual_value = actual[key]
            
            # Calculate percentage difference
            if benchmark_value > 0:
                percent_diff = (actual_value - benchmark_value) / benchmark_value * 100
            else:
                percent_diff = 0
            
            comparison[key] = {
                "benchmark": benchmark_value,
                "actual": actual_value,
                "percent_difference": round(percent_diff, 1),
                "performance": "above_average" if percent_diff > 10 else 
                              ("average" if percent_diff >= -10 else "below_average")
            }
    
    return comparison

async def identify_strengths_weaknesses(
    platform: str,
    content: str,
    metrics: Dict[str, int],
    post_type: str
) -> Dict[str, List[str]]:
    """
    Identify strengths and weaknesses of a post using LLM analysis
    
    Args:
        platform: Social media platform
        content: Post content
        metrics: Engagement metrics
        post_type: Type of post (post, story, carousel, etc.)
        
    Returns:
        Dict with strengths, weaknesses, and recommendations
    """
    # Prepare context for the LLM
    metrics_str = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
    
    prompt = f"""
    Analyze the following {platform} {post_type} and its performance metrics.
    
    CONTENT:
    {content}
    
    METRICS:
    {metrics_str}
    
    Based on the content and metrics, identify:
    1. Strengths: What worked well about this post?
    2. Weaknesses: What could be improved?
    3. Recommendations: Specific actions to improve engagement on similar future posts.
    
    Provide your analysis in JSON format with keys "strengths", "weaknesses", and "recommendations",
    each containing an array of string points.
    """
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert social media analyst specializing in engagement optimization."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return {
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("weaknesses", []),
            "recommendations": analysis.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}")
        return {
            "strengths": ["Good visual content"],
            "weaknesses": ["Could use more engaging caption"],
            "recommendations": ["Ask a question to encourage comments"]
        }

async def generate_comment_responses(
    platform: str,
    post_content: str,
    comments: List[Dict[str, Any]],
    brand_guidelines: Dict[str, Any],
    response_templates: Dict[str, List[str]],
    response_type: str = "auto"
) -> List[Dict[str, Any]]:
    """
    Generate responses to comments using templates or LLM
    
    Args:
        platform: Social media platform
        post_content: Content of the post
        comments: List of comments to respond to
        brand_guidelines: Brand voice and guidelines
        response_templates: Templates for different response types
        response_type: Type of response generation (auto, template, custom)
        
    Returns:
        List of generated responses
    """
    responses = []
    
    if not comments:
        return responses
    
    if response_type == "template":
        # Use only predefined templates
        for comment in comments:
            comment_text = comment.get("text", "")
            
            # Determine the type of comment (simple classification)
            if any(word in comment_text.lower() for word in ["thank", "thanks", "appreciate", "love", "great"]):
                template_key = "appreciation"
            elif any(word in comment_text.lower() for word in ["?", "how", "what", "when", "where", "why", "who"]):
                template_key = "question"
            elif any(word in comment_text.lower() for word in ["bad", "terrible", "hate", "awful", "disappointed"]):
                template_key = "complaint"
            else:
                template_key = "general"
            
            # Get a template response
            templates = response_templates.get(template_key, response_templates.get("general"))
            response_text = random.choice(templates)
            
            # If it's a question template with a placeholder, provide a generic answer
            if "{answer}" in response_text:
                response_text = response_text.replace("{answer}", "Our team is looking into this and will get back to you soon.")
            
            responses.append({
                "text": response_text,
                "type": template_key
            })
    
    elif response_type == "custom" or response_type == "auto":
        # Use LLM to generate custom responses
        # For auto, we'll use LLM but will fallback to templates if needed
        
        # Build prompt with context
        voice = brand_guidelines.get("voice", "professional yet approachable")
        tone = brand_guidelines.get("tone", "informative and helpful")
        taboo_topics = ", ".join(brand_guidelines.get("taboo_topics", []))
        
        prompt = f"""
        As a social media manager for a brand with a {voice} voice and {tone} tone,
        generate appropriate responses to these comments on a {platform} post.
        
        THE POST:
        {post_content}
        
        BRAND GUIDELINES:
        - Voice: {voice}
        - Tone: {tone}
        - Avoid discussing: {taboo_topics}
        - Keep responses concise and engaging
        - Add emojis where appropriate
        - For questions you can't confidently answer, offer to connect via DM
        
        COMMENTS TO RESPOND TO:
        {json.dumps([{
            "id": comment.get("id", ""),
            "username": comment.get("username", "user"),
            "text": comment.get("text", ""),
            "timestamp": comment.get("timestamp", "")
        } for comment in comments])}
        
        Generate one response per comment in JSON format with an array of objects containing:
        1. "comment_id": The ID of the comment
        2. "text": Your response text
        3. "type": The type of response (appreciation, question, complaint, general)
        """
        
        try:
            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an expert social media manager who crafts engaging, on-brand responses."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if "responses" in result:
                for item in result["responses"]:
                    responses.append({
                        "text": item.get("text", "Thanks for your comment!"),
                        "type": item.get("type", "general")
                    })
            else:
                # If the response doesn't match expected format, use the whole response
                # and generate template-based responses as fallback
                logger.warning("LLM response format incorrect, using templates as fallback")
                return await generate_comment_responses(
                    platform, post_content, comments, 
                    brand_guidelines, response_templates, "template"
                )
                
        except Exception as e:
            logger.error(f"Error generating responses with LLM: {str(e)}")
            # Fallback to templates
            return await generate_comment_responses(
                platform, post_content, comments, 
                brand_guidelines, response_templates, "template"
            )
    
    return responses

async def identify_top_performing_content(
    platform: str,
    posts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Identify top and underperforming content from recent posts
    
    Args:
        platform: Social media platform
        posts: List of recent posts with metrics
        
    Returns:
        Analysis of top and underperforming content
    """
    if not posts:
        return {
            "top_performing": [],
            "underperforming": []
        }
    
    # Calculate performance scores for all posts
    for post in posts:
        post["performance_score"] = calculate_performance_score(
            platform, post.get("metrics", {})
        )
        post["engagement_rate"] = calculate_engagement_rate(
            platform, post.get("metrics", {})
        )
    
    # Sort by performance score
    sorted_posts = sorted(posts, key=lambda x: x.get("performance_score", 0), reverse=True)
    
    # Get top 30% and bottom 30%
    top_count = max(1, len(sorted_posts) // 3)
    
    top_performing = sorted_posts[:top_count]
    underperforming = sorted_posts[-top_count:] if len(sorted_posts) > top_count else []
    
    # Extract key insights from top performing
    top_insights = await extract_content_insights(platform, top_performing) if top_performing else {}
    
    # Extract key issues from underperforming
    bottom_insights = await extract_content_insights(platform, underperforming, is_top=False) if underperforming else {}
    
    return {
        "top_performing": [{
            "post_id": post.get("id"),
            "type": post.get("type", "post"),
            "performance_score": post.get("performance_score", 0),
            "engagement_rate": post.get("engagement_rate", 0),
            "metrics": post.get("metrics", {}),
            "content_preview": post.get("content", "")[:100] + "..." if len(post.get("content", "")) > 100 else post.get("content", "")
        } for post in top_performing],
        "underperforming": [{
            "post_id": post.get("id"),
            "type": post.get("type", "post"),
            "performance_score": post.get("performance_score", 0),
            "engagement_rate": post.get("engagement_rate", 0),
            "metrics": post.get("metrics", {}),
            "content_preview": post.get("content", "")[:100] + "..." if len(post.get("content", "")) > 100 else post.get("content", "")
        } for post in underperforming],
        "insights": {
            "top_content_patterns": top_insights.get("patterns", []),
            "successful_elements": top_insights.get("elements", []),
            "underperforming_issues": bottom_insights.get("issues", []),
            "improvement_areas": bottom_insights.get("improvements", [])
        }
    }

async def extract_content_insights(
    platform: str,
    posts: List[Dict[str, Any]],
    is_top: bool = True
) -> Dict[str, List[str]]:
    """
    Extract insights from a set of posts using LLM
    
    Args:
        platform: Social media platform
        posts: List of posts to analyze
        is_top: Whether these are top performing posts (True) or underperforming posts (False)
        
    Returns:
        Insights about the content patterns
    """
    if not posts:
        return {}
    
    # Prepare post data for analysis
    posts_data = []
    for post in posts:
        posts_data.append({
            "content": post.get("content", ""),
            "type": post.get("type", "post"),
            "performance_score": post.get("performance_score", 0),
            "engagement_rate": post.get("engagement_rate", 0),
            "key_metrics": {
                k: v for k, v in post.get("metrics", {}).items() 
                if k in ["likes", "comments", "shares", "saves", "impressions", "reach"]
            }
        })
    
    analysis_type = "top-performing" if is_top else "underperforming"
    
    prompt = f"""
    Analyze the following {analysis_type} {platform} posts and identify common patterns.
    
    POSTS:
    {json.dumps(posts_data)}
    
    {"Identify patterns in these top-performing posts: What do they have in common? What elements make them successful?" if is_top else
     "Identify issues with these underperforming posts: What might be causing low engagement? What areas need improvement?"}
    
    Provide your analysis in JSON format with the following keys:
    {'"patterns": Array of common content patterns, "elements": Array of successful elements' if is_top else
     '"issues": Array of potential issues, "improvements": Array of suggested improvements'}
    """
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert social media analyst specializing in content optimization."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Error in content insight extraction: {str(e)}")
        
        if is_top:
            return {
                "patterns": ["Use of hashtags", "Question in caption", "High-quality visuals"],
                "elements": ["Emotional appeal", "Call to action", "Relevant to audience interests"]
            }
        else:
            return {
                "issues": ["Long captions", "No clear call to action", "Poor image quality"],
                "improvements": ["Add questions to encourage comments", "Use more relevant hashtags", "Improve visual quality"]
            }

async def recommend_engagement_actions(
    platform: str,
    performance_analysis: Dict[str, Any],
    brand_guidelines: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Recommend specific engagement actions based on performance analysis
    
    Args:
        platform: Social media platform
        performance_analysis: Results from the performance analysis
        brand_guidelines: Brand voice and guidelines
        
    Returns:
        List of recommended engagement actions
    """
    recommendations = []
    
    # Identify posts needing immediate response to comments
    underperforming = performance_analysis.get("underperforming", [])
    top_performing = performance_analysis.get("top_performing", [])
    
    # Recent underperforming posts with comments need attention
    for post in underperforming:
        comments_count = post.get("metrics", {}).get("comments", 0)
        if comments_count > 0:
            recommendations.append({
                "action": "respond_to_comments",
                "priority": "high",
                "post_id": post.get("post_id"),
                "platform": platform,
                "reason": f"Underperforming post with {comments_count} comments requires attention",
                "suggested_approach": "Use personalized responses to each comment to boost engagement"
            })
    
    # Top performing posts with active conversations
    for post in top_performing:
        comments_count = post.get("metrics", {}).get("comments", 0)
        if comments_count > 3:
            recommendations.append({
                "action": "respond_to_comments",
                "priority": "medium",
                "post_id": post.get("post_id"),
                "platform": platform,
                "reason": f"High-performing post with active conversation ({comments_count} comments)",
                "suggested_approach": "Engage in conversation to further boost visibility"
            })
    
    # Recommend engagement with followers' content
    recommendations.append({
        "action": "engage_with_followers",
        "priority": "medium",
        "platform": platform,
        "reason": "Regular engagement with followers' content increases overall account visibility",
        "suggested_approach": "Like and comment on recent posts from top followers"
    })
    
    # Recommend hashtag engagement
    if platform in ["instagram", "twitter"]:
        recommendations.append({
            "action": "engage_with_hashtags",
            "priority": "low",
            "platform": platform,
            "hashtags": get_relevant_hashtags(platform, performance_analysis),
            "reason": "Engaging with content from relevant hashtags increases visibility",
            "suggested_approach": "Like and leave meaningful comments on top posts from these hashtags"
        })
    
    # Add customized recommendations based on platform
    if platform == "instagram":
        recommendations.append({
            "action": "respond_to_stories",
            "priority": "high",
            "platform": platform,
            "reason": "Story interactions build stronger connections with followers",
            "suggested_approach": "Respond to all story mentions and reactions"
        })
    elif platform == "twitter":
        recommendations.append({
            "action": "join_conversations",
            "priority": "medium",
            "platform": platform,
            "reason": "Joining trending conversations increases visibility",
            "suggested_approach": "Find relevant trending topics and contribute meaningfully"
        })
    elif platform == "linkedin":
        recommendations.append({
            "action": "engage_with_industry",
            "priority": "medium",
            "platform": platform,
            "reason": "Engaging with industry leaders builds authority",
            "suggested_approach": "Comment on posts from industry thought leaders"
        })
    
    return recommendations

def get_relevant_hashtags(platform: str, performance_analysis: Dict[str, Any]) -> List[str]:
    """Get relevant hashtags based on performance analysis"""
    # This would ideally analyze content to extract relevant hashtags
    # Using placeholder data for demonstration
    if platform == "instagram":
        return ["picoftheday", "instagood", "photooftheday", "instadaily", "instamood"]
    elif platform == "twitter":
        return ["twittermarketing", "digitalmarketing", "contentcreator", "socialmediatips"]
    else:
        return ["marketing", "socialmedia", "content", "digital"]

async def schedule_engagement_tasks(
    platform_clients: Dict[str, Any],
    engagement_plan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Schedule engagement tasks based on the engagement plan
    
    Args:
        platform_clients: Dictionary of platform clients
        engagement_plan: Plan of engagement actions to schedule
        
    Returns:
        Schedule of engagement tasks
    """
    schedule = {
        "timestamp": datetime.now().isoformat(),
        "scheduled_tasks": []
    }
    
    actions = engagement_plan.get("actions", [])
    
    for action in actions:
        platform = action.get("platform")
        action_type = action.get("action")
        priority = action.get("priority", "medium")
        
        # Schedule time based on priority
        if priority == "high":
            schedule_time = datetime.now() + timedelta(hours=1)
        elif priority == "medium":
            schedule_time = datetime.now() + timedelta(hours=4)
        else:
            schedule_time = datetime.now() + timedelta(hours=24)
        
        # Add task to schedule
        task = {
            "id": f"task_{len(schedule['scheduled_tasks']) + 1}",
            "platform": platform,
            "action": action_type,
            "priority": priority,
            "scheduled_time": schedule_time.isoformat(),
            "status": "scheduled",
            "parameters": {k: v for k, v in action.items() if k not in ["action", "platform", "priority"]}
        }
        
        schedule["scheduled_tasks"].append(task)
        
        logger.info(f"Scheduled {action_type} task for {platform} at {schedule_time.isoformat()}")
    
    # Save schedule
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        with open(f"data/engagement/schedule_{timestamp}.json", "w") as f:
            json.dump(schedule, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving engagement schedule: {str(e)}")
    
    return schedule 