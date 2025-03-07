from flask import Flask, request, render_template, Response
from feedgen.feed import FeedGenerator
import feedparser
import validators
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Template error: {str(e)}")
        return "Error loading page template", 500

@app.route('/generate', methods=['POST'])
def generate_feed():
    try:
        url = request.form.get('url')
        
        if not url or not validators.url(url):
            return "Invalid URL provided", 400
        
        feed = feedparser.parse(url)
        
        if feed.bozo:
            return f"Invalid RSS feed: {feed.bozo_exception}", 400
        
        fg = FeedGenerator()
        fg.title(feed.feed.get('title', 'Untitled Feed'))
        fg.link(href=url)
        fg.description(feed.feed.get('description', 'No description available'))

        for entry in feed.entries[:10]:
            fe = fg.add_entry()
            fe.title(entry.get('title', 'No title'))
            fe.link(href=entry.get('link', '#'))
            fe.description(entry.get('description', 'No content available'))

        return Response(fg.rss_str(), mimetype='application/rss+xml')
    
    except Exception as e:
        app.logger.error(f"Error generating feed: {str(e)}\n{traceback.format_exc()}")
        return f"Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=False)
