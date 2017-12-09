from flask import Blueprint, render_template, send_from_directory


index = Blueprint('index', __name__, url_prefix='/')


@index.route('/', methods=['GET'])
def home():
    return render_template('parent.html')


@index.route('/static/<path:path>')
def static(path):
    return send_from_directory('static', path)
