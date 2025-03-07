from flask import Flask, request, render_template, Response
from feedgen.feed import FeedGenerator
import feedparser
import validators

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_feed():
    try:
        url = request.form.get('url')
        
        if not validators.url(url):
            return "Invalid URL format", 400

        # Parse feed with 10s timeout
        feed = feedparser.parse(url, timeout=10)
        
        # Check if feed is actually parsed
        if feed.bozo:
            return f"Invalid RSS feed: {feed.bozo_exception}", 400
            
        if not hasattr(feed, 'feed') or not feed.feed:
            return "No valid feed found at this URL", 400

        fg = FeedGenerator()
        
        # Safe attribute access with fallbacks
        fg.title(feed.feed.get('title', 'Untitled Feed'))
        fg.link(href=url)
        fg.description(feed.feed.get('description', 'No description available'))

        # Handle entries safely
        entries = feed.entries[:10] if hasattr(feed, 'entries') else []
        
        for entry in entries:
            fe = fg.add_entry()
            fe.title(entry.get('title', 'Untitled Entry'))
            fe.link(href=entry.get('link', '#'))
            fe.description(entry.get('description', 'No content available'))

        return Response(fg.rss_str(), mimetype='application/rss+xml')

    except Exception as e:
        app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
        return "Failed to generate feed. Please check if the URL contains a valid RSS feed.", 500
