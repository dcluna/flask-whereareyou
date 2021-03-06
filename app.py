import sqlite3
import geonames
import json
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, Response
from flask.ext.googlemaps import GoogleMaps
from flask.ext.googlemaps import Map

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
CITYINDEX = geonames.index_cities(CITYDATA)

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
GoogleMaps(app)

@app.route('/cities')
def show_cities():
    return jsonify(**CITYDATA)

@app.route('/countries')
def show_countries():
    return jsonify(**COUNTRYDATA)

def get_nearest_cities(request):
    lat = float(request.args.get('latitude'))
    lng = float(request.args.get('longitude'))
    sorttype = request.args.get('sort') or 'nearest'
    bboxsize = request.args.get('size') or geonames.DEFAULT_BBOX_SIZE
    bboxsize = int(bboxsize)
    results = request.args.get('num') or 1
    results = int(results)
    querymethod = request.args.get('method') or 'nearest'
    bbox = geonames.make_bounding_box(bboxsize, lat, lng)
    if querymethod == 'nearest':
        cityids = CITYINDEX.nearest(bbox, results, objects = False)
    elif querymethod == 'intersection':
        cityids = CITYINDEX.intersection(bbox)
    nearest_cities = list([CITYDATA[str(cityid)] for cityid in cityids])
    sortf = {
        'nearest' : lambda city : geonames.city_distance(lat, lng, city),
        'population' : lambda city : int(city['population'])
    }[sorttype]
    nearest_cities = sorted(nearest_cities, key = sortf, reverse=True)
    return nearest_cities[0:results]

@app.route('/nearest.json')
def find_nearest():
    nearest_cities = get_nearest_cities(request)
    return Response(json.dumps([len(nearest_cities)] + nearest_cities),  mimetype='application/json')

@app.route('/')
def show_nearest():
    nearest_cities = get_nearest_cities(request)
    cities = Map(
        identifier="cities",
        lat=float(request.args.get('latitude')),
        lng=float(request.args.get('longitude')),
        markers=[geonames.city_coords(city) for city in nearest_cities]
    )
    return render_template('layout.html', cities=cities)



if __name__ == '__main__':
    app.run()
