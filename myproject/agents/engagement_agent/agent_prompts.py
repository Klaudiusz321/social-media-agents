#!/usr/bin/env python3
"""
Engagement Agent Prompts - System and user prompts for the Engagement Agent's LLM calls.
"""

# System prompt for the Engagement Agent
SYSTEM_PROMPT = """
You are an expert Social Media Engagement Agent specialized in analyzing and optimizing engagement metrics.
Your primary goal is to monitor social media performance, respond to user comments, and suggest strategic
engagement actions to build stronger connections with the audience.

Key responsibilities:
1. Analyze post performance metrics (likes, comments, shares, saves, etc.)
2. Generate insightful and on-brand responses to user comments
3. Identify underperforming content and recommend improvement strategies
4. Suggest strategic engagement actions to increase visibility and follower growth

You understand platform-specific metrics and engagement patterns for:
- Instagram: Posts, Stories, Reels, Carousel posts
- Twitter/X: Tweets, Retweets, Quote Tweets, Threads
- LinkedIn: Posts, Articles, Documents, Events

You aim to provide data-driven insights while maintaining a consistent brand voice in all interactions.
"""

# Prompt for analyzing post performance
PERFORMANCE_ANALYSIS_PROMPT = """
Analyze the following {platform} {post_type} and its performance metrics.

CONTENT:
{content}

METRICS:
{metrics}

Based on the content and metrics, identify:
1. Strengths: What worked well about this post?
2. Weaknesses: What could be improved?
3. Recommendations: Specific actions to improve engagement on similar future posts.

Provide your analysis in JSON format with keys "strengths", "weaknesses", and "recommendations",
each containing an array of string points.
"""

# Prompt for generating comment responses
COMMENT_RESPONSE_PROMPT = """
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
{comments_json}

Generate one response per comment in JSON format with an array of objects containing:
1. "comment_id": The ID of the comment
2. "text": Your response text
3. "type": The type of response (appreciation, question, complaint, general)
"""

# Prompt for extracting content insights
CONTENT_INSIGHTS_PROMPT = """
Analyze the following {analysis_type} {platform} posts and identify common patterns.

POSTS:
{posts_json}

{analysis_instruction}

Provide your analysis in JSON format with the following keys:
{expected_keys}
"""

# Prompt for generating engagement strategy
ENGAGEMENT_STRATEGY_PROMPT = """
As an expert social media engagement strategist, develop a comprehensive engagement plan
for the following {platform} account.

ACCOUNT METRICS:
{account_metrics}

RECENT PERFORMANCE SUMMARY:
{performance_summary}

TOP PERFORMING CONTENT:
{top_performing}

UNDERPERFORMING CONTENT:
{underperforming}

BRAND GUIDELINES:
{brand_guidelines}

AUDIENCE DEMOGRAPHICS:
{audience_demographics}

Based on this data, create an engagement strategy that includes:
1. Priority engagement actions (responding to comments, engaging with followers, etc.)
2. Content types to focus on based on past performance
3. Optimal engagement times and frequency
4. Specific tactics to increase meaningful interactions
5. Metrics to track for measuring success

Provide your strategy in JSON format with clear, actionable recommendations.
"""

# Prompt for follower analysis
FOLLOWER_ANALYSIS_PROMPT = """
Analyze the following key followers and identify strategic engagement opportunities.

PLATFORM: {platform}

TOP FOLLOWERS:
{followers_data}

RECENT INTERACTIONS:
{interactions_data}

ENGAGEMENT GOALS:
{engagement_goals}

Based on this information, identify:
1. Which followers should receive priority engagement
2. What type of engagement would be most effective for each follower
3. How to time engagement for maximum impact
4. Expected benefits from targeted follower engagement

Provide actionable recommendations in JSON format.
"""

# Comment classification prompt
COMMENT_CLASSIFICATION_PROMPT = """
Classify the following comments on a {platform} post to determine appropriate response types.

THE POST:
{post_content}

COMMENTS:
{comments_json}

For each comment, classify it into one of these categories:
- appreciation: Positive feedback, thanks, praise
- question: Seeking information or clarification
- complaint: Expressing dissatisfaction or criticism
- suggestion: Offering ideas or recommendations
- general: General remarks or neutral statements

Provide classification results in JSON format with each object containing:
1. "comment_id": The ID of the comment
2. "text": The comment text
3. "classification": The comment category
4. "sentiment": Positive, neutral, or negative
5. "priority": High, medium, or low (based on urgency and potential impact)
"""

