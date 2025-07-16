# Production Robots.txt Update Guide

## Issue Identified
The production website www.ieltsaiprep.com/robots.txt is still showing the old version with only 4 bot permissions, while the development environment has the enhanced version with 20+ AI bots.

## Production Lambda Function
- **Function Name**: `ielts-genai-prep-api`
- **Region**: us-east-1
- **Current Status**: Shows old robots.txt content

## Enhanced Robots.txt Content (Deploy This)

Replace the current robots.txt handler in the production Lambda function with this enhanced version:

```
User-agent: *
Allow: /

# AI Search Engine Bots - Enhanced SEO Optimization
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bingbot
Allow: /

User-agent: BingPreview
Allow: /

User-agent: SlackBot
Allow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

User-agent: WhatsApp
Allow: /

User-agent: Applebot
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: YandexBot
Allow: /

User-agent: BaiduSpider
Allow: /

User-agent: NaverBot
Allow: /

# AI Model Training Bots
User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: YouBot
Allow: /

User-agent: Anthropic-AI
Allow: /

User-agent: OpenAI-SearchBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

User-agent: Gemini-Pro
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml
```

## AWS Lambda Update Steps

1. **Open AWS Lambda Console**
2. **Navigate to function**: `ielts-genai-prep-api`
3. **Find the handle_robots_txt function** in the code
4. **Update the robots_content variable** with the enhanced version above
5. **Deploy the changes**
6. **Test**: Visit www.ieltsaiprep.com/robots.txt to verify

## Expected Results After Deployment

- **Before**: 4 bot permissions (*, GPTBot, ClaudeBot, Google-Extended)
- **After**: 20+ bot permissions including social media and international search engines
- **SEO Impact**: Much better discoverability across AI-powered search systems
- **Cache**: 24-hour cache headers for optimal performance

## Verification

After deployment, www.ieltsaiprep.com/robots.txt should show the enhanced content with all the additional bot permissions, matching the development environment.

## Why This Matters

- **AI Search Engines**: Better visibility in ChatGPT, Claude, and other AI search systems
- **Social Media**: Proper crawling for link previews on Twitter, LinkedIn, Facebook
- **International Markets**: Support for Yandex, Baidu, Naver for global reach
- **SEO Performance**: Comprehensive bot permissions improve overall search ranking