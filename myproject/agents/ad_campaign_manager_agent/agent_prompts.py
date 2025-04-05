#!/usr/bin/env python3
"""
Ad Campaign Manager Agent Prompts - Contains system prompts and templates
for ad campaign creation, optimization, and reporting.
"""

# System prompt for the Ad Campaign Manager Agent
SYSTEM_PROMPT = """
You are an expert ad campaign manager specializing in digital advertising across multiple social media platforms.
Your goal is to help users create, manage, optimize, and analyze advertising campaigns on Facebook, Instagram,
Twitter/X, and LinkedIn.

You have deep expertise in:
- Creating targeted ad campaigns with specific objectives and audience targeting
- Generating platform-optimized ad creatives and copy
- Budget allocation and optimization across platforms
- A/B testing strategy and implementation
- Performance analysis and ROI optimization
- Custom audience creation and lookalike modeling

You understand the unique characteristics of each platform:
- Facebook: Detailed audience targeting, variety of ad formats, strong for B2C
- Instagram: Visual focus, powerful for brand awareness, strong with younger demographics
- Twitter/X: Real-time engagement, conversation-driven, good for news/events
- LinkedIn: Professional targeting, B2B focus, higher CPM but quality leads

You communicate in a clear, strategic manner, focusing on both creative and analytical aspects of ad campaign management.
Always tie recommendations to business objectives and provide data-driven insights when possible.
"""

# Campaign creation prompt template
CAMPAIGN_CREATION_PROMPT = """
Create an ad campaign strategy for {product_name} with the following details:

CAMPAIGN OBJECTIVE: {objective}
TARGET PLATFORMS: {platforms}
TOTAL BUDGET: ${budget}
DURATION: {duration} days
TARGET AUDIENCE: {audience_description}

Product/Service Information:
{product_info}

Generate a comprehensive campaign strategy that includes:
1. Campaign structure and naming conventions
2. Budget allocation across platforms
3. Platform-specific targeting recommendations
4. Ad format recommendations for each platform
5. Key performance indicators (KPIs) to track
6. Campaign schedule and optimization timeline

For each platform, provide specific recommendations that leverage the platform's unique strengths
and align with the campaign objective.
"""

# Campaign optimization prompt template
CAMPAIGN_OPTIMIZATION_PROMPT = """
Analyze the following campaign performance data and provide optimization recommendations:

CAMPAIGN: {campaign_name}
CAMPAIGN OBJECTIVE: {objective}
DURATION SO FAR: {days_running} days
TOTAL BUDGET: ${total_budget}
BUDGET SPENT: ${budget_spent}

PERFORMANCE DATA:
{performance_data_json}

Based on the performance data above, provide recommendations for:
1. Budget reallocation between platforms
2. Audience targeting adjustments
3. Ad creative/copy improvements
4. Bid strategy adjustments
5. Campaign schedule modifications

Prioritize recommendations that will have the highest impact on the primary campaign objective.
For each recommendation, explain the expected benefit and implementation approach.
"""

# Ad creation prompt template
AD_CREATION_PROMPT = """
Create ad content for the following campaign:

CAMPAIGN: {campaign_name}
PLATFORM: {platform}
AD FORMAT: {ad_format}
CAMPAIGN OBJECTIVE: {objective}
TARGET AUDIENCE: {audience_description}

Product/Service Information:
{product_info}

Brand Voice: {brand_voice}

Generate the following:
1. Headline(s) (maximum {headline_length} characters)
2. Primary text/description (maximum {description_length} characters)
3. Call-to-action button text
4. Image/video concept description

Ensure the content is optimized for the specified platform and ad format.
The messaging should align with the campaign objective and resonate with the target audience.
Incorporate the brand voice while maintaining high conversion potential.
"""

# Performance report prompt template
PERFORMANCE_REPORT_PROMPT = """
Generate a {report_type} report for the following campaign:

CAMPAIGN: {campaign_name}
CAMPAIGN OBJECTIVE: {objective}
CAMPAIGN PERIOD: {start_date} to {end_date}
TOTAL BUDGET: ${total_budget}
BUDGET SPENT: ${budget_spent}

PERFORMANCE DATA:
{performance_data_json}

Create a comprehensive report that includes:
1. Executive summary highlighting key performance metrics
2. Detailed analysis by platform
3. Creative performance breakdown
4. Audience insights
5. ROI and ROAS calculations
6. Key learnings and recommendations for future campaigns

Format the report in a professional manner suitable for presentation to stakeholders.
Include data visualizations where appropriate (described in text format).
Focus on insights that are most relevant to the campaign objective.
"""

# Audience creation prompt template
AUDIENCE_CREATION_PROMPT = """
Create a custom audience targeting strategy for the following:

CAMPAIGN: {campaign_name}
CAMPAIGN OBJECTIVE: {objective}
TARGET PLATFORMS: {platforms}
BUSINESS VERTICAL: {business_vertical}
IDEAL CUSTOMER PROFILE: {customer_profile}

Existing Customer Data Available: {has_customer_data}
Previous Campaign Performance Data Available: {has_campaign_data}

Develop a comprehensive audience targeting strategy that includes:
1. Core audience definition with demographic, psychographic, and behavioral attributes
2. Custom audience creation approach for each platform
3. Lookalike/similar audience recommendations
4. Exclusion audience recommendations
5. Audience expansion strategy for scaling

For each platform, provide specific audience targeting parameters that leverage the platform's
unique targeting capabilities. Balance reach with relevance based on the campaign objective.
"""

# Budget allocation prompt template
BUDGET_ALLOCATION_PROMPT = """
Develop a budget allocation strategy for the following campaign:

CAMPAIGN: {campaign_name}
CAMPAIGN OBJECTIVE: {objective}
TARGET PLATFORMS: {platforms}
TOTAL BUDGET: ${total_budget}
DURATION: {duration} days
TARGET AUDIENCE: {audience_description}

BUSINESS PRIORITIES:
{business_priorities}

PLATFORM PERFORMANCE HISTORY (if available):
{platform_performance_json}

Create a data-driven budget allocation strategy that includes:
1. Initial budget split across platforms (percentage and dollar amounts)
2. Daily/weekly spending caps
3. Bid strategy recommendations for each platform
4. Budget pacing approach (even, accelerated, front-loaded, etc.)
5. Budget flexibility and reallocation triggers
6. Performance thresholds for budget adjustments

Justify your allocation based on the campaign objective, audience targeting options,
platform strengths, and historical performance data if available.
"""

# A/B testing prompt template
AB_TESTING_PROMPT = """
Design an A/B testing strategy for the following campaign:

CAMPAIGN: {campaign_name}
PLATFORM(S): {platforms}
CAMPAIGN OBJECTIVE: {objective}
AVAILABLE BUDGET FOR TESTING: ${test_budget}

ELEMENTS TO TEST:
{test_elements}

Create a structured A/B testing approach that includes:
1. Test hypotheses for each element
2. Test structure and variant definitions
3. Sample size and duration calculations
4. Success metrics and statistical significance thresholds
5. Testing schedule and implementation plan
6. Analysis framework for interpreting results

Ensure the testing strategy balances statistical rigor with practical implementation constraints.
Focus on tests that are most likely to drive meaningful performance improvements aligned with
the campaign objective.
""" 