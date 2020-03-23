import feedparser
from flask import Flask

app = Flask(__name__)

BBC_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'}


@app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc"):
    feed = feedparser.parse(BBC_FEED[publication])
    first_article = feed['entries'][0]
    return """
            <html>
            <body>
                <h1> BCC Headlines</h1>
                <b>{0}</b>
                <i>{1}</i>
                <p>{2}</p> <br />
            </html>""".format(first_article.get("title"), first_article.get("published"), first_article.get("summary"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)