# Hashtag recommendation prompt
HASHTAG_RECOMMENDATION_PROMPT = """
Based on the following content analytics and trending topics, recommend optimal hashtags for
upcoming {platform} posts.

CONTENT CATEGORY: {content_category}

BRAND IDENTITY:
{brand_identity}

TARGET AUDIENCE:
{target_audience}

RECENT TOP-PERFORMING HASHTAGS:
{top_hashtags}

TRENDING TOPICS IN YOUR NICHE:
{trending_topics}

Recommend three sets of hashtags:
1. A set of 5-7 hashtags for maximum reach
2. A set of 5-7 hashtags for targeted engagement with your core audience
3. A set of 5-7 hashtags blending trending topics with your brand identity

For each set, explain the strategic reasoning behind the selections.
Provide results in JSON format with hashtag sets and explanations.
"""

# Competitive engagement analysis prompt
COMPETITIVE_ANALYSIS_PROMPT = """
Analyze the engagement strategies of these competitor accounts and identify actionable insights.

PLATFORM: {platform}

COMPETITOR ACCOUNTS:
{competitor_data}

YOUR ACCOUNT METRICS:
{your_metrics}

YOUR ENGAGEMENT STRENGTHS:
{your_strengths}

YOUR ENGAGEMENT WEAKNESSES:
{your_weaknesses}

Based on this comparison:
1. Identify engagement tactics competitors are using effectively
2. Spot engagement opportunities they're missing
3. Recommend specific strategies to adopt or adapt
4. Suggest ways to differentiate your engagement approach

Provide your analysis in JSON format with clear, actionable insights.
"""

# Platform-specific engagement optimization prompts
PLATFORM_OPTIMIZATION_PROMPTS = {
    "instagram": """
    Optimize Instagram engagement by analyzing these account metrics and content performance.
    
    ACCOUNT METRICS:
    {account_metrics}
    
    CONTENT PERFORMANCE BY TYPE:
    - Feed Posts: {feed_post_metrics}
    - Stories: {story_metrics}
    - Reels: {reels_metrics}
    - Carousel Posts: {carousel_metrics}
    
    AUDIENCE INSIGHTS:
    {audience_insights}
    
    Recommend:
    1. Optimal posting frequency for each content type
    2. Best times to post based on audience activity
    3. Content themes that drive highest engagement
    4. Story features to utilize more effectively
    5. Reel strategies to increase reach and engagement
    6. Hashtag and caption optimization suggestions
    
    Provide recommendations in JSON format with actionable tactics for each area.
    """,
    
    "twitter": """
    Optimize Twitter engagement by analyzing these account metrics and content performance.
    
    ACCOUNT METRICS:
    {account_metrics}
    
    CONTENT PERFORMANCE BY TYPE:
    - Text Tweets: {text_tweet_metrics}
    - Image Tweets: {image_tweet_metrics}
    - Video Tweets: {video_tweet_metrics}
    - Threads: {thread_metrics}
    
    AUDIENCE INSIGHTS:
    {audience_insights}
    
    Recommend:
    1. Optimal posting frequency and timing
    2. Content themes driving highest engagement
    3. Effective thread structures and length
    4. Strategic use of hashtags and mentions
    5. Reply and quote tweet strategies
    6. Trending topic engagement opportunities
    
    Provide recommendations in JSON format with actionable tactics for each area.
    """,
    
    "linkedin": """
    Optimize LinkedIn engagement by analyzing these account metrics and content performance.
    
    ACCOUNT METRICS:
    {account_metrics}
    
    CONTENT PERFORMANCE BY TYPE:
    - Text Posts: {text_post_metrics}
    - Image Posts: {image_post_metrics}
    - Document Posts: {document_metrics}
    - Video Posts: {video_metrics}
    - Articles: {article_metrics}
    
    AUDIENCE INSIGHTS:
    {audience_insights}
    
    Recommend:
    1. Optimal posting frequency and timing
    2. Content themes resonating with your professional audience
    3. Format preferences (text, images, documents, videos)
    4. Effective use of hashtags and mentions
    5. Comment engagement strategies
    6. Thought leadership positioning tactics
    
    Provide recommendations in JSON format with actionable tactics for each area.
    """
} 