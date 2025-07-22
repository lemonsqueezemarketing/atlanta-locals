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
    return 'Atlanta News & Events View'

@main.route('/blog')
def blog():
    return 'Atlanta Local Edu Hub Blog View'

@main.route('/shop')
def shop():
    return 'Atlanta Local Commerce Shop View'

@main.route('/book')
def book():
    return 'Atlanta Services Booking View'

@main.route('/digital-products')
def digital_products():
    return 'Atlanta Digital Products Marketplace View'

