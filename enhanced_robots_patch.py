
# Enhanced Robots.txt Handler - Production Deployment
# Deploy this to replace the existing handle_robots_txt function

def handle_robots_txt() -> Dict[str, Any]:
    """Handle robots.txt endpoint with enhanced AI SEO optimization"""
    robots_content = """User-agent: *
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

Sitemap: https://www.ieltsaiprep.com/sitemap.xml"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain',
            'Cache-Control': 'public, max-age=86400'
        },
        'body': robots_content
    }

# Deployment timestamp: 2025-07-16T15:26:53.383615
