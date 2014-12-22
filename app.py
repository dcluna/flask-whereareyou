import sqlite3
import geonames
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify

# configuration
DATABASE = '/tmp/dimagi.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

COUNTRYDATA = geonames.load_country_data()
CITYDATA = geonames.load_city_data()

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/cities')
def show_cities():
    return jsonify(**CITYDATA)

@app.route('/countries')
def show_countries():
    return jsonify(**COUNTRYDATA)

if __name__ == '__main__':
    app.run()
