import sqlite3
import geonames
import json
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, Response

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

@app.route('/cities')
def show_cities():
    return jsonify(**CITYDATA)

@app.route('/countries')
def show_countries():
    return jsonify(**COUNTRYDATA)

@app.route('/nearest')
def find_nearest():
    lat = float(request.args.get('latitude'))
    lng = float(request.args.get('longitude'))
    sorttype = request.args.get('sort') or 'nearest'
    bboxsize = request.args.get('size') or geonames.DEFAULT_BBOX_SIZE
    bboxsize = int(bboxsize)
    results = request.args.get('num') or 1
    results = int(results)
    bbox = geonames.make_bounding_box(bboxsize, lat, lng)
    cityids = CITYINDEX.nearest(bbox, results, objects = False)
    nearest_cities = list([CITYDATA[str(cityid)] for cityid in cityids])
    sortf = {
        'nearest' : lambda city : geonames.city_distance(lat, lng, city),
        'population' : lambda city : int(city['population'])
    }[sorttype]
    nearest_cities = sorted(nearest_cities, key = sortf)
    return Response(json.dumps([len(nearest_cities)] + nearest_cities),  mimetype='application/json')

@app.route('/intersection')
def find_intersection():
    lat = float(request.args.get('latitude'))
    lng = float(request.args.get('longitude'))
    bboxsize = request.args.get('size') or geonames.DEFAULT_BBOX_SIZE
    bboxsize = int(bboxsize)
    results = request.args.get('num') or 1
    results = int(results)
    bbox = geonames.make_bounding_box(bboxsize, lat, lng)
    cityids = CITYINDEX.intersection(bbox)
    intersection_cities = [CITYDATA[str(cityid)] for cityid in cityids]
    return Response(json.dumps([len(intersection_cities)] + intersection_cities),  mimetype='application/json')

if __name__ == '__main__':
    app.run()
