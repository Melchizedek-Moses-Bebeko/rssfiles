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
    url = request.form.get('url')
    
    if not validators.url(url):
        return "Invalid URL", 400
    
    # Parse existing feed
    feed = feedparser.parse(url)
    
    # Create new feed
    fg = FeedGenerator()
    fg.title(feed.feed.title)
    fg.link(href=url)
    fg.description(feed.feed.description)

    for entry in feed.entries[:10]:
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.description(entry.description)

    return Response(fg.rss_str(), mimetype='application/rss+xml')

if __name__ == '__main__':
    app.run()