"""Prompt templates for autonomous content and moderation workflows."""

CONTENT_STRATEGIST_PROMPT = """
You are a Telegram growth editor. Select ONE topic for a compliant community post.
Audience profile: {audience_profile}
Recent winning themes: {winning_themes}
Candidate trend facts: {trend_facts}
Rules: no misinformation, no harassment, no spam, no fake urgency, cite source when useful.
Return JSON with: title, angle, format, why_now, risk_notes, hashtags.
"""

POST_WRITER_PROMPT = """
Write a Telegram post in Russian.
Topic: {title}
Angle: {angle}
Format: {format}
Style memory: {style_memory}
Requirements: Markdown, emoji when natural, clear CTA, 1-3 hashtags, concise hook.
If facts are uncertain, say so. Do not invent statistics.
Return JSON with title, body_markdown, image_prompt, poll_options.
"""

MODERATION_PROMPT = """
Classify this Telegram message for moderation.
Message: {message}
Return JSON: action in [allow, warn, delete, ban], categories, confidence, explanation.
Policy: remove spam, scams, NSFW, hate, threats, doxxing, flooding. Allow criticism.
"""

IMAGE_PROMPT_TEMPLATE = """
Create a Telegram post cover, 16:9, high contrast, no copyrighted logos, no text unless requested.
Subject: {subject}. Mood: {mood}. Style: modern editorial digital art.
"""
