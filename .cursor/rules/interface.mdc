---
description: 
globs: 
alwaysApply: true
---
---
name: WebInterfaceAgent
description: Manages the UI/UX interface in Django for controlling AI agents and visualizing trends
version: "1.0"
globs: ["*.py", "*.html", "*.js"]
triggers: [manual]
---

rule_definition:
  description: |
    This agent builds and maintains the admin interface (in Django) for controlling other agents
    and visualizing trend statistics collected by TrendScannerAgent.
    
    Objectives:
    - Build a Django admin-like dashboard with multiple panels.
    - Enable edit/update/delete of:
      - ContentCreatorAgent scheduled times.
      - SchedulerAgent post frequency and queue.
      - TrendScannerAgent configuration (hashtags to monitor, refresh frequency, etc.)
    - Include visual dashboards for:
      - Recent trending topics per platform.
      - Trend evolution (charts per day).
      - API call stats, post engagement stats.

    Use Django’s class-based views, templates, and Django REST Framework for dynamic updates via AJAX if needed.

    The UI must be clean, modern (TailwindCSS or Bootstrap 5), and mobile-friendly.

    Pages:
    1. Agent Management Panel (/agents/)
        - List of all agents with buttons to edit actions/schedule.
        - Inline form to update content frequency, toggle active/inactive.

    2. Scheduler Configuration Panel (/scheduler/)
        - Table of scheduled posts with options to reschedule/delete/edit.
        - Set post timing by platform.

    3. Trend Dashboard (/trends/)
        - Table of trending hashtags/topics from each platform.
        - Line/bar charts showing frequency of trends over time (e.g., “#moon” usage over 7 days).
        - Filters by platform/date.

    4. Logs & Stats (/logs/)
        - Display of API usage logs (Twitter/IG/LinkedIn).
        - Errors/warnings with time and details.
        - Post engagement logs (likes, shares, impressions).

    Ensure all routes use Django’s authentication. Make the system modular (each panel its own app if needed).

    Include all needed database models, views, forms, templates, and URL routes.

    Output a single Django app or a full template ready to plug into the main project.
