from rtree import index
import decimal
import math
# getting all data from geonames
COUNTRYINFO = "/home/dancluna/code/python/dimagi/lastround/geonames-data/countryInfoPP.txt"

COUNTRYHEADERS = ["ISO","ISO3","ISO-Numeric","fips","Country","Capital","Area(in sq km)","Population","Continent","tld","CurrencyCode","CurrencyName","Phone","Postal Code Format","Postal Code Regex","Languages","geonameid","neighbours","EquivalentFipsCode"]

def load_data_file(filename, headers, indexkey='geonameid', spatialindex = None):
    filedata = {}
    for line in open(filename):
        split = line.rstrip('\n').split('\t')
        assert len(headers) == len(split)
        filedict = dict(zip(headers, split))
        filedata[filedict[indexkey]] = filedict
        assert spatialindex is None or spatialindex is index.Index
    return filedata

def load_country_data():
    return load_data_file(COUNTRYINFO, COUNTRYHEADERS)

# loading city data
# The main 'geoname' table has the following fields :
# ---------------------------------------------------
# geonameid         : integer id of record in geonames database
# name              : name of geographical point (utf8) varchar(200)
# asciiname         : name of geographical point in plain ascii characters, varchar(200)
# alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
# latitude          : latitude in decimal degrees (wgs84)
# longitude         : longitude in decimal degrees (wgs84)
# feature class     : see http://www.geonames.org/export/codes.html, char(1)
# feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
# country code      : ISO-3166 2-letter country code, 2 characters
# cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 60 characters
# admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
# admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
# admin3 code       : code for third level administrative division, varchar(20)
# admin4 code       : code for fourth level administrative division, varchar(20)
# population        : bigint (8 byte int) 
# elevation         : in meters, integer
# dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
# timezone          : the timezone id (see file timeZone.txt) varchar(40)
# modification date : date of last modification in yyyy-MM-dd format

CITYINFO = "/home/dancluna/code/python/dimagi/lastround/geonames-data/cities15000PP.txt"

CITYHEADERS = ["geonameid","name","asciiname","alternatenames","latitude","longitude","feature class","feature code","country code","cc2","admin1 code","admin2 code","admin3 code","admin4 code","population","elevation","dem","timezone","modification date"]

def make_bounding_box(s, centerx=0, centery=0):
    """Makes a bounding box with the given coordinates"""
    # result must be in the form: (left, bottom, right, top)
    return [ centerx - s/2, centery - s/2, centerx + s/2, centery + s/2 ]

def load_city_data():
    return load_data_file(CITYINFO, CITYHEADERS)

# COUNTRYDATA = load_country_data()
# CITYDATA = load_city_data()

DEFAULT_BBOX_SIZE = 0

def index_cities(citydata, bbox_size = DEFAULT_BBOX_SIZE):
    sptidx = index.Index()
    for city in citydata.values():
        lat = float(city['latitude'])
        lng = float(city['longitude'])
        bbox = make_bounding_box(bbox_size, lat, lng)
        geoid = city['geonameid']
        sptidx.insert(int(geoid), bbox)
    return sptidx

def city_distance(lat, lng, city): # not the best metric but it'll do to sort...
    """Euclidean distance between a city and a pair of lat/lng"""
    return math.sqrt((lat - float(city['latitude'])) ** 2 + (lng - float(city['longitude'])) ** 2)

def city_coords(city):
    """Returns the given city's latitude and longitude as a tuple"""
    return (float(city['latitude']), float(city['longitude']))

# city = CITYDATA.values()[0]

# print city_distance(0, 0, city)
        
