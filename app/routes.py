from flask import Blueprint, render_template
from .models import db, Property

main = Blueprint('main', __name__)

@main.route('/')
def home():
    news = [
        {
            "title": "Teaz Social Expands with More Live Events",
            "summary": "Atlanta's favorite social tea lounge is now hosting weekly open mic nights, live DJs, and community mixers.",
            "image": "/story_tea.png"
        },
        {
            "title": "Mike Launches the ATL Local App",
            "summary": "Founder Mike officially launches ATL Local, a new community-driven search engine built for Atlantans by Atlantans.",
            "image": "/story_mike_atl_local.png"
        }
    ]
    weather = {
        "icon": "/static/images/weather-sun.png",
        "temperature": "87°F",
        "condition": "Sunny",
        "location": "Atlanta, GA"
    }
    return render_template('home/index.html', news=news, weather=weather)


@main.route('/about')
def about():
    return render_template('home/about.html')

@main.route('/search-map')
def search_map():
    return render_template('search_map/index.html')

@main.route('/directory')
def directory():
    return render_template('directory/index.html')

@main.route('/news')
def news():
    return render_template('news/index.html')

@main.route('/blog')
def blog():
    return render_template('blog/index.html')

@main.route('/shop')
def shop():
    return render_template('shop/index.html')

@main.route('/book')
def book():
    return render_template('book/index.html')

@main.route('/digital-products')
def digital_products():
    return render_template('digital_products/index.html')

@main.route('/events')
def events():
    return render_template('events/index.html')

@main.route('/real-estate')
def real_estate():
    return render_template('real_estate/index.html')

@main.route('/api/test-properties')
def test_properties():
    properties = Property.query.all()
    for p in properties:
        print(p.title)
    return f"{len(properties)} properties printed in console."


