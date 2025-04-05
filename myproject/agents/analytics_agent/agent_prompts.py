#!/usr/bin/env python3
"""
Analytics Agent Prompts - Contains system prompts and templates
for the analytics agent to generate reports and insights.
"""

# System prompt for the Analytics Agent
SYSTEM_PROMPT = """
You are an expert social media analytics agent specializing in generating data-driven insights
and comprehensive reports from platform metrics. Your goal is to help users understand their
social media performance and provide actionable recommendations to improve engagement,
reach, and conversion.

You have access to data from multiple platforms including Instagram, Twitter/X, and LinkedIn.
You can analyze trends, identify patterns, and create visualizations to help communicate insights
effectively.

Your capabilities include:
- Analyzing engagement metrics across platforms
- Identifying content performance trends
- Generating audience demographics insights
- Creating cross-platform performance comparisons
- Producing customized reports (executive summaries, comprehensive reports, metrics snapshots)
- Visualizing data through charts and graphs
- Providing actionable, data-driven recommendations

You communicate in a clear, professional manner, focusing on insights rather than just data.
Always tie metrics to business outcomes and provide context for what the numbers mean.
"""

# Metrics analysis prompt template
METRICS_ANALYSIS_PROMPT = """
Analyze the following social media metrics data and provide insights:

Platform: {platform}
Date Range: {start_date} to {end_date}

METRICS:
{metrics_json}

Focus your analysis on:
1. Overall performance trends
2. Engagement rate patterns
3. Content type effectiveness
4. Audience growth indicators
5. Peak performance days/times
6. Areas for improvement

Provide 3-5 specific, actionable recommendations based on the data.
"""

# Report generation prompt template
REPORT_GENERATION_PROMPT = """
Generate a {report_type} for social media performance from {start_date} to {end_date}.

PLATFORMS DATA:
{platforms_data_json}

The report should include:
{sections}

For each section, provide data-driven insights and clear interpretations of what the metrics mean
for the business. Include comparisons to industry benchmarks where relevant, and highlight both
strengths and opportunities for improvement.

End with specific, actionable recommendations that are directly tied to the data findings.
Format your response as a structured JSON report.
"""

# Audience analysis prompt template
AUDIENCE_ANALYSIS_PROMPT = """
Analyze the following audience data for {platform} and provide insights:

AUDIENCE DATA:
{audience_data_json}

Focus your analysis on:
1. Demographic patterns and opportunities
2. Engagement by audience segment
3. Growth trends in specific demographics
4. Content preferences by audience type
5. Best times to reach key audience segments

Provide specific recommendations for:
- Content targeting opportunities
- Potential new audience segments to target
- Engagement strategies for key demographics
- Optimal posting schedules based on audience activity
"""

# Trend identification prompt template
TREND_IDENTIFICATION_PROMPT = """
Analyze the following platform performance data and identify key trends:

PLATFORM: {platform}
DATE RANGE: {start_date} to {end_date}

PERFORMANCE DATA:
{performance_data_json}

Identify trends in:
1. Content performance (by format, topic, etc.)
2. Engagement patterns (time of day, day of week, etc.)
3. Audience growth and behavior
4. Conversion metrics (if applicable)

For each trend identified, explain:
- What the data shows
- Why this trend matters
- How to leverage or address this trend
- What metrics to monitor going forward
"""

# Cross-platform comparison prompt template
CROSS_PLATFORM_COMPARISON_PROMPT = """
Compare performance across the following platforms from {start_date} to {end_date}:

PLATFORMS DATA:
{platforms_data_json}

Create a comprehensive cross-platform analysis that includes:
1. Overall performance comparison (engagement, reach, growth)
2. Platform-specific strengths and weaknesses
3. Content effectiveness across platforms
4. Audience differences between platforms
5. Resource allocation recommendations

For each platform, identify:
- What's working well
- What needs improvement
- Unique opportunities for that platform

Conclude with recommendations for cross-platform strategy optimization.
"""

# Visualization description prompt template
VISUALIZATION_PROMPT = """
Based on the following data, describe what visualizations would be most effective
for communicating the key insights:

DATA:
{data_json}

For each recommended visualization:
1. Specify the visualization type (line chart, bar chart, pie chart, etc.)
2. Explain what metrics should be displayed
3. Describe what insights this visualization would highlight
4. Suggest a title and basic layout

Focus on visualizations that would be most valuable for {visualization_purpose}
and appropriate for inclusion in a {report_type}.
""" 