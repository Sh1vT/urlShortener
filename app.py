# imports
from flask import Flask, request, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import os
import hashlib

# init flask app with db links and then accessing db with db var
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///urls.db'
db=SQLAlchemy(app)


# making the url table
class URL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), nullable=False)

# with app.app_context():
#     db.create_all()
#     print("Database tables created successfully!")

# generating short url from long urls
def generate_short_url(long_url):
    hash_object =  hashlib.md5(long_url.encode())
    return hash_object.hexdigest()[:6]

@app.route('/')
def home():
    return render_template('index.html')

# defining shortening request
@app.route('/shorten', methods=['POST'])
def shortenUrl():
    data = request.get_json()
    long_url = data.get('long_url')

    # if the url is empty(None) return error
    if not long_url:
        return jsonify({'error' : 'Missing long url parameter'}), 400

    # if the url is shortened before, return the shortened url
    existing_url = URL.query.filter_by(long_url=long_url).first()
    if existing_url:
        return jsonify({'short_url': f'http://127.0.0.1:5000/{existing_url.short_url}'})

    # if url never shortened, shorten and return
    short_url=generate_short_url(long_url)
    new_url = URL(long_url=long_url, short_url=short_url)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({"short_url": f"http://127.0.0.1:5000/{short_url}"})

# handle all other requests as a short url, and redirect them to longer ones
@app.route('/<short_url>')
def redirect_to_long(short_url):
    url_entry = URL.query.filter_by(short_url=short_url).first()
    if url_entry:
        return redirect(url_entry.long_url)
    return jsonify({'error': 'URL Not Found'}), 404

if __name__ == '__main__':
    port=int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port)