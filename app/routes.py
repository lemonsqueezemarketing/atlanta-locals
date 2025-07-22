from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home/index.html')

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

