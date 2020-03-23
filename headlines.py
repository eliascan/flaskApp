import feedparser
import json
import datetime
from flask import Flask
from flask import request
from flask import render_template
from flask import make_response
from urllib.request import urlopen
from urllib.parse import quote

app = Flask(__name__)

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=f2d0ed48e1ec31914b11835421e874eb'
CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=58e9130024b34a10beb1df26b51f1cc5'

RSS_FEED = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}

DEFAULTS = {
    'publication': 'bbc',
    'city': 'Montreal',
    'currency_from': 'USD',
    'currency_to': 'CAD'
}


@app.route("/")
def home():
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    city = get_value_with_fallback('city')
    weather = get_weather(city)

    currency_from = get_value_with_fallback("currency_from")

    currency_to = get_value_with_fallback("currency_to")

    rate, currencies = get_rate(currency_from, currency_to)

    response = make_response(render_template("home.html", articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


def get_rate(frm, to):
    all_currency = urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate / frm_rate, parsed.keys()


def get_weather(query):
    query = quote(str(query))
    url = WEATHER_URL.format(query)
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {
            "description": parsed["weather"][0]["description"],
            "temperature": parsed["main"]["temp"],
            "city": parsed["name"],
            "country": parsed['sys']['country']
        }
    return weather


def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    return feed['entries']


if __name__ == '__main__':
    app.run(port=5000, debug=True)
