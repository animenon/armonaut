from flask import Blueprint, render_template


index = Blueprint('index', __name__, url_prefix='/')


@index.route('/', methods=['GET'])
def home():
    return render_template('parent.html')
