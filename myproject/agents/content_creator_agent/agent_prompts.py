"""
Prompts for the Content Creator Agent

Contains system prompts, content creation prompts, and refinement prompts
for generating engaging social media content.
"""

# System prompt for the Content Creator Agent
SYSTEM_PROMPT = """
You are a professional Content Creator Agent specializing in creating engaging,
platform-optimized social media content. Your expertise spans across Instagram, 
Twitter/X, LinkedIn, and other social platforms.

Your capabilities include:
- Creating engaging captions, headlines, and calls-to-action
- Generating optimized hashtags for each platform
- Crafting detailed image prompts for AI image generation
- Adapting content to match brand voice and guidelines
- Creating content based on trending topics or creative briefs

You adapt to each platform's unique characteristics:
- Instagram: Visually focused, story-driven content with ample hashtags
- Twitter/X: Concise, attention-grabbing content with limited characters
- LinkedIn: Professional, value-driven content with business focus

You always adhere to the brand's voice, tone, and guidelines while creating content
that is likely to engage the target audience and drive meaningful interactions.
"""

# Content creation prompt template
CONTENT_CREATION_PROMPT = """
Create engaging social media content for {platform} based on the following:

Topic: {topic}
Category: {category}
Target audience: {target_audience}

Brand voice: {brand_voice}
Brand tone: {brand_tone}

The content should include:
1. An attention-grabbing headline (max 80 characters)
2. A compelling main text/caption that provides value to the audience
3. A clear call-to-action that encourages engagement
4. Relevant hashtags (max {hashtag_count} for this platform)

Avoid these topics: {taboo_topics}

Please format your response as JSON with the following structure:
{
    "headline": "The headline text",
    "caption": "The main caption text",
    "cta": "The call-to-action",
    "hashtags": ["hashtag1", "hashtag2", ...]
}
"""

# Content refinement prompt template
CONTENT_REFINEMENT_PROMPT = """
Refine the following {platform} content to make it more engaging and aligned with our brand:

Current content:
{current_content}

Brand voice: {brand_voice}
Brand tone: {brand_tone}
Target audience: {target_audience}

Areas to improve:
1. Make the headline more attention-grabbing
2. Ensure the caption provides clear value to the audience
3. Make the call-to-action more compelling
4. Optimize the hashtags for better discovery

Please maintain the core message while making these improvements.
Format your response as JSON using the same structure as the current content.
"""

# Image prompt generation template
IMAGE_PROMPT_TEMPLATE = """
Create a detailed, specific prompt for an AI image generator that would produce a
professional, engaging image for {platform} based on the following:

Topic: {topic}
Category: {category}
Content type: {content_type}

The image should:
1. Be visually striking and attention-grabbing
2. Clearly relate to the topic and category
3. Match the aesthetic expectations of {platform}
4. Have a {aspect_ratio} format

Include specific details about style, colors, composition, and focal elements.
Make the prompt detailed enough for an AI image generator to create a compelling image.
"""

# Platform-specific prompt adjustments
PLATFORM_ADJUSTMENTS = {
    "instagram": {
        "emphasis": "visual storytelling",
        "tone": "aspirational and lifestyle-focused",
        "format": "square or vertical format",
        "hashtag_count": 8
    },
    "twitter": {
        "emphasis": "brevity and engagement",
        "tone": "conversational and timely",
        "format": "horizontal format with clear focal point",
        "hashtag_count": 3
    },
    "linkedin": {
        "emphasis": "professional value and insights",
        "tone": "authoritative and solution-oriented",
        "format": "clean, professional aesthetic",
        "hashtag_count": 5
    }
}

# Content types with specifications
CONTENT_TYPES = {
    "post": {
        "description": "Standard feed post",
        "caption_length": "medium (100-150 words)",
        "image_aspect": "square 1:1"
    },
    "story": {
        "description": "24-hour temporary content",
        "caption_length": "short (30-50 words)",
        "image_aspect": "vertical 9:16"
    },
    "carousel": {
        "description": "Multi-slide swipeable post",
        "caption_length": "long (150-250 words)",
        "image_aspect": "square 1:1 for all slides"
    },
    "video": {
        "description": "Video content",
        "caption_length": "medium (100-150 words)",
        "thumbnail_aspect": "depends on platform"
    }
} 